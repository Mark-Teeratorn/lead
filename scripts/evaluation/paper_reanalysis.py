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
# Per-step controller fields written only by the gate-off agent (alpamayo_bridge_agent_nogate.py).
LOGGED_CONTROLLER_FIELDS = ['traj_extent', 'gate_would_fire', 'target_speed_kmh', 'raw_throttle', 'raw_brake']


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
    return parse_route_dirs(ep_dir, log_dir, f'{model} {route}')


def parse_route_dirs(ep_dir, log_dir, label, tolerate_partial_last_line=False):
    rec = json.load(open(ep_dir / 'checkpoint_endpoint.json'))['_checkpoint']['records'][0]
    model, route = label, ''
    if log_dir != ep_dir:
        # The step log comes from a fallback prefix; require the two endpoint records to agree.
        rec2 = json.load(open(log_dir / 'checkpoint_endpoint.json'))['_checkpoint']['records'][0]
        if rec2['scores'] != rec['scores'] or rec2['infractions'] != rec['infractions']:
            raise RuntimeError(f'{model} {route}: endpoint of {ep_dir.name} differs from {log_dir.name}')
    wps, speed, steer, thr, brk, coc, steps = [], [], [], [], [], [], []
    extra = {k: [] for k in LOGGED_CONTROLLER_FIELDS}
    with open(log_dir / 'predicted_trajectories.jsonl') as f:
        lines = [ln for ln in f if ln.strip()]
    for li, line in enumerate(lines):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            if tolerate_partial_last_line and li == len(lines) - 1:
                break
            raise
        for k in extra:
            if k in d:
                extra[k].append(d[k])
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
        'speed': speed, 'L': cum[:, -1].copy(), 'y_end': wp[:, -1, 1].copy(),
        'v_end': cum[:, -1] - cum[:, -11],   # m/s: path between waypoints 54 and 64 over 1.0 s (addendum 11-A)
        'steer': np.asarray(steer), 'throttle': np.asarray(thr), 'brake': np.asarray(brk),
        'target': target, 'coc': coc,
        'n_steps': len(speed), 'step_gaps': int(np.sum(np.diff(steps) != 1)),
        'logged_controller': {k: np.asarray(v, dtype=np.float64) for k, v in extra.items() if len(v) == len(speed)},
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
        try:
            res = stats.wilcoxon(x, y)
        except ValueError as e:
            out.update({'status': 'not_computable', 'reason': str(e)})
            return out
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
        res['models'][m] = summary_row([data[m][r] for r in CANONICAL_44], counts[m], expo[m])
    match = {}
    for m, v in MANUSCRIPT_MEAN_SPEED.items():
        e = res['models'][m]
        match[m] = {'manuscript': v, 'route_mean_2dp': round(e['mean_speed_route_mean'], 2),
                    'pooled_2dp': round(e['mean_speed_pooled'], 2),
                    'matches_route_mean': round(e['mean_speed_route_mean'], 2) == v,
                    'matches_pooled': round(e['mean_speed_pooled'], 2) == v}
    res['manuscript_mean_speed_match'] = match
    return res


def summary_row(rds, cnts, ex):
    """One row of summary table L for 44 route records (in CANONICAL_44 order)."""
    tot = {k: int(sum(c[k] for c in cnts)) for k in cnts[0]}
    pkm, okm = float(ex[:, 0].sum()), float(ex[:, 1].sum())
    jerk = [steer_jerk_moving(rd) for rd in rds]
    ss = np.array([pct(rd['speed'] < SS_V) for rd in rds])
    ss_ref = np.array([0.0 if rd['steplog_dir'] != rd['endpoint_dir'] else s for rd, s in zip(rds, ss)])
    inf_count = lambda k: int(sum(len(rd['infractions'].get(k, [])) for rd in rds))  # noqa: E731
    return {
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
          '', *([f"Additional runs with all 44 routes usable: {list(Lm['additional_models'])}", '',
                table(['metric'] + list(Lm['additional_models']),
                      [[k] + [f(Lm['additional_models'][m][k], 4) for m in Lm['additional_models']] for k in keys]), '']
                if Lm.get('additional_models') else []),
          'Manuscript mean-speed values vs the two definitions:', '',
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


# --------------------------------------------------------------------------- new runs (N-R)

# Additional result tags (ANALYSIS_ADDENDUM.md sections 4b, 4c, 5a, 5b). Arm name -> directory prefix.
NEW_RUN_TAGS = {
    'Golden-6400 rep1': 'model_matrix_golden_6400_rep1',
    'Flooded-6400-Matched rep1': 'model_matrix_flooded_6400_rep1',
    'Golden-6400 run2': 'model_matrix_golden_6400_run2',
    'Flooded-6400-Matched run2': 'model_matrix_flooded_6400_run2',
    'Golden-6400 nogate': 'model_matrix_golden_6400_nogate',
    'Flooded-6400-Matched nogate': 'model_matrix_flooded_6400_nogate',
    'Base run2': 'base_run2',
    'Balanced-6400 run1': 'model_matrix_fgbalanced_6400',   # ANALYSIS_ADDENDUM.md section 6
}
# First-pass arms, named the same way (tags from MODEL_PREFIXES).
RUN1_ARMS = {'Golden-6400 run1': G64, 'Flooded-6400-Matched run1': FM, 'Base run1': BASE,
             'Golden-1600': G16, 'Flooded-1600': F16}
# ANALYSIS_ADDENDUM.md section 4b (the 8 listed routes; = first 8 of every fifth CANONICAL_44 entry).
REPLICATE_ROUTES = ['2534', '3561', '1790', '23695', '28087', '2664', '17563', '26458']
# docs/provenance/train_eval_overlap_canonical44.json: canonical routes with Matrix training samples
# ("excluding 7 routes with training samples in the Matrix cells").
OVERLAP_FILE = ROOT / 'docs/provenance/train_eval_overlap_canonical44.json'
OVERLAP_7 = ['1852', '1825', '2286', '23901', '23695', '3464', '2164']
# Same file, "all_canonical_hit_by_any_gate_excluded_route" minus OVERLAP_7 (the 11-route exclusion).
GATE_FLAGGED_EXTRA_4 = ['2513', '2790', '2283', '23771']
ROUTE_SUBSETS = {
    '44 routes': CANONICAL_44,
    '37 routes (excl. 7 training-overlap routes)': [r for r in CANONICAL_44 if r not in OVERLAP_7],
    '33 routes (excl. 11 gate-flagged routes)': [r for r in CANONICAL_44 if r not in OVERLAP_7 + GATE_FLAGGED_EXTRA_4],
}
P_THRESHOLDS = [0.1, 0.5, 1.0]


def check_route_constants():
    # The addendum lists 8 routes; CANONICAL_44[::5] has a 9th entry (3464, index 40) that it omits.
    assert REPLICATE_ROUTES == CANONICAL_44[::5][:8], 'REPLICATE_ROUTES != first 8 of CANONICAL_44[::5]'
    ov = json.load(open(OVERLAP_FILE))
    sens = ov['sensitivity']
    ex7 = sens['excluding 7 routes with training samples in the Matrix cells']['excluded']
    ex11 = sens['excluding all 11 gate-flagged canonical routes']['excluded']
    assert sorted(ex7) == sorted(OVERLAP_7), 'OVERLAP_7 differs from the provenance file'
    assert sorted(ex11) == sorted(OVERLAP_7 + GATE_FLAGGED_EXTRA_4), 'GATE_FLAGGED_EXTRA_4 differs from the provenance file'
    assert [len(v) for v in ROUTE_SUBSETS.values()] == [44, 37, 33]
    return ov


def usable_dir(tag, route):
    """A route directory is usable only if checkpoint_endpoint.json parses, carries
    _checkpoint.global_record.scores_mean and a record, and predicted_trajectories.jsonl exists."""
    d = EVAL_DIR / f'{tag}_{route}'
    try:
        ck = json.load(open(d / 'checkpoint_endpoint.json'))['_checkpoint']
        ok = 'scores_mean' in ck['global_record'] and len(ck['records']) > 0
    except Exception:
        return None
    return d if ok and (d / 'predicted_trajectories.jsonl').exists() else None


def load_new_runs():
    runs, unparsable = {}, {}
    for name, tag in NEW_RUN_TAGS.items():
        routes = REPLICATE_ROUTES if name.endswith('rep1') else CANONICAL_44
        runs[name] = {}
        for r in routes:
            d = usable_dir(tag, r)
            if d is None:
                continue
            try:
                runs[name][r] = parse_route_dirs(d, d, f'{tag} {r}', tolerate_partial_last_line=True)
            except Exception as e:  # e.g. an empty step log: treated as absent
                unparsable.setdefault(tag, {})[r] = f'{type(e).__name__}: {e}'
        print(f'new runs {tag}: {len(runs[name])} usable', flush=True)
    return runs, unparsable


def arm_tag(name):
    if name in NEW_RUN_TAGS:
        return NEW_RUN_TAGS[name]
    return MODEL_PREFIXES[RUN1_ARMS[name]][0]


def ended_by_60s_rule(rd):
    return float(rd['status'] == 'Failed - TickRuntime' and round(rd['duration_game'] * 20) < TICK_CAP)


RUN_METRICS = {
    'standstill_pct': lambda rd: pct(rd['speed'] < SS_V),
    'driving_score': lambda rd: rd['ds'],
    'route_completion': lambda rd: rd['rc'],
    'mean_speed_mps': lambda rd: float(np.mean(rd['speed'])),
    'collision_events': lambda rd: float(route_counts(rd)['events_actor_id']),
    'n_steps': lambda rd: float(rd['n_steps']),
}
P_METRICS = {
    **{f'standstill_pct_v<{v}': (lambda rd, v=v: pct(rd['speed'] < v)) for v in P_THRESHOLDS},
    'mean_speed_mps': RUN_METRICS['mean_speed_mps'],
    'route_completion': RUN_METRICS['route_completion'],
    'driving_score': RUN_METRICS['driving_score'],
    'collision_events': RUN_METRICS['collision_events'],
    **{f'collision_events_{c}': (lambda rd, c=c: float(route_counts(rd)[f'events_actor_id_{c}']))
       for c in COLLISION_KEYS.values()},
    'n_steps': RUN_METRICS['n_steps'],
    'ended_by_60s_rule': ended_by_60s_rule,
}
OBR_METRICS = ['standstill_pct', 'driving_score', 'route_completion', 'collision_events']


def vec(arms, name, fn, routes):
    return np.array([fn(arms[name][r]) for r in routes], dtype=np.float64)


def pending(arms, req):
    """req: list of (arm name, routes). Returns None when every required route is usable."""
    have, need = {}, {}
    for name, routes in req:
        t = arm_tag(name)
        have[t] = min(have.get(t, 10 ** 9), sum(r in arms[name] for r in routes))
        need[t] = max(need.get(t, 0), len(routes))
    if all(have[t] >= need[t] for t in need):
        return None
    return {'status': 'pending', 'have': have, 'need': need}


def spread(d):
    d = np.asarray(d, float)
    return {'n': int(len(d)), 'mean': float(np.mean(d)) if len(d) else None,
            'sd': float(np.std(d, ddof=1)) if len(d) >= 2 else None,
            'mean_abs': float(np.mean(np.abs(d))) if len(d) else None}


def icc_1_1(a, b):
    """One-way random-effects, single-measure ICC(1,1) (Shrout & Fleiss 1979):
    (MSB - MSW) / (MSB + (k - 1) MSW), k = 2 runs, rows = routes."""
    x = np.column_stack([a, b]).astype(float)
    n, k = x.shape
    rm = x.mean(axis=1)
    msb = k * np.sum((rm - x.mean()) ** 2) / (n - 1)
    msw = np.sum((x - rm[:, None]) ** 2) / (n * (k - 1))
    return float((msb - msw) / (msb + (k - 1) * msw)) if (msb + (k - 1) * msw) > 0 else None


def decision_case(p):
    """CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md section 3: A1 CI upper < 0 and diff <= -4;
    A2 CI upper < 0 and -4 < diff < 0; B diff < 0 and CI includes 0; C diff >= 0."""
    if not isinstance(p.get('bca95'), list):
        return 'not_computable'
    d, hi = p['mean_diff'], p['bca95'][1]
    if hi < 0:
        return 'A1' if d <= -4.0 else 'A2'
    return 'B' if d < 0 else 'C'


def status_line(parts):
    """parts: dict of sub-analysis -> result; complete if none pending."""
    pend = [k for k, v in parts.items() if isinstance(v, dict) and v.get('status') == 'pending']
    if not pend:
        return 'complete'
    return f'pending: {len(pend)} of {len(parts)} parts ({", ".join(pend)})'


def analysis_N(arms):
    res = {'replicate_routes': REPLICATE_ROUTES, 'models': {},
           'icc_formula': icc_1_1.__doc__.strip().replace('\n   ', ''),
           'note': 'run1 = first pass (tag without suffix), rep1 = 8-route replicate, run2 = second 44-route pass.'}
    pend_any = []
    for short in ('Golden-6400', 'Flooded-6400-Matched'):
        names = {'run1': f'{short} run1', 'rep1': f'{short} rep1', 'run2': f'{short} run2'}
        done = {run: sum(r in arms[n] for r in REPLICATE_ROUTES) for run, n in names.items()}
        tbl = {r: {run: {**{k: fn(arms[n][r]) for k, fn in RUN_METRICS.items()}, 'status': arms[n][r]['status']}
                   for run, n in names.items() if r in arms[n]} for r in REPLICATE_ROUTES}
        diffs = {}
        for a, b in (('rep1', 'run1'), ('run2', 'run1'), ('run2', 'rep1')):
            routes = [r for r in CANONICAL_44 if r in arms[names[a]] and r in arms[names[b]]]
            e = {'n_routes': len(routes), 'routes': routes,
                 'same_status': int(sum(arms[names[a]][r]['status'] == arms[names[b]][r]['status'] for r in routes)),
                 'metrics': {}}
            for k, fn in RUN_METRICS.items():
                d = vec(arms, names[a], fn, routes) - vec(arms, names[b], fn, routes)
                e['metrics'][k] = {**spread(d), 'per_route': dict(zip(routes, d.tolist()))}
            diffs[f'{a} - {b}'] = e
        three = [r for r in CANONICAL_44 if all(r in arms[n] for n in names.values())]
        sd3 = {}
        for k, fn in RUN_METRICS.items():
            per = {r: float(np.std([fn(arms[n][r]) for n in names.values()], ddof=1)) for r in three}
            sd3[k] = {'per_route_sd': per, 'mean_sd': float(np.mean(list(per.values()))) if per else None}
        p = pending(arms, [(names['run1'], CANONICAL_44), (names['run2'], CANONICAL_44)])
        if p:
            tr = p
            pend_any.append(short)
        else:
            tr = {}
            for k in ('standstill_pct', 'driving_score', 'route_completion'):
                x = vec(arms, names['run2'], RUN_METRICS[k], CANONICAL_44)
                y = vec(arms, names['run1'], RUN_METRICS[k], CANONICAL_44)
                tr[k] = {'run2_minus_run1': paired(x, y), 'sd_of_per_route_difference': float(np.std(x - y, ddof=1)),
                         'icc_1_1': icc_1_1(y, x)}
        res['models'][short] = {
            'replicate_routes_done': {run: f'{n}/{len(REPLICATE_ROUTES)}' for run, n in done.items()},
            'per_route_table_replicate_routes': tbl,
            'run_to_run_differences': diffs,
            'routes_with_three_runs': three, 'three_run_sd': sd3,
            'test_retest_44': tr}
    done_rep = sum(sum(r in arms[f'{s} rep1'] for r in REPLICATE_ROUTES) for s in ('Golden-6400', 'Flooded-6400-Matched'))
    res['status_line'] = ('complete' if not pend_any and done_rep == 16 else
                          f'partial: rep1 routes usable {done_rep}/16; 44-route test-retest pending for {pend_any or "none"}')
    return res


def analysis_O(arms):
    G1, F1, G2, F2 = 'Golden-6400 run1', 'Flooded-6400-Matched run1', 'Golden-6400 run2', 'Flooded-6400-Matched run2'
    comps = {
        '(i) run2 Golden vs run2 Flooded': ((G2,), (F2,)),
        '(ii) mean of run1 and run2, Golden vs Flooded': ((G1, G2), (F1, F2)),
        '(iii-a) run1 Golden vs run2 Flooded': ((G1,), (F2,)),
        '(iii-b) run2 Golden vs run1 Flooded': ((G2,), (F1,)),
    }
    res = {'endpoint': 'standstill_pct (primary); driving_score, route_completion, collision_events secondary',
           'comparisons': {}}
    for cname, (ga, fa) in comps.items():
        out = {}
        for sname, routes in ROUTE_SUBSETS.items():
            p = pending(arms, [(n, routes) for n in ga + fa])
            if p:
                out[sname] = p
                continue
            out[sname] = {k: paired(np.mean([vec(arms, n, RUN_METRICS[k], routes) for n in ga], axis=0),
                                    np.mean([vec(arms, n, RUN_METRICS[k], routes) for n in fa], axis=0))
                          for k in OBR_METRICS}
        if cname.startswith(('(i)', '(ii)')) and 'status' not in out['44 routes']:
            out['replication_readout_decision_case_44'] = {
                'case': decision_case(out['44 routes']['standstill_pct']),
                'label': 'replication readout, not a confirmatory test (rule of the pre-registration, section 3)'}
        res['comparisons'][cname] = out
    res['status_line'] = status_line({f'{c} | {s}': v for c, o in res['comparisons'].items()
                                      for s, v in o.items() if s in ROUTE_SUBSETS})
    return res


def analysis_P(arms):
    names = {'Golden-6400': ('Golden-6400 nogate', 'Golden-6400 run1', 'Golden-6400 run2'),
             'Flooded-6400-Matched': ('Flooded-6400-Matched nogate', 'Flooded-6400-Matched run1', 'Flooded-6400-Matched run2')}
    res = {'metric_definitions': {'ended_by_60s_rule': 'status Failed - TickRuntime with round(duration_game*20) < 4000 (1/0 per route)',
                                  'collision_events': 'actor-id merged, as in F'}}
    # (1) per model, gate-off vs default run1, on the usable routes
    part1 = {}
    for short, (ng, d1, _) in names.items():
        routes = [r for r in CANONICAL_44 if r in arms[ng]]
        e = {'n_routes': len(routes), 'partial': len(routes) < 44,
             'label': ('complete (44 routes)' if len(routes) == 44 else f'PARTIAL: {len(routes)}/44 routes usable'),
             'routes': routes}
        if routes:
            e['metrics'] = {k: paired(vec(arms, ng, fn, routes), vec(arms, d1, fn, routes))
                            for k, fn in P_METRICS.items()}
            e['n_ended_by_60s_rule'] = {'gate_off': int(vec(arms, ng, ended_by_60s_rule, routes).sum()),
                                        'default': int(vec(arms, d1, ended_by_60s_rule, routes).sum())}
        part1[short] = e
    res['(1) gate-off minus default (run1), per model'] = part1
    GN, FN = names['Golden-6400'][0], names['Flooded-6400-Matched'][0]
    G1, F1, G2, F2 = names['Golden-6400'][1], names['Flooded-6400-Matched'][1], names['Golden-6400'][2], names['Flooded-6400-Matched'][2]
    full = lambda *ns: pending(arms, [(n, CANONICAL_44) for n in ns])  # noqa: E731
    v = lambda n, fn: vec(arms, n, fn, CANONICAL_44)  # noqa: E731
    p_ng = full(GN, FN)
    res['(2) Golden minus Flooded, gate-off'] = p_ng or {k: paired(v(GN, fn), v(FN, fn)) for k, fn in P_METRICS.items()}
    inter_keys = [f'standstill_pct_v<{t}' for t in P_THRESHOLDS] + ['mean_speed_mps']
    res['(3) interaction (G_nogate - F_nogate) - (G_default - F_default), default = run1'] = p_ng or {
        k: paired(v(GN, P_METRICS[k]) - v(FN, P_METRICS[k]), v(G1, P_METRICS[k]) - v(F1, P_METRICS[k])) for k in inter_keys}
    p_all = full(GN, FN, G2, F2)
    res['(3) interaction, default = mean of run1 and run2'] = p_all or {
        k: paired(v(GN, P_METRICS[k]) - v(FN, P_METRICS[k]),
                  (v(G1, P_METRICS[k]) + v(G2, P_METRICS[k])) / 2 - (v(F1, P_METRICS[k]) + v(F2, P_METRICS[k])) / 2)
        for k in inter_keys}
    p_r2 = full(G2, F2)
    res['(4) noise reference (G_run2 - F_run2) - (G_run1 - F_run1)'] = p_r2 or {
        k: paired(v(G2, P_METRICS[k]) - v(F2, P_METRICS[k]), v(G1, P_METRICS[k]) - v(F1, P_METRICS[k])) for k in inter_keys}
    if p_ng:
        res['(5) common-window distance (m)'] = p_ng
    else:
        dist = {n: [] for n in (GN, FN, G1, F1)}
        for r in CANONICAL_44:
            n = min(arms[a][r]['n_steps'] for a in dist)
            for a in dist:
                dist[a].append(float(np.sum(arms[a][r]['speed'][:n]) * DT))
        dist = {a: np.array(x) for a, x in dist.items()}
        res['(5) common-window distance (m)'] = {
            'window': 'first n = min over the four arms (both models gate-off and default run1) of logged steps, per route',
            'Golden-6400 gate-off minus default': paired(dist[GN], dist[G1]),
            'Flooded-6400-Matched gate-off minus default': paired(dist[FN], dist[F1]),
            'Golden minus Flooded, gate-off': paired(dist[GN], dist[FN]),
            'Golden minus Flooded, default': paired(dist[G1], dist[F1]),
            'interaction': paired(dist[GN] - dist[FN], dist[G1] - dist[F1])}
    part6 = {}
    for short, (ng, _, _) in names.items():
        routes = [r for r in CANONICAL_44 if r in arms[ng]]
        rds = [arms[ng][r] for r in routes if 'traj_extent' in arms[ng][r]['logged_controller']
               and 'gate_would_fire' in arms[ng][r]['logged_controller']]
        e = {'n_routes': len(rds), 'label': 'complete (44 routes)' if len(rds) == 44 else f'PARTIAL: {len(rds)}/44 routes'}
        if rds:
            gw_all, gw_ss, band_all, band_share, maxdiff, mism = [], [], [], [], 0.0, 0
            for rd in rds:
                lc = rd['logged_controller']
                gw, ext = lc['gate_would_fire'] > 0.5, lc['traj_extent']
                ss = rd['speed'] < SS_V
                gw_all.append(pct(gw))
                if ss.any():
                    gw_ss.append(float(np.mean(gw[ss]) * 100.0))
                b = band_index({'L': ext, 'speed': rd['speed']})
                band_all.append([pct((b == k) & ss) for k in range(4)])
                if ss.any():
                    band_share.append([float(np.mean(b[ss] == k) * 100.0) for k in range(4)])
                maxdiff = max(maxdiff, float(np.max(np.abs(ext - rd['L']))))
                mism += int(np.sum(gw != ((ext < 1.5) | ((rd['speed'] < 0.5) & (ext < 2.0)))))
            e.update({
                'pct_of_all_steps_gate_would_fire': float(np.mean(gw_all)),
                'pct_of_standstill_steps_gate_would_fire': float(np.mean(gw_ss)) if gw_ss else None,
                'band_split_logged_extent': {
                    'pct_of_all_steps_standstill_and_in_band': dict(zip(BANDS, np.mean(band_all, axis=0).tolist())),
                    'share_of_standstill_steps_in_band_pct': dict(zip(BANDS, np.mean(band_share, axis=0).tolist())) if band_share else None},
                'max_abs_diff_logged_extent_vs_waypoint_chord_m': maxdiff,
                'n_steps_gate_would_fire_disagrees_with_rule_on_logged_extent': mism})
        part6[short] = e
    res['(6) gate-off logged fields'] = part6
    res['status_line'] = status_line({k: v for k, v in res.items() if k.startswith(('(2)', '(3)', '(4)', '(5)'))})
    if p_ng:
        res['status_line'] += f"; (1) and (6) partial: Golden {part1['Golden-6400']['n_routes']}/44, Flooded {part1['Flooded-6400-Matched']['n_routes']}/44"
    return res


def analysis_Q(arms, primary_p):
    B2 = 'Base run2'
    res = {}
    routes_u = [r for r in CANONICAL_44 if r in arms[B2]]
    st = Counter(arms[B2][r]['status'] for r in routes_u)
    tick = [r for r in routes_u if arms[B2][r]['status'] == 'Failed - TickRuntime']
    cap = [r for r in tick if round(arms[B2][r]['duration_game'] * 20) >= TICK_CAP]
    res['base_run2_status'] = {'n_routes_usable': len(routes_u), 'status_counts': dict(sorted(st.items())),
                               'tickruntime_60s_rule': [r for r in tick if r not in cap], 'tickruntime_4000_cap': cap,
                               'label': 'complete (44 routes)' if len(routes_u) == 44 else f'PARTIAL: {len(routes_u)}/44 routes'}
    keys = ['driving_score', 'route_completion', 'standstill_pct']
    comps = {}
    for first in ('Golden-1600', 'Flooded-1600'):
        out = {}
        for sname, routes in ROUTE_SUBSETS.items():
            p = pending(arms, [(first, routes), (B2, routes)])
            out[sname] = p or {k: paired(vec(arms, first, RUN_METRICS[k], routes), vec(arms, B2, RUN_METRICS[k], routes))
                               for k in keys}
        comps[f'{first} vs Base run2'] = out
    res['comparisons'] = comps
    h1 = comps['Golden-1600 vs Base run2']['44 routes']
    if 'status' in h1:
        res['holm_H1_base_run2_and_H2'] = h1
        res['base_run2_minus_base_original'] = pending(arms, [(B2, CANONICAL_44)])
    else:
        raw = [h1['driving_score']['wilcoxon']['p'], primary_p]
        res['holm_H1_base_run2_and_H2'] = {'tests': ['H1 Golden-1600 vs Base run2 DS (two-sided Wilcoxon)',
                                                     'H2 Golden-6400 vs Flooded-6400-Matched standstill (primary)'],
                                           'raw_p': raw, 'holm_p': holm_adjust(raw)}
        res['base_run2_minus_base_original'] = {
            'label': 'different termination rule AND a different run: not a pure test-retest',
            **{k: paired(vec(arms, B2, RUN_METRICS[k], CANONICAL_44), vec(arms, 'Base run1', RUN_METRICS[k], CANONICAL_44),
                         routes=CANONICAL_44) for k in keys}}
    res['status_line'] = status_line({f'{c} | {s}': v for c, o in comps.items() for s, v in o.items()})
    return res


def _printed_matches(value, printed):
    """True if value rounds to the printed string at its printed precision (decimals for
    differences and CIs, significant digits for p-values)."""
    return float(printed) == round(value, len(printed.split('.')[1])) if '.' in printed else float(printed) == round(value)


def _p_matches(value, printed):
    sig = len(printed.split('.')[1].lstrip('0'))
    return float(f'{value:.{sig}g}') == float(printed)


def analysis_R(arms, ov):
    key_by_subset = {'44 routes': 'all 44',
                     '37 routes (excl. 7 training-overlap routes)': 'excluding 7 routes with training samples in the Matrix cells',
                     '33 routes (excl. 11 gate-flagged routes)': 'excluding all 11 gate-flagged canonical routes'}
    pat = re.compile(r'N=(\d+) delta=([-\d.]+) CI\[([-\d.]+),([-\d.]+)\] p=([\d.]+)')
    res = {'source_of_expected_values': str(OVERLAP_FILE.relative_to(ROOT)), 'subsets': {}}
    all_ok = True
    for sname, routes in ROUTE_SUBSETS.items():
        h1 = paired(vec(arms, 'Golden-1600', RUN_METRICS['driving_score'], routes),
                    vec(arms, 'Base run1', RUN_METRICS['driving_score'], routes))
        h2 = paired(vec(arms, 'Golden-6400 run1', RUN_METRICS['standstill_pct'], routes),
                    vec(arms, 'Flooded-6400-Matched run1', RUN_METRICS['standstill_pct'], routes))
        e = {'H1 Golden-1600 vs Base (original) DS': h1, 'H2 Golden-6400 vs Flooded-6400-Matched standstill': h2,
             'reproduction': {}}
        exp = ov['sensitivity'][key_by_subset[sname]]
        for lab, p, k in (('H1', h1, 'H1_driving_score'), ('H2', h2, 'H2_standstill_pp')):
            n, d, lo, hi, pv = pat.search(exp[k]).groups()
            ok = {'n': int(n) == p['n'], 'delta': _printed_matches(p['mean_diff'], d),
                  'ci_low': _printed_matches(p['bca95'][0], lo), 'ci_high': _printed_matches(p['bca95'][1], hi),
                  'p': _p_matches(p['wilcoxon']['p'], pv)}
            e['reproduction'][lab] = {'expected_text': exp[k], 'matches': ok, 'all_match': all(ok.values())}
            all_ok &= all(ok.values())
        res['subsets'][sname] = e
    res['all_reproduced'] = bool(all_ok)
    res['status_line'] = 'complete' + ('' if all_ok else ' (NOT all expected values reproduced)')
    return res


def analysis_L_additional(arms):
    rows = {}
    for name in NEW_RUN_TAGS:
        if name.endswith('rep1') or pending(arms, [(name, CANONICAL_44)]):
            continue
        rds = [arms[name][r] for r in CANONICAL_44]
        rows[name] = summary_row(rds, [route_counts(rd) for rd in rds], np.array([exposures(rd) for rd in rds]))
    return rows


def analysis_S(arms):
    """Decoupling arm (ANALYSIS_ADDENDUM.md section 6): Matrix-FloodedGroups-Balanced-6400, one pass,
    against each 6,400-frame model. Comparator = per-route mean of its two default-controller passes;
    each pass separately as a sensitivity row. Exploratory."""
    B = 'Balanced-6400 run1'
    comparators = {'Flooded-6400-Matched': ('Flooded-6400-Matched run1', 'Flooded-6400-Matched run2'),
                   'Golden-6400': ('Golden-6400 run1', 'Golden-6400 run2')}
    res = {'endpoint': 'standstill_pct (v < 0.1 m/s); driving_score, route_completion, collision_events descriptive',
           'label': 'exploratory; one training seed, one evaluation pass of the Balanced model',
           'comparisons': {}}
    for cmp_name, (r1, r2) in comparators.items():
        for row, comp_arms in ((f'Balanced minus {cmp_name} (mean of run1 and run2)', (r1, r2)),
                               (f'Balanced minus {cmp_name} run1', (r1,)),
                               (f'Balanced minus {cmp_name} run2', (r2,))):
            out = {}
            for sname, routes in ROUTE_SUBSETS.items():
                p = pending(arms, [(n, routes) for n in (B,) + comp_arms])
                if p:
                    out[sname] = p
                    continue
                out[sname] = {k: paired(vec(arms, B, RUN_METRICS[k], routes),
                                        np.mean([vec(arms, n, RUN_METRICS[k], routes) for n in comp_arms], axis=0))
                              for k in OBR_METRICS}
            res['comparisons'][row] = out
    # Reading fixed in the addendum, on 44 routes with the two-run-mean comparators.
    vf = res['comparisons']['Balanced minus Flooded-6400-Matched (mean of run1 and run2)']['44 routes']
    vg = res['comparisons']['Balanced minus Golden-6400 (mean of run1 and run2)']['44 routes']
    if is_pending(vf) or is_pending(vg):
        res['prespecified_reading_44'] = {'status': 'pending', 'have': {**vf.get('have', {}), **vg.get('have', {})},
                                          'need': {**vf.get('need', {}), **vg.get('need', {})}}
    else:
        cf, cg = vf['standstill_pct']['bca95'], vg['standstill_pct']['bca95']
        below_f, sep_g_above = cf[1] < 0, cg[0] > 0
        sep_f, sep_g = (cf[1] < 0 or cf[0] > 0), (cg[1] < 0 or cg[0] > 0)
        if below_f and not sep_g:
            reading = 'follows manoeuvre mix and stationary share, not the group mix'
        elif sep_g_above and not sep_f:
            reading = 'follows the group mix'
        else:
            reading = 'inconclusive'
        res['prespecified_reading_44'] = {
            'reading': reading, 'balanced_minus_flooded_bca95': cf, 'balanced_minus_golden_bca95': cg,
            'rule': 'Balanced below Flooded (interval excludes 0) and not separable from Golden -> manoeuvre mix and '
                    'stationary share; Balanced above Golden (interval excludes 0) and not separable from Flooded -> '
                    'group mix; anything else -> inconclusive'}
    res['status_line'] = status_line({f'{c} | {s}': v for c, o in res['comparisons'].items()
                                      for s, v in o.items() if s in ROUTE_SUBSETS})
    return res


EP_MIN, EP_LONG, EP_60S = 20, 200, 1190   # steps at 20 Hz: 1 s, 10 s, 59.5 s (ANALYSIS_ADDENDUM.md section 7b)
EP_CLASSES = ['start', 'resumed_short', 'resumed_long', 'terminal_60s', 'terminal_other', 'brief']
EP_FREEZE, EP_WAIT = ['resumed_long', 'terminal_60s'], ['start', 'resumed_short', 'brief']
PLAN_THRESHOLDS = [1.5, 0.64, 2.0]


def stop_episodes(rd):
    """Maximal runs of consecutive logged steps with speed < 0.1 m/s as (first, end_exclusive, class).
    Runs under 20 steps are 'brief'. A run reaching the last step is terminal even if it begins at step 0."""
    ss = np.asarray(rd['speed']) < SS_V
    n, out, i = len(ss), [], 0
    while i < n:
        if not ss[i]:
            i += 1
            continue
        j = i
        while j < n and ss[j]:
            j += 1
        ln = j - i
        if ln < EP_MIN:
            c = 'brief'
        elif j == n:
            c = 'terminal_60s' if ln >= EP_60S else 'terminal_other'
        elif i == 0:
            c = 'start'
        else:
            c = 'resumed_long' if ln >= EP_LONG else 'resumed_short'
        out.append((i, j, c))
        i = j
    return out


def episode_time_pct(rd, classes):
    return float(sum(j - i for i, j, c in stop_episodes(rd) if c in classes) / rd['n_steps'] * 100.0)


T_METRICS = {
    **{f'plan_rate_L<{t}_pct': (lambda rd, t=t: pct(rd['L'] < t)) for t in PLAN_THRESHOLDS},
    'standstill_pct': RUN_METRICS['standstill_pct'],
    **{f'time_{c}_pct': (lambda rd, c=c: episode_time_pct(rd, [c])) for c in EP_CLASSES},
    'time_freeze_sum_pct': lambda rd: episode_time_pct(rd, EP_FREEZE),
    'time_wait_sum_pct': lambda rd: episode_time_pct(rd, EP_WAIT),
    'episodes_per_route': lambda rd: float(sum(c != 'brief' for _, _, c in stop_episodes(rd))),
}


def episode_descriptives(arm, routes):
    """Pooled over routes: episode counts, median duration (s) and plan state within each class."""
    out = {}
    for c in EP_CLASSES:
        durs, Ls = [], []
        for r in routes:
            rd = arm[r]
            for i, j, cc in stop_episodes(rd):
                if cc == c:
                    durs.append((j - i) / 20.0)
                    Ls.append(np.asarray(rd['L'])[i:j])
        Lc = np.concatenate(Ls) if Ls else np.array([])
        out[c] = {'n_runs': len(durs), 'median_duration_s': float(np.median(durs)) if durs else None,
                  'steps': int(len(Lc)),
                  'plan_L<0.64_pct': pct(Lc < 0.64) if len(Lc) else None,
                  'plan_0.64<=L<2.0_pct': pct((Lc >= 0.64) & (Lc < 2.0)) if len(Lc) else None,
                  'plan_L>=2.0_pct': pct(Lc >= 2.0) if len(Lc) else None}
    return out


def analysis_T(arms):
    """ANALYSIS_ADDENDUM.md section 7: near-stationary plan rate (7a) and stop episodes (7b).
    Post hoc, exploratory, existing step logs only. Golden minus Flooded, paired over the 44 routes."""
    G1, F1, G2, F2 = 'Golden-6400 run1', 'Flooded-6400-Matched run1', 'Golden-6400 run2', 'Flooded-6400-Matched run2'
    GN, FN = 'Golden-6400 nogate', 'Flooded-6400-Matched nogate'
    rows = {'default controller, run1': ((G1,), (F1,)), 'default controller, run2': ((G2,), (F2,)),
            'default controller, mean of run1 and run2': ((G1, G2), (F1, F2)), 'gate-off controller': ((GN,), (FN,))}
    res = {'label': 'post hoc, exploratory; section 7a was first looked at on a partial route set before it was written down',
           'definitions': {'episode': stop_episodes.__doc__.strip().replace('\n   ', ''),
                           'classes': {'start': 'begins at the first logged step', 'resumed_short': 'ends before the last step, < 200 steps',
                                       'resumed_long': 'ends before the last step, >= 200 steps',
                                       'terminal_60s': 'runs to the last step, >= 1190 steps',
                                       'terminal_other': 'runs to the last step, < 1190 steps', 'brief': 'run under 20 steps'},
                           'freeze_sum': EP_FREEZE, 'wait_sum': EP_WAIT,
                           'terminal_60s_note': 'counted from the step log; wider than the status-based ended_by_60s_rule of analysis P, which misses routes whose final status is "Agent got blocked" or "Completed" although the log ends with 1,200 or more standstill steps'},
           'golden_minus_flooded': {}, 'descriptives': {}}
    for row, (ga, fa) in rows.items():
        p = pending(arms, [(n, CANONICAL_44) for n in ga + fa])
        if p:
            res['golden_minus_flooded'][row] = p
            continue
        res['golden_minus_flooded'][row] = {
            k: paired(np.mean([vec(arms, n, fn, CANONICAL_44) for n in ga], axis=0),
                      np.mean([vec(arms, n, fn, CANONICAL_44) for n in fa], axis=0)) for k, fn in T_METRICS.items()}
    for name in (G1, F1, G2, F2, GN, FN):
        p = pending(arms, [(name, CANONICAL_44)])
        res['descriptives'][name] = p if p else episode_descriptives(arms[name], CANONICAL_44)
    r1 = res['golden_minus_flooded']['default controller, run1']
    tot = r1['standstill_pct']['mean_diff']
    parts = sum(r1[f'time_{c}_pct']['mean_diff'] for c in EP_CLASSES)
    assert abs(tot - parts) < 1e-6, 'episode classes do not add up to the standstill difference'
    fz, wt = r1['time_freeze_sum_pct'], r1['time_wait_sum_pct']
    excl = lambda p: isinstance(p.get('bca95'), list) and (p['bca95'][1] < 0 or p['bca95'][0] > 0)
    share_f, share_w = fz['mean_diff'] / tot, wt['mean_diff'] / tot
    reading = ('freeze-type' if share_f >= 2 / 3 and excl(fz) else
               'wait-type' if share_w >= 2 / 3 and excl(wt) else 'mixed')
    res['prespecified_reading_run1'] = {
        'reading': reading, 'standstill_diff_pp': tot,
        'freeze_sum_diff_pp': fz['mean_diff'], 'freeze_sum_bca95': fz.get('bca95'), 'freeze_share_of_diff': share_f,
        'wait_sum_diff_pp': wt['mean_diff'], 'wait_sum_bca95': wt.get('bca95'), 'wait_share_of_diff': share_w,
        'terminal_other_diff_pp': r1['time_terminal_other_pct']['mean_diff'],
        'rule': 'freeze-type: resumed_long + terminal_60s >= 2/3 of the difference and interval excludes 0; '
                'wait-type: start + resumed_short + brief >= 2/3 and interval excludes 0; otherwise mixed',
        'caveat': 'duration and ending are proxies; the logs do not record whether a hazard was ahead'}
    res['status_line'] = status_line(res['golden_minus_flooded'])
    return res


# section 8 of ANALYSIS_ADDENDUM.md: driven standstill ("blocked" time)
U_THR, U_RUN = 0.35, 100
U_CLASSES = ['blocked', 'driven_transient', 'not_driven']
U_SENS = {'run>=40 steps': (0.35, 40), 'run>=200 steps': (0.35, 200), 'throttle>=0.2': (0.2, 100)}


def blocked_masks(rd, thr=U_THR, run=U_RUN):
    """Standstill steps split by the logged final command: (blocked, driven_transient, not_driven) boolean masks.
    driven = speed < 0.1 m/s, throttle >= thr, brake == 0; blocked = driven steps in a run of >= `run` consecutive driven steps."""
    ss = np.asarray(rd['speed']) < SS_V
    drv = ss & (np.asarray(rd['throttle']) >= thr) & (np.asarray(rd['brake']) == 0)
    blk = np.zeros(len(ss), bool)
    i, n = 0, len(ss)
    while i < n:
        if not drv[i]:
            i += 1
            continue
        j = i
        while j < n and drv[j]:
            j += 1
        if j - i >= run:
            blk[i:j] = True
        i = j
    return blk, drv & ~blk, ss & ~drv


def u_metrics(thr=U_THR, run=U_RUN):
    return {'standstill_pct': RUN_METRICS['standstill_pct'],
            **{f'time_{c}_pct': (lambda rd, k=k: pct(blocked_masks(rd, thr, run)[k])) for k, c in enumerate(U_CLASSES)},
            'standstill_without_blocked_pct': lambda rd: pct((np.asarray(rd['speed']) < SS_V) & ~blocked_masks(rd, thr, run)[0])}


def analysis_U(arms, scen=None, data=None):
    """ANALYSIS_ADDENDUM.md section 8. Post hoc, exploratory, existing step logs only."""
    G1, F1, G2, F2 = 'Golden-6400 run1', 'Flooded-6400-Matched run1', 'Golden-6400 run2', 'Flooded-6400-Matched run2'
    GN, FN = 'Golden-6400 nogate', 'Flooded-6400-Matched nogate'
    rows = {'default controller, run1': ((G1,), (F1,)), 'default controller, run2': ((G2,), (F2,)),
            'default controller, mean of run1 and run2': ((G1, G2), (F1, F2)), 'gate-off controller': ((GN,), (FN,))}
    M = u_metrics()
    mean_vec = lambda names, fn: np.mean([vec(arms, n, fn, CANONICAL_44) for n in names], axis=0)
    res = {'label': 'post hoc, exploratory; written down (section 8) after a per-episode listing of long stops had been seen',
           'definitions': {'driven': f'speed < {SS_V} m/s, throttle >= {U_THR}, brake == 0 (logged final command)',
                           'blocked': f'driven steps in a run of >= {U_RUN} consecutive driven steps',
                           'driven_transient': 'driven steps not in such a run',
                           'not_driven': 'all other standstill steps',
                           'caveat': 'inferred from the command log, not from a contact sensor'},
           'golden_minus_flooded': {}, 'gate_off_minus_default_run1': {}, 'interaction_run1': {}, 'sensitivity_golden_minus_flooded': {},
           'routes_with_blocked_time': {}}
    for row, (ga, fa) in rows.items():
        p = pending(arms, [(n, CANONICAL_44) for n in ga + fa])
        if p:
            res['golden_minus_flooded'][row] = p
            continue
        res['golden_minus_flooded'][row] = {k: paired(mean_vec(ga, fn), mean_vec(fa, fn)) for k, fn in M.items()}
        r = res['golden_minus_flooded'][row]
        assert abs(r['standstill_pct']['mean_diff'] - sum(r[f'time_{c}_pct']['mean_diff'] for c in U_CLASSES)) < 1e-6
        res['sensitivity_golden_minus_flooded'][row] = {
            lab: {k: paired(mean_vec(ga, fn), mean_vec(fa, fn)) for k, fn in u_metrics(t, n).items()
                  if k in ('time_blocked_pct', 'standstill_without_blocked_pct')} for lab, (t, n) in U_SENS.items()}
    p = pending(arms, [(n, CANONICAL_44) for n in (G1, F1, GN, FN)])
    if p:
        res['gate_off_minus_default_run1'] = res['interaction_run1'] = p
    else:
        for lab, (a, b) in {'Golden-6400': (GN, G1), 'Flooded-6400-Matched': (FN, F1)}.items():
            res['gate_off_minus_default_run1'][lab] = {k: paired(vec(arms, a, fn, CANONICAL_44), vec(arms, b, fn, CANONICAL_44))
                                                       for k, fn in M.items()}
        res['interaction_run1'] = {k: paired(vec(arms, GN, fn, CANONICAL_44) - vec(arms, FN, fn, CANONICAL_44),
                                             vec(arms, G1, fn, CANONICAL_44) - vec(arms, F1, fn, CANONICAL_44)) for k, fn in M.items()}
    for name in (G1, F1, G2, F2, GN, FN):
        p = pending(arms, [(name, CANONICAL_44)])
        if p:
            res['routes_with_blocked_time'][name] = p
            continue
        blk = vec(arms, name, M['time_blocked_pct'], CANONICAL_44) > 0
        col = vec(arms, name, RUN_METRICS['collision_events'], CANONICAL_44) > 0
        runs = [int(np.sum(np.diff(np.concatenate([[0], blocked_masks(arms[name][r])[0].astype(int)])) == 1)) for r in CANONICAL_44]
        res['routes_with_blocked_time'][name] = {
            'n_routes_with_blocked_time': int(blk.sum()), 'blocked_routes_with_collision_event': int((blk & col).sum()),
            'n_routes_without_blocked_time': int((~blk).sum()), 'other_routes_with_collision_event': int((~blk & col).sum()),
            'routes': [r for r, b in zip(CANONICAL_44, blk) if b], 'n_blocked_runs': int(sum(runs)),
            'mean_blocked_pct': float(np.mean(vec(arms, name, M['time_blocked_pct'], CANONICAL_44))),
            'mean_standstill_pct': float(np.mean(vec(arms, name, M['standstill_pct'], CANONICAL_44)))}
    # descriptive: on the routes where Golden has blocked time, what the other model's standstill consists of
    res['same_route_detail'] = {}
    for lab, (ga, fa) in {'default controller, run1': (G1, F1), 'gate-off controller': (GN, FN)}.items():
        if pending(arms, [(ga, CANONICAL_44), (fa, CANONICAL_44)]):
            continue
        rows_d = {}
        for r in CANONICAL_44:
            g, fl = arms[ga][r], arms[fa][r]
            gb = pct(blocked_masks(g)[0])
            if gb <= 0:
                continue
            rows_d[r] = {'scenario': scen[r] if scen else None,
                         'golden': {'blocked_pct': gb, 'not_driven_pct': pct(blocked_masks(g)[2]), 'status': g['status'],
                                    'route_completion': g['rc'], 'collision_events': RUN_METRICS['collision_events'](g)},
                         'flooded': {'blocked_pct': pct(blocked_masks(fl)[0]), 'not_driven_pct': pct(blocked_masks(fl)[2]),
                                     'status': fl['status'], 'route_completion': fl['rc'],
                                     'collision_events': RUN_METRICS['collision_events'](fl)}}
        sel = list(rows_d)
        rest = [r for r in CANONICAL_44 if r not in rows_d]
        m = lambda arm, rs, fn: float(np.mean([fn(arms[arm][r]) for r in rs])) if rs else None
        nd = lambda rd: pct(blocked_masks(rd)[2])
        res['same_route_detail'][lab] = {
            'routes_where_golden_has_blocked_time': rows_d,
            'flooded_not_driven_pct_on_these_routes': m(fa, sel, nd), 'flooded_not_driven_pct_on_other_routes': m(fa, rest, nd),
            'golden_not_driven_pct_on_these_routes': m(ga, sel, nd), 'golden_not_driven_pct_on_other_routes': m(ga, rest, nd),
            'route_completion_on_these_routes': {'golden': m(ga, sel, lambda rd: rd['rc']), 'flooded': m(fa, sel, lambda rd: rd['rc'])},
            'route_completion_on_other_routes': {'golden': m(ga, rest, lambda rd: rd['rc']), 'flooded': m(fa, rest, lambda rd: rd['rc'])},
            'collision_events_on_these_routes': {'golden': m(ga, sel, RUN_METRICS['collision_events']),
                                                 'flooded': m(fa, sel, RUN_METRICS['collision_events'])},
            'collision_events_on_other_routes': {'golden': m(ga, rest, RUN_METRICS['collision_events']),
                                                 'flooded': m(fa, rest, RUN_METRICS['collision_events'])}}
    # section 8a: the other models, default controller, run-1 logs
    if data is not None:
        dv = lambda mname, fn: np.array([fn(data[mname][r]) for r in CANONICAL_44])
        res['all_models_default_run1'] = {}
        for mname in MODELS:
            blk = dv(mname, M['time_blocked_pct'])
            col = dv(mname, RUN_METRICS['collision_events']) > 0
            res['all_models_default_run1'][mname] = {
                'mean_standstill_pct': float(dv(mname, M['standstill_pct']).mean()),
                **{f'mean_{c}_pct': float(dv(mname, M[f'time_{c}_pct']).mean()) for c in U_CLASSES},
                'mean_standstill_without_blocked_pct': float(dv(mname, M['standstill_without_blocked_pct']).mean()),
                'n_routes_with_blocked_time': int((blk > 0).sum()),
                'blocked_routes_with_collision_event': int(((blk > 0) & col).sum()),
                'routes': [r for r, b in zip(CANONICAL_44, blk) if b > 0]}
        res['other_contrasts_default_run1'] = {
            f'{a} minus {b}': {k: paired(dv(a, M[k]), dv(b, M[k])) for k in ('time_blocked_pct', 'standstill_without_blocked_pct', 'standstill_pct')}
            for a, b in ((G16, F16), (G64, FH), (G64, G16), (FM, F16), (G16, BASE), (F16, BASE))}
    res['status_line'] = status_line(res['golden_minus_flooded'])
    return res


# section 10 of ANALYSIS_ADDENDUM.md: plans by speed, by stated reason, and lateral plans
V_MIN, V_LAT, V_LAT_SENS = 20, 1.0, [0.5, 2.0]
BYPASS_9 = BYPASS_SINGLE + BYPASS_TWOWAY


def v_masks(rd, cache):
    """name -> (numerator mask, conditioning mask), per logged step."""
    v, L, y = np.asarray(rd['speed']), np.asarray(rd['L']), np.asarray(rd['y_end'])
    cls = np.array([coc_class(t, cache) for t in rd['coc']])
    low, mov, far = v <= 0.5, v > 0.5, L >= 2.0
    out = {'low_speed_stays_put': (L < 0.64, low), 'low_speed_starts_moving': (L >= 2.0, low),
           'low_speed_in_between': ((L >= 0.64) & (L < 2.0), low),
           'moving_plans_stop': (L < 1.5, mov),
           'proceed_text_plan_below_1.5m': (L < 1.5, cls == 0), 'caution_text_plan_below_1.5m': (L < 1.5, cls == 1),
           'left_plan': (y >= V_LAT, far), 'right_plan': (y <= -V_LAT, far)}
    for t in V_LAT_SENS:
        out[f'left_plan_{t}m'] = (y >= t, far)
        out[f'right_plan_{t}m'] = (y <= -t, far)
    return out


def v_route_table(arm, routes, cache):
    """metric -> route -> (numerator steps, conditioning steps)."""
    tab = {}
    for r in routes:
        for k, (num, cond) in v_masks(arm[r], cache).items():
            tab.setdefault(k, {})[r] = (int(np.sum(num & cond)), int(np.sum(cond)))
    return tab


def v_paired(tg, tf, routes):
    out = {}
    for k in tg:
        use = [r for r in routes if tg[k][r][1] >= V_MIN and tf[k][r][1] >= V_MIN]
        if len(use) < 5:
            out[k] = {'n': len(use), 'note': 'fewer than 5 routes with 20 conditioning steps in both arms'}
            continue
        x = [100.0 * tg[k][r][0] / tg[k][r][1] for r in use]
        y = [100.0 * tf[k][r][0] / tf[k][r][1] for r in use]
        out[k] = paired(x, y)
    return out


def v_pooled(tab, routes):
    return {k: {'pct': 100.0 * sum(v[r][0] for r in routes) / max(1, sum(v[r][1] for r in routes)),
                'conditioning_steps': int(sum(v[r][1] for r in routes))} for k, v in tab.items()}


def analysis_V(arms, data):
    """ANALYSIS_ADDENDUM.md section 10. Post hoc, exploratory, existing step logs only."""
    cache = {}
    G1, F1, G2, F2 = 'Golden-6400 run1', 'Flooded-6400-Matched run1', 'Golden-6400 run2', 'Flooded-6400-Matched run2'
    GN, FN = 'Golden-6400 nogate', 'Flooded-6400-Matched nogate'
    rows = {'default controller, run1': (G1, F1), 'default controller, run2': (G2, F2), 'gate-off controller': (GN, FN)}
    res = {'label': 'post hoc, exploratory; defined in addendum section 10 before computing',
           'definitions': {'conditioning': 'low speed: speed <= 0.5 m/s; moving: speed > 0.5 m/s; text classes as in analysis J; '
                                           'lateral: steps with L >= 2.0 m, y_end = lateral coordinate of the last waypoint, positive left',
                           'per_route_rule': f'a route is used only if both arms have at least {V_MIN} conditioning steps',
                           'lateral_threshold_m': V_LAT, 'lateral_sensitivity_m': V_LAT_SENS, 'bypass_routes': BYPASS_9},
           'golden_minus_flooded': {}, 'golden_minus_flooded_bypass_routes': {}, 'pooled_all_models_default_run1': {},
           'pooled_bypass_routes_default_run1': {}, 'pooled_new_arms': {}}
    for row, (ga, fa) in rows.items():
        p = pending(arms, [(ga, CANONICAL_44), (fa, CANONICAL_44)])
        if p:
            res['golden_minus_flooded'][row] = p
            res['golden_minus_flooded_bypass_routes'][row] = p
            continue
        tg, tf = v_route_table(arms[ga], CANONICAL_44, cache), v_route_table(arms[fa], CANONICAL_44, cache)
        res['golden_minus_flooded'][row] = v_paired(tg, tf, CANONICAL_44)
        res['golden_minus_flooded_bypass_routes'][row] = v_paired(tg, tf, BYPASS_9)
        if row != 'default controller, run1':
            res['pooled_new_arms'][ga] = v_pooled(tg, CANONICAL_44)
            res['pooled_new_arms'][fa] = v_pooled(tf, CANONICAL_44)
    for m in MODELS:
        tab = v_route_table(data[m], CANONICAL_44, cache)
        res['pooled_all_models_default_run1'][m] = v_pooled(tab, CANONICAL_44)
        res['pooled_bypass_routes_default_run1'][m] = v_pooled(tab, BYPASS_9)
    res['training_set_reference'] = {
        'low_speed_stays_put_pct': {'golden_1600': 11.4, 'flooded_1600': 30.6, 'golden_6400': 10.9, 'flooded_6400': 31.0},
        'manoeuvre_targets_pct': {'golden': {'straight': 50, 'swerve_left': 13, 'swerve_right': 13, 'turn_left': 12, 'turn_right': 12},
                                  'flooded': {'straight': 22, 'swerve_left': 37, 'swerve_right': 12, 'turn_left': 14.5, 'turn_right': 14.5}},
        'source': 'docs/provenance/A100_TRAINING_PROVENANCE.md (copied, not recomputed here)'}
    res['status_line'] = status_line(res['golden_minus_flooded'])
    return res


# --------------------------------------------------------------------------- report N-S

def is_pending(v):
    return isinstance(v, dict) and v.get('status') == 'pending'


def pending_str(v):
    return f"pending: have {v['have']}, need {v['need']}"


def paired_block(title, obj, nd=3):
    """Markdown for a dict {label: paired()} or a pending marker."""
    if is_pending(obj):
        return [f'**{title}**: {pending_str(obj)}', '']
    rows = [pair_row(k, v, nd) for k, v in obj.items() if isinstance(v, dict) and 'wilcoxon' in v]
    return [f'**{title}**', '', table(PAIR_HDR, rows), '']


def render_new(man):
    L = []
    N = man['N']
    L += ['## N. Replicates and test–retest', '', f"Status: {N['status_line']}", '', N['note'], '']
    for short, v in N['models'].items():
        L += [f"### {short}", '', f"Replicate routes done: {v['replicate_routes_done']}", '']
        rows = [[r, run, f(x['standstill_pct'], 2), f(x['driving_score'], 2), f(x['route_completion'], 1),
                 f(x['mean_speed_mps'], 3), int(x['collision_events']), int(x['n_steps']), x['status']]
                for r, runs in v['per_route_table_replicate_routes'].items() for run, x in runs.items()]
        L += [table(['route', 'run', 'standstill %', 'DS', 'RC %', 'mean speed', 'coll. events', 'steps', 'status'], rows), '']
        rows = []
        for pair, e in v['run_to_run_differences'].items():
            if not e['n_routes']:
                rows.append([pair, 0, '-', 'no routes with both runs yet', '', '', ''])
                continue
            for k, s in e['metrics'].items():
                rows.append([pair, e['n_routes'], f"{e['same_status']}/{e['n_routes']}", k, f(s['mean']), f(s['sd']), f(s['mean_abs'])])
        L += ['Run-to-run differences (all routes with both runs):', '',
              table(['pair', 'N', 'same status', 'metric', 'mean', 'SD', 'mean |d|'], rows), '']
        if v['routes_with_three_runs']:
            L += [f"Three-run per-route SD (routes {v['routes_with_three_runs']}): " +
                  '; '.join(f"{k}: {f(s['mean_sd'])}" for k, s in v['three_run_sd'].items()), '']
        tr = v['test_retest_44']
        if is_pending(tr):
            L += [f'44-route test–retest: {pending_str(tr)}', '']
        else:
            L += table(PAIR_HDR + ['SD of d', 'ICC(1,1)'],
                       [pair_row(f'{k} run2 - run1', e['run2_minus_run1']) + [f(e['sd_of_per_route_difference']), f(e['icc_1_1'])]
                        for k, e in tr.items()]).split('\n') + ['']
    L += [f"ICC formula: {N['icc_formula']}", '']

    O = man['O']
    L += ['## O. H2 replication', '', f"Status: {O['status_line']}", '', O['endpoint'], '']
    for c, o in O['comparisons'].items():
        for s in ROUTE_SUBSETS:
            L += paired_block(f'{c}, {s}', o[s])
        if 'replication_readout_decision_case_44' in o:
            d = o['replication_readout_decision_case_44']
            L += [f"Decision case (44 routes): **{d['case']}** — {d['label']}", '']

    P = man['P']
    L += ['## P. Gate-off controller', '', f"Status: {P['status_line']}", '']
    for short, e in P['(1) gate-off minus default (run1), per model'].items():
        if e['n_routes']:
            L += paired_block(f"(1) {short} gate-off minus default — {e['label']}", e['metrics'])
            L += [f"Routes ended by the 60 s rule: {e['n_ended_by_60s_rule']}", '']
        else:
            L += [f"**(1) {short}**: no usable gate-off routes yet", '']
    for k in [k for k in P if k.startswith(('(2)', '(3)', '(4)'))]:
        L += paired_block(k, P[k])
    d5 = P['(5) common-window distance (m)']
    L += paired_block('(5) common-window distance (m)', d5 if is_pending(d5) else {k: v for k, v in d5.items() if k != 'window'}, 2)
    for short, e in P['(6) gate-off logged fields'].items():
        if e['n_routes']:
            b = e['band_split_logged_extent']
            L += [f"**(6) {short}** ({e['label']}): gate_would_fire {f(e['pct_of_all_steps_gate_would_fire'], 2)} % of all steps, "
                  f"{f(e['pct_of_standstill_steps_gate_would_fire'], 2)} % of standstill steps; max |logged traj_extent − waypoint chord| = "
                  f"{f(e['max_abs_diff_logged_extent_vs_waypoint_chord_m'], 4)} m; steps where gate_would_fire disagrees with the rule: "
                  f"{e['n_steps_gate_would_fire_disagrees_with_rule_on_logged_extent']}", '',
                  table(['band', '% all steps standstill ∧ band', 'share of standstill steps %'],
                        [[bn, f(b['pct_of_all_steps_standstill_and_in_band'][bn], 2),
                          f(b['share_of_standstill_steps_in_band_pct'][bn], 1) if b['share_of_standstill_steps_in_band_pct'] else 'n/a']
                         for bn in BANDS]), '']
        else:
            L += [f"**(6) {short}**: no usable gate-off routes yet", '']

    Q = man['Q']
    s = Q['base_run2_status']
    L += ['## Q. H1 with the re-run Base', '', f"Status: {Q['status_line']}", '',
          f"base_run2 status ({s['label']}): {s['status_counts']}; TickRuntime by 60 s rule {s['tickruntime_60s_rule']}, by 4000 cap {s['tickruntime_4000_cap']}", '']
    for c, o in Q['comparisons'].items():
        for sn in ROUTE_SUBSETS:
            L += paired_block(f'{c}, {sn}', o[sn])
    h = Q['holm_H1_base_run2_and_H2']
    if is_pending(h):
        L += [f'Holm {{H1 base_run2, H2}}: {pending_str(h)}', '']
    else:
        L += [table(['test', 'raw p', 'Holm p'], [[t, fp(a), fp(b)] for t, a, b in zip(h['tests'], h['raw_p'], h['holm_p'])]), '']
    b = Q['base_run2_minus_base_original']
    L += paired_block('base_run2 minus original Base' + ('' if is_pending(b) else f" ({b['label']})"), b)

    R = man['R']
    L += ['## R. Overlap sensitivity (H1, H2 on 44 / 37 / 33 routes)', '', f"Status: {R['status_line']}", '',
          f"Expected values from `{R['source_of_expected_values']}`; all reproduced at printed precision: {R['all_reproduced']}", '']
    for sn, e in R['subsets'].items():
        L += paired_block(sn, {k: v for k, v in e.items() if k != 'reproduction'})
        L += [f"- {lab}: expected `{x['expected_text']}` → {'reproduced' if x['all_match'] else 'NOT reproduced ' + str(x['matches'])}"
              for lab, x in e['reproduction'].items()] + ['']
    S = man['S']
    L += ['## S. Decoupling arm (FloodedGroups-Balanced-6400)', '', f"Status: {S['status_line']}", '', S['label'], '']
    for c, o in S['comparisons'].items():
        for sn in ROUTE_SUBSETS:
            L += paired_block(f'{c}, {sn}', o[sn])
    r = S['prespecified_reading_44']
    L += [f"Pre-specified reading (44 routes): {pending_str(r) if is_pending(r) else r['reading']}", '']
    T = man['T']
    L += ['## T. Near-stationary plans and stop episodes (Golden minus Flooded)', '', f"Status: {T['status_line']}", '', T['label'], '']
    for row, o in T['golden_minus_flooded'].items():
        L += paired_block(row, o, 2)
    for name, d in T['descriptives'].items():
        if is_pending(d):
            L += [f'**{name}**: {pending_str(d)}', '']
            continue
        L += [f'**{name}** (pooled over 44 routes)', '',
              table(['class', 'runs', 'median s', 'steps', 'L<0.64 %', '0.64<=L<2.0 %', 'L>=2.0 %'],
                    [[c, x['n_runs'], f(x['median_duration_s'], 1), x['steps'], f(x['plan_L<0.64_pct'], 1),
                      f(x['plan_0.64<=L<2.0_pct'], 1), f(x['plan_L>=2.0_pct'], 1)] for c, x in d.items()]), '']
    r = T['prespecified_reading_run1']
    L += [f"Pre-specified reading (default controller, run 1): **{r['reading']}** — freeze share {f(r['freeze_share_of_diff'], 2)}, "
          f"wait share {f(r['wait_share_of_diff'], 2)} of {f(r['standstill_diff_pp'], 2)} pp. {r['caveat']}.", '']
    U = man['U']
    L += ['## U. Driven standstill ("blocked" time), addendum section 8', '', f"Status: {U['status_line']}", '', U['label'], '',
          '; '.join(f'{k}: {v}' for k, v in U['definitions'].items()), '']
    for row, o in U['golden_minus_flooded'].items():
        L += paired_block('Golden minus Flooded, ' + row, o, 2)
    if is_pending(U['interaction_run1']):
        L += [f"Gate-off minus default: {pending_str(U['interaction_run1'])}", '']
    else:
        for lab, o in U['gate_off_minus_default_run1'].items():
            L += paired_block(f'{lab}: gate-off minus default (run 1)', o, 2)
        L += paired_block('Interaction (G_nogate - F_nogate) - (G_default - F_default), run 1', U['interaction_run1'], 2)
    for row, o in U['sensitivity_golden_minus_flooded'].items():
        for lab, oo in o.items():
            L += paired_block(f'Sensitivity ({lab}), Golden minus Flooded, {row}', oo, 2)
    rows_u = [[n, d['n_routes_with_blocked_time'], d['blocked_routes_with_collision_event'],
               f"{d['other_routes_with_collision_event']} of {d['n_routes_without_blocked_time']}", d['n_blocked_runs'],
               f(d['mean_blocked_pct'], 2), f(d['mean_standstill_pct'], 2)]
              for n, d in U['routes_with_blocked_time'].items() if not is_pending(d)]
    L += [table(['arm', 'routes with blocked time', 'of these with a collision event', 'other routes with a collision event',
                'blocked runs', 'mean blocked %', 'mean standstill %'], rows_u), '']
    if 'all_models_default_run1' in U:
        L += ['**All six models, default controller, run 1** (addendum section 8a, descriptive)', '',
              table(['model', 'standstill %', 'blocked %', 'driven transient %', 'not driven %', 'standstill w/o blocked %',
                     'routes with blocked time', 'of these with a collision event'],
                    [[mn, f(x['mean_standstill_pct'], 2), f(x['mean_blocked_pct'], 2), f(x['mean_driven_transient_pct'], 2),
                      f(x['mean_not_driven_pct'], 2), f(x['mean_standstill_without_blocked_pct'], 2),
                      x['n_routes_with_blocked_time'], x['blocked_routes_with_collision_event']]
                     for mn, x in U['all_models_default_run1'].items()]), '']
        for lab, o in U['other_contrasts_default_run1'].items():
            L += paired_block(lab + ' (default controller, run 1)', o, 2)
    for lab, d in U.get('same_route_detail', {}).items():
        L += [f'**Routes where Golden-6400 has blocked time, {lab}** (descriptive)', '',
              table(['route', 'scenario', 'G blocked %', 'G not driven %', 'G RC', 'G coll', 'G status',
                     'F blocked %', 'F not driven %', 'F RC', 'F coll', 'F status'],
                    [[r, x['scenario'], f(x['golden']['blocked_pct'], 1), f(x['golden']['not_driven_pct'], 1), f(x['golden']['route_completion'], 1),
                      int(x['golden']['collision_events']), x['golden']['status'],
                      f(x['flooded']['blocked_pct'], 1), f(x['flooded']['not_driven_pct'], 1), f(x['flooded']['route_completion'], 1),
                      int(x['flooded']['collision_events']), x['flooded']['status']]
                     for r, x in d['routes_where_golden_has_blocked_time'].items()]), '',
              f"Flooded not-driven standstill: {f(d['flooded_not_driven_pct_on_these_routes'], 2)} % on these routes, "
              f"{f(d['flooded_not_driven_pct_on_other_routes'], 2)} % on the others. Route completion on these routes: Golden "
              f"{f(d['route_completion_on_these_routes']['golden'], 1)}, Flooded {f(d['route_completion_on_these_routes']['flooded'], 1)}; "
              f"on the others: Golden {f(d['route_completion_on_other_routes']['golden'], 1)}, Flooded {f(d['route_completion_on_other_routes']['flooded'], 1)}.", '']
    V = man['V']
    L += ['## V. Plans by speed, by stated reason, and lateral plans (addendum section 10)', '', f"Status: {V['status_line']}", '',
          V['label'], '', '; '.join(f'{k}: {v}' for k, v in V['definitions'].items()), '']
    for row, o in V['golden_minus_flooded'].items():
        L += paired_block('Golden minus Flooded, per-route shares (%), ' + row, o, 2)
    for row, o in V['golden_minus_flooded_bypass_routes'].items():
        L += paired_block('Golden minus Flooded, nine bypass routes, ' + row, o, 2)
    for title, key in (('Pooled shares (%), all 44 routes, default controller, run 1', 'pooled_all_models_default_run1'),
                       ('Pooled shares (%), nine bypass routes, default controller, run 1', 'pooled_bypass_routes_default_run1'),
                       ('Pooled shares (%), all 44 routes, other arms', 'pooled_new_arms')):
        d = V[key]
        if d:
            ks = list(next(iter(d.values())).keys())
            L += [f'**{title}**', '', table(['arm'] + ks, [[mn] + [f(x[k]['pct'], 2) for k in ks] for mn, x in d.items()]), '']
    L += [f"Training-set reference: {json.dumps(V['training_set_reference'])}", '']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------- W. motion-history swap

# ANALYSIS_ADDENDUM.md section 11. These runs use alpamayo_bridge_agent_histswap.py and enter no other analysis.
W_TAGS = {G64: 'model_matrix_golden_6400_histswap', FM: 'model_matrix_flooded_6400_histswap'}
W_MIN = 20


def w_load(tag, route):
    d = ROOT / f'outputs/local_evaluation/{tag}_{route}'
    ep, lg = d / 'checkpoint_endpoint.json', d / 'predicted_trajectories.jsonl'
    if not ep.exists() or not lg.exists() or not json.load(open(ep)).get('_checkpoint', {}).get('records'):
        return None
    rows = [json.loads(ln) for ln in open(lg) if ln.strip()]
    if any(r.get('controller_variant') != 'histswap' or r.get('hist_kind') not in ('true', 'moving', 'stationary')
           for r in rows):
        raise RuntimeError(f'{d.name}: step log is not from the history-swap agent')
    wp = np.asarray([r['pred_waypoints'] for r in rows], dtype=np.float64)
    _, cum = chord_profile(wp)
    kind = np.asarray([r['hist_kind'] for r in rows])
    v_end = cum[:, -1] - cum[:, -11]                       # m/s over the last 1.0 s of the plan
    v_start = np.hypot(wp[:, 0, 0], wp[:, 0, 1]) / 0.1     # m/s over the first 0.1 s
    after_swap = np.concatenate([[False], kind[:-1] != 'true'])   # the previous logged step was a swap step
    return {'speed': np.asarray([float(r['speed']) for r in rows]), 'L': cum[:, -1].copy(), 'v_end': v_end,
            'dv': v_end - v_start, 'wp1': v_start * 0.1, 'kind': kind, 'after_swap': after_swap}


def w_reading(p, rule):
    ci = p.get('bca95')
    if not (isinstance(ci, (list, tuple)) and len(ci) == 2 and all(isinstance(x, (int, float)) and x == x for x in ci)):
        return 'no reading'
    lo, hi = ci
    if rule == 'two-sided':
        return 'the learned controls depend on the ego history' if (lo > 0 or hi < 0) else 'no detectable dependence of the controls on the ego history'
    return 'stay-put plans are not matched by braking plans' if (p['mean_diff'] < 0 and hi < 0) else 'no detectable difference'


# addendum 11-B: outcome -> (plan test, low-speed stratum?, swapped kind, reading rule or None)
W_OUTCOMES = {
    'W-a low speed, plan holds speed (|dv| < 0.5 m/s): moving history minus true history': (lambda v: np.abs(v['dv']) < 0.5, True, 'moving', 'two-sided'),
    'W-b low speed, plan ends at rest (v_end < 0.5 m/s): moving history minus true history': (lambda v: v['v_end'] < 0.5, True, 'moving', 'negative'),
    'description: low speed, plan accelerates (dv >= 0.5 m/s)': (lambda v: v['dv'] >= 0.5, True, 'moving', None),
    'description: low speed, plan decelerates (dv <= -0.5 m/s)': (lambda v: v['dv'] <= -0.5, True, 'moving', None),
    'description: low speed, stays put (L < 0.64 m)': (lambda v: v['L'] < 0.64, True, 'moving', None),
    'description: moving, plan holds speed (|dv| < 0.5 m/s): stationary history minus true history': (lambda v: np.abs(v['dv']) < 0.5, False, 'stationary', None),
    'description: moving, plan ends at rest (v_end < 0.5 m/s): stationary history minus true history': (lambda v: v['v_end'] < 0.5, False, 'stationary', None),
}


def w_outcomes(runs, drop_after_swap):
    out = {}
    for name, (plan, low, kind, rule) in W_OUTCOMES.items():
        cnt = {}
        for r, v in runs.items():
            cond = (v['speed'] <= 0.5) if low else (v['speed'] > 0.5)
            hit = plan(v)
            sw, tr = cond & (v['kind'] == kind), cond & (v['kind'] == 'true')
            if drop_after_swap:
                tr = tr & ~v['after_swap']
            cnt[r] = (int(np.sum(hit & sw)), int(np.sum(sw)), int(np.sum(hit & tr)), int(np.sum(tr)))
        use = [r for r in runs if cnt[r][1] >= W_MIN and cnt[r][3] >= W_MIN]
        o = {'pooled_swapped_pct': 100.0 * sum(c[0] for c in cnt.values()) / max(1, sum(c[1] for c in cnt.values())),
             'pooled_true_pct': 100.0 * sum(c[2] for c in cnt.values()) / max(1, sum(c[3] for c in cnt.values())),
             'steps_swapped': sum(c[1] for c in cnt.values()), 'steps_true': sum(c[3] for c in cnt.values()),
             'routes_used': use}
        if len(use) >= 5:
            o['paired'] = paired([100.0 * cnt[r][0] / cnt[r][1] for r in use], [100.0 * cnt[r][2] / cnt[r][3] for r in use])
            if rule:
                o['reading'] = w_reading(o['paired'], rule)
        else:
            o['paired'] = {'n': len(use), 'note': f'fewer than 5 routes with {W_MIN} steps in both conditions'}
            if rule:
                o['reading'] = 'no reading'
        out[name] = o
    return out


def analysis_W():
    """ANALYSIS_ADDENDUM.md sections 11 and 11-B (11-B replaces the outcomes and reading rule of 11 and 11-A)."""
    res = {'label': 'new runs, exploratory; outcomes and reading rule fixed in addendum section 11-B before any swap run existed',
           'definitions': {'swap steps': 'about one step in five from step 60; plan logged, not acted on',
                           'low speed': 'speed <= 0.5 m/s, swap = moving history (4.0 m/s straight)',
                           'moving': 'speed > 0.5 m/s, swap = stationary history',
                           'v_start': '|first waypoint| / 0.1 s', 'v_end': 'path length between waypoints 54 and 64 / 1.0 s',
                           'dv': 'v_end - v_start (planned speed change; set by the learned controls, not by the initial speed)',
                           'per_route_rule': f'a route is used only if it has at least {W_MIN} steps in both conditions'},
           'models': {}}
    audit = ROOT / 'outputs/revision_suite4_audit.log'
    queue_ended = audit.exists() and 'suite4 end' in audit.read_text()
    for model, tag in W_TAGS.items():
        runs = {r: w_load(tag, r) for r in REPLICATE_ROUTES}
        runs = {r: v for r, v in runs.items() if v is not None}
        if len(runs) < len(REPLICATE_ROUTES) and not (queue_ended and len(runs) >= 1):
            res['models'][model] = {'status': 'pending', 'have': {tag: len(runs)}, 'need': {tag: len(REPLICATE_ROUTES)}}
            continue
        chk = {k: float(np.median(np.concatenate([v['wp1'][v['kind'] == k] for v in runs.values()]))) if any(np.any(v['kind'] == k) for v in runs.values()) else None
               for k in ('moving', 'stationary')}
        out = {'n_routes': len(runs), 'routes': sorted(runs),
               'steps': {k: int(sum(np.sum(v['kind'] == k) for v in runs.values())) for k in ('true', 'moving', 'stationary')},
               'median_first_waypoint_distance_m': chk}
        out.update(w_outcomes(runs, False))
        out['sensitivity: true-history steps directly after a swap step left out'] = w_outcomes(runs, True)
        res['models'][model] = out
    res['status_line'] = status_line(res['models'])
    return res


def render_W(man):
    W = man['W']
    L = ['## W. Motion-history swap test (addendum sections 11 and 11-B)', '', f"Status: {W['status_line']}", '', W['label'], '',
         '; '.join(f'{k}: {v}' for k, v in W['definitions'].items()), '']

    def block(o):
        out = []
        for name, v in o.items():
            if not isinstance(v, dict) or 'pooled_true_pct' not in v:
                continue
            out += [f"- {name}: pooled {f(v['pooled_swapped_pct'], 2)} % ({v['steps_swapped']} steps) against "
                    f"{f(v['pooled_true_pct'], 2)} % ({v['steps_true']} steps); routes used {len(v['routes_used'])}"
                    + (f"; reading: {v['reading']}" if 'reading' in v else '')]
            if 'mean_diff' in v['paired']:
                out += ['', table(PAIR_HDR, [pair_row('swapped minus true', v['paired'], 2)]), '']
        return out
    for model, o in W['models'].items():
        if is_pending(o):
            L += [f'**{model}**: {pending_str(o)}', '']
            continue
        L += [f"**{model}** ({o['n_routes']} routes; steps by history: {o['steps']}; "
              f"median first-waypoint distance by history (m): {o['median_first_waypoint_distance_m']})", '']
        L += block(o) + ['']
        sens = [k for k in o if k.startswith('sensitivity')]
        for k in sens:
            L += [f'*{model}, {k}*', ''] + block(o[k]) + ['']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------- X. crawling speed

X_METRICS = {'crawl_pct_0.1_to_1.0': lambda rd: pct((rd['speed'] >= 0.1) & (rd['speed'] < 1.0)),
             'crawl_pct_0.1_to_0.5 (sensitivity)': lambda rd: pct((rd['speed'] >= 0.1) & (rd['speed'] < 0.5))}


def analysis_X(arms, data):
    """ANALYSIS_ADDENDUM.md section 12b. Post hoc, exploratory, existing step logs only."""
    rows = {'default controller, run1': ('Golden-6400 run1', 'Flooded-6400-Matched run1'),
            'default controller, run2': ('Golden-6400 run2', 'Flooded-6400-Matched run2'),
            'gate-off controller': ('Golden-6400 nogate', 'Flooded-6400-Matched nogate')}
    res = {'label': 'post hoc, exploratory; defined in addendum section 12b',
           'definition': 'share of logged route steps with 0.1 <= speed < 1.0 m/s (sensitivity: < 0.5 m/s)',
           'golden_minus_flooded': {}, 'all_models_default_run1': {}}
    for row, (ga, fa) in rows.items():
        p = pending(arms, [(ga, CANONICAL_44), (fa, CANONICAL_44)])
        res['golden_minus_flooded'][row] = p or {k: paired(vec(arms, ga, fn, CANONICAL_44), vec(arms, fa, fn, CANONICAL_44))
                                                 for k, fn in X_METRICS.items()}
    for m in MODELS:
        res['all_models_default_run1'][m] = {k: float(np.mean([fn(data[m][r]) for r in CANONICAL_44])) for k, fn in X_METRICS.items()}
    res['status_line'] = status_line(res['golden_minus_flooded'])
    return res


def render_X(man):
    X = man['X']
    L = ['## X. Time at crawling speed (addendum section 12b)', '', f"Status: {X['status_line']}", '', X['label'], '', X['definition'], '']
    for row, o in X['golden_minus_flooded'].items():
        L += paired_block('Golden minus Flooded, per-route share (%), ' + row, o, 2)
    ks = list(X_METRICS)
    L += ['**Mean of per-route shares (%), default controller, run 1**', '',
          table(['model'] + ks, [[m] + [f(v[k], 2) for k in ks] for m, v in X['all_models_default_run1'].items()]), '']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------- Y. plans at rest and at slow speed

def y_masks(rd):
    v, L, ve = np.asarray(rd['speed']), np.asarray(rd['L']), np.asarray(rd['v_end'])
    out = {}
    for sname, cond in (('at_rest', v < 0.1), ('slow_0.1_to_0.5', (v >= 0.1) & (v <= 0.5))):
        out[f'{sname}: stays_put (L<0.64)'] = (L < 0.64, cond)
        out[f'{sname}: ends_at_rest (v_end<0.5)'] = (ve < 0.5, cond)
    return out


def y_route_table(arm, routes):
    tab = {}
    for r in routes:
        for k, (num, cond) in y_masks(arm[r]).items():
            tab.setdefault(k, {})[r] = (int(np.sum(num & cond)), int(np.sum(cond)))
    return tab


def analysis_Y(arms, data):
    """ANALYSIS_ADDENDUM.md section 13. Post hoc, exploratory, existing step logs only."""
    G1, F1, G2, F2 = 'Golden-6400 run1', 'Flooded-6400-Matched run1', 'Golden-6400 run2', 'Flooded-6400-Matched run2'
    GN, FN = 'Golden-6400 nogate', 'Flooded-6400-Matched nogate'
    rows = {'default controller, run1': (G1, F1), 'default controller, run2': (G2, F2), 'gate-off controller': (GN, FN)}
    res = {'label': 'post hoc, exploratory; defined in addendum section 13 before computing',
           'definitions': {'at rest': 'speed < 0.1 m/s', 'slow': '0.1 <= speed <= 0.5 m/s', 'stays put': 'L < 0.64 m',
                           'ends at rest': 'v_end < 0.5 m/s, v_end = path length between waypoints 54 and 64 / 1.0 s',
                           'per_route_rule': f'a route is used only if both arms have at least {V_MIN} steps in the stratum'},
           'golden_minus_flooded': {}, 'pooled_all_models_default_run1': {}}
    for row, (ga, fa) in rows.items():
        p = pending(arms, [(ga, CANONICAL_44), (fa, CANONICAL_44)])
        if p:
            res['golden_minus_flooded'][row] = p
            continue
        res['golden_minus_flooded'][row] = v_paired(y_route_table(arms[ga], CANONICAL_44), y_route_table(arms[fa], CANONICAL_44), CANONICAL_44)
    for m in MODELS:
        res['pooled_all_models_default_run1'][m] = v_pooled(y_route_table(data[m], CANONICAL_44), CANONICAL_44)
    res['status_line'] = status_line(res['golden_minus_flooded'])
    return res


def render_Y(man):
    Y = man['Y']
    L = ['## Y. Plans at rest and at slow speed (addendum section 13)', '', f"Status: {Y['status_line']}", '', Y['label'], '',
         '; '.join(f'{k}: {v}' for k, v in Y['definitions'].items()), '']
    for row, o in Y['golden_minus_flooded'].items():
        L += paired_block('Golden minus Flooded, per-route shares (%), ' + row, o, 2)
    d = Y['pooled_all_models_default_run1']
    ks = list(next(iter(d.values())).keys())
    L += ['**Pooled shares (%), all 44 routes, default controller, run 1** (steps in the stratum in brackets, first model)', '',
          table(['arm'] + ks, [[mn] + [f(x[k]['pct'], 2) for k in ks] for mn, x in d.items()]), '']
    return '\n'.join(L) + '\n'


# --------------------------------------------------------------------------- Z. H1 without the controller-tuning routes

def analysis_Z(arms, data, tuning_union):
    """ANALYSIS_ADDENDUM.md section 14. Post hoc sensitivity, existing results only."""
    tuned = {str(r) for r in tuning_union}
    routes = [r for r in CANONICAL_44 if r not in tuned]
    res = {'label': 'post hoc sensitivity; defined in addendum section 14 before computing',
           'routes_not_used_for_controller_tuning': routes, 'n_routes': len(routes), 'comparisons': {}}
    for treat in (G16, F16):
        for base_name, base in (('Base (original run)', data[BASE]), ('Base run2', arms.get('Base run2', {}))):
            key = f'{treat} minus {base_name}'
            if any(r not in base for r in routes):
                res['comparisons'][key] = {'status': 'pending', 'have': {'base_run2': sum(r in base for r in routes)}, 'need': {'base_run2': len(routes)}}
                continue
            res['comparisons'][key] = {met: paired([fn(data[treat][r]) for r in routes], [fn(base[r]) for r in routes])
                                       for met, fn in (('driving_score', lambda rd: rd['ds']), ('route_completion', lambda rd: rd['rc']))}
    res['status_line'] = status_line(res['comparisons'])
    return res


def render_Z(man):
    Z = man['Z']
    L = ['## Z. H1 on the routes not used to tune the controller (addendum section 14)', '', f"Status: {Z['status_line']}", '', Z['label'], '',
         f"{Z['n_routes']} routes: {', '.join(Z['routes_not_used_for_controller_tuning'])}", '']
    for k, o in Z['comparisons'].items():
        L += paired_block(k, o, 2)
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

    # N-S: additional runs (whatever subset is usable now)
    ov = check_route_constants()
    runs, unparsable = load_new_runs()
    arms = {**{n: data[m] for n, m in RUN1_ARMS.items()}, **runs}
    man['data_checks_new_runs'] = {
        'usable_routes': {NEW_RUN_TAGS[n]: len(v) for n, v in runs.items()},
        'usable_route_ids': {NEW_RUN_TAGS[n]: sorted(v) for n, v in runs.items()},
        'usable_but_unparsable_treated_as_absent': unparsable,
        'usability_rule': usable_dir.__doc__.strip().replace('\n   ', '')}
    extra_rows = analysis_L_additional(arms)
    if extra_rows:
        man['L']['additional_models'] = extra_rows
    man['N'] = analysis_N(arms)
    man['O'] = analysis_O(arms)
    man['P'] = analysis_P(arms)
    man['Q'] = analysis_Q(arms, man['A']['pairs'][f'{G64} vs {FM}']['standstill_pct']['wilcoxon']['p'])
    man['R'] = analysis_R(arms, ov)
    man['S'] = analysis_S(arms)
    man['T'] = analysis_T(arms)
    man['U'] = analysis_U(arms, scen, data)
    man['V'] = analysis_V(arms, data)
    man['W'] = analysis_W()
    man['X'] = analysis_X(arms, data)
    man['Y'] = analysis_Y(arms, data)
    man['Z'] = analysis_Z(arms, data, man['H']['tuning_routes_union'])
    man = clean(man)
    OUT_MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=False, ensure_ascii=False) + '\n')
    OUT_REPORT.write_text(render(man) + '\n' + render_new(man) + '\n' + render_W(man) + '\n' + render_X(man) + '\n' + render_Y(man) + '\n' + render_Z(man))
    p = man['A']['pairs'][f'{G64} vs {FM}']['standstill_pct']
    print(f"primary H2 reproduced: diff={p['mean_diff']:.4f} BCa={p['bca95']} W={p['wilcoxon']['statistic']} p={p['wilcoxon']['p']:.6f}")
    print(f'wrote {OUT_MANIFEST}\nwrote {OUT_REPORT}')


if __name__ == '__main__':
    main()
