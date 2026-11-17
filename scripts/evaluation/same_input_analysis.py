#!/usr/bin/env python3
"""Analysis of the same-input replay (ANALYSIS_ADDENDUM section 21).

Reads outputs/same_input/<expert>.jsonl (written by same_input_replay.py) and writes
docs/provenance/same_input_results.json. Statistics are those of paper_reanalysis.py
(paired BCa interval with 20,000 resamples and seed 0, two-sided Wilcoxon signed-rank test),
with the source log (route) of the validation clips as the unit.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path("/home/aimslab/lead")
sys.path.insert(0, str(ROOT / "scripts/evaluation"))
from paper_reanalysis import paired  # noqa: E402  (importing does not run its main)

IN_DIR = ROOT / "outputs/same_input"
OUT = ROOT / "docs/provenance/same_input_results.json"
EXPERTS = ["Base", "Golden-6400", "Flooded-6400-Matched", "Balanced-6400", "Golden-1600", "Flooded-1600"]
G, F, B, BASE, G16, F16 = "Golden-6400", "Flooded-6400-Matched", "Balanced-6400", "Base", "Golden-1600", "Flooded-1600"


def load(name, suffix=""):
    p = IN_DIR / f"{name}{suffix}.jsonl"
    rows = {}
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["state"]] = r
    return rows


def state_metrics(r):
    L = np.asarray(r["L"], float)
    return {"p_stay": float(np.mean(L < 0.64)), "p_start": float(np.mean(L >= 2.0)), "p_below_1.5": float(np.mean(L < 1.5)),
            "mean_L": float(np.mean(L)), "p_ends_at_rest": float(np.mean(np.asarray(r["last_second_path"], float) < 0.5))}


def by_log(rows_a, rows_b, key, states):
    """Per source log: mean over its states of metric(a) and metric(b)."""
    logs = {}
    for s in states:
        logs.setdefault(rows_a[s]["lead_log"], []).append(s)
    a = [float(np.mean([state_metrics(rows_a[s])[key] for s in ss])) * 100 for ss in logs.values()]
    b = [float(np.mean([state_metrics(rows_b[s])[key] for s in ss])) * 100 for ss in logs.values()]
    return a, b, len(logs)


def compare(D, a, b, states, key="p_stay", scale=100.0):
    xa, xb, n_logs = by_log(D[a], D[b], key, states)
    if key == "mean_L":
        xa, xb = [v / 100 for v in xa], [v / 100 for v in xb]
    res = paired(xa, xb)
    sa = np.array([state_metrics(D[a][s])[key] for s in states]) * (scale if key != "mean_L" else 1.0)
    sb = np.array([state_metrics(D[b][s])[key] for s in states]) * (scale if key != "mean_L" else 1.0)
    d = sa - sb
    nz = int(np.sum(d != 0))
    res.update({"unit": "source log", "n_logs": n_logs, "n_states": len(states),
                "pooled_over_states": {"mean_first": float(sa.mean()), "mean_second": float(sb.mean()), "mean_diff": float(d.mean()),
                                       "states_first_greater": int(np.sum(d > 0)), "states_first_less": int(np.sum(d < 0)),
                                       "states_equal": int(np.sum(d == 0)),
                                       "sign_test_p_ignoring_clustering": float(stats.binomtest(int(np.sum(d > 0)), nz, 0.5).pvalue) if nz else None}})
    return res


def reading(c):
    lo, hi = c["bca95"]
    if hi < 0:
        return "difference negative with the interval below 0: on identical inputs the obstacle-heavy expert returns stay-put plans more often"
    if lo > 0:
        return "difference positive with the interval above 0: contrary to the closed-loop pattern"
    return "interval includes 0: a difference between the experts on identical inputs is not shown"


def main():
    D, errors = {}, {}
    for e in EXPERTS:
        rows = load(e)
        errors[e] = sorted(s for s, r in rows.items() if "error" in r)
        D[e] = {s: r for s, r in rows.items() if "error" not in r}
    common = sorted(set.intersection(*[set(D[e]) for e in EXPERTS]))
    n_all = max(len(load(e)) for e in EXPERTS)
    res = {"label": "ANALYSIS_ADDENDUM section 21; rule fixed before any inference of this analysis was run",
           "n_states_selected": n_all, "n_states_usable_for_all_experts": len(common),
           "states_with_error": {e: len(v) for e, v in errors.items()},
           "k_plans_per_state": sorted({D[e][s]["n_plans"] for e in EXPERTS for s in common}),
           "n_source_logs": len({D[G][s]["lead_log"] for s in common}), "n_clips": len({D[G][s]["clip_id"] for s in common})}
    gt = np.array([D[G][s]["future_path_m"] for s in common])
    sp = np.array([D[G][s]["speed_mps"] for s in common])
    res["demonstrated_future"] = {"stays_put_n": int(np.sum(gt < 0.64)), "starts_n": int(np.sum(gt >= 2.0)),
                                  "between_n": int(np.sum((gt >= 0.64) & (gt < 2.0))), "stays_put_pct": float(np.mean(gt < 0.64) * 100)}
    # check of the common-random-number set-up: was the backbone output (rationale text) the same for the experts?
    same = {}
    for e in EXPERTS[1:]:
        same[f"{e} vs Base"] = float(np.mean([D[e][s].get("cot") == D[BASE][s].get("cot") for s in common]) * 100)
    same[f"{G} vs {F}"] = float(np.mean([D[G][s].get("cot") == D[F][s].get("cot") for s in common]) * 100)
    res["states_with_identical_rationale_texts_pct"] = same
    res["distinct_rationale_texts_per_state_mean"] = float(np.mean([len(set(D[G][s].get("cot") or [])) for s in common]))

    res["pooled_means_pct"] = {e: {k: float(np.mean([state_metrics(D[e][s])[k] for s in common]) * (1 if k == "mean_L" else 100))
                                   for k in ("p_stay", "p_start", "p_below_1.5", "p_ends_at_rest", "mean_L")} for e in EXPERTS}
    res["per_log_means_pct"] = {}
    for e in EXPERTS:
        xa, _, _ = by_log(D[e], D[e], "p_stay", common)
        res["per_log_means_pct"][e] = {"p_stay": float(np.mean(xa))}

    prim = compare(D, G, F, common)
    prim["reading"] = reading(prim)
    res["SI-1 primary: p_stay, Golden-6400 minus Flooded-6400-Matched"] = prim

    sec = {}
    pairs = [(B, F), (B, G), (BASE, G), (BASE, F), (BASE, B), (G16, F16), (BASE, G16), (BASE, F16)]
    for a, b in pairs:
        sec[f"p_stay, {a} minus {b}"] = compare(D, a, b, common)
    rest = [s for s in common if D[G][s]["speed_mps"] < 0.1]
    sec["p_stay, Golden-6400 minus Flooded-6400-Matched, states with speed below 0.1 m/s"] = compare(D, G, F, rest)
    for key in ("p_start", "p_below_1.5", "p_ends_at_rest", "mean_L"):
        sec[f"{key}, Golden-6400 minus Flooded-6400-Matched"] = compare(D, G, F, common, key)
    res["secondary"] = sec

    cls = {"stays_put": [s for s in common if D[G][s]["future_path_m"] < 0.64],
           "starts": [s for s in common if D[G][s]["future_path_m"] >= 2.0],
           "between": [s for s in common if 0.64 <= D[G][s]["future_path_m"] < 2.0]}
    res["p_stay_pct_by_class_of_demonstrated_future"] = {
        c: {"n_states": len(ss), **{e: float(np.mean([state_metrics(D[e][s])["p_stay"] for s in ss]) * 100) if ss else None for e in EXPERTS}}
        for c, ss in cls.items()}
    res["p_start_pct_by_class_of_demonstrated_future"] = {
        c: {"n_states": len(ss), **{e: float(np.mean([state_metrics(D[e][s])["p_start"] for s in ss]) * 100) if ss else None for e in EXPERTS}}
        for c, ss in cls.items()}
    res["states_with_any_stay_put_plan"] = {e: int(sum(state_metrics(D[e][s])["p_stay"] > 0 for s in common)) for e in EXPERTS}
    res["speed_of_states"] = {"n_below_0.1": int(np.sum(sp < 0.1)), "n_0.1_to_0.5": int(np.sum(sp >= 0.1))}

    # reset check: every expert repeats its first states at the end of its process with the same seeds; state 0 was the
    # first state of the fresh process, so agreement shows that the per-state stream reset reproduces a fresh stream
    res["reset_check"] = {}
    for e in EXPERTS:
        try:
            chk = load(e, ".resetcheck")
        except FileNotFoundError:
            res["reset_check"][e] = "not run"
            continue
        ss = [s for s in chk if s in D[e] and "error" not in chk[s]]
        diffs = [float(np.max(np.abs(np.asarray(chk[s]["L"]) - np.asarray(D[e][s]["L"])))) for s in ss]
        res["reset_check"][e] = {"n_states": len(ss), "max_abs_difference_of_L_m": max(diffs) if diffs else None,
                                 "difference_of_L_state_0_m": diffs[0] if 0 in ss and diffs else None,
                                 "identical_rationale_texts": bool(all(chk[s].get("cot") == D[e][s].get("cot") for s in ss)),
                                 "stay_put_plans_first_run": [int(np.sum(np.asarray(D[e][s]["L"]) < 0.64)) for s in ss],
                                 "stay_put_plans_repeat": [int(np.sum(np.asarray(chk[s]["L"]) < 0.64)) for s in ss]}
    res["seconds_per_state_median"] = float(np.median([D[G][s]["seconds"] for s in common]))

    # control of ANALYSIS_ADDENDUM section 23: the expert of the base model loaded through the patch step
    CTRL = "Base-SelfPatch"
    if (IN_DIR / f"{CTRL}.jsonl").exists():
        rows = load(CTRL)
        D[CTRL] = {s: r for s, r in rows.items() if "error" not in r}
        cs = [s for s in common if s in D[CTRL]]
        maxd = [float(np.max(np.abs(np.asarray(D[CTRL][s]["L"]) - np.asarray(D[BASE][s]["L"])))) for s in cs]
        ctrl = {"label": "ANALYSIS_ADDENDUM section 23; reading fixed before the control was run",
                "n_states": len(cs), "states_with_error": len(rows) - len(D[CTRL]),
                "states_with_identical_rationale_text_pct": {f"{CTRL} vs {e}": float(np.mean([D[CTRL][s].get("cot") == D[e][s].get("cot") for s in cs]) * 100) for e in EXPERTS},
                "states_with_identical_rationale_text_n": {f"{CTRL} vs {e}": int(sum(D[CTRL][s].get("cot") == D[e][s].get("cot") for s in cs)) for e in EXPERTS},
                "states_with_identical_plans_vs_Base_n": int(sum(d == 0.0 for d in maxd)),
                "states_with_plans_within_1cm_of_Base_n": int(sum(d < 0.01 for d in maxd)),
                "max_abs_difference_of_L_vs_Base_m": float(max(maxd)), "median_abs_max_difference_of_L_vs_Base_m": float(np.median(maxd)),
                "pooled_means_pct": {k: float(np.mean([state_metrics(D[CTRL][s])[k] for s in cs]) * (1 if k == "mean_L" else 100))
                                     for k in ("p_stay", "p_start", "p_below_1.5", "p_ends_at_rest", "mean_L")},
                "comparisons": {f"p_stay, {CTRL} minus {e}": compare(D, CTRL, e, cs) for e in EXPERTS}}
        same_text = [s for s in cs if D[CTRL][s].get("cot") == D[BASE][s].get("cot")]
        ctrl["states_with_identical_text_vs_Base"] = {"n": len(same_text), "identical_plans_n": int(sum(maxd[cs.index(s)] == 0.0 for s in same_text))}
        res["control_base_selfpatch"] = ctrl
        print("CONTROL", json.dumps({k: v for k, v in ctrl.items() if k != "comparisons"}, indent=1))
        for k, v in ctrl["comparisons"].items():
            print(f"{k}: {v['mean_first']:.2f} vs {v['mean_second']:.2f}, diff {v['mean_diff']:.2f}, CI {[round(x, 2) for x in v['bca95']] if isinstance(v['bca95'], list) else v['bca95']}, p {v['wilcoxon'].get('p')}")
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "secondary"}, indent=1)[:6000])
    for k, v in sec.items():
        print(f"{k}: {v['mean_first']:.2f} vs {v['mean_second']:.2f}, diff {v['mean_diff']:.2f}, CI {[round(x, 2) for x in v['bca95']] if isinstance(v['bca95'], list) else v['bca95']}, "
              f"p {v['wilcoxon'].get('p')}, logs {v['n_logs']}, states {v['n_states']}")


if __name__ == "__main__":
    main()
