#!/usr/bin/env python3
"""Motion-history swap test with the checkpoints loaded in full (ANALYSIS_ADDENDUM sections 11, 11-B and 32).

Outcomes, per-route rule, statistics and reading rule are those of analysis W in paper_reanalysis.py (imported,
not copied). A route counts only with a score, a step log of the history-swap agent and a clean loading report.
The result file is written only when all eight routes of both checkpoints count, or with --queue-ended.

Usage: .venv/bin/python scripts/evaluation/fullload_histswap.py [--queue-ended]
       [--dry-run-tags golden_tag,flooded_tag]   test of the code path on the first-series runs; nothing is written
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'Golden-6400 full': 'model_matrix_golden_6400_histswap_full', 'Flooded-6400-Matched full': 'model_matrix_flooded_6400_histswap_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_histswap_results.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--queue-ended', action='store_true', help='the queue has ended: use the routes that exist (addendum 11-B)')
    ap.add_argument('--dry-run-tags', default='')
    a = ap.parse_args()
    tags, require = dict(TAGS), True
    if a.dry_run_tags:
        g, f = a.dry_run_tags.split(',')
        tags, require = {'Golden-6400 full': g, 'Flooded-6400-Matched full': f}, False
    res = {'label': 'ANALYSIS_ADDENDUM sections 11, 11-B and 32: motion-history swap test, checkpoints loaded in full; exploratory, rules fixed before any such run',
           'tags': tags, 'models': {}}
    complete = True
    for model, tag in tags.items():
        runs, skipped = {}, {}
        for r in pr.REPLICATE_ROUTES:
            d = pr.ROOT / f'outputs/local_evaluation/{tag}_{r}'
            if require and not fa.loading_ok(d):
                skipped[r] = 'no clean loading report in run_provenance.json'
                continue
            v = pr.w_load(tag, r)
            if v is None:
                skipped[r] = 'no score or step log'
                continue
            runs[r] = v
        if len(runs) < len(pr.REPLICATE_ROUTES):
            complete = False
        if not runs or (len(runs) < len(pr.REPLICATE_ROUTES) and not a.queue_ended and not a.dry_run_tags):
            res['models'][model] = {'status': 'pending', 'routes_counted': len(runs), 'routes_not_counted': skipped}
            continue
        chk = {k: float(np.median(np.concatenate([v['wp1'][v['kind'] == k] for v in runs.values()])))
               if any(np.any(v['kind'] == k) for v in runs.values()) else None for k in ('moving', 'stationary')}
        out = {'n_routes': len(runs), 'routes': sorted(runs), 'routes_not_counted': skipped,
               'steps': {k: int(sum(np.sum(v['kind'] == k) for v in runs.values())) for k in ('true', 'moving', 'stationary')},
               'median_first_waypoint_distance_m': chk}
        out.update(pr.w_outcomes(runs, False))
        out['sensitivity: true-history steps directly after a swap step left out'] = pr.w_outcomes(runs, True)
        res['models'][model] = out

    for model, out in res['models'].items():
        print(model, {k: out[k] for k in ('status', 'n_routes', 'routes_counted', 'steps', 'median_first_waypoint_distance_m') if k in out})
        for sec, d in (('', out), ('  [sensitivity] ', out.get('sensitivity: true-history steps directly after a swap step left out', {}))):
            for k, o in d.items():
                if not (isinstance(o, dict) and 'pooled_swapped_pct' in o):
                    continue
                p = o['paired']
                line = f"{sec}{k}: pooled {o['pooled_swapped_pct']:.2f} vs {o['pooled_true_pct']:.2f} ({o['steps_swapped']} / {o['steps_true']} steps)"
                if 'mean_diff' in p:
                    b = p['bca95']
                    ci = [round(x, 2) for x in b] if isinstance(b, (list, tuple)) else 'no interval'
                    line += f"; per route {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {ci}, n {p['n']}"
                print('  ' + line + ('  -> ' + o['reading'] if 'reading' in o else ''))
    if a.dry_run_tags:
        print('dry run: nothing written')
        return
    if not complete and not a.queue_ended:
        print('incomplete: nothing written')
        return
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
