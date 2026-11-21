#!/usr/bin/env python3
"""Where and how the fully loaded checkpoints are blocked (ANALYSIS_ADDENDUM section 28; post hoc, descriptive).

Definitions of sections 8 and 18a of paper_reanalysis.py, unchanged, applied to the fully loaded Golden-6400 (two passes)
and the fully loaded decoupling checkpoint (one pass), default controller.

Usage: .venv/bin/python scripts/evaluation/fullload_blocked_diagnosis.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

TAGS = {'Golden-6400 full, first pass': 'model_matrix_golden_6400_full', 'Golden-6400 full, second pass': 'model_matrix_golden_6400_run2_full',
        'Decoupling-6400 full': 'model_matrix_fgbalanced_6400_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_blocked_diagnosis.json'


def main():
    scen = pr.load_route_scenarios()
    res = {'label': 'ANALYSIS_ADDENDUM section 28; post hoc, descriptive', 'tags': TAGS}
    for name, tag in TAGS.items():
        arm, sk = fa.load_arm(tag)
        assert len(arm) == 44, (name, sk)
        contact, _ = pr.contact_arm(arm)
        by_scen, Ls, runs = defaultdict(int), [], []
        for x in contact['runs']:
            rd = arm[x['route']]
            i, j = x['onset_step'], x['onset_step'] + x['steps']
            L = np.asarray(rd['L'])[i:j]
            Ls.append(L)
            s = scen.get(x['route'], 'unknown') if isinstance(scen, dict) else 'unknown'
            by_scen[str(s)] += x['steps']
            runs.append({'route': x['route'], 'scenario': str(s), 'seconds': round(x['steps'] * pr.DT, 1), 'gap_m': x['gap_m'],
                         'collision_actors': x['collision_actors'], 'status': rd['status'],
                         'ends_at_last_logged_step': bool(j >= len(rd['speed']) - 1),
                         'median_L_m': float(np.median(L)), 'share_L_ge_2_pct': float(100 * np.mean(L >= 2.0))})
        allL = np.concatenate(Ls) if Ls else np.array([])
        res[name] = {k: v for k, v in contact.items() if k != 'runs'}
        res[name].update({
            'routes_with_blocked_time': len({r['route'] for r in runs}),
            'plans_during_blocked_steps': {'n_steps': int(len(allL)), 'share_L_lt_1.5_pct': float(100 * np.mean(allL < 1.5)) if len(allL) else None,
                                           'share_L_ge_2_pct': float(100 * np.mean(allL >= 2.0)) if len(allL) else None,
                                           'median_L_m': float(np.median(allL)) if len(allL) else None},
            'blocked_steps_by_scenario': dict(sorted(by_scen.items(), key=lambda kv: -kv[1])),
            'runs_ending_at_last_logged_step': int(sum(r['ends_at_last_logged_step'] for r in runs)),
            'status_of_routes_with_blocked_time': {s: int(sum(1 for r in {q['route']: q for q in runs}.values() if r['status'] == s))
                                                   for s in sorted({r['status'] for r in runs})},
            'runs': runs})
        o = res[name]
        print(name, '| runs', o['n_blocked_runs'], '| routes', o['routes_with_blocked_time'], '| at collision position', o['share_of_blocked_steps_at_collision_position_pct'],
              '| blocked % without those', round(o['mean_blocked_pct_without_runs_at_collision_position'], 2))
        print('  plans while blocked', o['plans_during_blocked_steps'], '| runs ending at last step', o['runs_ending_at_last_logged_step'], '| status', o['status_of_routes_with_blocked_time'])
        print('  by scenario', o['blocked_steps_by_scenario'])
        for r in runs:
            print('   ', r['route'], r['scenario'], r['seconds'], 's gap', None if r['gap_m'] is None else round(r['gap_m'], 1), r['collision_actors'], r['status'], 'medL', round(r['median_L_m'], 1))
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
