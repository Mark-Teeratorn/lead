#!/usr/bin/env python3
"""Qualitative figure of the same-input replay (ANALYSIS_ADDENDUM section 27; illustrative, no test).

For the two states chosen by the rule of section 27 (state 7, the typical state; state 120, the largest
difference), the figure shows the front camera frame of the state and the 16 sampled plans of each of the three
6,400-sample checkpoints, one line per plan with its extent L, sorted by L. The planned paths are nearly straight
(lateral displacement below 0.2 m in both states), so paths drawn in the ego frame would lie on top of each other.
Plans with L < 0.64 m (stay put) have an open marker and are counted in the panel title; the dotted and dashed
lines are the thresholds 0.64 m and 1.5 m.

Input: the files written by scripts/evaluation/run_same_input_qualitative.sh (plan waypoints and camera frames
of the re-run) and the stored replays in outputs/same_input (plan lengths of the original replay). The plan
lengths of the re-run are compared with the stored ones; the comparison is printed and written next to the figure.

Usage: python3 scripts/paper/make_qualitative_figure.py [--plans-dir DIR] [--out docs/figures/revision/figure_2.png]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/home/aimslab/lead")
STATES = [(7, "(a) typical state"), (120, "(b) largest difference")]
EXPERTS = [("Golden-6400-Full", "Golden-6400", "#0072B2"), ("Flooded-6400-Matched-Full", "Flooded-6400", "#D55E00"),
           ("Balanced-6400-Full", "Decoupling-6400", "#009E73")]
STAY = 0.64     # stay-put plan: L < 0.64 m (dotted line)
GATE = 1.5      # near-stationary plan, first clause of the standstill gate: L < 1.5 m (dashed line)
FRONT_CAMERA_INDEX = 1   # front wide camera of the model's camera rig (checked on the saved frames: ego hood visible)
DISPLAY_GAMMA = {120: 0.6}   # night scene: frame brightened for print only (stated in the caption); the model input is unchanged
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})


def extent(xyz):
    return np.linalg.norm(np.diff(xyz[..., :2], axis=1), axis=-1).sum(1)


def front_frame(npz, gamma=1.0):
    """Last frame of the front camera as an (H, W, 3) uint8 image."""
    img, cams = npz["images"], [int(c) for c in npz["camera_indices"].reshape(-1)]
    n_cam = len(cams)
    img = img.reshape(n_cam, img.shape[0] // n_cam, *img.shape[1:])     # (camera, frame, ...)
    k = cams.index(FRONT_CAMERA_INDEX) if FRONT_CAMERA_INDEX in cams else 0
    f = img[k, -1]
    if f.shape[0] in (1, 3) and f.shape[-1] not in (1, 3):               # channels first
        f = np.moveaxis(f, 0, -1)
    f = f.astype(np.float32)
    if f.max() <= 1.5:
        f = f * 255.0
    f = 255.0 * (np.clip(f, 0, 255) / 255.0) ** gamma
    return np.clip(f, 0, 255).astype(np.uint8)


def stored_lengths(name, state):
    for line in open(ROOT / f"outputs/same_input/{name}.jsonl"):
        r = json.loads(line)
        if r["state"] == state:
            return np.asarray(r["L"], dtype=np.float64), r
    raise SystemExit(f"state {state} not in the stored replay of {name}")


def selection_check():
    """Rule of section 27 recomputed from the stored replays: candidates at <= 0.5 m/s, d = stay-put plans of
    Flooded minus those of Golden; panel (a) closest to the mean of d, panel (b) the largest d (lowest index on ties)."""
    rec = {n: {json.loads(l)["state"]: json.loads(l) for l in open(ROOT / f"outputs/same_input/{n}.jsonl")}
           for n in ("Golden-6400-Full", "Flooded-6400-Matched-Full")}
    cand = sorted(s for s, r in rec["Golden-6400-Full"].items() if r["speed_mps"] <= 0.5 and s in rec["Flooded-6400-Matched-Full"])
    n_stay = lambda n, s: int((np.asarray(rec[n][s]["L"]) < STAY).sum())
    d = {s: n_stay("Flooded-6400-Matched-Full", s) - n_stay("Golden-6400-Full", s) for s in cand}
    mean_d = float(np.mean(list(d.values())))
    typical = min(cand, key=lambda s: (abs(d[s] - mean_d), s))
    largest = min(cand, key=lambda s: (-d[s], s))
    return {"candidate_states": len(cand), "mean_d": mean_d, "pooled_stay_put_difference_pp": 100.0 * mean_d / 16.0, "typical_state": typical, "d_typical": d[typical],
            "largest_state": largest, "d_largest": d[largest],
            "matches_figure": [typical, largest] == [s for s, _ in STATES]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plans-dir", default="/mnt/disk2/r4_sameinput/qualitative/plans")
    ap.add_argument("--out", default=str(ROOT / "docs/figures/revision/figure_2.png"))
    a = ap.parse_args()
    pd = Path(a.plans_dir)
    fig, axes = plt.subplots(len(STATES), 4, figsize=(13.0, 6.2), gridspec_kw={"width_ratios": [1.6, 1, 1, 1], "hspace": 0.45, "wspace": 0.3})
    report = {"label": "ANALYSIS_ADDENDUM section 27: plan lengths of the re-run against the stored replay", "states": {}}
    lateral = 0.0
    for row, (state, panel) in enumerate(STATES):
        plans, meta = {}, None
        for name, _, _ in EXPERTS:
            z = np.load(pd / f"{name}_state{state}.npz")
            xyz = np.asarray(z["pred_xyz"], dtype=np.float64).reshape(-1, 64, 3)
            L_old, meta = stored_lengths(name, state)
            L_new = extent(xyz)
            same = bool(L_new.shape == L_old.shape and np.allclose(np.round(L_new, 4), L_old, atol=1e-3))
            report["states"].setdefault(str(state), {})[name] = {
                "plans": int(len(L_new)), "identical_lengths": same,
                "stay_put_rerun": int((L_new < STAY).sum()), "stay_put_stored": int((L_old < STAY).sum()),
                "median_L_rerun": float(np.median(L_new)), "median_L_stored": float(np.median(L_old)),
                "largest_abs_difference_sorted_m": float(np.max(np.abs(np.sort(L_new) - np.sort(L_old)))) if len(L_new) == len(L_old) else None}
            plans[name] = (xyz, L_new, z)
            lateral = max(lateral, float(np.abs(xyz[..., 1]).max()))
        top = max(2.2, max(float(p[1].max()) for p in plans.values()) * 1.08)
        ax = axes[row, 0]
        ax.imshow(front_frame(plans[EXPERTS[0][0]][2], DISPLAY_GAMMA.get(state, 1.0)))
        ax.set_xticks([]), ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(f"{panel} (state {state})\n{meta['scenario']}\nspeed {meta['speed_mps']:.2f} m/s, \"{meta['nav_text']}\"", fontsize=8.5, loc="left")
        for col, (name, label, colour) in enumerate(EXPERTS, start=1):
            _, L, _ = plans[name]
            ax = axes[row, col]
            Ls = np.sort(L)
            k = np.arange(1, len(Ls) + 1)
            stay = Ls < STAY
            ax.vlines(k, 0, Ls, color=colour, lw=2.2, alpha=0.85)                 # one line per sampled plan
            ax.scatter(k[~stay], Ls[~stay], s=16, color=colour, zorder=3)
            ax.scatter(k[stay], Ls[stay], s=30, facecolor="white", edgecolor=colour, lw=1.3, zorder=3)
            ax.axhline(STAY, color="k", lw=0.8, ls=":")
            ax.axhline(GATE, color="k", lw=0.8, ls="--")
            ax.set_xlim(0.2, len(Ls) + 0.8), ax.set_ylim(0, top)
            ax.set_xticks([1, 4, 8, 12, 16])
            n_stay = int(stay.sum())
            ax.set_title(f"{label}: {n_stay} of {len(L)} stay put\nmedian $L$ = {np.median(L):.2f} m", fontsize=9)
            if row == len(STATES) - 1:
                ax.set_xlabel("sampled plan (sorted by $L$)")
            if col == 1:
                ax.set_ylabel("plan extent $L$ (m)")
    out = Path(a.out)
    report["selection_rule"] = selection_check()
    report["largest_abs_lateral_displacement_m"] = lateral
    fig.savefig(out, dpi=300, bbox_inches="tight", metadata={"Software": None})
    print("wrote", out)
    rep = ROOT / "docs/provenance/same_input_qualitative_check.json"
    rep.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report["selection_rule"]), "largest lateral", round(lateral, 3))
    print("wrote", rep)


if __name__ == "__main__":
    main()
