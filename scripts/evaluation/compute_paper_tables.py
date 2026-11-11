#!/usr/bin/env python3
"""Unified Paper Table Computation & Verification Script.

Computes all tables, disaggregated metrics, BCa bootstrap confidence intervals,
and paired Wilcoxon signed-rank tests directly from raw CARLA telemetry logs.
"""

import os
import json
import glob
import numpy as np
from pathlib import Path
from scipy import stats

ROOT_DIR = Path('/home/aimslab/lead')

CANONICAL_44 = [
    '2534', '1852', '2204', '2513', '1825', '3561', '3086', '17752', '2201', '3540',
    '1790', '3436', '2286', '23687', '23901', '23695', '2790', '2283', '23771', '2084',
    '28087', '2115', '2082', '2127', '1773', '2664', '3248', '1711', '1956', '14194',
    '17563', '3936', '28099', '2050', '2709', '26458', '2390', '2416', '14842', '3144',
    '3464', '2144', '2164', '3364'
]

STRATA_MAP = {
    'Overtaking': ['2534', '1852', '2513', '1825', '1790', '3436', '1773', '2664', '3464'],
    'Merging': ['3086', '2201', '2286', '23687', '23901', '23695', '2283', '23771', '2084', '28087', '2115', '1956', '17563', '3936', '28099', '2050'],
    'Emergency_Braking': ['2204', '3561', '17752', '3540', '2082', '2127', '3248', '1711', '14194', '2709', '2144', '2164'],
    'Traffic_Signs': ['26458', '2390', '2416', '14842', '3144'],
    'Give_Way': ['2790', '3364']
}

MODEL_PREFIXES = {
    'Base': ['base', 'alpamayo'],
    'Flooded-1600': ['model_matrix_flooded_1600'],
    'Golden-1600': ['model_matrix_golden_1600'],
    'Flooded-6400-Hist': ['model_6400'],
    'Flooded-6400-Matched': ['model_matrix_flooded_6400'],
    'Golden-6400': ['model_matrix_golden_6400']
}


def bootstrap_ci_diff(x, y, n_resamples=20000, seed=0, alpha=0.05):
    """Computes BCa bootstrap confidence interval for paired differences."""
    rng = np.random.RandomState(seed)
    diff = np.array(x) - np.array(y)
    n = len(diff)
    orig_mean = np.mean(diff)

    # Resample means
    boot_indices = rng.randint(0, n, (n_resamples, n))
    boot_means = np.mean(diff[boot_indices], axis=1)

    # Acceleration factor a via jackknife
    jack_means = np.array([np.mean(np.delete(diff, i)) for i in range(n)])
    jack_bar = np.mean(jack_means)
    num = np.sum((jack_bar - jack_means) ** 3)
    denom = 6.0 * (np.sum((jack_bar - jack_means) ** 2) ** 1.5)
    a = num / denom if denom != 0 else 0.0

    # Bias correction z0
    z0 = stats.norm.ppf(np.mean(boot_means < orig_mean))

    # BCa percentiles
    z_alpha = stats.norm.ppf(alpha / 2.0)
    z_1_minus_alpha = stats.norm.ppf(1.0 - alpha / 2.0)

    def bca_pct(z):
        p = stats.norm.cdf(z0 + (z0 + z) / (1.0 - a * (z0 + z)))
        return np.clip(p * 100.0, 0.0, 100.0)

    low_pct = bca_pct(z_alpha)
    high_pct = bca_pct(z_1_minus_alpha)

    return float(np.percentile(boot_means, low_pct)), float(np.percentile(boot_means, high_pct)), orig_mean


def load_model_data(prefix_list):
    results = {}
    for r in CANONICAL_44:
        found_dir = None
        for pref in prefix_list:
            cand = ROOT_DIR / f'outputs/local_evaluation/{pref}_{r}'
            if cand.exists() and (cand / 'checkpoint_endpoint.json').exists():
                found_dir = cand
                break
        if found_dir is None:
            continue

        endpoint_p = found_dir / 'checkpoint_endpoint.json'
        traj_p = found_dir / 'predicted_trajectories.jsonl'

        with open(endpoint_p) as f:
            d = json.load(f)
        recs = d.get('_checkpoint', {}).get('records', [])
        if not recs:
            continue
        rec = recs[0]

        scores = rec.get('scores', {})
        infractions = rec.get('infractions', {})

        col_v = len(infractions.get('collisions_vehicle', []))
        col_l = len(infractions.get('collisions_layout', []))
        col_p = len(infractions.get('collisions_pedestrian', []))

        # Read trajectory logs
        speeds, ltrajs, gates, standstill_gates = [], [], [], []
        if traj_p.exists():
            with open(traj_p) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        step_data = json.loads(line)
                        v = float(step_data.get('speed', 0.0))
                        pts = step_data.get('pred_waypoints', [])
                        if pts and len(pts) > 1:
                            l = sum(np.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) for i in range(1, len(pts)))
                        else:
                            l = 0.0
                        gate = (l < 1.5) or (v < 0.5 and l < 2.0)

                        speeds.append(v)
                        ltrajs.append(l)
                        gates.append(gate)
                        if v < 0.10:
                            standstill_gates.append(gate)
                    except Exception:
                        pass

        results[r] = {
            'ds': float(scores.get('score_composed', 0.0)),
            'rc': float(scores.get('score_route', 0.0)),
            'penalty': float(scores.get('score_penalty', 1.0)),
            'col_vehicle': col_v,
            'col_layout': col_l,
            'col_pedestrian': col_p,
            'col_total': col_v + col_l + col_p,
            'speeds': speeds,
            'ltrajs': ltrajs,
            'gates': gates,
            'standstill_gates': standstill_gates,
            'standstill_fraction': np.mean(np.array(speeds) < 0.10) if speeds else 0.0,
            'gate_fraction': np.mean(gates) if gates else 0.0,
            'gate_during_standstill': np.mean(standstill_gates) if standstill_gates else 0.0,
            'mean_speed': np.mean(speeds) if speeds else 0.0,
            'mean_ltraj': np.mean(ltrajs) if ltrajs else 0.0
        }
    return results


def main():
    print("=" * 80)
    print("UNIFIED EMPIRICAL PAPER TABLE COMPUTATION & VERIFICATION")
    print("=" * 80)

    loaded = {}
    for name, prefs in MODEL_PREFIXES.items():
        data = load_model_data(prefs)
        loaded[name] = data
        print(f"Loaded {name:<22}: {len(data)} / 44 routes present.")

    # Write summary metrics
    out_file = ROOT_DIR / 'outputs/paper_tables_unified_manifest.json'
    manifest = {}

    for name, data in loaded.items():
        if len(data) == 0:
            continue
        routes_present = sorted(data.keys())
        ds_vals = [data[r]['ds'] for r in routes_present]
        rc_vals = [data[r]['rc'] for r in routes_present]
        standstill_vals = [data[r]['standstill_fraction'] * 100.0 for r in routes_present]
        gate_vals = [data[r]['gate_fraction'] * 100.0 for r in routes_present]
        gate_ss_vals = [data[r]['gate_during_standstill'] * 100.0 for r in routes_present]

        manifest[name] = {
            'n_routes': len(routes_present),
            'mean_ds': float(np.mean(ds_vals)),
            'std_ds': float(np.std(ds_vals)),
            'mean_rc': float(np.mean(rc_vals)),
            'mean_standstill_pct': float(np.mean(standstill_vals)),
            'mean_gate_pct': float(np.mean(gate_vals)),
            'mean_gate_during_ss_pct': float(np.mean(gate_ss_vals)),
            'total_col_veh': int(sum(data[r]['col_vehicle'] for r in routes_present)),
            'total_col_lay': int(sum(data[r]['col_layout'] for r in routes_present)),
            'total_col_ped': int(sum(data[r]['col_pedestrian'] for r in routes_present)),
            'total_col_all': int(sum(data[r]['col_total'] for r in routes_present)),
            'strata_standstill_pct': {}
        }

        # Strata calculations
        for sname, sroutes in STRATA_MAP.items():
            s_ss = [data[r]['standstill_fraction'] * 100.0 for r in sroutes if r in data]
            manifest[name]['strata_standstill_pct'][sname] = float(np.mean(s_ss)) if s_ss else 0.0

        # Open Maneuvers (Overtaking + Merging, 25 routes)
        maneuver_routes = STRATA_MAP['Overtaking'] + STRATA_MAP['Merging']
        m_ss = [data[r]['standstill_fraction'] * 100.0 for r in maneuver_routes if r in data]
        manifest[name]['strata_standstill_pct']['Open_Maneuver_25'] = float(np.mean(m_ss)) if m_ss else 0.0

    # Paired comparisons if Golden-6400 and Flooded models exist
    if 'Golden-6400' in loaded and len(loaded['Golden-6400']) == 44:
        g64 = loaded['Golden-6400']
        for fl_key in ['Flooded-6400-Hist', 'Flooded-6400-Matched']:
            if fl_key in loaded and len(loaded[fl_key]) == 44:
                fl = loaded[fl_key]
                g_ss = [g64[r]['standstill_fraction'] * 100.0 for r in CANONICAL_44]
                fl_ss = [fl[r]['standstill_fraction'] * 100.0 for r in CANONICAL_44]

                w_stat, p_val = stats.wilcoxon(g_ss, fl_ss)
                low_ci, high_ci, mean_diff = bootstrap_ci_diff(g_ss, fl_ss)

                manifest[f'Comparison_Golden6400_vs_{fl_key}'] = {
                    'standstill_delta_pct': float(mean_diff),
                    'wilcoxon_stat': float(w_stat),
                    'wilcoxon_p': float(p_val),
                    'bca_ci_95_low': float(low_ci),
                    'bca_ci_95_high': float(high_ci)
                }

    with open(out_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest successfully written to: {out_file}")


if __name__ == '__main__':
    main()
