#!/usr/bin/env python3
"""Bench2Drive Driving Efficiency of the fully loaded runs (ANALYSIS_ADDENDUM section 30; post hoc, descriptive).

Definition of the official tool (Bench2Drive tools/efficiency_smoothness_benchmark.py): per route the mean of the
percentages in the min_speed_infractions records, values above 1000 left out, routes without a record left out;
per run the mean over the remaining routes.

Usage: .venv/bin/python scripts/evaluation/fullload_b2d_efficiency.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G1': 'model_matrix_golden_6400_full', 'F1': 'model_matrix_flooded_6400_full',
        'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full',
        'D': 'model_matrix_fgbalanced_6400_full', 'GN': 'model_matrix_golden_6400_nogate_full',
        'FN': 'model_matrix_flooded_6400_nogate_full', 'B': 'base_run2'}
OUT = pr.ROOT / 'docs/provenance/fullload_b2d_efficiency.json'
PCT = re.compile(r"\b\d+\.?\d*%")  # the expression of the official tool


def route_eff(rd):
    """(efficiency or None, number of records used) for one route, as in the official tool."""
    vals = []
    for msg in rd['infractions'].get('min_speed_infractions', []):
        x = float(PCT.search(msg).group().rstrip('%'))
        if x > 1000:
            continue
        vals.append(x)
    return (sum(vals) / len(vals) if vals else None), len(vals)


def main():
    eff, nrec = {}, {}
    for k, tag in TAGS.items():
        arm, skipped = fa.load_arm(tag, require_loading=(k != 'B'))
        if len(arm) != 44:
            sys.exit(f'{tag}: {len(arm)} of 44 routes count ({skipped})')
        e = {r: route_eff(arm[r]) for r in pr.CANONICAL_44}
        eff[k] = {r: v[0] for r, v in e.items()}
        nrec[k] = {r: v[1] for r, v in e.items()}

    def compare(first, second):
        runs = first + second
        rs = [r for r in pr.CANONICAL_44 if all(eff[a][r] is not None for a in runs)]
        if len(rs) < 5:
            return {'n': len(rs), 'note': 'fewer than 5 routes: not computable'}
        v = lambda group: np.mean([[eff[a][r] for r in rs] for a in group], axis=0)
        return pr.paired(v(first), v(second))

    res = {'label': 'ANALYSIS_ADDENDUM section 30: Bench2Drive Driving Efficiency (official definition), post hoc, descriptive',
           'tags': TAGS,
           'per run': {k: {'driving_efficiency': float(np.mean([x for x in eff[k].values() if x is not None])),
                           'routes_with_a_record': int(sum(x is not None for x in eff[k].values())),
                           'mean_records_per_route': float(np.mean(list(nrec[k].values())))} for k in TAGS},
           'paired': {'Golden minus Flooded, mean of the two passes': compare(['G1', 'G2'], ['F1', 'F2']),
                      'Golden minus Flooded, first pass': compare(['G1'], ['F1']),
                      'Golden minus Flooded, second pass': compare(['G2'], ['F2']),
                      'Decoupling minus Flooded (two-pass mean)': compare(['D'], ['F1', 'F2']),
                      'Decoupling minus Golden (two-pass mean)': compare(['D'], ['G1', 'G2']),
                      'Golden (two-pass mean) minus Base-Rerun': compare(['G1', 'G2'], ['B']),
                      'Flooded (two-pass mean) minus Base-Rerun': compare(['F1', 'F2'], ['B']),
                      'Decoupling minus Base-Rerun': compare(['D'], ['B']),
                      'Golden gate-off minus its two-pass default mean': compare(['GN'], ['G1', 'G2']),
                      'Flooded gate-off minus its two-pass default mean': compare(['FN'], ['F1', 'F2']),
                      'Golden minus Flooded, gate-off': compare(['GN'], ['FN'])}}
    for k, v in res['per run'].items():
        print(f"{k}: efficiency {v['driving_efficiency']:.2f}, routes {v['routes_with_a_record']}, records per route {v['mean_records_per_route']:.2f}")
    for k, p in res['paired'].items():
        if 'mean_diff' not in p:
            print(f'{k}: {p}')
            continue
        b = p['bca95']
        ci = [round(x, 2) for x in b] if isinstance(b, (list, tuple)) else 'no interval'
        print(f"{k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {ci}, p {p['wilcoxon'].get('p'):.3g}, n {p['n']}")
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
