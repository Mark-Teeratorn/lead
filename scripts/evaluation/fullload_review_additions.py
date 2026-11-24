#!/usr/bin/env python3
"""Two descriptive additions for the fully loaded runs (ANALYSIS_ADDENDUM section 33; post hoc, no rule).

  (a) comparison rate of the position match (section 22d, function position_match unchanged)
  (b) Bench2Drive Success Rate: route completed and no infraction other than min_speed_infractions

Usage: .venv/bin/python scripts/evaluation/fullload_review_additions.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'G1': 'model_matrix_golden_6400_full', 'G2': 'model_matrix_golden_6400_run2_full',
        'F1': 'model_matrix_flooded_6400_full', 'F2': 'model_matrix_flooded_6400_run2_full',
        'D': 'model_matrix_fgbalanced_6400_full', 'GN': 'model_matrix_golden_6400_nogate_full',
        'FN': 'model_matrix_flooded_6400_nogate_full', 'G16': 'model_matrix_golden_1600_full',
        'F16': 'model_matrix_flooded_1600_full', 'B': 'base_run2'}
OUT = pr.ROOT / 'docs/provenance/fullload_review_additions.json'


def success(rd):
    return 100.0 * float(rd['status'] in ('Completed', 'Perfect')
                         and sum(len(v) for k, v in rd['infractions'].items() if k != 'min_speed_infractions') == 0)


def main():
    arms = {}
    for k, tag in TAGS.items():
        arms[k], skipped = fa.load_arm(tag, require_loading=(k != 'B'))
        if len(arms[k]) != 44:
            sys.exit(f'{tag}: {len(arms[k])} of 44 routes count ({skipped})')
    res = {'label': 'ANALYSIS_ADDENDUM section 33; post hoc, descriptive', 'tags': TAGS}
    pm = {k: pr.position_match(arms[k]) for k in TAGS if k != 'B'}
    pooled = {'long_runs': sum(x['long_standstill_runs_not_blocked'] for x in pm.values()),
              'at_collision_position': sum(x['of_these_at_collision_position_10m'] for x in pm.values()),
              'on_route_with_collision': sum(x['of_these_on_a_route_with_a_collision'] for x in pm.values())}
    pooled['match_rate_pct'] = 100.0 * pooled['at_collision_position'] / pooled['long_runs'] if pooled['long_runs'] else None
    pooled['match_rate_on_routes_with_a_collision_pct'] = (100.0 * pooled['at_collision_position'] / pooled['on_route_with_collision']
                                                           if pooled['on_route_with_collision'] else None)
    res['a_position_match'] = {'per run': pm, 'pooled over the nine fully loaded runs': pooled}
    v = lambda k: np.array([success(arms[k][r]) for r in pr.CANONICAL_44])
    res['b_success_rate'] = {'per run': {k: {'routes': int((v(k) > 0).sum()), 'pct': float(v(k).mean())} for k in TAGS},
                             'Golden-6400 minus Flooded-6400, mean of the two passes': pr.paired((v('G1') + v('G2')) / 2, (v('F1') + v('F2')) / 2)}
    for k, x in pm.items():
        print(k, json.dumps(x))
    print('pooled', json.dumps(pooled))
    print(json.dumps(res['b_success_rate']['per run']))
    p = res['b_success_rate']['Golden-6400 minus Flooded-6400, mean of the two passes']
    print(f"success, two-pass mean: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {p['bca95']}")
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
