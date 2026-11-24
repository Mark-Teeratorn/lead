#!/usr/bin/env python3
"""Sensitivity and pass-to-pass variation of the fully loaded 6,400-sample pair (ANALYSIS_ADDENDUM section 34;
post hoc, descriptive).

  (a) F1 and F2 on the 37 routes not touched by training samples and on the 24 routes not used to tune the controller
  (b) per checkpoint: SD of the per-route difference between the two passes and ICC(1,1), for standstill time,
      near-stationary plans and Driving Score

Usage: .venv/bin/python scripts/evaluation/fullload_sensitivity.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G1': 'model_matrix_golden_6400_full', 'F1': 'model_matrix_flooded_6400_full',
        'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_sensitivity.json'
M = {'F1 share of steps with L < 1.5 m': pr.T_METRICS['plan_rate_L<1.5_pct'], 'F2 standstill time': pr.RUN_METRICS['standstill_pct']}


def main():
    arms = {}
    for k, tag in TAGS.items():
        arms[k], sk = fa.load_arm(tag)
        if len(arms[k]) != 44:
            sys.exit(f'{tag}: {len(arms[k])} of 44 routes ({sk})')
    tuned = {str(r) for r in json.load(open(pr.ROOT / 'docs/provenance/paper_reanalysis_manifest.json'))['H']['tuning_routes_union']}
    subsets = {'44 routes': list(pr.CANONICAL_44),
               '37 routes not touched by training samples': [r for r in pr.CANONICAL_44 if r not in pr.OVERLAP_7],
               '24 routes not used to tune the controller': [r for r in pr.CANONICAL_44 if r not in tuned]}
    v = lambda k, fn, rs: np.array([fn(arms[k][r]) for r in rs], dtype=np.float64)
    res = {'label': 'ANALYSIS_ADDENDUM section 34; post hoc, descriptive', 'tags': TAGS, 'a_route_subsets': {}, 'b_pass_to_pass': {}}
    for sname, rs in subsets.items():
        out = {'n_routes': len(rs), 'routes': rs}
        for mname, fn in M.items():
            out[mname] = {'first pass': pr.paired(v('G1', fn, rs), v('F1', fn, rs)),
                          'second pass': pr.paired(v('G2', fn, rs), v('F2', fn, rs)),
                          'mean of the two passes': pr.paired((v('G1', fn, rs) + v('G2', fn, rs)) / 2, (v('F1', fn, rs) + v('F2', fn, rs)) / 2)}
        res['a_route_subsets'][sname] = out
    R = pr.CANONICAL_44
    for name, (a, b) in {'Golden-6400': ('G1', 'G2'), 'Flooded-6400': ('F1', 'F2')}.items():
        res['b_pass_to_pass'][name] = {
            mname: {'sd_of_route_difference': float(np.std(v(b, fn, R) - v(a, fn, R), ddof=1)), 'icc_1_1': pr.icc_1_1(v(a, fn, R), v(b, fn, R)),
                    'mean_first_pass': float(v(a, fn, R).mean()), 'mean_second_pass': float(v(b, fn, R).mean())}
            for mname, fn in {**M, 'Driving Score': pr.RUN_METRICS['driving_score']}.items()}
    for sname, out in res['a_route_subsets'].items():
        for mname in M:
            for pname, p in out[mname].items():
                print(f"{sname} | {mname} | {pname}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, "
                      f"CI {[round(x, 2) for x in p['bca95']]}, p {p['wilcoxon']['p']:.3g}, n {p['n']}")
    print(json.dumps(res['b_pass_to_pass'], indent=1))
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
