#!/usr/bin/env python3
"""Readings of the second stage of the full-loading evaluation that need both passes of the 6,400-sample pair.

  (a) decoupling checkpoint loaded in full: ANALYSIS_ADDENDUM sections 6 and 15, rules unchanged. The comparators are the
      per-route means of the two default-controller passes of the fully loaded Golden-6400 and Flooded-6400; each pass
      alone and the 37 routes without training overlap are sensitivity rows. Metrics and reading logic are those of
      paper_reanalysis.py (s15_metrics, analysis_S, analysis_S15), applied to the fully loaded runs.
  (b) collision events per odometer kilometre for the two passes of the pair together (measure of manuscript Table 3;
      ratio with a percentile interval from 20,000 route resamples, seed 0). Descriptive.
  (c) extension of section 26: each pass and the two-pass mean of the fully loaded 6,400-sample checkpoints, and the one
      pass of the decoupling checkpoint, against Base-Rerun. Post hoc, descriptive.

A route counts only with a score and a clean loading report (not required for Base-Rerun, which has no fine-tuned expert).

Usage: .venv/bin/python scripts/evaluation/fullload_stage2_readings.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G1': 'model_matrix_golden_6400_full', 'F1': 'model_matrix_flooded_6400_full',
        'G2': 'model_matrix_golden_6400_run2_full', 'F2': 'model_matrix_flooded_6400_run2_full',
        'B': 'model_matrix_fgbalanced_6400_full'}
BASE_TAG = 'base_run2'
OUT = pr.ROOT / 'docs/provenance/fullload_stage2_readings.json'
COMPS = {'Flooded-6400': ('F1', 'F2'), 'Golden-6400': ('G1', 'G2')}


def main():
    arms = {k: fa.load_arm(t)[0] for k, t in TAGS.items()}
    arms['Base'] = fa.load_arm(BASE_TAG, require_loading=False)[0]
    counted = {k: len(v) for k, v in arms.items()}
    assert all(n == 44 for n in counted.values()), counted
    R44 = list(pr.CANONICAL_44)
    R37 = [r for r in R44 if r not in pr.OVERLAP_7]
    v = lambda a, fn, rs=R44: np.array([fn(arms[a][r]) for r in rs], dtype=np.float64)
    res = {'tags': {**TAGS, 'Base': BASE_TAG}, 'routes_counted': counted}

    def pair_nan(x, y):
        ok = ~np.isnan(x) & ~np.isnan(y)
        return pr.paired(x[ok], y[ok]) if int(ok.sum()) >= 5 else {'n': int(ok.sum()), 'note': 'fewer than 5 usable routes'}

    # ---- (a) decoupling checkpoint, sections 6 and 15
    M = pr.s15_metrics()
    dec = {'label': 'ANALYSIS_ADDENDUM sections 6 and 15 applied to the fully loaded runs; the decoupling checkpoint has one pass',
           'per_route_rule': f'conditional shares need at least {pr.V_MIN} conditioning steps in every pass used', 'comparisons': {}}
    for cname, names in COMPS.items():
        rows = {'mean of the two passes': names, 'first pass': names[:1], 'second pass': names[1:]}
        for row, ns in rows.items():
            for sname, rs in (('44 routes', R44), ('37 routes without training overlap', R37)):
                dec['comparisons'].setdefault(f'Balanced minus {cname}, {row}', {})[sname] = {
                    k: pair_nan(v('B', fn, rs), np.mean([v(n, fn, rs) for n in ns], axis=0)) for k, fn in M.items()}
    d1 = dec['comparisons']['Balanced minus Flooded-6400, mean of the two passes']['44 routes']
    d2 = dec['comparisons']['Balanced minus Golden-6400, mean of the two passes']['44 routes']
    inc = lambda c: c[0] <= 0 <= c[1]
    # section 6: standstill time
    cf, cg = d1['standstill_pct']['bca95'], d2['standstill_pct']['bca95']
    sep = lambda c: c[1] < 0 or c[0] > 0
    if cf[1] < 0 and not sep(cg):
        r6 = 'follows manoeuvre mix and stationary share, not the group mix'
    elif cg[0] > 0 and not sep(cf):
        r6 = 'follows the group mix'
    else:
        r6 = 'inconclusive'
    dec['section 6 reading (standstill time)'] = {'reading': r6, 'balanced_minus_flooded_bca95': cf, 'balanced_minus_golden_bca95': cg}
    # section 15: plan rate and remedy
    c1, c2 = d1['plan_rate_L<1.5_pct']['bca95'], d2['plan_rate_L<1.5_pct']['bca95']
    if c1[1] < 0 and inc(c2):
        ingredient = 'near-stationary planning follows the manoeuvre mix and the stationary share, not the scenario-group mix'
    elif c2[0] > 0 and inc(c1):
        ingredient = 'near-stationary planning follows the scenario-group mix'
    elif c1[1] < 0 and c2[0] > 0:
        ingredient = 'both contribute (the Balanced value lies between the two, both intervals exclude 0)'
    else:
        ingredient = 'inconclusive'
    f_mean, g_mean = d1['plan_rate_L<1.5_pct']['mean_second'], d2['plan_rate_L<1.5_pct']['mean_second']
    b_mean = d1['plan_rate_L<1.5_pct']['mean_first']
    cb, cd = d1['time_blocked_pct']['bca95'], d1['driving_score']['bca95']
    less, blocked_ok, score_ok = c1[1] < 0, not cb[0] > 0, not cd[1] < 0
    if less and blocked_ok and score_ok:
        remedy = 'candidate remedy for hesitation'
    elif less:
        remedy = 'reduces hesitation at a cost: ' + ', '.join(x for x, bad in (('more blocked time', not blocked_ok), ('lower Driving Score', not score_ok)) if bad)
    else:
        remedy = 'not a remedy: near-stationary plans are not clearly less frequent than for the obstacle-heavy model'
    dec['section 15 reading'] = {'D1 Balanced minus Flooded, plan rate': d1['plan_rate_L<1.5_pct']['mean_diff'], 'D1_bca95': c1,
                                 'D2 Balanced minus Golden, plan rate': d2['plan_rate_L<1.5_pct']['mean_diff'], 'D2_bca95': c2,
                                 'ingredient': ingredient,
                                 'fraction_of_flooded_minus_golden_gap_closed': (f_mean - b_mean) / (f_mean - g_mean) if f_mean != g_mean else None,
                                 'remedy': remedy}
    ce = pr.RUN_METRICS['collision_events']
    um = pr.u_metrics()
    dec['totals'] = {a: {'collision_events': float(v(a, ce).sum()),
                         'routes_completed': int(sum(arms[a][r]['status'] in ('Completed', 'Perfect') for r in R44)),
                         'routes_with_blocked_time': int((v(a, um['time_blocked_pct']) > 0).sum())} for a in list(TAGS) + ['Base']}
    res['decoupling checkpoint loaded in full'] = dec

    # ---- (b) collision events per odometer kilometre
    odo = lambda a: np.array([float(np.sum(np.asarray(arms[a][r]['speed']))) * 0.05 / 1000 for r in R44])
    per = {a: {'events': float(v(a, ce).sum()), 'odometer_km': float(odo(a).sum()), 'events_per_km': float(v(a, ce).sum() / odo(a).sum())}
           for a in list(TAGS) + ['Base']}
    gE, fE, gO, fO = v('G1', ce) + v('G2', ce), v('F1', ce) + v('F2', ce), odo('G1') + odo('G2'), odo('F1') + odo('F2')
    idx = np.random.default_rng(pr.SEED).integers(0, 44, size=(20000, 44))
    boot = (gE[idx].sum(1) / gO[idx].sum(1)) / (fE[idx].sum(1) / fO[idx].sum(1))
    res['collision events per odometer km'] = {
        'per_arm': per,
        'two passes together': {'Golden-6400': {'events': float(gE.sum()), 'odometer_km': float(gO.sum()), 'events_per_km': float(gE.sum() / gO.sum())},
                                'Flooded-6400': {'events': float(fE.sum()), 'odometer_km': float(fO.sum()), 'events_per_km': float(fE.sum() / fO.sum())},
                                'rate_ratio_golden_over_flooded': float((gE.sum() / gO.sum()) / (fE.sum() / fO.sum())),
                                'rate_ratio_ci95_percentile': [float(x) for x in np.percentile(boot, [2.5, 97.5])]}}

    # ---- (c) against Base-Rerun
    P = {'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion'],
         'standstill_pct': pr.RUN_METRICS['standstill_pct'], 'plan_rate_L<1.5_pct': pr.T_METRICS['plan_rate_L<1.5_pct'],
         'time_blocked_pct': um['time_blocked_pct'], 'collision_events': ce, 'mean_speed_mps': pr.RUN_METRICS['mean_speed_mps']}
    rows = {'Golden-6400 second pass': ('G2',), 'Golden-6400 mean of the two passes': ('G1', 'G2'),
            'Flooded-6400 second pass': ('F2',), 'Flooded-6400 mean of the two passes': ('F1', 'F2'), 'Balanced-6400 one pass': ('B',)}
    res['against Base-Rerun (extension of section 26, post hoc, descriptive)'] = {
        row: {k: pr.paired(np.mean([v(n, fn) for n in ns], axis=0), v('Base', fn)) for k, fn in P.items()} for row, ns in rows.items()}

    def show(k, p):
        if not isinstance(p.get('bca95'), (list, tuple)):
            print(f"  {k}: {p.get('mean_first', float('nan')):.2f} vs {p.get('mean_second', float('nan')):.2f}, no interval, n {p['n']}")
            return
        print(f"  {k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {[round(x, 2) for x in p['bca95']]}, p {p['wilcoxon']['p']:.3g}, n {p['n']}")
    for row in ('Balanced minus Flooded-6400, mean of the two passes', 'Balanced minus Golden-6400, mean of the two passes'):
        print(row)
        for k, p in dec['comparisons'][row]['44 routes'].items():
            show(k, p)
    print(json.dumps(dec['section 6 reading (standstill time)']), json.dumps(dec['section 15 reading']), json.dumps(dec['totals']), sep='\n')
    print(json.dumps(res['collision events per odometer km']['two passes together']))
    for row, o in res['against Base-Rerun (extension of section 26, post hoc, descriptive)'].items():
        print(row, 'minus Base-Rerun')
        for k, p in o.items():
            show(k, p)
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
