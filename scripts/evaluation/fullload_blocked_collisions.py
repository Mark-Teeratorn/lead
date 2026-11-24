#!/usr/bin/env python3
"""Collision events on the routes with blocked time (ANALYSIS_ADDENDUM section 35; post hoc, descriptive).

For each pass of the fully loaded 6,400-sample pair, the blocked routes are those on which Golden-6400 has blocked
time above zero in that pass. Reported for the blocked routes and for the remaining routes: number of routes,
collision events of each checkpoint, events per route, paired difference per route (statistics of
paper_reanalysis.py, imported). Definitions as in the other fully loaded analyses.

Usage: .venv/bin/python scripts/evaluation/fullload_blocked_collisions.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

PASSES = {'first pass': ('model_matrix_golden_6400_full', 'model_matrix_flooded_6400_full'),
          'second pass': ('model_matrix_golden_6400_run2_full', 'model_matrix_flooded_6400_run2_full')}
OUT = pr.ROOT / 'docs/provenance/fullload_blocked_collisions.json'
COLL = pr.RUN_METRICS['collision_events']


def block(G, F, rs):
    g = np.array([COLL(G[r]) for r in rs], dtype=np.float64)
    f = np.array([COLL(F[r]) for r in rs], dtype=np.float64)
    out = {'n_routes': len(rs), 'collision_events': {'Golden-6400': float(g.sum()), 'Flooded-6400': float(f.sum())},
           'events_per_route': {'Golden-6400': float(g.mean()) if len(rs) else None, 'Flooded-6400': float(f.mean()) if len(rs) else None},
           'routes': {r: {'Golden-6400': float(a), 'Flooded-6400': float(b)} for r, a, b in zip(rs, g, f)}}
    out['paired'] = pr.paired(g, f) if len(rs) >= 5 else {'n': len(rs), 'note': 'fewer than 5 routes'}
    return out


def main():
    blocked_pct = pr.u_metrics()['time_blocked_pct']
    res = {'label': 'ANALYSIS_ADDENDUM section 35: collision events on the routes with blocked time; post hoc, descriptive', 'passes': {}}
    for name, (tg, tf) in PASSES.items():
        (G, _), (F, _) = fa.load_arm(tg), fa.load_arm(tf)
        routes = [r for r in pr.CANONICAL_44 if r in G and r in F]
        blk = [r for r in routes if blocked_pct(G[r]) > 0]
        rest = [r for r in routes if r not in blk]
        res['passes'][name] = {'tags': [tg, tf], 'n_routes': len(routes),
                               'flooded_routes_with_blocked_time': int(sum(blocked_pct(F[r]) > 0 for r in routes)),
                               'blocked routes of Golden-6400': block(G, F, blk), 'remaining routes': block(G, F, rest)}
        for k in ('blocked routes of Golden-6400', 'remaining routes'):
            b = res['passes'][name][k]
            p = b['paired']
            ci = [round(x, 2) for x in p['bca95']] if isinstance(p.get('bca95'), (list, tuple)) else p.get('note', 'no interval')
            print(f"{name}, {k}: n {b['n_routes']}, events {b['collision_events']}, per route "
                  f"{b['events_per_route']['Golden-6400']:.2f} vs {b['events_per_route']['Flooded-6400']:.2f}, diff CI {ci}")
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
