#!/usr/bin/env python3
"""Gate-off runs of the fully loaded 6,400-sample pair (ANALYSIS_ADDENDUM section 4c, applied to the fully loaded runs by section 25).

Mirrors analysis_P of paper_reanalysis.py (metrics imported): (1) gate-off minus default per checkpoint; (2) Golden minus
Flooded without the gate; (3) the model x controller interaction as the paired difference of differences, with the first
default pass and with the two-pass mean as the default arm; (4) the difference of differences between the two default
passes as the noise reference. Added to the endpoints of section 4c, as in sections 7, 8 and 12 of the first series:
near-stationary plan rate, blocked time, standstill outside blocked time, crawling.
All of this is exploratory; the reading fixed in section 4c is unchanged.

Usage: .venv/bin/python scripts/evaluation/fullload_gateoff_analysis.py [--partial]
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
        'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full',
        'GN': 'model_matrix_golden_6400_nogate_full', 'FN': 'model_matrix_flooded_6400_nogate_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_gateoff_results.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--partial', action='store_true', help='print the look on the routes scored so far; nothing is written')
    a = ap.parse_args()
    arms = {k: fa.load_arm(t)[0] for k, t in TAGS.items()}
    um = pr.u_metrics()
    M = {**pr.P_METRICS, 'plan_rate_L<1.5_pct': pr.T_METRICS['plan_rate_L<1.5_pct'], 'time_blocked_pct': um['time_blocked_pct'],
         'standstill_without_blocked_pct': um['standstill_without_blocked_pct'], 'crawl_pct_0.1_to_1.0': pr.X_METRICS['crawl_pct_0.1_to_1.0']}
    res = {'label': 'ANALYSIS_ADDENDUM section 4c applied to the fully loaded runs; exploratory', 'tags': TAGS,
           'routes_counted': {k: len(v) for k, v in arms.items()}}
    v = lambda n, fn, rs: np.array([fn(arms[n][r]) for r in rs], dtype=np.float64)
    p1 = {}
    for name, (ng, d1, d2) in {'Golden-6400': ('GN', 'G1', 'G2'), 'Flooded-6400': ('FN', 'F1', 'F2')}.items():
        rs = [r for r in pr.CANONICAL_44 if r in arms[ng]]
        if len(rs) < 5:
            p1[name] = {'n_routes': len(rs)}
            continue
        p1[name] = {'n_routes': len(rs),
                    'gate-off minus first default pass': {k: pr.paired(v(ng, fn, rs), v(d1, fn, rs)) for k, fn in M.items()},
                    'gate-off minus mean of the two default passes': {k: pr.paired(v(ng, fn, rs), (v(d1, fn, rs) + v(d2, fn, rs)) / 2) for k, fn in M.items()},
                    'n_ended_by_60s_rule': {x: int(v(x, pr.ended_by_60s_rule, rs).sum()) for x in (ng, d1, d2)},
                    'collision_events_total': {x: float(v(x, M['collision_events'], rs).sum()) for x in (ng, d1, d2)},
                    'routes_completed': {x: int(sum(arms[x][r]['status'] in ('Completed', 'Perfect') for r in rs)) for x in (ng, d1, d2)}}
    res['(1) gate-off minus default, per checkpoint'] = p1
    rs = [r for r in pr.CANONICAL_44 if r in arms['GN'] and r in arms['FN']]
    res['routes_in_both_gate_off_runs'] = len(rs)
    complete = len(rs) == 44
    if len(rs) >= 5:
        res['(2) Golden minus Flooded, gate-off'] = {k: pr.paired(v('GN', fn, rs), v('FN', fn, rs)) for k, fn in M.items()}
        d = v('GN', M['time_blocked_pct'], rs) - v('FN', M['time_blocked_pct'], rs)
        res['(2) Golden minus Flooded, gate-off']['time_blocked_pct']['sign_flip_permutation'] = pr.perm_signflip(d)
        res['(2b) Golden minus Flooded, mean of the two default passes, same routes'] = {
            k: pr.paired((v('G1', fn, rs) + v('G2', fn, rs)) / 2, (v('F1', fn, rs) + v('F2', fn, rs)) / 2) for k, fn in M.items()}
        ik = [k for k in M if k.startswith('standstill_pct_v<')] + ['mean_speed_mps', 'plan_rate_L<1.5_pct', 'time_blocked_pct',
                                                                  'standstill_without_blocked_pct', 'crawl_pct_0.1_to_1.0', 'driving_score', 'route_completion']
        gn = lambda k: v('GN', M[k], rs) - v('FN', M[k], rs)
        res['(3) interaction (G_nogate - F_nogate) - (G_default - F_default), default = first pass'] = {
            k: pr.paired(gn(k), v('G1', M[k], rs) - v('F1', M[k], rs)) for k in ik}
        res['(3) interaction, default = mean of the two passes'] = {
            k: pr.paired(gn(k), (v('G1', M[k], rs) + v('G2', M[k], rs)) / 2 - (v('F1', M[k], rs) + v('F2', M[k], rs)) / 2) for k in ik}
        res['(4) noise reference (G_run2 - F_run2) - (G_run1 - F_run1)'] = {
            k: pr.paired(v('G2', M[k], rs) - v('F2', M[k], rs), v('G1', M[k], rs) - v('F1', M[k], rs)) for k in ik}

    def show(k, p):
        if not isinstance(p.get('bca95'), (list, tuple)):
            print(f"    {k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, no interval, n {p['n']}")
            return
        print(f"    {k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {[round(x, 2) for x in p['bca95']]}, p {p['wilcoxon']['p']:.3g}, n {p['n']}")
    print(json.dumps(res['routes_counted']))
    for name, o in p1.items():
        for sec in ('gate-off minus first default pass', 'gate-off minus mean of the two default passes'):
            if sec in o:
                print(name, sec)
                for k, p in o[sec].items():
                    show(k, p)
        print('  ', {k: o[k] for k in ('n_ended_by_60s_rule', 'collision_events_total', 'routes_completed') if k in o})
    for sec in [k for k in res if k.startswith('(2') or k.startswith('(3') or k.startswith('(4')]:
        print(sec, f"({len(rs)} routes)")
        for k, p in res[sec].items():
            show(k, p)
    if not complete or a.partial:
        print('nothing written (incomplete or --partial)')
        return
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
