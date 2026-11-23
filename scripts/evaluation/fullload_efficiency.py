#!/usr/bin/env python3
"""Driving efficiency of the fully loaded checkpoints (ANALYSIS_ADDENDUM section 29; post hoc, descriptive).

  E1  time to complete (s of game time), on routes completed by every compared run
  E2  progress rate: route completion x route length / route time (m/s), 44 routes
  E3  mean speed over the steps at 0.1 m/s or more (m/s), routes with at least 20 such steps in every compared run
  also the mean infraction penalty factor (score_penalty) per run

Golden minus Flooded on the per-route mean of the two passes and on each pass alone; the decoupling checkpoint (one
pass) minus the two-pass mean of each. Statistics are those of paper_reanalysis.py (imported, not copied).

Usage: .venv/bin/python scripts/evaluation/fullload_efficiency.py
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
        'D': 'model_matrix_fgbalanced_6400_full'}
OUT = pr.ROOT / 'docs/provenance/fullload_efficiency.json'
DONE = ('Completed', 'Perfect')


def moving_speed(rd):
    s = np.asarray(rd['speed'])
    return float(np.mean(s[s >= 0.1]))


def n_moving(rd):
    return int(np.sum(np.asarray(rd['speed']) >= 0.1))


E = {'E1 time to complete (s)': lambda rd: rd['duration_game'],
     'E2 progress rate (m/s)': lambda rd: rd['rc'] / 100.0 * rd['route_length'] / rd['duration_game'],
     'E3 speed while moving (m/s)': moving_speed,
     'penalty factor': lambda rd: rd['penalty']}


def main():
    arms = {}
    for k, tag in TAGS.items():
        arms[k], skipped = fa.load_arm(tag)
        if len(arms[k]) != 44:
            sys.exit(f'{tag}: {len(arms[k])} of 44 routes count ({skipped})')

    def routes_for(name, runs):
        if name.startswith('E1'):
            return [r for r in pr.CANONICAL_44 if all(arms[a][r]['status'] in DONE for a in runs)]
        if name.startswith('E3'):
            return [r for r in pr.CANONICAL_44 if all(n_moving(arms[a][r]) >= pr.V_MIN for a in runs)]
        return list(pr.CANONICAL_44)

    def val(runs, fn, rs):
        return np.mean([[fn(arms[a][r]) for r in rs] for a in runs], axis=0)

    def compare(first, second):
        out = {}
        for name, fn in E.items():
            rs = routes_for(name, first + second)
            if len(rs) < 5:
                out[name] = {'n': len(rs), 'note': 'fewer than 5 routes: not computable'}
                continue
            out[name] = pr.paired(val(first, fn, rs), val(second, fn, rs))
            out[name]['routes'] = rs
        return out

    res = {'label': 'ANALYSIS_ADDENDUM section 29: driving efficiency of the fully loaded checkpoints (post hoc, descriptive)',
           'tags': TAGS,
           'Golden minus Flooded, mean of the two passes': compare(['G1', 'G2'], ['F1', 'F2']),
           'Golden minus Flooded, first pass': compare(['G1'], ['F1']),
           'Golden minus Flooded, second pass': compare(['G2'], ['F2']),
           'Decoupling minus Flooded (two-pass mean)': compare(['D'], ['F1', 'F2']),
           'Decoupling minus Golden (two-pass mean)': compare(['D'], ['G1', 'G2']),
           'routes completed': {a: int(sum(arms[a][r]['status'] in DONE for r in pr.CANONICAL_44)) for a in TAGS},
           'mean route time, all 44 routes (s)': {a: float(np.mean([arms[a][r]['duration_game'] for r in pr.CANONICAL_44])) for a in TAGS}}
    for sec, d in res.items():
        if not isinstance(d, dict) or sec in ('tags',):
            continue
        print(sec)
        for k, p in d.items():
            if isinstance(p, dict) and 'mean_diff' in p:
                b = p['bca95']
                ci = [round(x, 2) for x in b] if isinstance(b, (list, tuple)) else 'no interval'
                pv = p['wilcoxon'].get('p') if isinstance(p['wilcoxon'], dict) else None
                print(f"    {k}: {p['mean_first']:.2f} vs {p['mean_second']:.2f}, diff {p['mean_diff']:.2f}, CI {ci}, "
                      f"p {pv if pv is None else format(pv, '.3g')}, n {p['n']}")
            else:
                print(f'    {k}: {p}')
    OUT.write_text(json.dumps(res, indent=1) + '\n')
    print('written', OUT)


if __name__ == '__main__':
    main()
