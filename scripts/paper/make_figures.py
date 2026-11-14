#!/usr/bin/env python3
"""Generate revision figures (PNG, 300 dpi) into docs/figures/revision/.

figure_1.png  fig_pipeline: inference/control pipeline schematic
figure_2.png  fig_paired_standstill: per-route standstill dumbbell (Golden-6400 vs Flooded-6400-Matched)
figure_3.png  fig_extent_cdf: empirical CDFs of predicted trajectory extent L
figure_4.png  fig_model_by_controller: model x controller standstill, split into blocked time and the rest
              (only if the gate-off runs are complete; needs analysis U in the manifest)
figure_5.png  fig_low_speed_plans: plans at 0.5 m/s or less (analysis V of the manifest): plan mix of the
              matched pair under both controllers, and stay-put share of all six models against their training sets
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path("/home/aimslab/lead")
OUT = ROOT / "docs/figures/revision"
sys.path.insert(0, str(ROOT / "scripts/evaluation"))
from compute_paper_tables import CANONICAL_44, MODEL_PREFIXES, load_model_data  # noqa: E402

C_GOLD, C_FLOOD = "#0072B2", "#D55E00"
MANIFEST = ROOT / "docs/provenance/paper_reanalysis_manifest.json"
NAME_G, NAME_F = "Golden-6400", "Flooded-6400-Matched"
LABEL = {NAME_G: "Golden-6400", NAME_F: "Flooded-6400"}  # names used in the manuscript
OVERLAP_7 = ["1852", "1825", "2286", "23901", "23695", "3464", "2164"]  # train_eval_overlap_canonical44.json
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.hashsalt": "0", "savefig.dpi": 300})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=300, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    print(f"wrote {OUT / name}")


def fig_paired_standstill(g, f):
    routes = [r for r in CANONICAL_44 if r in g and r in f]
    vg = np.array([g[r]["standstill_fraction"] * 100 for r in routes])
    vf = np.array([f[r]["standstill_fraction"] * 100 for r in routes])
    order = np.argsort(vf - vg, kind="stable")
    routes, vg, vf = [routes[i] for i in order], vg[order], vf[order]
    print(f"fig_paired_standstill: n={len(routes)} mean {NAME_G}={vg.mean():.2f}  mean {NAME_F}={vf.mean():.2f}")
    y = np.arange(len(routes))
    fig, ax = plt.subplots(figsize=(6.5, 9))
    ax.hlines(y, vg, vf, color="0.7", lw=1.5, zorder=1)
    ax.scatter(vg, y, color=C_GOLD, s=28, zorder=2, label=LABEL[NAME_G])
    ax.scatter(vf, y, color=C_FLOOD, s=28, zorder=2, label=LABEL[NAME_F])
    ax.axvline(vg.mean(), color=C_GOLD, ls="--", lw=1.2)
    ax.axvline(vf.mean(), color=C_FLOOD, ls="--", lw=1.2)
    man = json.loads(MANIFEST.read_text())
    overlap = set(man["R"]["overlap_routes_7"]) if "overlap_routes_7" in man.get("R", {}) else set(OVERLAP_7)
    tuning = {str(r) for r in man["H"]["tuning_routes_union"]}
    print(f"fig_paired_standstill: marked {len(overlap & set(routes))} overlap and {len(tuning & set(routes))} tuning routes")
    labels = [r + ("*" if r in overlap else "") + ("\u2020" if r in tuning else "") for r in routes]
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(-0.8, len(routes) - 0.2)
    ax.set_xlabel("Standstill time (% of route steps)")
    ax.set_ylabel("Route")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    save(fig, "figure_2.png")


def fig_extent_cdf(g, f):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for d, name, c in ((g, NAME_G, C_GOLD), (f, NAME_F, C_FLOOD)):
        L = np.concatenate([np.asarray(d[r]["ltrajs"], float) for r in CANONICAL_44 if r in d])
        L = np.clip(np.sort(L), 0.1, None)
        ax.step(L, np.arange(1, len(L) + 1) / len(L), where="post", color=c, lw=1.8, label=f"{LABEL[name]} (n={len(L):,} steps)")
    for x, lab, ha in ((0.64, "0.64 m", "right"), (1.5, "1.5 m", "right"), (2.0, "2.0 m", "left")):
        ax.axvline(x, color="0.4", ls="--", lw=1)
        ax.text(x, 1.02, lab, ha=ha, va="bottom", fontsize=9, color="0.25",
                transform=ax.get_xaxis_transform())
    ax.set_xscale("log")
    ax.set_xlim(0.1, 100)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted trajectory extent L (m)")
    ax.set_ylabel("Cumulative fraction of steps")
    ax.legend(loc="lower right", frameon=False)
    save(fig, "figure_3.png")


def route_bootstrap_ci(vals, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    vals = np.asarray(vals, float)
    means = vals[rng.integers(0, len(vals), (n, len(vals)))].mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def fig_model_by_controller():
    """Standstill by model and controller, split into blocked time (analysis U of the manifest) and the rest."""
    pref = {"Golden": "model_matrix_golden_6400_nogate", "Flooded": "model_matrix_flooded_6400_nogate"}
    nog = {k: load_model_data([p]) for k, p in pref.items()}
    if any(len(v) < len(CANONICAL_44) for v in nog.values()):
        print("fig_model_by_controller skipped: gate-off runs incomplete "
              f"({', '.join(f'{k}: {len(v)}/{len(CANONICAL_44)}' for k, v in nog.items())})")
        return
    dflt = {"Golden": load_model_data(MODEL_PREFIXES["Golden-6400"]),
            "Flooded": load_model_data(MODEL_PREFIXES["Flooded-6400-Matched"])}
    U = json.loads(MANIFEST.read_text())["U"]["routes_with_blocked_time"]
    arm = {("Golden", 0): "Golden-6400 run1", ("Flooded", 0): "Flooded-6400-Matched run1",
           ("Golden", 1): "Golden-6400 nogate", ("Flooded", 1): "Flooded-6400-Matched nogate"}
    fig, ax = plt.subplots(figsize=(6, 4.2))
    x, w = np.arange(2), 0.36
    for j, data in enumerate((dflt, nog)):
        for i, k in enumerate(("Golden", "Flooded")):
            v = [data[k][r]["standstill_fraction"] * 100 for r in CANONICAL_44]
            m, (lo, hi) = np.mean(v), route_bootstrap_ci(v)
            u = U[arm[(k, j)]]
            assert abs(u["mean_standstill_pct"] - m) < 1e-6, "manifest and step logs disagree on mean standstill"
            blk = u["mean_blocked_pct"]
            c, xpos = (C_GOLD, C_FLOOD)[i], x[j] + (i - 0.5) * w
            ax.bar(xpos, m - blk, w, color=c, edgecolor="white", label=LABEL[(NAME_G, NAME_F)[i]] if j == 0 else None)
            ax.bar(xpos, blk, w, bottom=m - blk, color=c, alpha=0.45, hatch="///", edgecolor="white")
            ax.errorbar(xpos, m, yerr=[[m - lo], [hi - m]], color="k", capsize=3, lw=1)
            print(f"fig_model_by_controller: {arm[(k, j)]}: standstill {m:.2f} %, of which blocked {blk:.2f} %")
    ax.bar(0, 0, 0, color="0.6", alpha=0.45, hatch="///", edgecolor="white", label="of which blocked time")
    ax.set_xticks(x)
    ax.set_xticklabels(["Default controller", "Gate-off controller"])
    ax.set_ylabel("Standstill time (% of route steps)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.14), ncol=3, fontsize=9.5,
              columnspacing=1.2, handlelength=1.6)
    save(fig, "figure_4.png")


def fig_low_speed_plans():
    """Plans at low speed, from analysis V of the manifest (no step logs are read here)."""
    V = json.loads(MANIFEST.read_text())["V"]
    rows = V["golden_minus_flooded"]
    parts = [("low_speed_stays_put", "stays put (L < 0.64 m)", 1.0),
             ("low_speed_in_between", "in between", 0.5),
             ("low_speed_starts_moving", "starts moving (L \u2265 2 m)", 0.2)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 4.3), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.3})
    x, w = np.arange(2), 0.36
    for j, key in enumerate(("default controller, run1", "gate-off controller")):
        for i, side in enumerate(("mean_first", "mean_second")):  # first = Golden, second = Flooded
            c, xpos, bottom = (C_GOLD, C_FLOOD)[i], x[j] + (i - 0.5) * w, 0.0
            vals = [rows[key][k][side] for k, _, _ in parts]
            assert abs(sum(vals) - 100) < 1e-6, "the three plan classes must add to 100 %"
            for v, (_, _, alpha) in zip(vals, parts):
                a.bar(xpos, v, w, bottom=bottom, color=c, alpha=alpha, edgecolor="white")
                bottom += v
            a.text(xpos, vals[0] + 2.5, f"{vals[0]:.0f} %", ha="center", va="bottom", fontsize=10)
            print(f"fig_low_speed_plans: {key}, {('Golden', 'Flooded')[i]}: "
                  + ", ".join(f"{lab} {v:.2f} %" for v, (_, lab, _) in zip(vals, parts)))
    for i, name in enumerate((NAME_G, NAME_F)):
        a.bar(0, 0, 0, color=(C_GOLD, C_FLOOD)[i], label=LABEL[name])
    a.bar(0, 0, 0, color="none", label=" ")  # filler so that the second legend column holds the three plan classes
    for _, lab, alpha in parts:
        a.bar(0, 0, 0, color="0.25", alpha=alpha, label=lab)
    a.set_xticks(x)
    a.set_xticklabels(["Default controller", "Gate-off controller"])
    a.set_ylim(0, 100)
    a.set_ylabel("Plans at \u2264 0.5 m/s (% of steps, route mean)")
    a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.3), ncol=2, fontsize=9, columnspacing=1.0)
    a.set_title("(a)", loc="left", fontsize=11, y=1.3)

    pooled = V["pooled_all_models_default_run1"]
    train = V["training_set_reference"]["low_speed_stays_put_pct"]
    models = [("Base", "Base", "0.55", None), ("Flooded-1600", "Flooded-\n1600", C_FLOOD, "flooded_1600"),
              ("Golden-1600", "Golden-\n1600", C_GOLD, "golden_1600"),
              ("Flooded-6400-Hist", "Flooded-\n6400-Hist", C_FLOOD, None),
              ("Flooded-6400-Matched", "Flooded-\n6400", C_FLOOD, "flooded_6400"),
              ("Golden-6400", "Golden-\n6400", C_GOLD, "golden_6400")]
    for k, (name, lab, c, tkey) in enumerate(models):
        v = pooled[name]["low_speed_stays_put"]["pct"]
        b.bar(k, v, 0.62, color=c, edgecolor="white", alpha=0.6 if name == "Flooded-6400-Hist" else 1.0)
        b.text(k, v + 0.8, f"{v:.1f}", ha="center", va="bottom", fontsize=9.5)
        if tkey:
            b.plot([k - 0.36, k + 0.36], [train[tkey]] * 2, color="k", lw=2,
                   label="share in its training set" if tkey == "flooded_1600" else None)
        print(f"fig_low_speed_plans: pooled stay-put share {name}: {v:.2f} %"
              + (f" (training set {train[tkey]} %)" if tkey else ""))
    b.set_xticks(range(len(models)))
    b.set_xticklabels([m[1] for m in models], fontsize=9)
    b.set_ylim(0, 40)
    b.set_ylabel("Plan stays put at \u2264 0.5 m/s (% of steps, pooled)")
    b.legend(frameon=False, loc="upper right", fontsize=9.5)
    b.set_title("(b)", loc="left", fontsize=11, y=1.3)
    save(fig, "figure_5.png")


def fig_pipeline():
    steps = [
        "Cameras, ego history,\nnavigation command",
        "Frozen VLM backbone (W4A8)",
        "Flow-matching action expert\n(fine-tuned)",
        "64-waypoint trajectory,\nextent L",
        "Target speed and standstill gate:\nstop if L < 1.5 m or\n(v < 0.5 m/s and L < 2.0 m)",
        "PID controller",
        "CARLA vehicle",
    ]
    fig, ax = plt.subplots(figsize=(6.5, 8.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    bw, bh = 5.0, 0.95
    cx = 4.0
    ys = np.linspace(9.3, 0.7, len(steps))
    for k, (t, y) in enumerate(zip(steps, ys)):
        h = bh * (1.5 if k == 4 else 1.0)
        ax.add_patch(FancyBboxPatch((cx - bw / 2, y - h / 2), bw, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc="white", ec="black", lw=1.2))
        ax.text(cx, y, t, ha="center", va="center", fontsize=10)
    hs = [bh * (1.5 if k == 4 else 1.0) for k in range(len(steps))]
    for k in range(len(steps) - 1):
        ax.add_patch(FancyArrowPatch((cx, ys[k] - hs[k] / 2), (cx, ys[k + 1] + hs[k + 1] / 2),
                                     arrowstyle="-|>", mutation_scale=14, color="black", lw=1.2))
    # feedback: vehicle -> ego history
    xr = cx + bw / 2 + 1.2
    ax.plot([cx + bw / 2, xr], [ys[-1], ys[-1]], color="black", lw=1.2)
    ax.plot([xr, xr], [ys[-1], ys[0]], color="black", lw=1.2)
    ax.add_patch(FancyArrowPatch((xr, ys[0]), (cx + bw / 2, ys[0]), arrowstyle="-|>", mutation_scale=14,
                                 color="black", lw=1.2))
    ax.text(xr + 0.15, (ys[0] + ys[-1]) / 2, "ego state feedback", rotation=90, ha="left", va="center", fontsize=10)
    save(fig, "figure_1.png")


def main():
    g = load_model_data(MODEL_PREFIXES[NAME_G])
    f = load_model_data(MODEL_PREFIXES[NAME_F])
    fig_paired_standstill(g, f)
    fig_extent_cdf(g, f)
    fig_model_by_controller()
    fig_low_speed_plans()
    fig_pipeline()


if __name__ == "__main__":
    main()
