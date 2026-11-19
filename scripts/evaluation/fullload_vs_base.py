#!/usr/bin/env python3
"""Fully loaded 6,400-sample checkpoints against Base-Rerun in closed loop (ANALYSIS_ADDENDUM section 26; post hoc, descriptive).

Paired over the 44 routes; statistics and definitions of paper_reanalysis.py (imported).
Usage: .venv/bin/python scripts/evaluation/fullload_vs_base.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fullload_analysis as fa  # noqa: E402
import paper_reanalysis as pr  # noqa: E402

BASE_TAG = 'base_run2'
OUT = pr.ROOT / 'docs/provenance/fullload_vs_base_results.json'


def main():
    B, skB = fa.load_arm(BASE_TAG, require_loading=False)
    res = {'label': 'ANALYSIS_ADDENDUM section 26; post hoc, descriptive; fully loaded checkpoint minus Base-Rerun', 'base_tag': BASE_TAG,
           'base_routes_not_counted': skB}
    L, sp = (lambda rd: np.asarray(rd['L'])), (lambda rd: np.asarray(rd['speed']))
    plain = {'driving_score': pr.RUN_METRICS['driving_score'], 'route_completion': pr.RUN_METRICS['route_completion'],
             'standstill_pct': pr.RUN_METRICS['standstill_pct'], 'plan_rate_L<1.5_pct': pr.T_METRICS['plan_rate_L<1.5_pct'],
             'collision_events': pr.RUN_METRICS['collision_events'], 'mean_speed_mps': pr.RUN_METRICS['mean_speed_mps']}
    for name, tag in fa.TAGS.items():
        A, skA = fa.load_arm(tag, require_loading=True)
        routes = [r for r in pr.CANONICAL_44 if r in A and r in B]
        v = lambda arm, fn: np.array([fn(arm[r]) for r in routes], dtype=np.float64)
        out = {'n_routes': len(routes), 'routes_not_counted': skA}
        for k, fn in plain.items():
            out[k] = pr.paired(v(A, fn), v(B, fn))
        ta = fa.cond_share(A, routes, lambda rd: L(rd) < 0.64, lambda rd: sp(rd) <= 0.5)
        tb = fa.cond_share(B, routes, lambda rd: L(rd) < 0.64, lambda rd: sp(rd) <= 0.5)
        out['stays_put_at_0.5_or_less (L<0.64)'] = fa.paired_cond(ta, tb, routes)
        out['totals'] = {'collision_events': {'first': float(v(A, plain['collision_events']).sum()), 'second': float(v(B, plain['collision_events']).sum())},
                         'routes_completed': {'first': int(sum(A[r]['status'] in ('Completed', 'Perfect') for r in routes)),
                                              'second': int(sum(B[r]['status'] in ('Completed', 'Perfect') for r in routes))}}
        res[f'{name} minus Base-Rerun'] = out
        print(name, 'minus Base-Rerun, n', len(routes), out['totals'])
        for k, p in out.items():
            if isinstance(p, dict) and 'bca95' in p:
                print(f"  {k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {[round(x, 2) for x in p['bca95']]}, p {p['wilcoxon']['p']:.3g}, n {p['n']}")
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
