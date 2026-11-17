#!/usr/bin/env python3
"""Stage 1 of the closed-loop evaluation of the fully loaded checkpoints (ANALYSIS_ADDENDUM section 25).

Golden-6400 against Flooded-6400 (schedule-matched), 44 routes, default controller, checkpoints served by the
full-loading model server. Statistics, definitions and code are those of paper_reanalysis.py (imported, not copied):
paired by route, Golden minus Flooded, 95 % BCa interval (20,000 resamples, seed 0), two-sided Wilcoxon signed-rank.

  F1 (primary)  share of logged steps with predicted extent L < 1.5 m
  F2            share of route time below 0.1 m/s, read by the cases of the H2 pre-specification
  descriptive   stay-put shares, standstill outside blocked time, blocked time (sign-flip permutation test),
                crawling, Driving Score, route completion, collision events; next to the partly loaded models

A route counts only if it has a score and a provenance record with a clean loading report (416 tensors in the
file, none left unpatched, largest difference 0 between memory and file). The tests use the routes that count
in both arms.

Usage: .venv/bin/python scripts/evaluation/fullload_analysis.py [--out docs/provenance/fullload_stage1_results.json]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import paper_reanalysis as pr  # noqa: E402

TAGS = {'Golden-6400 full': 'model_matrix_golden_6400_full', 'Flooded-6400-Matched full': 'model_matrix_flooded_6400_full'}
SERVED = {'Golden-6400 full': pr.G64, 'Flooded-6400-Matched full': pr.FM}


def loading_ok(d):
    """True if the provenance record of the route carries a clean loading report of the full-loading server."""
    try:
        e = json.load(open(d / 'run_provenance.json'))['expert_loading']
        return (e['tensors_in_file'] == 416 and not e['expert_tensors_left_unpatched']
                and e['largest_difference_memory_vs_file'] == 0)
    except Exception:
        return False


def load_arm(tag, require_loading=True):
    arm, skipped = {}, {}
    for r in pr.CANONICAL_44:
        d = pr.usable_dir(tag, r)
        if d is None:
            skipped[r] = 'no usable score or step log'
            continue
        if require_loading and not loading_ok(d):
            skipped[r] = 'no clean loading report in run_provenance.json'
            continue
        try:
            arm[r] = pr.parse_route_dirs(d, d, f'{tag} {r}', tolerate_partial_last_line=True)
        except Exception as e:
            skipped[r] = f'{type(e).__name__}: {e}'
    return arm, skipped


def cond_share(arm, routes, num_fn, cond_fn):
    """route -> (numerator steps, conditioning steps)."""
    out = {}
    for r in routes:
        rd = arm[r]
        c = cond_fn(rd)
        out[r] = (int(np.sum(num_fn(rd) & c)), int(np.sum(c)))
    return out


def paired_cond(tg, tf, routes):
    use = [r for r in routes if tg[r][1] >= pr.V_MIN and tf[r][1] >= pr.V_MIN]
    if len(use) < 5:
        return {'n': len(use), 'note': 'fewer than 5 routes with 20 conditioning steps in both arms'}
    return pr.paired([100.0 * tg[r][0] / tg[r][1] for r in use], [100.0 * tf[r][0] / tf[r][1] for r in use])


def descriptives(G, F, routes):
    v = lambda arm, fn: np.array([fn(arm[r]) for r in routes], dtype=np.float64)
    um = pr.u_metrics()
    out = {}
    plain = {'standstill_without_blocked_pct': um['standstill_without_blocked_pct'], 'time_blocked_pct': um['time_blocked_pct'],
             'crawl_pct_0.1_to_1.0': pr.X_METRICS['crawl_pct_0.1_to_1.0'],
             'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion'],
             'collision_events': pr.RUN_METRICS['collision_events'], 'mean_speed_mps': pr.RUN_METRICS['mean_speed_mps'],
             'n_steps': pr.RUN_METRICS['n_steps'], 'ended_by_60s_rule': pr.ended_by_60s_rule,
             'plan_rate_L<0.64_pct': pr.T_METRICS['plan_rate_L<0.64_pct']}
    for k, fn in plain.items():
        out[k] = pr.paired(v(G, fn), v(F, fn))
    d = v(G, um['time_blocked_pct']) - v(F, um['time_blocked_pct'])
    out['time_blocked_pct']['sign_flip_permutation'] = pr.perm_signflip(d)
    L, sp = (lambda rd: np.asarray(rd['L'])), (lambda rd: np.asarray(rd['speed']))
    cond = {'stays_put_at_0.5_or_less (L<0.64)': (lambda rd: L(rd) < 0.64, lambda rd: sp(rd) <= 0.5),
            'stays_put_at_rest (L<0.64, v<0.1)': (lambda rd: L(rd) < 0.64, lambda rd: sp(rd) < 0.1),
            'starts_moving_at_0.5_or_less (L>=2.0)': (lambda rd: L(rd) >= 2.0, lambda rd: sp(rd) <= 0.5)}
    for k, (num, c) in cond.items():
        tg, tf = cond_share(G, routes, num, c), cond_share(F, routes, num, c)
        out[k] = paired_cond(tg, tf, routes)
        out[k]['pooled_over_steps_pct'] = {'first': 100.0 * sum(x[0] for x in tg.values()) / max(1, sum(x[1] for x in tg.values())),
                                           'second': 100.0 * sum(x[0] for x in tf.values()) / max(1, sum(x[1] for x in tf.values()))}
    out['totals'] = {'collision_events': {'first': float(v(G, pr.RUN_METRICS['collision_events']).sum()),
                                          'second': float(v(F, pr.RUN_METRICS['collision_events']).sum())},
                     'routes_completed': {'first': int(sum(G[r]['status'] in ('Completed', 'Perfect') for r in routes)),
                                          'second': int(sum(F[r]['status'] in ('Completed', 'Perfect') for r in routes))}}
    return out


def f2_reading(p):
    d, lo, hi = p['mean_diff'], p['bca95'][0], p['bca95'][1]
    if d >= 0:
        return 'not shown (point estimate 0 or positive)'
    if hi < 0:
        return 'strong (interval below 0, point estimate at most -4.0 pp)' if d <= -4.0 else 'partial (interval below 0, point estimate above -4.0 pp)'
    return 'inconclusive (negative point estimate, interval includes 0)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(pr.ROOT / 'docs/provenance/fullload_stage1_results.json'))
    ap.add_argument('--dry-run-tags', default='',
                    help='test of the code path only: "golden_tag,flooded_tag" of earlier runs, without the loading requirement; nothing is written')
    a = ap.parse_args()
    tags, require = dict(TAGS), True
    if a.dry_run_tags:
        g, f = a.dry_run_tags.split(',')
        tags, require = {'Golden-6400 full': g, 'Flooded-6400-Matched full': f}, False
    (G, skG), (F, skF) = load_arm(tags['Golden-6400 full'], require), load_arm(tags['Flooded-6400-Matched full'], require)
    routes = [r for r in pr.CANONICAL_44 if r in G and r in F]
    res = {'label': 'ANALYSIS_ADDENDUM section 25, Stage 1; rules committed on 17 Nov 2026 at 22:17, before any route of a fully loaded checkpoint',
           'tags': tags, 'routes_counted': {'Golden-6400 full': len(G), 'Flooded-6400-Matched full': len(F), 'in_both': len(routes)},
           'routes_not_counted': {'Golden-6400 full': skG, 'Flooded-6400-Matched full': skF}}
    if len(routes) < 44:
        res['status'] = f'incomplete: {len(routes)} of 44 routes count in both arms'
    if len(routes) >= 5:
        v = lambda arm, fn: np.array([fn(arm[r]) for r in routes], dtype=np.float64)
        f1 = pr.paired(v(G, pr.T_METRICS['plan_rate_L<1.5_pct']), v(F, pr.T_METRICS['plan_rate_L<1.5_pct']), routes=routes)
        f2 = pr.paired(v(G, pr.RUN_METRICS['standstill_pct']), v(F, pr.RUN_METRICS['standstill_pct']), routes=routes)
        p1, p2 = f1['wilcoxon']['p'], f2['wilcoxon']['p']
        lo, hi = sorted([p1, p2])
        holm = {lo: min(1.0, 2 * lo), hi: min(1.0, max(2 * lo, hi))}
        f1['p_holm_over_F1_F2'], f2['p_holm_over_F1_F2'] = holm[p1], holm[p2]
        f1['decision'] = 'met' if (f1['mean_diff'] < 0 and f1['bca95'][1] < 0 and p1 < 0.05) else 'not met'
        f2['reading'] = f2_reading(f2)
        res['F1 primary: share of steps with L < 1.5 m, Golden minus Flooded'] = f1
        res['F2: standstill time (v < 0.1 m/s), Golden minus Flooded'] = f2
        res['descriptive'] = descriptives(G, F, routes)
        if not a.dry_run_tags:
            # the same quantities for the partly loaded models (first pass), on the same routes
            Gs = {r: pr.load_route(SERVED['Golden-6400 full'], r) for r in routes}
            Fs = {r: pr.load_route(SERVED['Flooded-6400-Matched full'], r) for r in routes}
            res['partly_loaded_models_first_pass_same_routes'] = {
                'share of steps with L < 1.5 m': pr.paired(v(Gs, pr.T_METRICS['plan_rate_L<1.5_pct']), v(Fs, pr.T_METRICS['plan_rate_L<1.5_pct'])),
                'standstill time': pr.paired(v(Gs, pr.RUN_METRICS['standstill_pct']), v(Fs, pr.RUN_METRICS['standstill_pct'])),
                'descriptive': descriptives(Gs, Fs, routes)}
            res['full_minus_partly_loaded'] = {
                name: {k: pr.paired(v(full, fn), v(served, fn)) for k, fn in
                       {'share of steps with L < 1.5 m': pr.T_METRICS['plan_rate_L<1.5_pct'], 'standstill time': pr.RUN_METRICS['standstill_pct'],
                        'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion']}.items()}
                for name, full, served in (('Golden-6400', G, Gs), ('Flooded-6400-Matched', F, Fs))}

    def show(k, p):
        print(f"{k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {[round(x, 2) for x in p['bca95']]}, "
              f"p {p['wilcoxon']['p']:.3g}, n {p['n']}  {p.get('decision', p.get('reading', ''))}")
    print(json.dumps(res['routes_counted']), res.get('status', 'complete'))
    for k in res:
        if k.startswith(('F1', 'F2')):
            show(k, res[k])
    for k, p in res.get('descriptive', {}).items():
        if 'bca95' in p:
            show(k, p)
    if a.dry_run_tags:
        print('dry run: nothing written')
        return
    Path(a.out).write_text(json.dumps(res, indent=1) + '\n')
    print('written', a.out)


if __name__ == '__main__':
    main()
