"""Audit a PAI output against the curation-matrix paper spec (ad-research `docs/R03-...`).

Three independent checks, all read-only, over `annotations_*{,_all}.json` and
`metadata/lead_source.parquet` of an on-disk PAI output:

1. **Composition** -- per functional scenario group, per manoeuvre and per behavioural flag,
   so the spec's section 3 / 5 percentages can be compared against what the data holds.
2. **Eval overlap** -- how much of a split sits on a route that overlaps a Bench2Drive eval
   route, counted against lead2hipad's `eval/gate_validation_lead.json` (the 69-folder
   CONTRACTS union) and against the 44-route main test. The PAI sets are deliberately exempt
   from that filter (CONTRACTS 2026-10-12), so this measures the exemption, it does not
   enforce anything.
3. **Mix feasibility** -- can a draw of N samples hit a group mix and a manoeuvre mix at the
   same time? Solved exactly as a transportation LP over the group x manoeuvre table.
   Run it against the **verified pool** (`--pool verified`, the default and the only sound
   source for a fresh dataset); `--pool curated` re-draws from an already-mixed output and is
   there only to show that doing so inherits that output's bias and can turn infeasible.

    $V/python scripts/audit_curation_matrix.py --pai-dir dataset/lead_multirig_pai_v4 \
        --gate ../lead2hipad/eval/gate_validation_lead.json \
        --eval-subset ../lead2hipad/eval/bench2drive44.xml --out docs/audit_v4.json
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

# The paper spec's own 6-way grouping of the 41 scenarios (section 2).
GROUPS: dict[str, list[str]] = {
    "A. Obstacle & Construction": ["ConstructionObstacleTwoWays", "ConstructionObstacle",
        "ParkedObstacle", "ParkedObstacleTwoWays", "VehicleOpensDoorTwoWays", "StaticCutIn"],
    "B. Junctions": ["VehicleTurningRoute", "BlockedIntersection", "PriorityAtJunction",
        "T_Junction", "SignalizedJunctionLeftTurn", "SignalizedJunctionRightTurn",
        "NonSignalizedJunctionLeftTurn", "NonSignalizedJunctionRightTurn",
        "SignalizedJunctionLeftTurnEnterFlow", "NonSignalizedJunctionLeftTurnEnterFlow"],
    "C. Hazards & Emergency": ["Accident", "AccidentTwoWays", "ControlLoss",
        "HazardAtSideLane", "HazardAtSideLaneTwoWays"],
    "D. Highway & Merging": ["HighwayExit", "HighwayCutIn", "MergerIntoSlowTraffic",
        "MergerIntoSlowTrafficV2", "ParkingCutIn", "InterurbanAdvancedActorFlow",
        "InterurbanActorFlow", "EnterActorFlow", "EnterActorFlowV2"],
    "E. VRUs & Dynamic Conflicts": ["DynamicObjectCrossing", "PedestrianCrossing",
        "VehicleTurningRoutePedestrian", "ParkingCrossingPedestrian", "CrossingBicycleFlow",
        "OppositeVehicleRunningRedLight", "OppositeVehicleTakingPriority", "InvadingTurn"],
    "F. Baseline & Signals": ["noScenarios", "RedLightWithoutLeadVehicle", "HardBreakRoute"],
}
GROUP_OF = {s: g for g, ss in GROUPS.items() for s in ss}
GROUP_NAMES = list(GROUPS)
MANEUVERS = ["STRAIGHT", "SWERVE_LEFT", "SWERVE_RIGHT", "TURN_LEFT", "TURN_RIGHT"]
FLAGS = ["stationary", "brake", "hazard"]


def verified(s: dict) -> bool:
    """`convert.curate_samples.verified`, repeated here so the audit needs no import."""
    if s["nav_maneuver"] == "STRAIGHT":
        return s.get("turn_check") != "contradicted"
    return s.get("turn_check") == "ok"


# A LEAD log name carries its route XML stem in one of three forms; the catalogue's
# `route_NNNNNN`, the 50x38 sets' `<id>_<k>`, and the older `<Town>_Scenario<N>_<k>`.
_STEM_PATTERNS = (r"_(route_\d+)_route0_", r"Rep-\d+_(\d+_\d+)_route0_",
                  r"Rep-\d+_(\w+?_Scenario\d+_\d+)_route0_")


def route_key(scenario: str, log_name: str) -> tuple[str, str] | None:
    for pat in _STEM_PATTERNS:
        m = re.search(pat, log_name)
        if m:
            return scenario, m.group(1)
    return None


def composition(ann: list[dict]) -> dict:
    n = len(ann)
    pct = lambda c: {k: round(100 * v / n, 2) for k, v in c.items()}  # noqa: E731
    groups = Counter(GROUP_OF.get(a["scenario"], f"UNGROUPED:{a['scenario']}") for a in ann)
    man = Counter(a["nav_maneuver"] for a in ann)
    lat = {d: sum(man[f"{p}_{d}"] for p in ("SWERVE", "TURN")) for d in ("LEFT", "RIGHT")}
    return {
        "n": n,
        "by_group": dict(groups), "by_group_pct": pct(groups),
        "by_maneuver": dict(man), "by_maneuver_pct": pct(man),
        "lateral_left_right_pct": [round(100 * lat["LEFT"] / n, 2),
                                   round(100 * lat["RIGHT"] / n, 2)],
        "flags": {f: sum(1 for a in ann if a.get(f)) for f in FLAGS},
        "flags_pct": {f: round(100 * sum(1 for a in ann if a.get(f)) / n, 2) for f in FLAGS},
        "scenarios_present": len({a["scenario"] for a in ann}),
    }


def eval_overlap(ann: list[dict], source: pd.DataFrame, split: str,
                 gate_path: Path, subset_path: Path | None) -> dict:
    gate = json.loads(gate_path.read_text())
    by_folder = {r["route"]: r for r in gate["routes"]}
    subset_ids = set()
    if subset_path and subset_path.exists():
        subset_ids = {r.get("id") for r in ET.parse(subset_path).getroot().iter("route")}

    gate_key = lambda p: (lambda m: (m.group(1), m.group(2)) if m else None)(  # noqa: E731
        re.search(r"/([^/]+)/([^/]+)\.xml$", p or ""))
    excluded, on_subset = {}, {}
    for folder in gate["exclusion"]["route_folders"]:
        r = by_folder.get(folder)
        if r is None:
            continue
        key = gate_key(r["route_xml"])
        if key is None:
            continue
        hits = set(r.get("driven") or {}) | set(r.get("xml") or {}) | set(r.get("rule_a_ids") or [])
        excluded.setdefault(key, set()).update(hits)
        if hits & subset_ids:
            on_subset.setdefault(key, set()).update(hits & subset_ids)

    s = source[source.split == split]
    keys = [route_key(sc, n) for sc, n in zip(s.scenario, s.lead_log)]
    unresolved_routes = sum(1 for k, _ in zip(keys, s.lead_log) if k is None)
    present = {k for k in keys if k}

    sample_keys = [route_key(a["scenario"], a["lead_log"]) for a in ann]
    n = len(ann)
    n220 = sum(1 for k in sample_keys if k in excluded)
    n44 = sum(1 for k in sample_keys if k in on_subset)
    return {
        "gate_excluded_routes": len(excluded),
        "gate_excluded_on_subset": len(on_subset),
        "routes_in_split": len(present),
        "routes_overlapping_full_eval": len(present & set(excluded)),
        "routes_overlapping_subset": len(present & set(on_subset)),
        "routes_overlapping_subset_list": sorted(present & set(on_subset)),
        "samples": n,
        "samples_overlapping_full_eval": n220,
        "samples_overlapping_full_eval_pct": round(100 * n220 / n, 2),
        "samples_overlapping_subset": n44,
        "samples_overlapping_subset_pct": round(100 * n44 / n, 2),
        "unresolved_log_names": unresolved_routes,
        "note": "lower bound: unresolved log names are counted as non-overlapping",
    }


def feasible(pool: list[dict], n: int, group_pct: dict[str, float],
             man_pct: dict[str, float]) -> dict:
    """Exact transportation feasibility: can `n` samples meet both marginals at once?"""
    from scipy.optimize import linprog

    avail = np.zeros((len(GROUP_NAMES), len(MANEUVERS)))
    for s in pool:
        g = GROUP_OF.get(s["scenario"])
        if g is not None:
            avail[GROUP_NAMES.index(g), MANEUVERS.index(s["nav_maneuver"])] += 1
    rows = np.array([group_pct[g] for g in GROUP_NAMES]) / 100 * n
    cols = np.array([man_pct[m] for m in MANEUVERS]) / 100 * n

    nv = avail.size
    a_eq, b_eq = [], []
    for i in range(len(GROUP_NAMES)):
        r = np.zeros(nv); r[i * len(MANEUVERS):(i + 1) * len(MANEUVERS)] = 1
        a_eq.append(r); b_eq.append(rows[i])
    for j in range(len(MANEUVERS)):
        r = np.zeros(nv); r[j::len(MANEUVERS)] = 1
        a_eq.append(r); b_eq.append(cols[j])
    res = linprog(np.zeros(nv), A_eq=np.array(a_eq), b_eq=np.array(b_eq),
                  bounds=[(0, v) for v in avail.flat], method="highs")

    short = {}
    for i, g in enumerate(GROUP_NAMES):
        if rows[i] > avail[i].sum():
            short[g] = [int(rows[i]), int(avail[i].sum())]
    for j, m in enumerate(MANEUVERS):
        if cols[j] > avail[:, j].sum():
            short[m] = [int(cols[j]), int(avail[:, j].sum())]
    return {"n": n, "feasible": res.status == 0, "pool": len(pool),
            "availability": {g: dict(zip(MANEUVERS, avail[i].astype(int).tolist()))
                             for i, g in enumerate(GROUP_NAMES)},
            "short_by": short}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pai-dir", type=Path, required=True)
    p.add_argument("--splits", nargs="+", default=["train", "val"])
    p.add_argument("--gate", type=Path, help="lead2hipad eval/gate_validation_lead.json")
    p.add_argument("--eval-subset", type=Path, help="eval/bench2drive44.xml")
    p.add_argument("--pool", choices=["verified", "curated"], default="verified",
                   help="feasibility source: the verified pool (sound) or a curated output")
    p.add_argument("--target-n", type=int, nargs="*", default=[1600, 6400])
    p.add_argument("--group-pct", type=float, nargs=6, metavar="PCT",
                   help="group mix A..F to test for feasibility")
    p.add_argument("--maneuver-pct", type=float, nargs=5, metavar="PCT",
                   help="manoeuvre mix in the order " + " ".join(MANEUVERS))
    p.add_argument("--out", type=Path, help="write the full report as JSON")
    args = p.parse_args()

    source = pd.read_parquet(args.pai_dir / "metadata/lead_source.parquet")
    report: dict = {"pai_dir": str(args.pai_dir),
                    "scenarios_in_source": int(source.scenario.nunique())}

    for split in args.splits:
        ann = json.loads((args.pai_dir / f"annotations_{split}.json").read_text())
        every = json.loads((args.pai_dir / f"annotations_{split}_all.json").read_text())
        pool = [s for s in every if verified(s)]
        out: dict = {"curated": composition(ann), "verified_pool": composition(pool)}

        if args.gate and args.gate.exists():
            out["eval_overlap"] = eval_overlap(ann, source, split, args.gate, args.eval_subset)

        if args.group_pct and args.maneuver_pct:
            src = pool if args.pool == "verified" else ann
            out["feasibility"] = {
                "pool_source": args.pool,
                "cells": [feasible(src, n, dict(zip(GROUP_NAMES, args.group_pct)),
                                   dict(zip(MANEUVERS, args.maneuver_pct)))
                          for n in args.target_n],
            }
        report[split] = out

        c = out["curated"]
        print(f"\n### {args.pai_dir.name} / {split}: {c['n']} curated, "
              f"{out['verified_pool']['n']} verified, {c['scenarios_present']} scenarios")
        for g in GROUP_NAMES:
            print(f"   {g:30s} {c['by_group'].get(g, 0):6d}  {c['by_group_pct'].get(g, 0):5.1f} %")
        for m in MANEUVERS:
            print(f"   {m:30s} {c['by_maneuver'].get(m, 0):6d}  {c['by_maneuver_pct'].get(m, 0):5.1f} %")
        print(f"   {'lateral L vs R':30s}        {c['lateral_left_right_pct'][0]:5.1f} % vs "
              f"{c['lateral_left_right_pct'][1]:5.1f} %")
        for f in FLAGS:
            print(f"   {f:30s} {c['flags'][f]:6d}  {c['flags_pct'][f]:5.1f} %")
        if "eval_overlap" in out:
            e = out["eval_overlap"]
            print(f"   eval overlap: {e['routes_overlapping_full_eval']}/{e['routes_in_split']} routes "
                  f"({e['samples_overlapping_full_eval']} samples, "
                  f"{e['samples_overlapping_full_eval_pct']} %) touch the full eval set; "
                  f"{e['routes_overlapping_subset']} routes / {e['samples_overlapping_subset']} samples "
                  f"({e['samples_overlapping_subset_pct']} %) touch the subset")
        if "feasibility" in out:
            for cell in out["feasibility"]["cells"]:
                tag = "FEASIBLE" if cell["feasible"] else "INFEASIBLE"
                print(f"   mix at N={cell['n']} from the {args.pool} pool "
                      f"({cell['pool']}): {tag} {cell['short_by'] or ''}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=1, default=str) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
