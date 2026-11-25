#!/usr/bin/env python3
"""Means per checkpoint for the summary table of the manuscript (descriptive compilation; no test).

One column per checkpoint, one row per measure, each the mean of per-route values over the 44 routes with the
definitions of the other fully loaded analyses (imported, not copied). For the two 6,400-sample checkpoints of
the main pair the value is the mean of the two passes. Nothing here is a new analysis: every value is the mean
that the paired comparisons of the result files already contain; the table only puts them side by side.

Usage: .venv/bin/python scripts/evaluation/fullload_checkpoint_table.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import fullload_b2d_efficiency as b2d  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

RUNS = {'Golden-6400': ['model_matrix_golden_6400_full', 'model_matrix_golden_6400_run2_full'],
        'Flooded-6400': ['model_matrix_flooded_6400_full', 'model_matrix_flooded_6400_run2_full'],
        'Decoupling-6400': ['model_matrix_fgbalanced_6400_full'],
        'Golden-1600': ['model_matrix_golden_1600_full'], 'Flooded-1600': ['model_matrix_flooded_1600_full'],
        'Base-Rerun': ['base_run2']}
OUT = pr.ROOT / 'docs/provenance/fullload_checkpoint_table.json'
um = pr.u_metrics()
M = {'near_stationary_plans_pct': pr.T_METRICS['plan_rate_L<1.5_pct'], 'standstill_time_pct': pr.RUN_METRICS['standstill_pct'],
     'blocked_time_pct': um['time_blocked_pct'], 'route_completion': pr.RUN_METRICS['route_completion'],
     'driving_score': pr.RUN_METRICS['driving_score'], 'collision_events_per_route': pr.RUN_METRICS['collision_events']}


def main():
    res = {'label': 'Means per checkpoint over the 44 routes (two-pass mean for the main 6,400-sample pair); descriptive compilation', 'checkpoints': {}}
    for name, tags in RUNS.items():
        arms = [fa.load_arm(t, require_loading=(name != 'Base-Rerun'))[0] for t in tags]
        routes = [r for r in pr.CANONICAL_44 if all(r in a for a in arms)]
        row = {'tags': tags, 'n_routes': len(routes), 'passes': len(tags)}
        for k, fn in M.items():
            row[k] = float(np.mean([np.mean([fn(a[r]) for a in arms]) for r in routes]))
        eff = [[b2d.route_eff(a[r])[0] for r in routes] for a in arms]
        row['b2d_driving_efficiency_per_pass'] = [float(np.mean([x for x in e if x is not None])) for e in eff]
        row['b2d_routes_with_a_record_per_pass'] = [int(sum(x is not None for x in e)) for e in eff]
        res['checkpoints'][name] = row
        print(name, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items() if k != 'tags'})
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
