#!/usr/bin/env python3
"""Repeat test on the second pass of the fully loaded 6,400-sample pair (ANALYSIS_ADDENDUM sections 9 and 25).

Section 25, Stage 2: "Second pass of both checkpoints (repeat test with the rule of Section 9, R1 to R3, applied to
the fully loaded runs)". The rule, definitions, thresholds and statistics are those of Section 9 and of
paper_reanalysis.py (imported, not copied): run 2 only, Golden minus Flooded, paired by route, 95 % BCa interval,
two-sided Wilcoxon signed-rank test.

  R1 (primary)  share of logged steps with L < 1.5 m: replicated if diff < 0, interval below 0, p < 0.05
  R2            standstill outside blocked time: replicated if diff < 0, interval below 0, Holm p < 0.05
  R3            blocked time: replicated if diff > 0, interval above 0, Holm p < 0.05     (Holm over R2 and R3)
  no decision   standstill on run 2 alone and on the two-pass mean (case of Section 1 named), the three contrasts
                on the 37 routes without training overlap and with the settings of Section 8, two-pass means of
                the measures of Section 25, and each checkpoint's second pass against its first

A route counts only with a score and a clean loading report. The tests use the routes that count in both
second passes; the result file is written only when all 44 do (use --partial to print an incomplete look).

Usage: .venv/bin/python scripts/evaluation/fullload_repeat_test.py [--partial]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G1': 'model_matrix_golden_6400_full', 'F1': 'model_matrix_flooded_6400_full',
        'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_repeat_test_results.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--partial', action='store_true', help='print the look on the routes scored so far; nothing is written')
    a = ap.parse_args()
    arms, skipped = {}, {}
    for k, tag in TAGS.items():
        arms[k], skipped[k] = fa.load_arm(tag)
    routes = [r for r in pr.CANONICAL_44 if r in arms['G2'] and r in arms['F2']]
    both = [r for r in routes if r in arms['G1'] and r in arms['F1']]
    res = {'label': 'ANALYSIS_ADDENDUM sections 9 and 25: repeat test R1 to R3 on the second pass of the fully loaded pair',
           'tags': TAGS, 'routes_counted': {k: len(v) for k, v in arms.items()}, 'routes_in_both_second_passes': len(routes),
           'routes_not_counted': skipped}
    complete = len(routes) == 44 and len(both) == 44
    if not complete:
        res['status'] = f'incomplete: {len(routes)} of 44 routes count in both second passes'
    if len(routes) < 5:
        print(json.dumps(res['routes_counted']), res['status'])
        return
    um = pr.u_metrics()
    v = lambda arm, fn, rs: np.array([fn(arms[arm][r]) for r in rs], dtype=np.float64)
    mean2 = lambda x, y, fn, rs: (v(x, fn, rs) + v(y, fn, rs)) / 2.0
    R = {'R1 near-stationary plan rate (L < 1.5 m)': pr.T_METRICS['plan_rate_L<1.5_pct'],
         'R2 standstill without blocked time': um['standstill_without_blocked_pct'], 'R3 blocked time': um['time_blocked_pct']}
    t = {k: pr.paired(v('G2', fn, routes), v('F2', fn, routes), routes=routes) for k, fn in R.items()}
    r1, r2, r3 = (t[k] for k in R)
    p2, p3 = r2['wilcoxon']['p'], r3['wilcoxon']['p']
    lo, hi = sorted([p2, p3])
    adj = {lo: min(1.0, 2 * lo), hi: min(1.0, max(2 * lo, hi))}
    r2['p_holm_over_R2_R3'], r3['p_holm_over_R2_R3'] = adj[p2], adj[p3]
    r1['decision'] = 'replicated' if r1['mean_diff'] < 0 and r1['bca95'][1] < 0 and r1['wilcoxon']['p'] < 0.05 else 'not replicated'
    r2['decision'] = 'replicated' if r2['mean_diff'] < 0 and r2['bca95'][1] < 0 and adj[p2] < 0.05 else 'not replicated'
    r3['decision'] = 'replicated' if r3['mean_diff'] > 0 and r3['bca95'][0] > 0 and adj[p3] < 0.05 else 'not replicated'
    r3['sign_flip_permutation'] = pr.perm_signflip(v('G2', R['R3 blocked time'], routes) - v('F2', R['R3 blocked time'], routes))
    res['second pass alone, Golden minus Flooded'] = t

    ss = pr.RUN_METRICS['standstill_pct']
    s2 = pr.paired(v('G2', ss, routes), v('F2', ss, routes))
    s2['case_by_rule_of_section_1'] = pr.h2_case(s2)
    res['no decision'] = {'standstill time, second pass alone': s2}
    r37 = [r for r in routes if r not in pr.OVERLAP_7]
    res['no decision']['37 routes without training overlap, second pass alone'] = {
        k: pr.paired(v('G2', fn, r37), v('F2', fn, r37)) for k, fn in R.items()}
    res['no decision']['settings of section 8, second pass alone'] = {
        lab: {k: pr.paired(v('G2', fn, routes), v('F2', fn, routes)) for k, fn in pr.u_metrics(th, n).items()
              if k in ('time_blocked_pct', 'standstill_without_blocked_pct')} for lab, (th, n) in pr.U_SENS.items()}
    M = {**R, 'standstill time': ss, 'crawl_pct_0.1_to_1.0': pr.X_METRICS['crawl_pct_0.1_to_1.0'],
         'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion'],
         'collision_events': pr.RUN_METRICS['collision_events'], 'mean_speed_mps': pr.RUN_METRICS['mean_speed_mps']}
    res['no decision']['second pass alone, further measures'] = {
        k: pr.paired(v('G2', fn, routes), v('F2', fn, routes)) for k, fn in M.items() if k not in R}
    if both:
        tm = {k: pr.paired(mean2('G1', 'G2', fn, both), mean2('F1', 'F2', fn, both)) for k, fn in M.items()}
        tm['standstill time']['case_by_rule_of_section_1'] = pr.h2_case(tm['standstill time'])
        res['no decision']['mean of the two passes, Golden minus Flooded'] = tm
        res['no decision']['second pass minus first pass'] = {
            name: {k: pr.paired(v(b, fn, both), v(a_, fn, both)) for k, fn in M.items()}
            for name, a_, b in (('Golden-6400', 'G1', 'G2'), ('Flooded-6400-Matched', 'F1', 'F2'))}
        res['no decision']['totals'] = {
            arm: {'collision_events': float(v(arm, M['collision_events'], both).sum()),
                  'routes_completed': int(sum(arms[arm][r]['status'] in ('Completed', 'Perfect') for r in both)),
                  'routes_with_blocked_time': int((v(arm, R['R3 blocked time'], both) > 0).sum())} for arm in TAGS}

    def show(k, p):
        print(f"{k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {[round(x, 2) for x in p['bca95']]}, "
              f"p {p['wilcoxon']['p']:.3g}, n {p['n']}  {p.get('decision', p.get('case_by_rule_of_section_1', ''))}")
    print(json.dumps(res['routes_counted']), res.get('status', 'complete'))
    for k, p in t.items():
        show(k, p)
    for sec in ('standstill time, second pass alone',):
        show(sec, res['no decision'][sec])
    for k, p in res['no decision']['second pass alone, further measures'].items():
        show('  run 2: ' + k, p)
    for k, p in res['no decision'].get('mean of the two passes, Golden minus Flooded', {}).items():
        show('  two-pass mean: ' + k, p)
    for name, d in res['no decision'].get('second pass minus first pass', {}).items():
        for k, p in d.items():
            show(f'  {name} run 2 - run 1: {k}', p)
    print(json.dumps(res['no decision'].get('totals', {})))
    if not complete or a.partial:
        print('nothing written (incomplete or --partial)')
        return
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
