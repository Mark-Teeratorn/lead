#!/usr/bin/env python3
"""The 1,600-sample pair loaded in full (ANALYSIS_ADDENDUM section 31; rules committed 23 Nov 2026, 22:29).

Golden-1600 minus Flooded-1600, 44 routes, one pass each, default controller, clean loading report required.
Statistics, definitions and code are those of paper_reanalysis.py and of the earlier fully loaded analyses
(imported, not copied): paired by route, 95 % BCa interval (20,000 resamples, seed 0), two-sided Wilcoxon.

  S1 (primary)  share of logged steps with L < 1.5 m: met if diff < 0, interval below 0, p < 0.05
  S2            share of route time below 0.1 m/s, read by the four cases of F2
  S3            Bench2Drive Driving Efficiency (section 30), routes with a record in both runs:
                met if diff > 0, interval above 0, Holm p < 0.05          (Holm over S2 and S3)
  descriptive   the other measures of sections 25 and 29; each 1,600 checkpoint against base_run2;
                size contrast: difference of the 6,400 pair (per-route mean of its two passes) minus the
                difference of the 1,600 pair, for S1, S2 and S3

Usage: .venv/bin/python scripts/evaluation/fullload_pair1600.py
       [--dry-run-tags golden_tag,flooded_tag]   test of the code path on earlier runs; nothing is written
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import fullload_b2d_efficiency as b2d  # noqa: E402
import fullload_efficiency as fe  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G16': 'model_matrix_golden_1600_full', 'F16': 'model_matrix_flooded_1600_full'}
TAGS_6400 = {'G1': 'model_matrix_golden_6400_full', 'F1': 'model_matrix_flooded_6400_full',
             'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full'}
BASE_TAG = 'base_run2'
OUT = pr.ROOT / 'docs/provenance/fullload_pair1600_results.json'
PLAN, STAND = pr.T_METRICS['plan_rate_L<1.5_pct'], pr.RUN_METRICS['standstill_pct']
eff = lambda rd: b2d.route_eff(rd)[0]


def vec(arm, fn, rs):
    return np.array([fn(arm[r]) for r in rs], dtype=np.float64)


def eff_routes(arms, rs):
    return [r for r in rs if all(eff(a[r]) is not None for a in arms)]


def efficiency_29(A, B, rs):
    """E1 to E3 and the penalty factor of section 29, first run minus second run."""
    out = {}
    for name, fn in fe.E.items():
        use = rs
        if name.startswith('E1'):
            use = [r for r in rs if A[r]['status'] in fe.DONE and B[r]['status'] in fe.DONE]
        elif name.startswith('E3'):
            use = [r for r in rs if fe.n_moving(A[r]) >= pr.V_MIN and fe.n_moving(B[r]) >= pr.V_MIN]
        out[name] = pr.paired(vec(A, fn, use), vec(B, fn, use)) if len(use) >= 5 else {'n': len(use), 'note': 'fewer than 5 routes: not computable'}
    return out


def against_base(A, B, rs):
    plain = {'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion'],
             'standstill_pct': STAND, 'plan_rate_L<1.5_pct': PLAN, 'collision_events': pr.RUN_METRICS['collision_events'],
             'mean_speed_mps': pr.RUN_METRICS['mean_speed_mps']}
    out = {k: pr.paired(vec(A, fn, rs), vec(B, fn, rs)) for k, fn in plain.items()}
    er = eff_routes([A, B], rs)
    out['b2d_driving_efficiency'] = pr.paired(vec(A, eff, er), vec(B, eff, er)) if len(er) >= 5 else {'n': len(er)}
    out['totals'] = {'collision_events': {'first': float(vec(A, plain['collision_events'], rs).sum()),
                                          'second': float(vec(B, plain['collision_events'], rs).sum())},
                     'routes_completed': {'first': int(sum(A[r]['status'] in fe.DONE for r in rs)),
                                          'second': int(sum(B[r]['status'] in fe.DONE for r in rs))}}
    return out


def show(k, p):
    if 'mean_diff' not in p:
        print(f'{k}: {p}')
        return
    b = p['bca95']
    ci = [round(x, 2) for x in b] if isinstance(b, (list, tuple)) else 'no interval'
    pv = p['wilcoxon'].get('p') if isinstance(p.get('wilcoxon'), dict) else None
    print(f"{k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {ci}, "
          f"p {pv if pv is None else format(pv, '.3g')}, n {p['n']}  {p.get('decision', p.get('reading', ''))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run-tags', default='', help='"golden_tag,flooded_tag" of earlier fully loaded runs; nothing is written')
    a = ap.parse_args()
    tags = dict(TAGS)
    if a.dry_run_tags:
        tags['G16'], tags['F16'] = a.dry_run_tags.split(',')
    (G, skG), (F, skF) = fa.load_arm(tags['G16']), fa.load_arm(tags['F16'])
    routes = [r for r in pr.CANONICAL_44 if r in G and r in F]
    res = {'label': 'ANALYSIS_ADDENDUM section 31: the 1,600-sample pair loaded in full; rules committed 23 Nov 2026, 22:29, before any value of these runs was computed',
           'tags': tags, 'routes_counted': {'Golden-1600': len(G), 'Flooded-1600': len(F), 'in_both': len(routes)},
           'routes_not_counted': {'Golden-1600': skG, 'Flooded-1600': skF}}
    if len(routes) < 5:
        sys.exit(f'{len(routes)} routes count in both runs')

    s1 = pr.paired(vec(G, PLAN, routes), vec(F, PLAN, routes), routes=routes)
    s1['decision'] = 'met' if (s1['mean_diff'] < 0 and s1['bca95'][1] < 0 and s1['wilcoxon']['p'] < 0.05) else 'not met'
    s2 = pr.paired(vec(G, STAND, routes), vec(F, STAND, routes), routes=routes)
    s2['reading'] = fa.f2_reading(s2)
    er = eff_routes([G, F], routes)
    s3 = pr.paired(vec(G, eff, er), vec(F, eff, er), routes=er)
    p2, p3 = s2['wilcoxon']['p'], s3['wilcoxon']['p']
    lo, hi = sorted([p2, p3])
    holm = {lo: min(1.0, 2 * lo), hi: min(1.0, max(2 * lo, hi))}
    s2['p_holm_over_S2_S3'], s3['p_holm_over_S2_S3'] = holm[p2], holm[p3]
    s3['decision'] = 'met' if (s3['mean_diff'] > 0 and s3['bca95'][0] > 0 and holm[p3] < 0.05) else 'not met'
    res['S1 primary: share of steps with L < 1.5 m, Golden-1600 minus Flooded-1600'] = s1
    res['S2: standstill time (v < 0.1 m/s)'] = s2
    res['S3: Bench2Drive Driving Efficiency'] = s3
    res['per run'] = {name: {'b2d_driving_efficiency': float(np.mean([eff(arm[r]) for r in routes if eff(arm[r]) is not None])),
                             'routes_with_a_record': int(sum(eff(arm[r]) is not None for r in routes)),
                             'mean_route_time_s': float(np.mean([arm[r]['duration_game'] for r in routes]))}
                      for name, arm in (('Golden-1600', G), ('Flooded-1600', F))}
    res['descriptive'] = fa.descriptives(G, F, routes)
    res['descriptive, efficiency of section 29'] = efficiency_29(G, F, routes)

    if not a.dry_run_tags:
        B, skB = fa.load_arm(BASE_TAG, require_loading=False)
        rb = [r for r in routes if r in B]
        res['against Base-Rerun'] = {'base_tag': BASE_TAG, 'n_routes': len(rb), 'base_routes_not_counted': skB,
                                     'Golden-1600 minus Base-Rerun': against_base(G, B, rb),
                                     'Flooded-1600 minus Base-Rerun': against_base(F, B, rb)}
        big = {k: fa.load_arm(t)[0] for k, t in TAGS_6400.items()}
        rs6 = [r for r in routes if all(r in arm for arm in big.values())]
        size = {'n_routes_6400_pair': len(rs6)}
        for name, fn in (('S1 share of steps with L < 1.5 m', PLAN), ('S2 standstill time', STAND), ('S3 Bench2Drive Driving Efficiency', eff)):
            use = eff_routes([G, F, *big.values()], rs6) if name.startswith('S3') else rs6
            d64 = (vec(big['G1'], fn, use) + vec(big['G2'], fn, use)) / 2.0 - (vec(big['F1'], fn, use) + vec(big['F2'], fn, use)) / 2.0
            d16 = vec(G, fn, use) - vec(F, fn, use)
            size[name] = pr.paired(d64, d16)
            size[name]['note'] = 'first = difference of the 6,400 pair (two-pass mean), second = difference of the 1,600 pair'
        res['size contrast: 6,400 difference minus 1,600 difference'] = size

    print(json.dumps(res['routes_counted']))
    for k in res:
        if k.startswith(('S1', 'S2', 'S3')):
            show(k, res[k])
    print(json.dumps(res['per run']))
    for k, p in res['descriptive'].items():
        if isinstance(p, dict) and 'mean_diff' in p:
            show('  ' + k, p)
    print('  totals', json.dumps(res['descriptive']['totals']))
    for k, p in res['descriptive, efficiency of section 29'].items():
        show('  ' + k, p)
    for sec in ('Golden-1600 minus Base-Rerun', 'Flooded-1600 minus Base-Rerun'):
        d = res.get('against Base-Rerun', {}).get(sec, {})
        for k, p in d.items():
            if isinstance(p, dict) and 'mean_diff' in p:
                show(f'  {sec}: {k}', p)
        if d:
            print(f'  {sec}: totals', json.dumps(d['totals']))
    for k, p in res.get('size contrast: 6,400 difference minus 1,600 difference', {}).items():
        if isinstance(p, dict):
            show('  size contrast: ' + k, p)
    if a.dry_run_tags:
        print('dry run: nothing written')
        return
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
