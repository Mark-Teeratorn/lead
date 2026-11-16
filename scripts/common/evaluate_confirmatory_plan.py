#!/usr/bin/env python3
"""
44-Route Canonical Benchmark & 20 Hz Kinematic Telemetry Evaluator for:
"Few Edge Cases Are All You Need" (H1, H2, H3 + Golden-1600 220-Route Holdout Validation).
"""
import glob
import json
import os
import numpy as np
from scipy import stats

os.chdir("/home/aimslab/lead")

DELTA = 8.0
ALPHA = 0.05
N_RESAMPLES = 20000
RNG_SEED = 0

R44_DATA = json.load(open("outputs/final_2x2_anova_matrix_report.json"))["per_route_scores"]
ROUTES_44 = sorted(R44_DATA.keys())
SET_44 = set(ROUTES_44)

MODELS = {
    "Base": "base",
    "Flooded_1600": "model_matrix_flooded_1600",
    "Golden_1600": "model_matrix_golden_1600",
    "Flooded_6400": "model_6400",
    "Golden_6400": "model_matrix_golden_6400",
}


def load_route_record(tag, rid):
    paths = [f"outputs/local_evaluation/{tag}_{rid}/checkpoint_endpoint.json"]
    if tag == "base":
        paths.append(f"outputs/local_evaluation/alpamayo_{rid}/checkpoint_endpoint.json")
    for p in paths:
        if os.path.exists(p):
            try:
                d = json.load(open(p))
                recs = d.get("_checkpoint", {}).get("records", [])
                if not recs:
                    continue
                r = recs[0]
                inf = r.get("infractions", {})
                crashes = sum(
                    len(inf.get(k, []))
                    for k in ("collisions_layout", "collisions_vehicle", "collisions_pedestrian")
                )
                return {
                    "ds": float(r["scores"]["score_composed"]),
                    "rc": float(r["scores"]["score_route"]),
                    "crashes": int(crashes),
                }
            except Exception:
                pass
    return None


def load_telemetry(tag, rid):
    paths = [f"outputs/local_evaluation/{tag}_{rid}/predicted_trajectories.jsonl"]
    if tag == "base":
        paths.append(f"outputs/local_evaluation/alpamayo_{rid}/predicted_trajectories.jsonl")
    p = next((x for x in paths if os.path.exists(x) and os.path.getsize(x) > 0), None)
    if p is None:
        return None
    brakes, speeds, steers = [], [], []
    with open(p) as f:
        for line in f:
            d = json.loads(line)
            brakes.append(d["brake"])
            speeds.append(d["speed"])
            steers.append(d["steer"])
    brakes, speeds, steers = np.array(brakes), np.array(speeds), np.array(steers)
    mov = speeds[:-1] >= 0.1
    return {
        "stationary_frac": float(np.mean(speeds < 0.1)),
        "hard_brake_frac": float(np.mean(brakes > 0.5)),
        "steer_jerk": float(np.mean(np.abs(np.diff(steers)))),
        "steer_jerk_moving": float(np.mean(np.abs(np.diff(steers))[mov])) if np.any(mov) else float("nan"),
        "speed_mean": float(np.mean(speeds)),
    }


def bca_ci_and_boot_p(diff, delta=DELTA, confidence=0.90, n_resamples=N_RESAMPLES, seed=RNG_SEED):
    res = stats.bootstrap(
        (diff,),
        np.mean,
        confidence_level=confidence,
        method="BCa",
        n_resamples=n_resamples,
        random_state=seed,
    )
    lo, hi = float(res.confidence_interval.low), float(res.confidence_interval.high)
    rng = np.random.default_rng(seed)
    boot_means = rng.choice(diff, size=(n_resamples, len(diff)), replace=True).mean(axis=1)
    p_gt_neg_delta = float(np.mean(boot_means <= -delta))
    p_lt_pos_delta = float(np.mean(boot_means >= delta))
    p_tost = max(p_gt_neg_delta, p_lt_pos_delta)
    return lo, hi, p_gt_neg_delta, p_tost


def holm_adjust(pvals):
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.zeros(m)
    prev = 0.0
    for i, idx in enumerate(order):
        prev = max(prev, (m - i) * pvals[idx])
        adj[idx] = min(prev, 1.0)
    return [float(x) for x in adj]


def main():
    ds = {m: [] for m in MODELS}
    rc = {m: [] for m in MODELS}
    cr = {m: [] for m in MODELS}
    tel = {m: {"stationary_frac": [], "hard_brake_frac": [], "steer_jerk": [], "speed_mean": []} for m in MODELS}

    for rid in ROUTES_44:
        for m, tag in MODELS.items():
            if m in R44_DATA[rid]:
                ds[m].append(float(R44_DATA[rid][m]["ds"]))
                rc[m].append(float(R44_DATA[rid][m]["rc"]))
                cr[m].append(int(R44_DATA[rid][m]["crashes"]))
            else:
                rec = load_route_record(tag, rid)
                ds[m].append(rec["ds"])
                rc[m].append(rec["rc"])
                cr[m].append(rec["crashes"])
            t = load_telemetry(tag, rid)
            for k in tel[m]:
                tel[m][k].append(t[k] if t else np.nan)

    for m in MODELS:
        ds[m] = np.array(ds[m])
        rc[m] = np.array(rc[m])
        cr[m] = np.array(cr[m])
        for k in tel[m]:
            tel[m][k] = np.array(tel[m][k])

    # H1: Golden_1600 > Base (one-sided paired Wilcoxon on DS + steering jerk telemetry)
    d_h1 = ds["Golden_1600"] - ds["Base"]
    p_h1 = float(stats.wilcoxon(ds["Golden_1600"], ds["Base"], alternative="greater").pvalue)
    lo_h1, hi_h1, _, _ = bca_ci_and_boot_p(d_h1)
    mask_jb = ~np.isnan(tel["Golden_1600"]["steer_jerk"]) & ~np.isnan(tel["Base"]["steer_jerk"])
    p_h1_jerk = float(stats.wilcoxon(tel["Golden_1600"]["steer_jerk"][mask_jb], tel["Base"]["steer_jerk"][mask_jb]).pvalue)

    # H2: Golden_6400 vs Golden_1600 equivalence within (-8, +8) DS + steering jerk saturation
    d_h2 = ds["Golden_6400"] - ds["Golden_1600"]
    lo_h2, hi_h2, _, p_h2 = bca_ci_and_boot_p(d_h2, delta=DELTA)
    p_h2_wilcox = float(stats.wilcoxon(ds["Golden_6400"], ds["Golden_1600"]).pvalue)
    p_h2_jerk = float(stats.wilcoxon(tel["Golden_6400"]["steer_jerk"], tel["Golden_1600"]["steer_jerk"]).pvalue)

    # H3: Golden_1600 vs Flooded_6400 non-inferiority (> -8 DS) + stationary freezing reduction (Golden_6400 vs Flooded_6400)
    d_h3 = ds["Golden_1600"] - ds["Flooded_6400"]
    lo_h3, hi_h3, p_h3_ni, _ = bca_ci_and_boot_p(d_h3, delta=DELTA)
    stat_diff = tel["Golden_6400"]["stationary_frac"] - tel["Flooded_6400"]["stationary_frac"]
    p_h3_stat = float(stats.wilcoxon(tel["Golden_6400"]["stationary_frac"], tel["Flooded_6400"]["stationary_frac"], alternative="less").pvalue)
    p_h3_speed = float(stats.wilcoxon(tel["Golden_6400"]["speed_mean"], tel["Flooded_6400"]["speed_mean"], alternative="greater").pvalue)

    # Holm-Bonferroni across the 3 primary tests [p_h1, p_h2, p_h3_ni] and telemetry tests
    holm_ds = holm_adjust([p_h1, p_h2, p_h3_ni])
    holm_mech = holm_adjust([p_h1, p_h2, p_h3_stat])

    # Out-of-sample 220-route generalization check for Golden-1600 (deduplicated by route ID)
    g16_unseen, g16_all, seen_g16_rids = [], [], set()
    for p in sorted(glob.glob("outputs/local_evaluation/model_matrix_golden_1600_*/checkpoint_endpoint.json")):
        bname = os.path.basename(os.path.dirname(p))
        if "retest" in bname:
            continue
        rid = bname.split("_")[-1]
        if rid in seen_g16_rids:
            continue
        rec = load_route_record("model_matrix_golden_1600", rid)
        if rec:
            seen_g16_rids.add(rid)
            g16_all.append(rec["ds"])
            if rid not in SET_44:
                g16_unseen.append(rec["ds"])
    g16_unseen, g16_all = np.array(g16_unseen), np.array(g16_all)

    report = {
        "n_canonical_routes": 44,
        "delta_ds": DELTA,
        "H1_Adaptation": {
            "mean_diff_ds": float(d_h1.mean()),
            "bca_90_ci": [lo_h1, hi_h1],
            "p_one_sided_wilcoxon": p_h1,
            "p_holm_primary": holm_mech[0],
            "p_holm_ds": holm_ds[0],
            "steer_jerk_diff_pct": float((np.nanmean(tel["Golden_1600"]["steer_jerk"]) - np.nanmean(tel["Base"]["steer_jerk"])) / np.nanmean(tel["Base"]["steer_jerk"]) * 100),
            "steer_jerk_p": p_h1_jerk,
            "passed": bool(holm_mech[0] < ALPHA),
        },
        "H2_Saturation": {
            "mean_diff_ds": float(d_h2.mean()),
            "bca_90_ci": [lo_h2, hi_h2],
            "ci_within_plus_minus_8": bool(lo_h2 > -DELTA and hi_h2 < DELTA),
            "p_tost_bootstrap": p_h2,
            "p_holm_primary": holm_mech[1],
            "p_holm_ds": holm_ds[1],
            "p_wilcoxon_two_sided": p_h2_wilcox,
            "steer_jerk_wilcoxon_p": p_h2_jerk,
            "passed": bool(lo_h2 > -DELTA and hi_h2 < DELTA and holm_mech[1] < ALPHA),
        },
        "H3_Curation_Efficiency_and_Kinematics": {
            "ds_diff_g1600_vs_f6400": float(d_h3.mean()),
            "bca_90_ci": [lo_h3, hi_h3],
            "ci_lower_above_minus_8": bool(lo_h3 > -DELTA),
            "p_noninf_bootstrap": p_h3_ni,
            "p_holm_ds": holm_ds[2],
            "stationary_frac_f6400": float(tel["Flooded_6400"]["stationary_frac"].mean()),
            "stationary_frac_g6400": float(tel["Golden_6400"]["stationary_frac"].mean()),
            "stationary_diff_abs": float(stat_diff.mean()),
            "stationary_one_sided_wilcoxon_p": p_h3_stat,
            "stationary_p_holm": holm_mech[2],
            "speed_one_sided_wilcoxon_p": p_h3_speed,
            "passed": bool(lo_h3 > -DELTA and holm_mech[2] < ALPHA),
        },
        "Golden_1600_220_Holdout_Validation": {
            "completed_total": int(len(g16_all)),
            "completed_unseen": int(len(g16_unseen)),
            "mean_ds_all": float(g16_all.mean()),
            "mean_ds_unseen": float(g16_unseen.mean()),
            "unseen_vs_base_mannwhitney_one_sided_p": float(stats.mannwhitneyu(g16_unseen, ds["Base"], alternative="greater").pvalue),
            "unseen_vs_44_mannwhitney_two_sided_p": float(stats.mannwhitneyu(g16_unseen, ds["Golden_1600"]).pvalue),
        },
    }
    with open("outputs/confirmatory_statistical_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
