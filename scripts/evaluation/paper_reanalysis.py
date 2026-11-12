#!/usr/bin/env python3
"""Reviewer-round-1 re-analyses of the six-model, 44-route closed-loop evaluation.

Everything is computed from existing logs (CPU only):
  outputs/local_evaluation/{prefix}_{route}/checkpoint_endpoint.json
  outputs/local_evaluation/{prefix}_{route}/predicted_trajectories.jsonl

Definitions follow docs/ANALYSIS_ADDENDUM.md and scripts/evaluation/compute_paper_tables.py
(standstill: speed < 0.10 m/s; L: x-y chord length of the 64 predicted waypoints;
gate: L < 1.5 or (speed < 0.5 and L < 2.0)).

Outputs (regenerated on every run, deterministic):
  outputs/paper_reanalysis_manifest.json   every number, keyed A..M
  outputs/paper_reanalysis_report.md       readable rendering of the manifest

Run:  python3 scripts/evaluation/paper_reanalysis.py
"""

import glob
import json
import math
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path('/home/aimslab/lead')
sys.path.insert(0, str(ROOT / 'scripts/evaluation'))
from compute_paper_tables import (  # noqa: E402
    CANONICAL_44, STRATA_MAP, MODEL_PREFIXES, bootstrap_ci_diff, load_model_data)

EVAL_DIR = ROOT / 'outputs/local_evaluation'
ROUTE_XML_DIR = ROOT / 'src/lead/routes/benchmark_routes/bench2drive'
SCENARIO_SCRIPT = ROOT / 'scripts/common/run_full_44_matrix_flooded_6400.sh'
OUT_MANIFEST = ROOT / 'outputs/paper_reanalysis_manifest.json'
OUT_REPORT = ROOT / 'outputs/paper_reanalysis_report.md'

MODELS = ['Base', 'Flooded-1600', 'Golden-1600', 'Flooded-6400-Hist', 'Flooded-6400-Matched', 'Golden-6400']
G64, FM, FH, G16, F16, BASE = ('Golden-6400', 'Flooded-6400-Matched', 'Flooded-6400-Hist',
                               'Golden-1600', 'Flooded-1600', 'Base')

DT = 0.05                 # 20 Hz simulation step
SS_V = 0.10               # standstill threshold (m/s)
N_BOOT = 20000
SEED = 0
TICK_CAP = 4000           # scenario_manager.py: tick_count > 4000
STANDSTILL_RULE_STEPS = 1200  # 60 s at 20 Hz
TOST_DELTA = 8.0          # DS margin used in evaluate_confirmatory_plan.py

# The fixed confirmatory result (docs/provenance/paper_tables_confirmatory_record.json).
# These are the only result numbers in this file; they are used for a sanity assertion only.
PRIMARY_FIXED = {'mean_diff': -8.0616, 'ci_low': -15.0763, 'ci_high': -1.2499,
                 'statistic': 213.0, 'p': 0.000709}

# Mean-speed values quoted in the manuscript text (inputs used only to identify which
# mean-speed definition the manuscript used; not results of this script).
MANUSCRIPT_MEAN_SPEED = {G64: 1.96, G16: 1.70, FH: 1.61, F16: 1.67, BASE: 1.47}

# Official Bench2Drive ability lists, copied verbatim from
# /home/aimslab/Bench2Drive/tools/ability_benchmark.py (`Ability`); not imported (it imports carla).
ABILITY = {
    "Overtaking": ['Accident', 'AccidentTwoWays', 'ConstructionObstacle', 'ConstructionObstacleTwoWays',
                   'HazardAtSideLaneTwoWays', 'HazardAtSideLane', 'ParkedObstacleTwoWays', 'ParkedObstacle',
                   'VehicleOpensDoorTwoWays'],
    "Merging": ['CrossingBicycleFlow', 'EnterActorFlow', 'HighwayExit', 'InterurbanActorFlow', 'HighwayCutIn',
                'InterurbanAdvancedActorFlow', 'MergerIntoSlowTrafficV2', 'MergerIntoSlowTraffic',
                'NonSignalizedJunctionLeftTurn', 'NonSignalizedJunctionRightTurn',
                'NonSignalizedJunctionLeftTurnEnterFlow', 'ParkingExit', 'SequentialLaneChange',
                'SignalizedJunctionLeftTurn', 'SignalizedJunctionRightTurn', 'SignalizedJunctionLeftTurnEnterFlow'],
    "Emergency_Brake": ['BlockedIntersection', 'DynamicObjectCrossing', 'HardBreakRoute',
                        'OppositeVehicleTakingPriority', 'OppositeVehicleRunningRedLight', 'ParkingCutIn',
                        'PedestrianCrossing', 'ParkingCrossingPedestrian', 'StaticCutIn', 'VehicleTurningRoute',
                        'VehicleTurningRoutePedestrian', 'ControlLoss'],
    "Give_Way": ['InvadingTurn', 'YieldToEmergencyVehicle'],
    "Traffic_Signs": ['BlockedIntersection', 'OppositeVehicleTakingPriority', 'OppositeVehicleRunningRedLight',
                      'PedestrianCrossing', 'VehicleTurningRoute', 'VehicleTurningRoutePedestrian',
                      'EnterActorFlow', 'CrossingBicycleFlow', 'NonSignalizedJunctionLeftTurn',
                      'NonSignalizedJunctionRightTurn', 'NonSignalizedJunctionLeftTurnEnterFlow',
                      'OppositeVehicleTakingPriority', 'OppositeVehicleRunningRedLight', 'PedestrianCrossing',
                      'SignalizedJunctionLeftTurn', 'SignalizedJunctionRightTurn',
                      'SignalizedJunctionLeftTurnEnterFlow', 'T_Junction', 'VanillaNonSignalizedTurn',
                      'VanillaSignalizedTurnEncounterGreenLight', 'VanillaSignalizedTurnEncounterRedLight',
                      'VanillaNonSignalizedTurnEncounterStopsign', 'VehicleTurningRoute',
                      'VehicleTurningRoutePedestrian'],
}
# ANALYSIS_ADDENDUM.md section 2: order used to pick the primary ability, and the STRATA_MAP key names.
PRIMARY_ABILITY_ORDER = ['Overtaking', 'Merging', 'Emergency_Brake', 'Give_Way', 'Traffic_Signs']
STRATA_KEY = {'Overtaking': 'Overtaking', 'Merging': 'Merging', 'Emergency_Brake': 'Emergency_Braking',
              'Give_Way': 'Give_Way', 'Traffic_Signs': 'Traffic_Signs'}
NO_JUNCTION_EXTRA = ['2286', '23687', '23901', '23695', '2283', '23771', '1956', '17563']
BYPASS_SINGLE = ['2534', '2513', '1790', '1773']
BYPASS_TWOWAY = ['1852', '1825', '3436', '2664', '3464']

COLLISION_KEYS = {'collisions_vehicle': 'vehicle', 'collisions_pedestrian': 'pedestrian',
                  'collisions_layout': 'layout'}
# Infraction keys excluded as "timeout-type" for analysis F(vi). result_parser.py has no timeout
# category of its own: it counts every key, treats min_speed_infractions as a percentage and
# outside_route_lanes as km; here every remaining key is counted as the number of list entries.
TIMEOUT_KEYS = ['min_speed_infractions', 'scenario_timeouts', 'route_timeout']
EXTRA_VRU_ROUTES = ['2164', '17752', '14194', '3248', '3086']

# Analysis J keyword heuristic (lower-cased coc text, regex word boundaries). Chosen after
# inspecting the 40 most frequent standstill rationales (listed in the report).
CAUTION_PATTERNS = [r'\bstop\b', r'\byield', r'\bwait', r'keep distance', r'slow down', r'\bred\b',
                    r'\bobstacle']
PROCEED_PATTERNS = [r'\bclear\b', r'\bproceed', r'\bcontinue', r'keep lane', r'\baccelerat', r'\bnudge',
                    r'\bgo\b', r'\bresume']

GATE_SWEEP_L = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
SWEEP_V = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
SENS_V = [0.05, 0.1, 0.2, 0.5]
COMPARATORS = [FM, FH]


# --------------------------------------------------------------------------- loading

def _route_dir(prefixes, route, filename):
    for p in prefixes:
        cand = EVAL_DIR / f'{p}_{route}'
        if (cand / filename).exists() and (cand / filename).stat().st_size > 0:
            return cand
    return None


def chord_profile(wp):
    """Per-step segment lengths and cumulative chord (x-y), identical arithmetic to
    compute_paper_tables.load_model_data (np.hypot per segment, sequential summation)."""
    seg = np.hypot(np.diff(wp[:, :, 0], axis=1), np.diff(wp[:, :, 1], axis=1))
    cum = np.concatenate([np.zeros((wp.shape[0], 1)), np.cumsum(seg, axis=1)], axis=1)
    return seg, cum


def controller_target_speed(wp, speed, cum):
    """Offline re-implementation of alpamayo_bridge_agent.py (run_step, section 6) target speed
    before the standstill gate (km/h). Returns (target_kmh, max_turn_angle).

    Frames: the agent flips y (Alpamayo -> CARLA local), measures chord length in world x-y after the
    rigid ego transform, and the turn angle in the local frame (abs(y), so the flip is irrelevant).
    Here chord lengths are taken in the logged local x-y frame; this equals the world x-y chord
    exactly when ego pitch and roll are zero (yaw and translation preserve x-y distances)."""
    n = wp.shape[0]
    L = cum[:, -1]
    ang = np.arctan2(np.abs(wp[:, 5:35, 1]), np.maximum(wp[:, 5:35, 0], 1.0))
    max_turn = ang.max(axis=1)
    turning = max_turn > 0.087
    lookahead = np.where(turning, np.clip(5.5 + 0.3 * speed, 5.0, 8.5), np.clip(5.0 + 0.4 * speed, 5.0, 12.0))
    # np.searchsorted(cum, lookahead) (side='left') == number of cum entries < lookahead
    tidx = np.minimum((cum < lookahead[:, None]).sum(axis=1), wp.shape[1] - 1)
    t_target = (tidx + 1) * 0.1
    v_planned = cum[np.arange(n), tidx] / t_target * 3.6
    idx_down = min(24, wp.shape[1] - 1)
    v_down = cum[:, idx_down] / ((idx_down + 1) * 0.1) * 3.6
    base = np.where(v_down < v_planned, 0.6 * v_down + 0.4 * v_planned, v_planned)
    v_extent = np.sqrt(np.maximum(0.0, 2.0 * 1.8 * L)) * 3.6
    target = np.clip(np.minimum(base, v_extent), 0.0, 35.0)
    curve_limit = np.maximum(10.0, 35.0 - max_turn * 100.0)
    target = np.where(max_turn > 0.06, np.minimum(target, curve_limit), target)
    return target, max_turn


def load_route(model, route):
    prefixes = MODEL_PREFIXES[model]
    ep_dir = _route_dir(prefixes, route, 'checkpoint_endpoint.json')
    log_dir = _route_dir(prefixes, route, 'predicted_trajectories.jsonl')
    if ep_dir is None or log_dir is None:
        raise RuntimeError(f'missing data for {model} route {route}')
    rec = json.load(open(ep_dir / 'checkpoint_endpoint.json'))['_checkpoint']['records'][0]
    if log_dir != ep_dir:
        # The step log comes from a fallback prefix; require the two endpoint records to agree.
        rec2 = json.load(open(log_dir / 'checkpoint_endpoint.json'))['_checkpoint']['records'][0]
        if rec2['scores'] != rec['scores'] or rec2['infractions'] != rec['infractions']:
            raise RuntimeError(f'{model} {route}: endpoint of {ep_dir.name} differs from {log_dir.name}')
    wps, speed, steer, thr, brk, coc, steps = [], [], [], [], [], [], []
    with open(log_dir / 'predicted_trajectories.jsonl') as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            wps.append(d['pred_waypoints'])
            speed.append(float(d['speed']))
            steer.append(float(d['steer']))
            thr.append(float(d['throttle']))
            brk.append(float(d['brake']))
            coc.append(d.get('coc', '') or '')
            steps.append(int(d['step']))
    wp = np.asarray(wps, dtype=np.float64)
    if wp.ndim != 3 or wp.shape[1] != 64:
        raise RuntimeError(f'{model} {route}: unexpected waypoint array {wp.shape}')
    speed = np.asarray(speed)
    seg, cum = chord_profile(wp)
    target, _ = controller_target_speed(wp, speed, cum)
    return {
        'endpoint_dir': ep_dir.name, 'steplog_dir': log_dir.name,
        'status': rec['status'],
        'ds': float(rec['scores']['score_composed']),
        'rc': float(rec['scores']['score_route']),
        'penalty': float(rec['scores']['score_penalty']),
        'route_length': float(rec['meta']['route_length']),
        'duration_game': float(rec['meta']['duration_game']),
        'infractions': rec['infractions'],
        'speed': speed, 'L': cum[:, -1].copy(),
        'steer': np.asarray(steer), 'throttle': np.asarray(thr), 'brake': np.asarray(brk),
        'target': target, 'coc': coc,
        'n_steps': len(speed), 'step_gaps': int(np.sum(np.diff(steps) != 1)),
    }


def load_all():
    data = {}
    for m in MODELS:
        data[m] = {r: load_route(m, r) for r in CANONICAL_44}
        print(f'loaded {m}: {len(data[m])} routes', flush=True)
    return data


def cross_check_with_reference_loader(data):
    """Compare this loader with compute_paper_tables.load_model_data on the primary pair."""
    out = {}
    for m in (G64, FM):
        ref = load_model_data(MODEL_PREFIXES[m])
        same = all(np.array_equal(np.asarray(ref[r]['speeds']), data[m][r]['speed'])
                   and np.array_equal(np.asarray(ref[r]['ltrajs']), data[m][r]['L'])
                   and ref[r]['ds'] == data[m][r]['ds'] for r in CANONICAL_44)
        if not same:
            raise RuntimeError(f'loader disagrees with load_model_data for {m}')
        out[m] = 'speeds, L and DS identical to load_model_data on all 44 routes'
    return out


# --------------------------------------------------------------------------- per-route metrics

def gate_mask(rd):
    return (rd['L'] < 1.5) | ((rd['speed'] < 0.5) & (rd['L'] < 2.0))


def pct(mask):
    return float(np.mean(mask) * 100.0) if len(mask) else float('nan')


def per_route(data, model, fn, routes=CANONICAL_44):
    return np.array([fn(data[model][r]) for r in routes], dtype=np.float64)


METRICS = {
    'standstill_pct': lambda rd: pct(rd['speed'] < SS_V),
    'driving_score': lambda rd: rd['ds'],
    'route_completion': lambda rd: rd['rc'],
    'mean_speed_mps': lambda rd: float(np.mean(rd['speed'])),
    'gate_pct': lambda rd: pct(gate_mask(rd)),
    'mean_L_m': lambda rd: float(np.mean(rd['L'])),
}


# --------------------------------------------------------------------------- statistics

def bca(x, y):
    d = np.asarray(x) - np.asarray(y)
    if np.all(d == d[0]):
        return {'status': 'not_computable', 'reason': 'all paired differences identical'}
    lo, hi, _ = bootstrap_ci_diff(x, y, n_resamples=N_BOOT, seed=SEED)
    return [float(lo), float(hi)]


def wilcoxon_full(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = x - y
    nz = d[d != 0]
    out = {'n_zero_differences': int(np.sum(d == 0))}
    if len(nz) == 0:
        out.update({'status': 'not_computable', 'reason': 'all differences are zero'})
        return out
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = stats.wilcoxon(x, y)
        out['statistic'] = float(res.statistic)
        out['p'] = float(res.pvalue)
        out['p_approx'] = float(stats.wilcoxon(x, y, method='approx').pvalue)
        ties = len(np.unique(np.abs(nz))) < len(nz)
        if out['n_zero_differences'] == 0 and not ties:
            out['p_exact'] = float(stats.wilcoxon(x, y, method='exact').pvalue)
        else:
            out['p_exact'] = 'not available (zero differences or tied |differences|)'
    ranks = stats.rankdata(np.abs(nz))
    r_plus, r_minus = float(ranks[nz > 0].sum()), float(ranks[nz < 0].sum())
    out['rank_biserial'] = (r_plus - r_minus) / (r_plus + r_minus)
    return out


def paired(x, y, ci=True, routes=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = x - y
    out = {'n': int(len(d)), 'mean_first': float(np.mean(x)), 'mean_second': float(np.mean(y)),
           'mean_diff': float(np.mean(d)),
           'n_first_greater': int(np.sum(d > 0)), 'n_first_less': int(np.sum(d < 0)),
           'n_tie': int(np.sum(d == 0))}
    if ci:
        out['bca95'] = bca(x, y)
    out['wilcoxon'] = wilcoxon_full(x, y)
    if routes is not None:
        out['per_route'] = {r: {'first': float(a), 'second': float(b)} for r, a, b in zip(routes, x, y)}
    return out


def holm_adjust(pvals):
    # Copied from scripts/common/evaluate_confirmatory_plan.py (holm_adjust).
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.zeros(m)
    prev = 0.0
    for i, idx in enumerate(order):
        prev = max(prev, (m - i) * pvals[idx])
        adj[idx] = min(prev, 1.0)
    return [float(v) for v in adj]


def bca_ci_and_boot_p(diff, delta=TOST_DELTA, confidence=0.90, n_resamples=N_BOOT, seed=SEED):
    # Copied from scripts/common/evaluate_confirmatory_plan.py (bca_ci_and_boot_p).
    res = stats.bootstrap((diff,), np.mean, confidence_level=confidence, method='BCa',
                          n_resamples=n_resamples, random_state=seed)
    lo, hi = float(res.confidence_interval.low), float(res.confidence_interval.high)
    rng = np.random.default_rng(seed)
    boot_means = rng.choice(diff, size=(n_resamples, len(diff)), replace=True).mean(axis=1)
    p_gt_neg_delta = float(np.mean(boot_means <= -delta))
    p_lt_pos_delta = float(np.mean(boot_means >= delta))
    p_tost = max(p_gt_neg_delta, p_lt_pos_delta)
    return lo, hi, p_gt_neg_delta, p_tost


def boot_indices(n):
    return np.random.RandomState(SEED).randint(0, n, (N_BOOT, n))


# --------------------------------------------------------------------------- route metadata

def load_route_scenarios():
    text = SCENARIO_SCRIPT.read_text()
    block = re.search(r'SCENARIOS=\((.*?)\)', text, re.S).group(1)
    pairs = re.findall(r'"([A-Za-z_0-9]+):(\d+)"', block)
    mapping = {rid: name for name, rid in pairs}
    missing = [r for r in CANONICAL_44 if r not in mapping]
    if missing:
        raise RuntimeError(f'no scenario name for routes {missing}')
    return mapping


def primary_ability(scenario):
    for ab in PRIMARY_ABILITY_ORDER:
        if scenario in ABILITY[ab]:
            return ab
    return None


def route_geometry(route):
    root = ET.parse(ROUTE_XML_DIR / f'{route}.xml').getroot()
    rt = root.find('route')
    pts = np.array([[float(p.get('x')), float(p.get('y'))] for p in rt.find('waypoints').findall('position')])
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    triggers = []
    for sc in rt.find('scenarios').findall('scenario'):
        tp = sc.find('trigger_point')
        q = np.array([float(tp.get('x')), float(tp.get('y'))])
        best = None
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            ab = b - a
            t = 0.0 if seg[i] == 0 else float(np.clip(np.dot(q - a, ab) / (seg[i] ** 2), 0.0, 1.0))
            dist = float(np.hypot(*(a + t * ab - q)))
            if best is None or dist < best[0]:
                best = (dist, cum[i] + t * seg[i])
        triggers.append({'name': sc.get('name'), 'type': sc.get('type'),
                         'trigger_xy': [float(q[0]), float(q[1])],
                         'distance_to_polyline_m': best[0],
                         'arc_length_m': float(best[1]),
                         'fraction_pct': float(best[1] / cum[-1] * 100.0)})
    return {'town': rt.get('town'), 'n_keypoints': int(len(pts)),
            'polyline_length_m': float(cum[-1]),
            'max_keypoint_spacing_m': float(seg.max()), 'triggers': triggers}


# --------------------------------------------------------------------------- A

def analysis_A(data):
    pairs = [(G64, FM), (G64, FH), (FH, FM), (G64, G16), (G16, F16), (G16, BASE), (F16, BASE), (FM, F16)]
    res = {'metric_definitions': {
        'standstill_pct': '% of logged steps with speed < 0.10 m/s',
        'driving_score': 'score_composed', 'route_completion': 'score_route (%)',
        'mean_speed_mps': 'mean over logged steps of speed (per route)',
        'gate_pct': '% of logged steps with L < 1.5 or (speed < 0.5 and L < 2.0)',
        'mean_L_m': 'mean predicted-trajectory chord length (m)'},
        'difference': 'first model minus second model, per route, 44 canonical routes',
        'pairs': {}}
    vals = {m: {k: per_route(data, m, f) for k, f in METRICS.items()} for m in MODELS}
    for a, b in pairs:
        res['pairs'][f'{a} vs {b}'] = {k: paired(vals[a][k], vals[b][k]) for k in METRICS}

    prim = res['pairs'][f'{G64} vs {FM}']['standstill_pct']
    got = {'mean_diff': round(prim['mean_diff'], 4), 'ci_low': round(prim['bca95'][0], 4),
           'ci_high': round(prim['bca95'][1], 4), 'statistic': prim['wilcoxon']['statistic'],
           'p': round(prim['wilcoxon']['p'], 6)}
    if got != PRIMARY_FIXED:
        raise SystemExit(f'ABORT: primary H2 result {got} does not reproduce the fixed record {PRIMARY_FIXED}')
    res['primary_reproduction_check'] = {'expected': PRIMARY_FIXED, 'obtained_rounded': got, 'passed': True}

    # Holm, 2-test pre-registered family
    h1 = res['pairs'][f'{G16} vs {BASE}']['driving_score']['wilcoxon']['p']
    h1_one = float(stats.wilcoxon(vals[G16]['driving_score'], vals[BASE]['driving_score'],
                                  alternative='greater').pvalue)
    h2 = prim['wilcoxon']['p']
    res['holm_2_test_family'] = {
        'tests': ['H1: Golden-1600 vs Base DS, two-sided Wilcoxon', 'H2: Golden-6400 vs Flooded-6400-Matched standstill'],
        'raw_p': [h1, h2], 'holm_p': holm_adjust([h1, h2]),
        'variant_H1_one_sided_greater': {'raw_p': [h1_one, h2], 'holm_p': holm_adjust([h1_one, h2])},
        'note': ("H1's p-value was known before the family was declared, so the correction adds no "
                 "protection for H2 (ANALYSIS_ADDENDUM.md section 1).")}

    # TOST / non-inferiority (logic of evaluate_confirmatory_plan.py, DS from checkpoint_endpoint.json)
    d_eq = vals[G64]['driving_score'] - vals[G16]['driving_score']
    lo, hi, _, p_tost = bca_ci_and_boot_p(d_eq)
    tost = {'Golden-6400 vs Golden-1600 equivalence (margin 8 DS)': {
        'mean_diff': float(d_eq.mean()), 'bca90': [lo, hi], 'ci_within_margin': bool(lo > -TOST_DELTA and hi < TOST_DELTA),
        'p_tost_bootstrap': p_tost}}
    fam = {}
    for X in COMPARATORS:
        d_ni = vals[G16]['driving_score'] - vals[X]['driving_score']
        lo2, hi2, p_ni, _ = bca_ci_and_boot_p(d_ni)
        key = f'Golden-1600 vs {X} non-inferiority (margin 8 DS)'
        tost[key] = {'mean_diff': float(d_ni.mean()), 'bca90': [lo2, hi2],
                     'ci_lower_above_minus_margin': bool(lo2 > -TOST_DELTA), 'p_noninferiority_bootstrap': p_ni}
        h2x = res['pairs'][f'{G64} vs {X}']['standstill_pct']['wilcoxon']['p']
        raw = [h1, h2x, p_tost, p_ni]
        fam[f'family_with_{X}'] = {
            'tests': ['H1 Golden-1600 vs Base DS (two-sided Wilcoxon)', f'H2 Golden-6400 vs {X} standstill',
                      'Golden-6400 vs Golden-1600 DS equivalence (bootstrap TOST p)',
                      f'Golden-1600 vs {X} DS non-inferiority (bootstrap p)'],
            'raw_p': raw, 'holm_p': holm_adjust(raw)}
    res['tost_noninferiority'] = tost
    res['tost_noninferiority']['method'] = (
        'bca_ci_and_boot_p copied from scripts/common/evaluate_confirmatory_plan.py: 90% BCa (scipy.stats.bootstrap, '
        '20,000 resamples, seed 0); p = share of default_rng(0) bootstrap means beyond the margin. DS taken from '
        'checkpoint_endpoint.json (that script reads outputs/final_2x2_anova_matrix_report.json where available; '
        'agreement is checked in ds_source_check).')
    res['holm_4_test_families'] = fam
    res['ds_source_check'] = ds_source_check(data)

    # 2x2 difference-in-differences
    did = {}
    for X in COMPARATORS:
        for k in ('mean_speed_mps', 'standstill_pct'):
            a = vals[G64][k] - vals[G16][k]
            b = vals[X][k] - vals[F16][k]
            did[f'{k}: (Golden-6400 - Golden-1600) - ({X} - Flooded-1600)'] = paired(a, b)
    res['difference_in_differences'] = did
    return res, vals


def ds_source_check(data):
    p = ROOT / 'outputs/final_2x2_anova_matrix_report.json'
    if not p.exists():
        return {'status': 'not_computable', 'reason': f'{p} missing'}
    per = json.load(open(p))['per_route_scores']
    keymap = {'Flooded_1600': F16, 'Golden_1600': G16, 'Flooded_6400': FH, 'Golden_6400': G64, 'Base': BASE}
    out = {}
    for k, m in keymap.items():
        diffs = [abs(per[r][k]['ds'] - data[m][r]['ds']) for r in CANONICAL_44 if r in per and k in per[r]]
        out[m] = {'n_routes_in_json': len(diffs), 'max_abs_ds_difference': float(max(diffs)) if diffs else None}
    return out


# --------------------------------------------------------------------------- B

def analysis_B(data):
    res = {}
    for X in COMPARATORS:
        key = f'{G64} vs {X}'
        win_a, win_b = [], []
        for r in CANONICAL_44:
            a, b = data[G64][r], data[X][r]
            n = min(a['n_steps'], b['n_steps'])
            win_a.append(pct(a['speed'][:n] < SS_V))
            win_b.append(pct(b['speed'][:n] < SS_V))
        sec = lambda rd: float(np.sum(rd['speed'] < SS_V) * DT)  # noqa: E731
        thr = {}
        for v in SENS_V:
            f = lambda rd, v=v: pct(rd['speed'] < v)  # noqa: E731
            thr[f'v<{v}'] = paired(per_route(data, G64, f), per_route(data, X, f))
        res[key] = {'common_tick_window_standstill_pct': paired(win_a, win_b),
                    'standstill_seconds': paired(per_route(data, G64, sec), per_route(data, X, sec)),
                    'standstill_thresholds_pct': thr}
    status = {}
    for m in MODELS:
        st = Counter(data[m][r]['status'] for r in CANONICAL_44)
        tick = [r for r in CANONICAL_44 if data[m][r]['status'] == 'Failed - TickRuntime']
        cap = [r for r in tick if round(data[m][r]['duration_game'] * 20) >= TICK_CAP]
        status[m] = {'status_counts': dict(sorted(st.items())),
                     'tickruntime_routes': tick,
                     'tickruntime_ended_at_cap_ge_4000_ticks': cap,
                     'tickruntime_ended_before_cap_60s_rule': [r for r in tick if r not in cap],
                     'n_cap': len(cap), 'n_60s_rule': len(tick) - len(cap)}
    res['termination_by_model'] = status
    res['termination_rule'] = 'ticks = round(duration_game * 20); >= 4000 -> cap, else 60 s standstill rule'
    return res


# --------------------------------------------------------------------------- C

def strata_groups(scen):
    groups = {}
    primary_check = {}
    for ab in PRIMARY_ABILITY_ORDER:
        derived = [r for r in CANONICAL_44 if primary_ability(scen[r]) == ab]
        primary_check[ab] = sorted(derived) == sorted(STRATA_MAP[STRATA_KEY[ab]])
        groups[f'primary:{ab}'] = STRATA_MAP[STRATA_KEY[ab]]
    groups['primary:Overtaking + Merging'] = STRATA_MAP['Overtaking'] + STRATA_MAP['Merging']
    for ab, lst in ABILITY.items():
        groups[f'official:{ab}'] = [r for r in CANONICAL_44 if scen[r] in lst]
    groups['no_junction_control_by_scenario_type'] = STRATA_MAP['Overtaking'] + NO_JUNCTION_EXTRA
    groups['bypass:single_direction'] = BYPASS_SINGLE
    groups['bypass:two_way'] = BYPASS_TWOWAY
    return groups, primary_check


def analysis_C(data, scen):
    groups, check = strata_groups(scen)
    res = {'primary_ability_rule_reproduces_STRATA_MAP': check, 'groups': {}}
    for g, routes in groups.items():
        entry = {'n': len(routes), 'routes': routes, 'models': {}, 'pairs': {}}
        for m in MODELS:
            entry['models'][m] = {k: float(np.mean(per_route(data, m, METRICS[k], routes)))
                                  for k in ('standstill_pct', 'mean_speed_mps', 'gate_pct')}
        for X in COMPARATORS:
            pr = {}
            for k in ('standstill_pct', 'mean_speed_mps', 'gate_pct'):
                pr[k] = paired(per_route(data, G64, METRICS[k], routes), per_route(data, X, METRICS[k], routes),
                               ci=len(routes) >= 9, routes=None if len(routes) >= 9 else routes)
            entry['pairs'][f'{G64} vs {X}'] = pr
        res['groups'][g] = entry
    return res


# --------------------------------------------------------------------------- D

BANDS = ['L<0.64', '0.64<=L<1.5', '1.5<=L<2.0 & v<0.5', 'gate inactive']


def band_index(rd):
    L, v = rd['L'], rd['speed']
    b = np.full(len(L), 3)
    b[(L >= 1.5) & (L < 2.0) & (v < 0.5)] = 2
    b[(L >= 0.64) & (L < 1.5)] = 1
    b[L < 0.64] = 0
    return b


def analysis_D(data):
    res = {'bands': BANDS, 'models': {}, 'pairs': {}}
    per = {}
    for m in MODELS:
        all_pct = np.zeros((44, 4)); ss_contrib = np.zeros((44, 4)); ss_share = np.full((44, 4), np.nan)
        for i, r in enumerate(CANONICAL_44):
            rd = data[m][r]
            b = band_index(rd)
            ss = rd['speed'] < SS_V
            for k in range(4):
                all_pct[i, k] = pct(b == k)
                ss_contrib[i, k] = pct((b == k) & ss)
                if ss.any():
                    ss_share[i, k] = float(np.mean(b[ss] == k) * 100.0)
        per[m] = (all_pct, ss_contrib)
        n_ss = int(np.sum(~np.isnan(ss_share[:, 0])))
        res['models'][m] = {
            'pct_of_all_steps_in_band': dict(zip(BANDS, all_pct.mean(axis=0).tolist())),
            'pct_of_all_steps_standstill_and_in_band': dict(zip(BANDS, ss_contrib.mean(axis=0).tolist())),
            'share_of_standstill_steps_in_band_pct': dict(zip(BANDS, np.nanmean(ss_share, axis=0).tolist())),
            'n_routes_with_standstill_steps': n_ss}
    for X in COMPARATORS:
        a_all, a_ss = per[G64]; b_all, b_ss = per[X]
        total = paired(per_route(data, G64, METRICS['standstill_pct']), per_route(data, X, METRICS['standstill_pct']))
        band_diffs = {BANDS[k]: paired(a_ss[:, k], b_ss[:, k]) for k in range(4)}
        s = sum(band_diffs[b]['mean_diff'] for b in BANDS)
        assert math.isclose(s, total['mean_diff'], abs_tol=1e-9), 'band decomposition does not sum to total'
        res['pairs'][f'{G64} vs {X}'] = {
            'total_standstill_diff': total['mean_diff'],
            'standstill_and_band_diff': band_diffs,
            'sum_of_band_diffs': s,
            'share_of_gap_by_band_pct': {b: band_diffs[b]['mean_diff'] / total['mean_diff'] * 100.0 for b in BANDS},
            'all_steps_band_diff': {BANDS[k]: paired(a_all[:, k], b_all[:, k]) for k in range(4)}}
    res['note'] = ('Route-level means of per-route percentages. "standstill_and_in_band" uses all steps as the '
                   'denominator, so the four bands sum to the route standstill %; the Golden-minus-Flooded band '
                   'differences therefore sum to the total standstill difference (asserted).')
    return res


# --------------------------------------------------------------------------- E

E_CLASSES = ['target<0.36km/h (plan is to stand still)', 'target>=0.36 & brake>0',
             'target>=0.36 & throttle>0', 'other']


def e_classes(rd):
    sel = (rd['speed'] < SS_V) & ~gate_mask(rd)
    t, br, th = rd['target'][sel], rd['brake'][sel], rd['throttle'][sel]
    c = np.full(len(t), 3)
    c[(t >= 0.36) & (th > 0)] = 2
    c[(t >= 0.36) & (br > 0)] = 1
    c[t < 0.36] = 0
    return sel, c


def analysis_E(data):
    res = {'classes': E_CLASSES, 'models': {}, 'pairs': {},
           'definition': ('Standstill steps (speed < 0.1 m/s) with the gate inactive, classified by the offline '
                          'pre-gate target speed and the logged (smoothed, mutually exclusive) brake/throttle.'),
           'approximations': [
               'Chord lengths (lookahead index, v_target_planned, v_downstream, v_extent_limit) use the logged '
               'local x-y waypoints; the agent uses world x-y after a rigid transform. Identical when ego pitch '
               'and roll are zero; otherwise the world x-y chord is shorter by the projection of the tilt.',
               'Turn angle uses the local frame as in the agent (abs(y), so the y-flip is irrelevant).',
               'speed is the logged speedometer value, the same variable the agent uses (current_speed).',
               'The PID output itself is not re-simulated; brake/throttle are the logged final commands.']}
    per = {}
    for m in MODELS:
        frac_all = np.zeros((44, 4)); share = np.full((44, 4), np.nan); pooled = np.zeros(4); n_sel = 0
        thr_vals = []
        sel_pct = np.zeros(44)
        for i, r in enumerate(CANONICAL_44):
            rd = data[m][r]
            sel, c = e_classes(rd)
            sel_pct[i] = pct(sel)
            thr_vals.append(rd['throttle'][sel][c == 2])
            for k in range(4):
                frac_all[i, k] = float(np.sum(c == k) / rd['n_steps'] * 100.0)
                pooled[k] += np.sum(c == k)
                if len(c):
                    share[i, k] = float(np.mean(c == k) * 100.0)
            n_sel += len(c)
        per[m] = frac_all
        res['models'][m] = {
            'pct_of_all_steps_standstill_gate_inactive': float(sel_pct.mean()),
            'pct_of_all_steps_by_class': dict(zip(E_CLASSES, frac_all.mean(axis=0).tolist())),
            'route_mean_share_within_class_set_pct': dict(zip(E_CLASSES, np.nanmean(share, axis=0).tolist())),
            'n_routes_with_such_steps': int(np.sum(~np.isnan(share[:, 0]))),
            'pooled_share_pct': dict(zip(E_CLASSES, (pooled / max(n_sel, 1) * 100.0).tolist())),
            'pooled_n_steps': int(n_sel),
            'throttle_in_throttle_class': (lambda t: {'median': float(np.median(t)), 'mean': float(np.mean(t)),
                                                      'pct_ge_0.35': pct(t >= 0.35)} if len(t) else None)(np.concatenate(thr_vals))}
    for X in COMPARATORS:
        res['pairs'][f'{G64} vs {X}'] = {E_CLASSES[k]: paired(per[G64][:, k], per[X][:, k]) for k in range(4)}
    return res


# --------------------------------------------------------------------------- F

COLL_RE = re.compile(r'type=(\S+) and id=(\d+) at \(x=([-\d.e]+), y=([-\d.e]+), z=([-\d.e]+)\)')


def parse_collisions(rd):
    out = []
    for key, cls in COLLISION_KEYS.items():
        for s in rd['infractions'].get(key, []):
            mt = COLL_RE.search(s)
            if mt is None:
                raise RuntimeError(f'unparsable collision string: {s}')
            out.append({'class': cls, 'actor_type': mt.group(1), 'actor_id': mt.group(2),
                        'x': float(mt.group(3)), 'y': float(mt.group(4)), 'string': s})
    return out


def exposures(rd):
    return rd['rc'] / 100.0 * rd['route_length'] / 1000.0, float(np.sum(rd['speed']) * DT / 1000.0)


def route_counts(rd):
    cols = parse_collisions(rd)
    c = {'raw': len(cols), 'events_actor_id': len({x['actor_id'] for x in cols}),
         'events_exact_string': len({x['string'] for x in cols})}
    for cls in COLLISION_KEYS.values():
        sub = [x for x in cols if x['class'] == cls]
        c[f'raw_{cls}'] = len(sub)
        c[f'events_actor_id_{cls}'] = len({x['actor_id'] for x in sub})
        c[f'events_exact_string_{cls}'] = len({x['string'] for x in sub})
    nt_keys = [k for k in rd['infractions'] if k not in TIMEOUT_KEYS]
    c['non_timeout_raw'] = sum(len(rd['infractions'][k]) for k in nt_keys)
    c['non_timeout_collisions_as_events'] = c['non_timeout_raw'] - c['raw'] + c['events_actor_id']
    return c


def analysis_F(data):
    idx = boot_indices(44)
    counts = {m: [route_counts(data[m][r]) for r in CANONICAL_44] for m in MODELS}
    expo = {m: np.array([exposures(data[m][r]) for r in CANONICAL_44]) for m in MODELS}
    res = {'models': {}, 'pairs': {},
           'definitions': {
               'events_actor_id': 'within a route, collision strings with the same actor id count once',
               'events_exact_string': 'within a route, only identical strings are merged',
               'progress_km': 'score_route/100 * route_length/1000', 'odometer_km': 'sum(speed)*0.05/1000',
               'non_timeout_infractions': f'all infraction keys except {TIMEOUT_KEYS}, counted as list entries',
               'bootstrap': '20,000 route resamples (np.random.RandomState(0).randint), percentile 95% CI'}}
    count_keys = ['raw', 'events_actor_id', 'events_exact_string', 'non_timeout_raw', 'non_timeout_collisions_as_events']
    for m in MODELS:
        tot = {k: int(sum(c[k] for c in counts[m])) for k in counts[m][0]}
        lens = {cls: int(sum(len(data[m][r]['infractions'].get(key, [])) for r in CANONICAL_44))
                for key, cls in COLLISION_KEYS.items()}
        assert all(tot[f'raw_{cls}'] == lens[cls] for cls in lens), 'raw counts differ from list lengths'
        rates = {}
        for ck in count_keys:
            e = np.array([c[ck] for c in counts[m]], float)
            for ei, ename in enumerate(('progress_km', 'odometer_km')):
                km = expo[m][:, ei]
                boot = e[idx].sum(axis=1) / km[idx].sum(axis=1)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                rates[f'{ck}_per_{ename}'] = {'rate': float(e.sum() / km.sum()), 'ci95': [float(lo), float(hi)]}
        res['models'][m] = {'totals': tot, 'progress_km': float(expo[m][:, 0].sum()),
                            'odometer_km': float(expo[m][:, 1].sum()), 'rates': rates}
    for b in (FM, FH, G16):
        pr = {}
        for ck in ('events_actor_id', 'raw', 'non_timeout_raw'):
            ea = np.array([c[ck] for c in counts[G64]], float); eb = np.array([c[ck] for c in counts[b]], float)
            entry = {'wilcoxon_per_route_counts': paired(ea, eb, ci=False)}
            for ei, ename in enumerate(('progress_km', 'odometer_km')):
                ka, kb = expo[G64][:, ei], expo[b][:, ei]
                if ea.sum() == 0 or eb.sum() == 0:
                    entry[f'rate_ratio_{ename}'] = {'status': 'not_computable', 'reason': 'zero pooled events'}
                    continue
                log_rr = math.log((ea.sum() / ka.sum()) / (eb.sum() / kb.sum()))
                na, nb = ea[idx].sum(axis=1), eb[idx].sum(axis=1)
                with np.errstate(divide='ignore'):
                    boot = (np.log(na / ka[idx].sum(axis=1)) - np.log(nb / kb[idx].sum(axis=1)))
                boot = np.where((na == 0) & (nb == 0), np.nan, boot)
                boot = boot[~np.isnan(boot)]
                lo, hi = np.quantile(boot, [0.025, 0.975], method='inverted_cdf')
                entry[f'rate_ratio_{ename}'] = {
                    'rate_ratio': math.exp(log_rr), 'log_rate_ratio': log_rr,
                    'log_ci95': [float(lo), float(hi)], 'ci95': [float(np.exp(lo)), float(np.exp(hi))],
                    'n_resamples_with_zero_events_in_one_arm': int(np.sum((na == 0) ^ (nb == 0)))}
            pr[ck] = entry
        res['pairs'][f'{G64} vs {b}'] = pr
    res['per_route_collisions'] = {m: {r: [{k: v for k, v in x.items() if k != 'string'}
                                          for x in parse_collisions(data[m][r])]
                                      for r in CANONICAL_44 if parse_collisions(data[m][r])} for m in MODELS}
    return res, counts, expo


# --------------------------------------------------------------------------- G

def analysis_G(data, scen):
    ped_routes = [r for r in CANONICAL_44 if any(data[m][r]['infractions'].get('collisions_pedestrian')
                                                for m in MODELS)]
    routes = ped_routes + [r for r in EXTRA_VRU_ROUTES if r not in ped_routes]
    res = {'routes_with_pedestrian_collision_any_model': ped_routes, 'routes': {},
           'trigger_method': (
               'Route XML <waypoints> keypoints joined by straight segments in x-y; each <trigger_point> is '
               'projected onto the nearest segment and its arc length divided by the polyline length gives the '
               'fraction. "Reached" means score_route >= that fraction. Approximate: the leaderboard measures '
               'completion on its own road-network interpolation of the keypoints (meta.route_length), so the '
               'fraction is only as exact as the polyline-to-route_length ratio and the keypoint spacing reported '
               'per route.')}
    for r in routes:
        geo = route_geometry(r)
        rl = data[G64][r]['route_length']
        geo['route_length_meta_m'] = rl
        geo['polyline_to_route_length_ratio'] = geo['polyline_length_m'] / rl
        main = [t for t in geo['triggers'] if t['type'] == scen[r]] or geo['triggers']
        frac = main[0]['fraction_pct']
        per = {}
        for m in MODELS:
            rd = data[m][r]
            peds = rd['infractions'].get('collisions_pedestrian', [])
            per[m] = {'rc': rd['rc'], 'status': rd['status'], 'pedestrian_collisions': len(peds),
                      'pedestrian_collision_strings': peds, 'reached_trigger': bool(rd['rc'] >= frac)}
        res['routes'][r] = {'scenario': scen[r], 'geometry': geo, 'trigger_fraction_used_pct': frac, 'models': per}
    return res


# --------------------------------------------------------------------------- H

def analysis_H(data, vals):
    sh = (ROOT / 'scripts/common/eval_faulty_routes.sh').read_text()
    block = re.search(r'^ROUTES=\((.*?)^\)', sh, re.S | re.M).group(1)
    script_routes = re.findall(r'^\s*"(\d+)"', block, re.M)
    md = (ROOT / 'docs/CONTROLLER_OPTIMIZATION_EXPERIMENT.md').read_text()
    doc_routes = re.findall(r'Test Route:\*\*\s*Route\s*(\d+)', md)
    dirs = {}
    for pat in ('model_v4_ctrl_opt_*', 'model_v4_ctrl_test_*'):
        dirs[pat] = sorted(Path(p).name.rsplit('_', 1)[1] for p in glob.glob(str(EVAL_DIR / pat)))
    dir_routes = sorted(set(dirs['model_v4_ctrl_opt_*']) | set(dirs['model_v4_ctrl_test_*']))
    union = sorted(set(script_routes) | set(doc_routes) | set(dir_routes))
    res = {'sources': {
        'docs/CONTROLLER_OPTIMIZATION_EXPERIMENT.md': {'routes': doc_routes,
                                                       'checkpoint': 'checkpoint-20050 (model_v4, 16,040 balanced samples)'},
        'scripts/common/eval_faulty_routes.sh ROUTES': {'routes': script_routes,
                                                       'checkpoint': '/home/aimslab/checkpoints/action_experts/model_v4 (checkpoint-20050 per script header)'},
        'result directories': dirs},
        'tuning_routes_union': union,
        'tuning_routes_with_result_directories': dir_routes,
        'canonical_in_union': [r for r in CANONICAL_44 if r in union],
        'note': ('The document describes changing the turn lookahead to 2.8-5.0 m and alpha_steer to 1.0/0.70; the '
                 'controller in alpamayo_bridge_agent.py used for the 44-route matrix has the "before" values '
                 '(5.5-8.5 m lookahead, alpha_steer 0.85/0.60). Which controller version produced the ctrl_opt '
                 'directories cannot be established from these files.'),
        'H2_excluding': {}}
    for name, excl in (('union', union), ('result_directories_only', dir_routes)):
        keep = [i for i, r in enumerate(CANONICAL_44) if r not in excl]
        x, y = vals[G64]['standstill_pct'][keep], vals[FM]['standstill_pct'][keep]
        res['H2_excluding'][name] = {'n_routes': len(keep), 'routes': [CANONICAL_44[i] for i in keep],
                                     'standstill_pct': paired(x, y)}
    return res


# --------------------------------------------------------------------------- I

def analysis_I(data):
    res = {'gate_like_L_thresholds': {}, 'velocity_thresholds': {}}
    ps = []
    for X in COMPARATORS:
        for t in GATE_SWEEP_L:
            f = lambda rd, t=t: pct(rd['L'] < t)  # noqa: E731
            p = paired(per_route(data, G64, f), per_route(data, X, f), ci=False)
            res['gate_like_L_thresholds'][f'{G64} vs {X} · L<{t}'] = p
            ps.append(p['wilcoxon']['p'])
        for v in SWEEP_V:
            f = lambda rd, v=v: pct(rd['speed'] < v)  # noqa: E731
            p = paired(per_route(data, G64, f), per_route(data, X, f), ci=False)
            res['velocity_thresholds'][f'{G64} vs {X} · v<{v}'] = p
            ps.append(p['wilcoxon']['p'])
    res['n_specifications'] = len(ps)
    res['min_p'] = float(min(ps)); res['max_p'] = float(max(ps))
    res['reference'] = ('Ported from stress_test_paper.py (tests 1-2): plain L < t and speed < v, per-route % of '
                        'logged steps, two-sided Wilcoxon; comparator set extended to matched and historical.')
    return res


# --------------------------------------------------------------------------- J

CAUTION_RE = [re.compile(p) for p in CAUTION_PATTERNS]
PROCEED_RE = [re.compile(p) for p in PROCEED_PATTERNS]


def coc_class(text, cache):
    if text not in cache:
        t = text.lower()
        if any(p.search(t) for p in CAUTION_RE):
            cache[text] = 1
        elif any(p.search(t) for p in PROCEED_RE):
            cache[text] = 0
        else:
            cache[text] = 2
    return cache[text]


def analysis_J(data):
    cache = {}
    top = Counter(); by_model = {m: Counter() for m in MODELS}
    for m in MODELS:
        for r in CANONICAL_44:
            rd = data[m][r]
            for s, v in zip(rd['coc'], rd['speed']):
                if v < SS_V:
                    by_model[m][s] += 1
    for m in MODELS:
        top.update(by_model[m])
    labels = ['proceed', 'caution', 'other']
    top40 = []
    for s, n in sorted(top.items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        top40.append({'coc': s, 'n_standstill_steps_all_models': n, 'class': labels[coc_class(s, cache)],
                      'by_model': {m: by_model[m][s] for m in MODELS}})
    per = {}
    res = {'heuristic': ('KEYWORD HEURISTIC, not a validated classifier. Lower-cased coc text; CAUTION if any '
                         'caution pattern matches; PROCEED if any proceed pattern matches and no caution pattern; '
                         'else OTHER. Patterns are Python regexes (\\b = word boundary, so "stop" does not match '
                         '"stopped").'),
           'caution_patterns': CAUTION_PATTERNS, 'proceed_patterns': PROCEED_PATTERNS,
           'top40_standstill_coc': top40, 'models': {}, 'pairs': {}}
    for m in MODELS:
        arr = np.zeros((44, 3))
        for i, r in enumerate(CANONICAL_44):
            rd = data[m][r]
            cls = np.array([coc_class(s, cache) for s in rd['coc']])
            ss = rd['speed'] < SS_V
            for k in range(3):
                arr[i, k] = pct(ss & (cls == k))
        per[m] = arr
        res['models'][m] = {f'pct_steps_standstill_and_{labels[k]}': float(arr[:, k].mean()) for k in range(3)}
    for X in COMPARATORS:
        res['pairs'][f'{G64} vs {X}'] = {labels[k]: paired(per[G64][:, k], per[X][:, k]) for k in range(3)}
    return res


# --------------------------------------------------------------------------- K

def analysis_K(vals, data):
    res = {}
    for b in (G16, FM):
        drc = vals[G64]['route_completion'] - vals[b]['route_completion']
        dp = per_route(data, G64, lambda rd: rd['penalty']) - per_route(data, b, lambda rd: rd['penalty'])
        dds = vals[G64]['driving_score'] - vals[b]['driving_score']
        sp, pe = stats.spearmanr(drc, dp), stats.pearsonr(drc, dp)
        res[f'{G64} vs {b}'] = {
            'mean_delta_rc': float(drc.mean()), 'mean_delta_penalty': float(dp.mean()),
            'mean_delta_ds': float(dds.mean()),
            'spearman_dRC_dP': {'rho': float(sp.statistic), 'p': float(sp.pvalue)},
            'pearson_dRC_dP': {'r': float(pe.statistic), 'p': float(pe.pvalue)},
            'n_routes_dRC_pos_dDS_neg': int(np.sum((drc > 0) & (dds < 0))),
            'n_routes_dRC_neg_dDS_pos': int(np.sum((drc < 0) & (dds > 0))),
            'per_route': {r: {'dRC': float(a), 'dP': float(p), 'dDS': float(d)}
                          for r, a, p, d in zip(CANONICAL_44, drc, dp, dds)}}
    res['note'] = 'All 44 routes; no subset selection.'
    return res


# --------------------------------------------------------------------------- L

def steer_jerk_moving(rd):
    # Definition from evaluate_confirmatory_plan.load_telemetry: mean |diff(steer)| over steps whose
    # earlier step has speed >= 0.1 m/s.
    mov = rd['speed'][:-1] >= 0.1
    dj = np.abs(np.diff(rd['steer']))
    return float(np.mean(dj[mov])) if np.any(mov) else float('nan')


def analysis_L(data, counts, expo):
    res = {'models': {}, 'definitions': {
        'mean_speed_route_mean': 'mean over routes of each route\'s mean logged speed (m/s)',
        'mean_speed_pooled': 'mean over all logged steps pooled across routes (m/s)',
        'moving_steer_jerk': 'evaluate_confirmatory_plan.load_telemetry steer_jerk_moving, averaged over routes',
        'hard_brake_pct': 'per-route % of steps with brake > 0.5, averaged over routes',
        'standstill_pct_as_compute_paper_tables': ('Base only: compute_paper_tables.load_model_data reads '
                                                   'base_23687, which has no step log, and scores it 0 %')}}
    for m in MODELS:
        rds = [data[m][r] for r in CANONICAL_44]
        tot = {k: int(sum(c[k] for c in counts[m])) for k in counts[m][0]}
        pkm, okm = float(expo[m][:, 0].sum()), float(expo[m][:, 1].sum())
        jerk = [steer_jerk_moving(rd) for rd in rds]
        ss = np.array([pct(rd['speed'] < SS_V) for rd in rds])
        ss_ref = np.array([0.0 if rd['steplog_dir'] != rd['endpoint_dir'] else s for rd, s in zip(rds, ss)])
        inf_count = lambda k: int(sum(len(rd['infractions'].get(k, [])) for rd in rds))  # noqa: E731
        res['models'][m] = {
            'mean_ds': float(np.mean([rd['ds'] for rd in rds])),
            'mean_rc': float(np.mean([rd['rc'] for rd in rds])),
            'mean_penalty': float(np.mean([rd['penalty'] for rd in rds])),
            'progress_km': pkm, 'odometer_km': okm,
            'collisions_raw': tot['raw'], 'collisions_events': tot['events_actor_id'],
            'collisions_raw_by_class': {c: tot[f'raw_{c}'] for c in COLLISION_KEYS.values()},
            'collisions_events_by_class': {c: tot[f'events_actor_id_{c}'] for c in COLLISION_KEYS.values()},
            'events_per_progress_km': tot['events_actor_id'] / pkm, 'events_per_odometer_km': tot['events_actor_id'] / okm,
            'non_timeout_infractions': tot['non_timeout_raw'],
            'non_timeout_per_progress_km': tot['non_timeout_raw'] / pkm,
            'non_timeout_per_odometer_km': tot['non_timeout_raw'] / okm,
            'standstill_pct': float(ss.mean()),
            'standstill_pct_as_compute_paper_tables': float(ss_ref.mean()),
            'routes_with_steplog_from_fallback_prefix': [r for r, rd in zip(CANONICAL_44, rds)
                                                         if rd['steplog_dir'] != rd['endpoint_dir']],
            'mean_speed_route_mean': float(np.mean([np.mean(rd['speed']) for rd in rds])),
            'mean_speed_pooled': float(np.concatenate([rd['speed'] for rd in rds]).mean()),
            'moving_steer_jerk': float(np.nanmean(jerk)),
            'hard_brake_pct': float(np.mean([pct(rd['brake'] > 0.5) for rd in rds])),
            'red_light': inf_count('red_light'), 'stop_infraction': inf_count('stop_infraction'),
            'outside_route_lanes': inf_count('outside_route_lanes'), 'vehicle_blocked': inf_count('vehicle_blocked'),
            'min_speed_infractions': inf_count('min_speed_infractions')}
    match = {}
    for m, v in MANUSCRIPT_MEAN_SPEED.items():
        e = res['models'][m]
        match[m] = {'manuscript': v, 'route_mean_2dp': round(e['mean_speed_route_mean'], 2),
                    'pooled_2dp': round(e['mean_speed_pooled'], 2),
                    'matches_route_mean': round(e['mean_speed_route_mean'], 2) == v,
                    'matches_pooled': round(e['mean_speed_pooled'], 2) == v}
    res['manuscript_mean_speed_match'] = match
    return res


# --------------------------------------------------------------------------- M

def truncate_at_60s_rule(speed):
    run = 0
    for i, v in enumerate(speed):
        run = run + 1 if v < SS_V else 0
        if run == STANDSTILL_RULE_STEPS:
            return i + 1
    return len(speed)


def analysis_M(data):
    res = {'rule': ('Truncate each step log after the first step that completes 1,200 consecutive logged steps '
                    'with speed < 0.1 m/s (harness: >1,200 ticks of 3-D velocity < 0.1). Driving Score cannot be '
                    'harmonised this way (infractions and completion after the cut are unknown).'),
           'models': {}}
    harm = {}
    for m in MODELS:
        orig, new, affected, has_run, removed = [], [], [], [], {}
        for r in CANONICAL_44:
            sp = data[m][r]['speed']
            n = truncate_at_60s_rule(sp)
            orig.append(pct(sp < SS_V)); new.append(pct(sp[:n] < SS_V))
            if n < len(sp):
                affected.append(r)
                removed[r] = int(len(sp) - n)
            if n < len(sp) or (n == len(sp) and n >= STANDSTILL_RULE_STEPS and np.all(sp[n - STANDSTILL_RULE_STEPS:n] < SS_V)):
                has_run.append(r)
        harm[m] = np.array(new)
        res['models'][m] = {'standstill_pct_original': float(np.mean(orig)), 'standstill_pct_harmonised': float(np.mean(new)),
                            'n_routes_shortened': len(affected), 'routes_shortened': affected,
                            'steps_removed_by_route': removed,
                            'n_routes_shortened_by_more_than_1_step': sum(1 for v in removed.values() if v > 1),
                            'n_routes_with_1200_step_standstill_run': len(has_run),
                            'steps_removed_total': int(sum(data[m][r]['n_steps'] - truncate_at_60s_rule(data[m][r]['speed'])
                                                           for r in CANONICAL_44))}
    res['pairs_harmonised_standstill'] = {f'{a} vs {b}': paired(harm[a], harm[b])
                                          for a, b in ((G16, BASE), (F16, BASE), (G64, FM), (G64, FH))}
    return res


# --------------------------------------------------------------------------- report

def f(x, nd=3):
    if isinstance(x, str):
        return x
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 'n/a'
    if isinstance(x, (int, np.integer)):
        return str(x)
    if x != 0 and abs(x) < 10 ** (-nd):
        return f'{x:.2e}'
    return f'{x:.{nd}f}'


def fp(p):
    return p if isinstance(p, str) else (f'{p:.2e}' if p < 1e-3 else f'{p:.4f}')


def table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)]
    out += ['| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows]
    return '\n'.join(out)


def ci_str(c, nd=3):
    return f'[{f(c[0], nd)}, {f(c[1], nd)}]' if isinstance(c, list) else 'n/a'


def pair_row(label, p, nd=3):
    w = p['wilcoxon']
    return [label, f(p['mean_first'], nd), f(p['mean_second'], nd), f(p['mean_diff'], nd),
            ci_str(p.get('bca95'), nd), f(w.get('statistic', 'n/a'), 1), w['n_zero_differences'],
            fp(w.get('p', 'n/a')), fp(w.get('p_exact', 'n/a')) if not isinstance(w.get('p_exact'), str) else 'n/a',
            fp(w.get('p_approx', 'n/a')), f"{p['n_first_greater']}/{p['n_first_less']}/{p['n_tie']}",
            f(w.get('rank_biserial', 'n/a'), 3)]


PAIR_HDR = ['comparison', 'mean 1st', 'mean 2nd', 'diff', 'BCa 95%', 'W', 'zeros', 'p', 'p exact', 'p approx',
            '1st>/</=', 'r_rb']


def render(man):
    L = ['# Paper re-analysis (reviewer round 1)', '',
         'Generated by `scripts/evaluation/paper_reanalysis.py`; every number is in '
         '`outputs/paper_reanalysis_manifest.json`. Differences are first model minus second, over the 44 '
         'canonical routes unless stated. Percentages are percentage points. W = Wilcoxon statistic, '
         'r_rb = matched-pairs rank-biserial, "1st>/</=" = routes where the first model is higher/lower/equal.', '']
    L += ['## Data checks', '', '```', json.dumps(man['data_checks'], indent=1), '```', '']

    A = man['A']
    L += ['## A. Pairwise tests', '', f"Primary reproduction check passed: `{A['primary_reproduction_check']['obtained_rounded']}`.", '']
    for k in ('standstill_pct', 'driving_score', 'route_completion', 'mean_speed_mps', 'gate_pct', 'mean_L_m'):
        L += [f'**{k}** ({A["metric_definitions"][k]})', '', table(PAIR_HDR, [pair_row(n, v[k]) for n, v in A['pairs'].items()]), '']
    h = A['holm_2_test_family']
    L += ['**Holm, 2-test family** (H1 two-sided; variant with one-sided H1 in manifest)', '',
          table(['test', 'raw p', 'Holm p'], [[t, fp(a), fp(b)] for t, a, b in zip(h['tests'], h['raw_p'], h['holm_p'])]),
          '', h['note'], '']
    L += ['**TOST / non-inferiority (margin 8 DS)**', '',
          table(['test', 'mean diff', 'BCa 90%', 'bootstrap p'],
                [[k, f(v['mean_diff']), ci_str(v['bca90']), fp(v.get('p_tost_bootstrap', v.get('p_noninferiority_bootstrap')))]
                 for k, v in A['tost_noninferiority'].items() if isinstance(v, dict)]), '',
          A['tost_noninferiority']['method'], '']
    for fam, v in A['holm_4_test_families'].items():
        L += [f'**Holm, 4-test {fam}**', '', table(['test', 'raw p', 'Holm p'],
                                                 [[t, fp(a), fp(b)] for t, a, b in zip(v['tests'], v['raw_p'], v['holm_p'])]), '']
    L += ['**DS source check** (endpoint DS vs `final_2x2_anova_matrix_report.json`)', '',
          table(['model', 'routes in json', 'max |ΔDS|'], [[m, v['n_routes_in_json'], f(v['max_abs_ds_difference'], 6)]
                                                         for m, v in A['ds_source_check'].items()]), '']
    L += ['**2×2 difference-in-differences**', '', table(PAIR_HDR, [pair_row(k, v) for k, v in A['difference_in_differences'].items()]), '']

    B = man['B']
    L += ['## B. Sensitivity of the primary comparison', '']
    rows = []
    for k, v in B.items():
        if not k.startswith(G64):
            continue
        rows.append(pair_row(f'{k} · common window %', v['common_tick_window_standstill_pct']))
        rows.append(pair_row(f'{k} · standstill s', v['standstill_seconds'], 2))
        for t, p in v['standstill_thresholds_pct'].items():
            rows.append(pair_row(f'{k} · {t}', p))
    L += [table(PAIR_HDR, rows), '', f"Termination ({B['termination_rule']}):", '',
          table(['model', 'status counts', 'TickRuntime: 60 s rule', 'TickRuntime: 4000 cap'],
                [[m, ', '.join(f'{s}: {n}' for s, n in v['status_counts'].items()),
                  f"{v['n_60s_rule']} {v['tickruntime_ended_before_cap_60s_rule']}",
                  f"{v['n_cap']} {v['tickruntime_ended_at_cap_ge_4000_ticks']}"]
                 for m, v in B['termination_by_model'].items()]), '']

    C = man['C']
    L += ['## C. Strata (exploratory, unadjusted)', '',
          f"Primary-ability rule reproduces STRATA_MAP: {C['primary_ability_rule_reproduces_STRATA_MAP']}", '']
    rows = []
    for g, v in C['groups'].items():
        mm = v['models']
        cells = [g, v['n']] + [f"{f(mm[m]['standstill_pct'], 1)} / {f(mm[m]['mean_speed_mps'], 2)} / {f(mm[m]['gate_pct'], 1)}" for m in MODELS]
        for X in COMPARATORS:
            p = v['pairs'][f'{G64} vs {X}']['standstill_pct']
            cells.append(f"{f(p['mean_diff'], 2)} {ci_str(p.get('bca95'), 2) if 'bca95' in p else ''} p={fp(p['wilcoxon'].get('p', 'n/a'))}")
        rows.append(cells)
    L += ['Cells per model: standstill % / mean speed m/s / gate %. Last two columns: Golden-6400 minus comparator, standstill (BCa only when N ≥ 9).', '',
          table(['group', 'N'] + MODELS + [f'Δ vs {X}' for X in COMPARATORS], rows), '']
    L += ['Per-route standstill % for groups with N < 9 (Golden-6400 / comparator):', '']
    for g, v in C['groups'].items():
        if v['n'] < 9:
            for X in COMPARATORS:
                pr = v['pairs'][f'{G64} vs {X}']['standstill_pct']['per_route']
                L.append(f"- {g}, vs {X}: " + ', '.join(f"{r}: {f(x['first'], 1)}/{f(x['second'], 1)}" for r, x in pr.items()))
    L.append('')

    D = man['D']
    L += ['## D. Offline gate decomposition', '', D['note'], '',
          table(['model'] + [f'{b}: all / ss∧band / share of ss' for b in BANDS],
                [[m] + [f"{f(v['pct_of_all_steps_in_band'][b], 2)} / {f(v['pct_of_all_steps_standstill_and_in_band'][b], 2)} / {f(v['share_of_standstill_steps_in_band_pct'][b], 1)}"
                        for b in BANDS] for m, v in D['models'].items()]), '']
    for k, v in D['pairs'].items():
        L += [f"**{k}**: total standstill diff {f(v['total_standstill_diff'])}, sum of bands {f(v['sum_of_band_diffs'])}", '',
              table(PAIR_HDR + ['share of gap %'], [pair_row(b, p) + [f(v['share_of_gap_by_band_pct'][b], 1)]
                                                   for b, p in v['standstill_and_band_diff'].items()]), '']

    E = man['E']
    L += ['## E. What binds at standstill with the gate inactive', '', E['definition'], '']
    L += ['Approximations: ' + ' '.join(E['approximations']), '',
          table(['model', '% steps ss & gate off'] + [f'{c} (% all steps)' for c in E_CLASSES] + ['pooled n'],
                [[m, f(v['pct_of_all_steps_standstill_gate_inactive'], 2)] + [f(v['pct_of_all_steps_by_class'][c], 2) for c in E_CLASSES]
                 + [v['pooled_n_steps']] for m, v in E['models'].items()]), '',
          'Pooled share within these steps (%): ' + '; '.join(
              f"{m}: " + ', '.join(f(v['pooled_share_pct'][c], 1) for c in E_CLASSES) for m, v in E['models'].items()), '',
          'Logged throttle in the "throttle>0" class (median / mean / % ≥ 0.35): ' + '; '.join(
              f"{m}: {f(v['throttle_in_throttle_class']['median'])} / {f(v['throttle_in_throttle_class']['mean'])} / "
              f"{f(v['throttle_in_throttle_class']['pct_ge_0.35'], 1)}" for m, v in E['models'].items()), '']
    for k, v in E['pairs'].items():
        L += [f'**{k}** (% of all steps)', '', table(PAIR_HDR, [pair_row(c, p) for c, p in v.items()]), '']

    F = man['F']
    L += ['## F. Collisions and infractions', '', '```', json.dumps(F['definitions'], indent=1), '```', '',
          table(['model', 'raw (veh/ped/lay)', 'events id-merged', 'events exact-merged', 'progress km', 'odometer km',
                 'events/progress km [95%]', 'events/odo km [95%]', 'non-timeout', 'non-timeout/progress km'],
                [[m, f"{v['totals']['raw']} ({v['totals']['raw_vehicle']}/{v['totals']['raw_pedestrian']}/{v['totals']['raw_layout']})",
                  v['totals']['events_actor_id'], v['totals']['events_exact_string'], f(v['progress_km'], 2), f(v['odometer_km'], 2),
                  f"{f(v['rates']['events_actor_id_per_progress_km']['rate'], 2)} {ci_str(v['rates']['events_actor_id_per_progress_km']['ci95'], 2)}",
                  f"{f(v['rates']['events_actor_id_per_odometer_km']['rate'], 2)} {ci_str(v['rates']['events_actor_id_per_odometer_km']['ci95'], 2)}",
                  v['totals']['non_timeout_raw'],
                  f"{f(v['rates']['non_timeout_raw_per_progress_km']['rate'], 2)} {ci_str(v['rates']['non_timeout_raw_per_progress_km']['ci95'], 2)}"]
                 for m, v in F['models'].items()]), '']
    rows = []
    for k, v in F['pairs'].items():
        for ck, e in v.items():
            rr = [f"{f(e[x]['rate_ratio'])} {ci_str(e[x]['ci95'])}" if 'rate_ratio' in e[x] else 'n/a'
                  for x in ('rate_ratio_progress_km', 'rate_ratio_odometer_km')]
            w = e['wilcoxon_per_route_counts']
            rows.append([k, ck, *rr, f(w['mean_diff']), fp(w['wilcoxon'].get('p', 'n/a'))])
    L += [table(['pair', 'count', 'RR progress [95%]', 'RR odometer [95%]', 'mean Δcount/route', 'Wilcoxon p'], rows), '']

    G = man['G']
    L += ['## G. Vulnerable-road-user routes', '', G['trigger_method'], '',
          f"Routes with a pedestrian collision in any model: {G['routes_with_pedestrian_collision_any_model']}", '']
    for r, v in G['routes'].items():
        g = v['geometry']
        L += [f"**Route {r}** ({v['scenario']}, {g['town']}): trigger at {f(v['trigger_fraction_used_pct'], 1)} % of polyline; "
              f"polyline/route_length = {f(g['polyline_to_route_length_ratio'], 3)}; trigger {f(g['triggers'][0]['distance_to_polyline_m'], 2)} m "
              f"from polyline; max keypoint spacing {f(g['max_keypoint_spacing_m'], 1)} m", '',
              table(['model', 'RC %', 'status', 'ped coll', 'reached trigger'],
                    [[m, f(x['rc'], 1), x['status'], x['pedestrian_collisions'], x['reached_trigger']] for m, x in v['models'].items()]), '']
        strs = [f"{m}: {s}" for m, x in v['models'].items() for s in x['pedestrian_collision_strings']]
        if strs:
            L += ['Pedestrian collision strings:', ''] + [f'- {s}' for s in strs] + ['']

    H = man['H']
    L += ['## H. Controller-tuning routes', '', '```', json.dumps(H['sources'], indent=1), '```', '',
          f"Union of tuning routes: {H['tuning_routes_union']}", '', H['note'], '',
          table(PAIR_HDR, [pair_row(f"H2 excluding {k} (N={v['n_routes']})", v['standstill_pct']) for k, v in H['H2_excluding'].items()]), '']

    I = man['I']
    L += ['## I. Threshold sweep', '', I['reference'], '',
          f"{I['n_specifications']} specifications; min p = {fp(I['min_p'])}, max p = {fp(I['max_p'])}.", '',
          table(PAIR_HDR, [pair_row(k, v) for k, v in {**I['gate_like_L_thresholds'], **I['velocity_thresholds']}.items()]), '']

    J = man['J']
    L += ['## J. Proceed-cued standstill (keyword heuristic)', '', J['heuristic'], '',
          f"Caution patterns: `{J['caution_patterns']}`", '', f"Proceed patterns: `{J['proceed_patterns']}`", '',
          '40 most frequent rationales during standstill (all models):', '',
          table(['#', 'coc', 'n', 'class'] + MODELS,
                [[i + 1, x['coc'], x['n_standstill_steps_all_models'], x['class']] + [x['by_model'][m] for m in MODELS]
                 for i, x in enumerate(J['top40_standstill_coc'])]), '',
          table(['model', '% steps ss∧proceed', '% ss∧caution', '% ss∧other'],
                [[m] + [f(x, 2) for x in v.values()] for m, v in J['models'].items()]), '']
    for k, v in J['pairs'].items():
        L += [f'**{k}**', '', table(PAIR_HDR, [pair_row(c, p) for c, p in v.items()]), '']

    K = man['K']
    L += ['## K. Driving Score plateau check', '', K['note'], '',
          table(['pair', 'mean ΔRC', 'mean ΔP', 'mean ΔDS', 'Spearman ρ (p)', 'Pearson r (p)', 'ΔRC>0 & ΔDS<0', 'ΔRC<0 & ΔDS>0'],
                [[k, f(v['mean_delta_rc'], 2), f(v['mean_delta_penalty'], 4), f(v['mean_delta_ds'], 2),
                  f"{f(v['spearman_dRC_dP']['rho'])} ({fp(v['spearman_dRC_dP']['p'])})",
                  f"{f(v['pearson_dRC_dP']['r'])} ({fp(v['pearson_dRC_dP']['p'])})",
                  v['n_routes_dRC_pos_dDS_neg'], v['n_routes_dRC_neg_dDS_pos']]
                 for k, v in K.items() if isinstance(v, dict)]), '']

    Lm = man['L']
    keys = ['mean_ds', 'mean_rc', 'mean_penalty', 'progress_km', 'odometer_km', 'collisions_raw', 'collisions_events',
            'events_per_progress_km', 'events_per_odometer_km', 'non_timeout_infractions', 'non_timeout_per_progress_km',
            'non_timeout_per_odometer_km', 'standstill_pct', 'standstill_pct_as_compute_paper_tables',
            'mean_speed_route_mean', 'mean_speed_pooled', 'moving_steer_jerk', 'hard_brake_pct', 'red_light',
            'stop_infraction', 'outside_route_lanes', 'vehicle_blocked', 'min_speed_infractions']
    L += ['## L. Summary table', '', '```', json.dumps(Lm['definitions'], indent=1), '```', '',
          table(['metric'] + MODELS, [[k] + [f(Lm['models'][m][k], 4) for m in MODELS] for k in keys]
                + [['collisions raw v/p/l'] + ['/'.join(str(x) for x in Lm['models'][m]['collisions_raw_by_class'].values()) for m in MODELS],
                   ['collisions events v/p/l'] + ['/'.join(str(x) for x in Lm['models'][m]['collisions_events_by_class'].values()) for m in MODELS]]),
          '', 'Manuscript mean-speed values vs the two definitions:', '',
          table(['model', 'manuscript', 'route mean', 'pooled', 'matches route mean', 'matches pooled'],
                [[m, v['manuscript'], v['route_mean_2dp'], v['pooled_2dp'], v['matches_route_mean'], v['matches_pooled']]
                 for m, v in Lm['manuscript_mean_speed_match'].items()]), '']

    M = man['M']
    L += ['## M. Harmonised 60 s termination rule', '', M['rule'], '',
          table(['model', 'standstill % original', 'harmonised', 'routes shortened', 'steps removed', 'routes with a 1,200-step run'],
                [[m, f(v['standstill_pct_original']), f(v['standstill_pct_harmonised']),
                  f"{v['n_routes_shortened']} ({v['n_routes_shortened_by_more_than_1_step']} by >1 step)",
                  f"{v['steps_removed_total']} {v['steps_removed_by_route']}", v['n_routes_with_1200_step_standstill_run']]
                 for m, v in M['models'].items()]), '',
          table(PAIR_HDR, [pair_row(k, v) for k, v in M['pairs_harmonised_standstill'].items()]), '']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------- main

def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        v = float(o)
        return None if math.isnan(v) or math.isinf(v) else v
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    data = load_all()
    scen = load_route_scenarios()
    checks = {'reference_loader_cross_check': cross_check_with_reference_loader(data),
              'step_log_fallbacks': {m: {r: f"endpoint {data[m][r]['endpoint_dir']}, step log {data[m][r]['steplog_dir']} (endpoint records identical)"
                                         for r in CANONICAL_44 if data[m][r]['steplog_dir'] != data[m][r]['endpoint_dir']}
                                     for m in MODELS},
              'routes_with_non_consecutive_logged_steps': {m: [r for r in CANONICAL_44 if data[m][r]['step_gaps']] for m in MODELS},
              'logged_steps_minus_round_duration_x20_counts': {
                  m: {str(k): v for k, v in sorted(Counter(int(data[m][r]['n_steps'] - round(data[m][r]['duration_game'] * 20))
                                                           for r in CANONICAL_44).items())} for m in MODELS}}
    man = {'data_checks': checks}
    man['A'], vals = analysis_A(data)
    print('A done', flush=True)
    man['B'] = analysis_B(data)
    man['C'] = analysis_C(data, scen)
    man['D'] = analysis_D(data)
    man['E'] = analysis_E(data)
    print('B-E done', flush=True)
    man['F'], counts, expo = analysis_F(data)
    man['G'] = analysis_G(data, scen)
    man['H'] = analysis_H(data, vals)
    man['I'] = analysis_I(data)
    man['J'] = analysis_J(data)
    man['K'] = analysis_K(vals, data)
    man['L'] = analysis_L(data, counts, expo)
    man['M'] = analysis_M(data)
    man = clean(man)
    OUT_MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=False, ensure_ascii=False) + '\n')
    OUT_REPORT.write_text(render(man))
    p = man['A']['pairs'][f'{G64} vs {FM}']['standstill_pct']
    print(f"primary H2 reproduced: diff={p['mean_diff']:.4f} BCa={p['bca95']} W={p['wilcoxon']['statistic']} p={p['wilcoxon']['p']:.6f}")
    print(f'wrote {OUT_MANIFEST}\nwrote {OUT_REPORT}')


if __name__ == '__main__':
    main()
