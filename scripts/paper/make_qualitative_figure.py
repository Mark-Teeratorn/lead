#!/usr/bin/env python3
"""Qualitative figure of the same-input replay (ANALYSIS_ADDENDUM section 27; illustrative, no test).

For the two states chosen by the rule of section 27 (state 7, the typical state; state 120, the largest
difference), the figure shows the front camera frame of the state and the 16 sampled plans of each of the three
6,400-sample checkpoints as paths in the ego frame (x forward, y left). Plans with L < 0.64 m (stay put) are
drawn as a marker at the origin and counted in the panel title.

Input: the files written by scripts/evaluation/run_same_input_qualitative.sh (plan waypoints and camera frames
of the re-run) and the stored replays in outputs/same_input (plan lengths of the original replay). The plan
lengths of the re-run are compared with the stored ones; the comparison is printed and written next to the figure.

Usage: python3 scripts/paper/make_qualitative_figure.py [--plans-dir DIR] [--out docs/figures/revision/figure_5.png]
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
STAY = 0.64
FRONT_CAMERA_INDEX = 1   # front wide camera of the model's camera rig (checked on the saved frames: ego hood visible)
DISPLAY_GAMMA = {120: 0.45}   # night scene: frame brightened for print only (stated in the caption); the model input is unchanged
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plans-dir", default="/mnt/disk2/r4_sameinput/qualitative/plans")
    ap.add_argument("--out", default=str(ROOT / "docs/figures/revision/figure_5.png"))
    a = ap.parse_args()
    pd = Path(a.plans_dir)
    fig, axes = plt.subplots(len(STATES), 4, figsize=(13.0, 6.4), gridspec_kw={"width_ratios": [1.5, 1, 1, 1]})
    report = {"label": "ANALYSIS_ADDENDUM section 27: plan lengths of the re-run against the stored replay", "states": {}}
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
        lim = max(2.0, max(float(np.abs(p[0][..., :2]).max()) for p in plans.values()) * 1.05)
        ax = axes[row, 0]
        ax.imshow(front_frame(plans[EXPERTS[0][0]][2], DISPLAY_GAMMA.get(state, 1.0)))
        ax.set_xticks([]), ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(f"{panel}: state {state}, {meta['scenario']}\nspeed {meta['speed_mps']:.2f} m/s, \"{meta['nav_text']}\"", fontsize=9, loc="left")
        for col, (name, label, colour) in enumerate(EXPERTS, start=1):
            xyz, L, _ = plans[name]
            ax = axes[row, col]
            for p, l in zip(xyz, L):
                if l >= STAY:
                    ax.plot(-p[:, 1], p[:, 0], color=colour, lw=1.1, alpha=0.75)   # y left -> plotted to the left
            n_stay = int((L < STAY).sum())
            if n_stay:
                ax.scatter([0], [0], s=40 + 14 * n_stay, color=colour, edgecolor="k", lw=0.6, zorder=3)
            ax.scatter([0], [0], s=14, marker="^", color="k", zorder=4)
            ax.set_xlim(-lim / 2, lim / 2), ax.set_ylim(-0.05 * lim, lim)
            ax.set_aspect("equal", adjustable="box")
            ax.set_title(f"{label}: {n_stay} of {len(L)} stay put\nmedian plan length {np.median(L):.1f} m", fontsize=9)
            ax.set_xlabel("lateral (m), left is negative")
            if col == 1:
                ax.set_ylabel("forward (m)")
    fig.tight_layout()
    out = Path(a.out)
    fig.savefig(out, dpi=300, bbox_inches="tight", metadata={"Software": None})
    print("wrote", out)
    rep = ROOT / "docs/provenance/same_input_qualitative_check.json"
    rep.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report["states"], indent=1))
    print("wrote", rep)


if __name__ == "__main__":
    main()
