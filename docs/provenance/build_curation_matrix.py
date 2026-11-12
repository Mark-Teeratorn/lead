"""Build the four curation-matrix cells (ad-research T19) from v4's verified train pool.

The 2x2 of the Alpamayo data user's paper spec: scale (1,600 / 6,400) x regime (Hazard-Flooded
/ Golden Ratio). Four annotation sets drawn from one pool by one code path, so scale and regime
are the only things that vary. **This is a draw over `annotations_train_all.json`, not a
conversion**: no GPU, no CARLA, no reconversion, and the 67 GB `camera/` tree is referenced
rather than copied. `lead2pai` and `convert.curate_samples` are untouched, so v3 and v4 keep
reproducing byte-identically.

Three stages, each runnable on its own:

``--stage allocate``
    How many samples each group x manoeuvre bucket contributes. The marginals (group shares,
    manoeuvre shares) leave a large feasible set and most of it is scientifically wrong -- a
    plain LP happily returns Flooded group A with no STRAIGHT at all while Golden group A is
    all STRAIGHT, which would let "regime" rewrite each group's internal manoeuvre mix in ways
    the 2x2 never specifies. So the allocation is pinned to the **minimum-divergence** point:
    iterative proportional fitting (RAS) of the availability matrix onto the required
    marginals, i.e. the allocation closest in KL to the pool's own group x manoeuvre
    association, then integerised to the nearest feasible point with every bucket divisible by
    4 so the nesting is exact. Compared against `--allocation` if one is given.

``--stage draw``
    Picks the samples. Within a bucket, `convert._round_robin_by_clip` spreads the draw over as
    many clips as possible instead of taking whole clips' worth of adjacent t0. The 6,400 cell
    is drawn first and each 1,600 cell is the per-bucket first quarter of it, so
    `set(1600) < set(6400)` holds exactly.

``--stage build``
    Writes the four cell directories. Big read-only trees (`camera/`, `labels/`,
    `calibration/`, `metadata/`) are symlinked to the source; the small generated files are
    real copies, because `write_index`-style writers truncate in place and the published sets
    must never be reachable through one of these cells.

Determinism is a done-criterion, not a nicety: selection is by SHA-1 order of clip id and
sample key with **no RNG anywhere**, so a rebuild is byte-identical. `--seed` is recorded in
`conversion_stats.json` and salts that hash, so the seed is a real knob rather than a label.

    $V/python scripts/build_curation_matrix.py --stage allocate \
        --pai-dir dataset/lead_multirig_pai_v4 --allocation ../ad-research/docs/R03-matrix-allocation.json
    $V/python scripts/build_curation_matrix.py --stage build \
        --pai-dir dataset/lead_multirig_pai_v4 --out-root dataset/lead_matrix \
        --gate ../lead2hipad/eval/gate_validation_lead.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_curation_matrix import (  # noqa: E402
    FLAGS, GROUP_NAMES, GROUP_OF, MANEUVERS, composition, eval_overlap, route_key, verified,
)

# Group shares are the spec's section 3. Manoeuvre shares are its section 5A with the junction
# turns equalised (Flooded 14 %/15 % -> 14.5 %/14.5 %): 1:1 junction turns are a standing
# decision (ad-research DECISIONS 2026-10-04) and v3/v4's measured turns are exactly equal, so
# 14/15 is a rounding artefact rather than a treatment. The lateral treatment that the paper is
# actually about -- SWERVE_LEFT 37 % against SWERVE_RIGHT 12 % -- is preserved in full.
#
# `stationary_pct` is the spec's section 5B, the third stated difference between the regimes
# ("5x reduction: eliminates hesitation and standstill freezing"). It is applied as a
# **within-bucket preference**, so it moves no group or manoeuvre marginal. `brake` and
# `hazard` are the other two rows of 5B and are deliberately *not* targets: they are observed
# outcomes of the draw and forcing them would make them uninterpretable.
#
# `floodedgroups_balanced` is the decoupling cell (T19 step 2c): Flooded's group mix with
# Golden's manoeuvre mix and stationary share, at N = 6,400 only. Against Flooded-6400 it holds
# the group mix fixed and varies the lateral balance; against Golden-6400 it holds the lateral
# balance fixed and varies the group mix. It is optional — nothing in the other four depends
# on it — and it separates group mix from the *lateral + stationary* bundle, not lateral from
# stationary, which would need a sixth cell.
TARGETS = {
    "flooded": {"groups": [35.0, 14.0, 22.0, 10.0, 9.0, 10.0],
                "maneuvers": [22.0, 37.0, 12.0, 14.5, 14.5],
                "stationary_pct": 10.0, "scales": [6400, 1600]},
    "golden": {"groups": [27.0, 18.0, 17.0, 14.0, 14.0, 10.0],
               "maneuvers": [50.0, 13.0, 13.0, 12.0, 12.0],
               "stationary_pct": 2.0, "scales": [6400, 1600]},
    "floodedgroups_balanced": {"groups": [35.0, 14.0, 22.0, 10.0, 9.0, 10.0],
                               "maneuvers": [50.0, 13.0, 13.0, 12.0, 12.0],
                               "stationary_pct": 2.0, "scales": [6400]},
}
SCALES = [6400, 1600]
NEST = 4  # every bucket divisible by this, so the 1,600 cell is an exact quarter of the 6,400

# A junction right turn is not a swerve and a hazard bypass is not a junction left turn: these
# two cells are empty by construction, not by sampling. A solver must never borrow across them.
STRUCTURAL_ZEROS = [("B. Junctions", "SWERVE_RIGHT"), ("C. Hazards & Emergency", "TURN_LEFT")]


def availability(pool: list[dict]) -> np.ndarray:
    a = np.zeros((len(GROUP_NAMES), len(MANEUVERS)), dtype=np.int64)
    for s in pool:
        g = GROUP_OF.get(s["scenario"])
        if g is not None:
            a[GROUP_NAMES.index(g), MANEUVERS.index(s["nav_maneuver"])] += 1
    return a


def ipf(avail: np.ndarray, rows: np.ndarray, cols: np.ndarray,
        iters: int = 10_000, tol: float = 1e-10) -> np.ndarray:
    """RAS: scale `avail` to the given marginals. Zeros stay zero (scaling is multiplicative)."""
    x = avail.astype(float).copy()
    for _ in range(iters):
        rs = x.sum(1, keepdims=True)
        x *= np.where(rs > 0, rows[:, None] / np.where(rs > 0, rs, 1), 0.0)
        cs = x.sum(0, keepdims=True)
        x *= np.where(cs > 0, cols[None, :] / np.where(cs > 0, cs, 1), 0.0)
        if (abs(x.sum(1) - rows).max() < tol) and (abs(x.sum(0) - cols).max() < tol):
            break
    return x


def integerise(ideal: np.ndarray, rows: np.ndarray, cols: np.ndarray,
               avail: np.ndarray, divisor: int = NEST) -> np.ndarray:
    """Nearest integer point to `ideal` with exact marginals, capacity and divisibility.

    Solved in units of `divisor` as a min-L1 transportation MILP, so the result is the closest
    feasible allocation rather than whatever a rounding heuristic happens to land on.
    """
    from scipy.optimize import LinearConstraint, milp

    assert rows.sum() == cols.sum()
    for v in (rows, cols):
        assert np.all(v % divisor == 0), f"marginal not divisible by {divisor}: {v}"
    n_g, n_m = ideal.shape
    z = ideal / divisor
    cap = avail // divisor
    nv = n_g * n_m

    # variables: y (nv, integer) then d (nv, continuous) with d >= |y - z|
    a_eq, b_eq = [], []
    for i in range(n_g):
        r = np.zeros(2 * nv); r[i * n_m:(i + 1) * n_m] = 1
        a_eq.append(r); b_eq.append(rows[i] / divisor)
    for j in range(n_m):
        r = np.zeros(2 * nv); r[j:nv:n_m] = 1
        a_eq.append(r); b_eq.append(cols[j] / divisor)
    cons = [LinearConstraint(np.array(a_eq), b_eq, b_eq)]

    a_ub, b_ub = [], []
    for k in range(nv):
        r = np.zeros(2 * nv); r[k] = 1; r[nv + k] = -1
        a_ub.append(r); b_ub.append(z.flat[k])          # y - d <= z
        r = np.zeros(2 * nv); r[k] = -1; r[nv + k] = -1
        a_ub.append(r); b_ub.append(-z.flat[k])         # -y - d <= -z
    cons.append(LinearConstraint(np.array(a_ub), -np.inf, b_ub))

    lb = np.zeros(2 * nv)
    ub = np.concatenate([cap.astype(float).ravel(), np.full(nv, np.inf)])
    integrality = np.concatenate([np.ones(nv), np.zeros(nv)])
    cost = np.concatenate([np.zeros(nv), np.ones(nv)])
    res = milp(c=cost, constraints=cons, integrality=integrality,
               bounds=__import__("scipy.optimize", fromlist=["Bounds"]).Bounds(lb, ub))
    if not res.success:
        raise SystemExit(f"integerisation infeasible: {res.message}")
    return (np.round(res.x[:nv]).astype(np.int64) * divisor).reshape(n_g, n_m)


def check_matrix(m: np.ndarray, avail: np.ndarray, rows: np.ndarray, cols: np.ndarray,
                 n: int, label: str, divisible: bool = True) -> None:
    assert m.sum() == n, f"{label}: total {m.sum()} != {n}"
    assert (m.sum(1) == rows).all(), f"{label}: row sums {m.sum(1)} != {rows}"
    assert (m.sum(0) == cols).all(), f"{label}: col sums {m.sum(0)} != {cols}"
    assert (m <= avail).all(), f"{label}: over availability at {np.argwhere(m > avail).tolist()}"
    assert (m >= 0).all(), f"{label}: negative bucket"
    # Only the big cell carries the divisibility: the small one is its exact quarter, so its
    # own buckets are whatever that quarter comes to.
    if divisible:
        assert (m % NEST == 0).all(), f"{label}: a bucket is not divisible by {NEST}"
    for g, mv in STRUCTURAL_ZEROS:
        assert m[GROUP_NAMES.index(g), MANEUVERS.index(mv)] == 0, \
            f"{label}: structural zero {g}/{mv} was filled"


def stationary_split(alloc: np.ndarray, still: np.ndarray, moving: np.ndarray,
                     target: int, divisor: int, label: str) -> np.ndarray:
    """How many of each bucket's samples are stationary, as close to the pool's own shape as
    the target allows.

    A bucket must take at least `alloc - moving` stationary samples (when moving ones cannot
    fill it) and at most `min(alloc, still)`. Within that box the split is the min-L1 integer
    point to the ideal that spreads the quota in proportion to each bucket's own stationary
    stock — the same minimum-divergence rule as the group x manoeuvre allocation, so the
    treatment does not quietly reshape which scenarios the stopped frames come from.
    """
    from scipy.optimize import Bounds, LinearConstraint, milp

    lower = np.maximum(0, alloc - moving)
    upper = np.minimum(alloc, still)
    assert lower.sum() <= target <= upper.sum(), (
        f"{label}: stationary target {target} outside [{lower.sum()}, {upper.sum()}]")
    assert target % divisor == 0, f"{label}: stationary target {target} not divisible by {divisor}"

    lo_u = np.ceil(lower / divisor).astype(np.int64)
    hi_u = np.floor(upper / divisor).astype(np.int64)
    if (lo_u > hi_u).any():
        bad = [(GROUP_NAMES[i], MANEUVERS[j], int(lower[i, j]), int(upper[i, j]))
               for i, j in np.argwhere(lo_u > hi_u)]
        raise SystemExit(f"{label}: no multiple of {divisor} fits a bucket's bounds: {bad}")
    if lo_u.sum() > target // divisor or hi_u.sum() < target // divisor:
        raise SystemExit(f"{label}: divisible-by-{divisor} stationary split infeasible "
                         f"({lo_u.sum() * divisor}..{hi_u.sum() * divisor} vs {target})")

    weight = still * (alloc > 0)
    ideal = (weight / weight.sum() * target / divisor) if weight.sum() else np.zeros_like(alloc, float)
    nv = alloc.size
    cons = [LinearConstraint(np.concatenate([np.ones(nv), np.zeros(nv)])[None, :],
                             target // divisor, target // divisor)]
    a_ub, b_ub = [], []
    for k in range(nv):
        r = np.zeros(2 * nv); r[k] = 1; r[nv + k] = -1
        a_ub.append(r); b_ub.append(ideal.flat[k])
        r = np.zeros(2 * nv); r[k] = -1; r[nv + k] = -1
        a_ub.append(r); b_ub.append(-ideal.flat[k])
    cons.append(LinearConstraint(np.array(a_ub), -np.inf, b_ub))
    res = milp(c=np.concatenate([np.zeros(nv), np.ones(nv)]), constraints=cons,
               integrality=np.concatenate([np.ones(nv), np.zeros(nv)]),
               bounds=Bounds(np.concatenate([lo_u.ravel().astype(float), np.zeros(nv)]),
                             np.concatenate([hi_u.ravel().astype(float), np.full(nv, np.inf)])))
    if not res.success:
        raise SystemExit(f"{label}: stationary split infeasible: {res.message}")
    s = (np.round(res.x[:nv]).astype(np.int64) * divisor).reshape(alloc.shape)
    assert s.sum() == target and (s >= lower).all() and (s <= upper).all(), label
    return s


def allocate(avail: np.ndarray, still: np.ndarray | None = None) -> dict[str, dict]:
    out: dict[str, dict] = {}
    moving = None if still is None else avail - still
    for regime, t in TARGETS.items():
        big = t["scales"][0]
        rows = np.array([p / 100 * big for p in t["groups"]])
        cols = np.array([p / 100 * big for p in t["maneuvers"]])
        assert abs(rows.sum() - big) < 1e-6 and abs(cols.sum() - big) < 1e-6, regime
        rows, cols = np.round(rows).astype(np.int64), np.round(cols).astype(np.int64)
        m = integerise(ipf(avail, rows.astype(float), cols.astype(float)), rows, cols, avail)
        check_matrix(m, avail, rows, cols, big, f"{regime}/{big}")
        cell: dict = {f"n{big}": m}
        nested = len(t["scales"]) > 1
        if nested:
            ratio = big // t["scales"][1]
            small = m // ratio
            check_matrix(small, avail, small.sum(1), small.sum(0), t["scales"][1],
                         f"{regime}/{t['scales'][1]}", divisible=False)
            assert (small * ratio == m).all(), f"{regime}: the quarter is not exact"
            cell[f"n{t['scales'][1]}"] = small
        if still is not None:
            # Divisible by 4 only where a nested cell has to take an exact quarter of it.
            target = int(round(t["stationary_pct"] / 100 * big))
            cell["stationary"] = stationary_split(m, still, moving, target,
                                                  NEST if nested else 1, f"{regime}/{big}")
        out[regime] = cell
    return out


def _salted_order(rows: list[dict], seed: int) -> list[dict]:
    key = lambda s: hashlib.sha1(  # noqa: E731
        f"{seed}|{s['clip_id']}|{s['t0_relative']}".encode()).digest()
    return sorted(rows, key=key)


def round_robin_by_clip(rows: list[dict], n: int, seed: int) -> list[dict]:
    """`convert._round_robin_by_clip`, with the seed salting both hash orders.

    Spreads the draw over as many clips as possible: truncating a flat hash order keeps whole
    clips' worth of adjacent t0 instead of covering scenes (v3 kept 1,398 straight samples from
    635 clips although 887 clips held one). A prefix of the result is itself clip-spread, which
    is what makes the nested 1,600 cell valid.
    """
    if n <= 0:
        return []
    by: dict[str, list[dict]] = {}
    for s in _salted_order(rows, seed):
        by.setdefault(s["clip_id"], []).append(s)
    clips = sorted(by, key=lambda c: hashlib.sha1(f"{seed}|{c}".encode()).digest())
    out: list[dict] = []
    for i in range(max(len(v) for v in by.values())):
        for c in clips:
            if i < len(by[c]):
                out.append(by[c][i])
                if len(out) == n:
                    return out
    return out


def draw(pool: list[dict], cell: dict, scales: list[int], seed: int) -> dict[str, list[dict]]:
    """Draw the big cell bucket by bucket, then take the small cell as its per-bucket prefix.

    Each bucket is drawn in two halves, stationary and moving, so the stationary target is met
    without touching any marginal. Both halves are clip round-robins and a prefix of one is
    still clip-spread, which is what makes the nested quarter valid.
    """
    big_n = scales[0]
    big, small = f"n{big_n}", f"n{scales[1]}" if len(scales) > 1 else None
    ratio = big_n // scales[1] if small else None
    buckets: dict[tuple[int, int], list[dict]] = {}
    for s in pool:
        g = GROUP_OF.get(s["scenario"])
        if g is not None:
            buckets.setdefault((GROUP_NAMES.index(g), MANEUVERS.index(s["nav_maneuver"])), []).append(s)

    picked: dict[str, list[dict]] = {big: []} | ({small: []} if small else {})
    for (i, j), rows in sorted(buckets.items()):
        want = int(cell[big][i, j])
        if want == 0:
            continue
        n_still = int(cell["stationary"][i, j]) if "stationary" in cell else 0
        parts = ((n_still, [s for s in rows if s.get("stationary")]),
                 (want - n_still, [s for s in rows if not s.get("stationary")]))
        for n, src in parts:
            if n == 0:
                continue
            got = round_robin_by_clip(src, n, seed)
            assert len(got) == n, (
                f"bucket {GROUP_NAMES[i]}/{MANEUVERS[j]}: wanted {n}, got {len(got)}")
            picked[big].extend(got)
            if small:
                assert n % ratio == 0, (
                    f"bucket {GROUP_NAMES[i]}/{MANEUVERS[j]}: {n} is not divisible by {ratio}, "
                    "so the nested cell cannot take an exact share")
                picked[small].extend(got[: n // ratio])
    for k in picked:
        picked[k].sort(key=lambda s: (s["clip_id"], s["t0_relative"]))
    return picked


def sample_id(s: dict) -> tuple[str, int]:
    return s["clip_id"], s["t0_relative"]


def clean_val(pai_dir: Path, gate: Path, subset: Path | None) -> tuple[list[dict], dict]:
    """v4's curated val minus every sample on a route the (c') union flags.

    A deliberate, narrow departure from the PAI eval-overlap exemption (ad-research T19 step 3,
    manager's call): the exemption exists so the published v3/v4 stay byte-reproducible, and
    these are fresh builds with nothing to reproduce. There is no reason to monitor -- or to
    read `minADE` off -- a split that contains eval routes. The **train** splits keep the
    exemption and each cell reports its own overlap count.
    """
    import pandas as pd

    ann = json.loads((pai_dir / "annotations_val.json").read_text())
    source = pd.read_parquet(pai_dir / "metadata/lead_source.parquet")
    before = eval_overlap(ann, source, "val", gate, subset)

    gate_json = json.loads(gate.read_text())
    by_folder = {r["route"]: r for r in gate_json["routes"]}
    import re
    flagged = set()
    for folder in gate_json["exclusion"]["route_folders"]:
        r = by_folder.get(folder)
        m = re.search(r"/([^/]+)/([^/]+)\.xml$", (r or {}).get("route_xml") or "")
        if m:
            flagged.add((m.group(1), m.group(2)))
    kept = [s for s in ann if route_key(s["scenario"], s["lead_log"]) not in flagged]
    after = eval_overlap(kept, source, "val", gate, subset)
    return kept, {"before": len(ann), "after": len(kept), "dropped": len(ann) - len(kept),
                  "overlap_before": before, "overlap_after": after}


def write_cell(out_dir: Path, src: Path, train: list[dict], val: list[dict], meta: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("camera", "labels", "calibration", "metadata"):
        link = out_dir / name
        if link.is_symlink():
            link.unlink()
        if not link.exists():
            link.symlink_to((src / name).resolve())
    for name in ("clip_index.parquet", "features.csv"):
        shutil.copy2(src / name, out_dir / name)

    (out_dir / "annotations_train.json").write_text(json.dumps(train, indent=1) + "\n")
    (out_dir / "annotations_val.json").write_text(json.dumps(val, indent=1) + "\n")
    for split, rows in (("train", train), ("val", val)):
        ids = sorted({s["clip_id"] for s in rows})
        (out_dir / f"clip_ids_{split}.txt").write_text("\n".join(ids) + "\n")
    (out_dir / "conversion_stats.json").write_text(json.dumps(meta, indent=1) + "\n")


def check_cells(root: Path, pool: list[dict], alloc: dict[str, dict]) -> None:
    """Re-verify cells on disk against the pool they claim to come from.

    Independent of how they were drawn, so it catches a build that silently used the wrong
    source. The pool-membership check is the one that matters: a cell drawn from the *raw*
    annotations instead of the `verified()` ones looks perfectly well-formed -- right marginals,
    right totals, structural zeros intact -- and is wrong, which is exactly how the first
    availability table for this task went unnoticed.
    """
    ids = {sample_id(s) for s in pool}
    vals: dict[str, str] = {}
    nested: dict[str, set] = {}
    bad = 0
    for d in sorted(root.iterdir()):
        stats = d / "conversion_stats.json"
        if not stats.exists():
            continue
        meta = json.loads(stats.read_text())
        rows = json.loads((d / "annotations_train.json").read_text())
        got = {sample_id(s) for s in rows}
        want = np.array(meta["allocation"], dtype=np.int64)
        m = availability(rows)
        still = sum(1 for s in rows if s.get("stationary"))
        target_still = meta["targets"]["stationary_pct"] / 100 * meta["n"]
        problems = []
        if len(got) != len(rows):
            problems.append(f"{len(rows) - len(got)} duplicate samples")
        if not got <= ids:
            problems.append(f"{len(got - ids)} samples outside the verified pool")
        if not (m == want).all():
            problems.append(f"allocation drifted, L1 {abs(m - want).sum()}")
        if still != target_still:
            problems.append(f"stationary {still} != {target_still:.0f}")
        for g, mv in STRUCTURAL_ZEROS:
            if m[GROUP_NAMES.index(g), MANEUVERS.index(mv)]:
                problems.append(f"structural zero {g}/{mv} filled")
        vals[d.name] = hashlib.sha256((d / "annotations_val.json").read_bytes()).hexdigest()[:16]
        nested.setdefault(meta["regime"], set())
        parent_path = root / (meta.get("nested_in") or "") / "annotations_train.json"
        if meta.get("nested_in") and not parent_path.exists():
            problems.append(f"nesting unchecked: {meta['nested_in']} is not in {root}")
        elif meta.get("nested_in"):
            parent = json.loads(parent_path.read_text())
            if not got < {sample_id(s) for s in parent}:
                problems.append(f"not nested in {meta['nested_in']}")
        print(f"{d.name:52s} {'OK' if not problems else 'FAIL: ' + '; '.join(problems)}")
        bad += bool(problems)
    if len(set(vals.values())) > 1:
        print(f"FAIL: the val split differs between cells: {vals}")
        bad += 1
    else:
        print(f"shared val identical across {len(vals)} cells ({next(iter(vals.values()))})")
    raise SystemExit(1 if bad else 0)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pai-dir", type=Path, required=True, help="source PAI set (v4)")
    p.add_argument("--out-root", type=Path, help="parent dir for the four cells")
    p.add_argument("--stage", choices=["allocate", "draw", "build", "check"], default="build")
    p.add_argument("--allocation", type=Path, help="allocation JSON to check against")
    p.add_argument("--gate", type=Path, help="lead2hipad eval/gate_validation_lead.json")
    p.add_argument("--eval-subset", type=Path)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--unverified-pool", action="store_true",
                   help="skip the verified() filter (diagnostic only; not a valid source)")
    p.add_argument("--out", type=Path, help="write the allocation/report JSON here")
    args = p.parse_args()

    every = json.loads((args.pai_dir / "annotations_train_all.json").read_text())
    pool = every if args.unverified_pool else [s for s in every if verified(s)]
    avail = availability(pool)
    print(f"pool: {len(pool)} samples, {len({s['scenario'] for s in pool})} scenarios "
          f"({'UNVERIFIED' if args.unverified_pool else 'verified'})")
    print(f"{'':30s}" + "".join(f"{m[:9]:>10s}" for m in MANEUVERS) + f"{'total':>9s}")
    for i, g in enumerate(GROUP_NAMES):
        print(f"{g:30s}" + "".join(f"{avail[i, j]:10d}" for j in range(len(MANEUVERS)))
              + f"{avail[i].sum():9d}")
    print(f"{'total':30s}" + "".join(f"{avail[:, j].sum():10d}" for j in range(len(MANEUVERS)))
          + f"{avail.sum():9d}")

    still = availability([s for s in pool if s.get("stationary")])
    alloc = allocate(avail, still)

    if args.stage == "check":
        if not args.out_root:
            raise SystemExit("--stage check needs --out-root")
        check_cells(args.out_root, pool, alloc)
        return
    report: dict = {"pool": len(pool), "seed": args.seed,
                    "availability": avail.tolist(),
                    "availability_stationary": still.tolist(),
                    "allocation": {r: {k: (v.tolist() if hasattr(v, "tolist") else v)
                                       for k, v in d.items()} for r, d in alloc.items()}}

    if args.allocation and args.allocation.exists():
        ref = json.loads(args.allocation.read_text())
        diffs = []
        if "availability" in ref and not (np.array(ref["availability"]) == avail).all():
            diffs.append({"cell": "availability", "l1": int(abs(np.array(ref["availability"]) - avail).sum())})
        for regime, cells in alloc.items():
            for key, m in cells.items():
                if key == "stationary" or key not in ref.get(regime, {}):
                    continue
                want = np.array(ref[regime][key], dtype=np.int64)
                if not (want == m).all():
                    diffs.append({"cell": f"{regime}/{key}", "delta": (m - want).tolist(),
                                  "l1": int(abs(m - want).sum())})
        report["allocation_matches_reference"] = not diffs
        report["allocation_diff"] = diffs
        print("\nallocation vs reference: " + ("MATCH" if not diffs else
              "DIFFERS — " + ", ".join(f"{d['cell']} L1={d['l1']}" for d in diffs)))

    if args.stage == "allocate":
        if args.out:
            args.out.write_text(json.dumps(report, indent=1) + "\n")
            print(f"wrote {args.out}")
        return

    picked = {r: draw(pool, cells, TARGETS[r]["scales"], args.seed) for r, cells in alloc.items()}
    for regime, cells in picked.items():
        scales = TARGETS[regime]["scales"]
        print(f"\n{regime}" + ("  [optional decoupling cell]" if len(scales) == 1 else ""))
        if len(scales) > 1:
            big = set(map(sample_id, cells[f"n{scales[0]}"]))
            small = set(map(sample_id, cells[f"n{scales[1]}"]))
            assert len(big) == scales[0] and len(small) == scales[1], f"{regime}: duplicate samples"
            assert small < big, f"{regime}: the {scales[1]} cell is not nested in the {scales[0]} cell"
            print(f"   nested OK ({len(small)} \u2282 {len(big)})")
        for n in scales:
            rows = cells[f"n{n}"]
            per_clip: dict[str, int] = {}
            for s in rows:
                per_clip[s["clip_id"]] = per_clip.get(s["clip_id"], 0) + 1
            c = composition(rows)
            print(f"   N={n}: {len(per_clip)} clips, max {max(per_clip.values())}/clip; groups "
                  + "/".join(f"{c['by_group_pct'].get(g, 0):.1f}" for g in GROUP_NAMES)
                  + "; manoeuvres "
                  + "/".join(f"{c['by_maneuver_pct'].get(m, 0):.1f}" for m in MANEUVERS)
                  + f"; stationary {c['flags_pct']['stationary']:.2f} % "
                  f"(target {TARGETS[regime]['stationary_pct']}); "
                  f"brake {c['flags_pct']['brake']:.1f} %, hazard {c['flags_pct']['hazard']:.1f} % (observed)")

    if args.stage == "draw":
        if args.out:
            args.out.write_text(json.dumps(report, indent=1) + "\n")
        return

    if not args.out_root or not args.gate:
        raise SystemExit("--stage build needs --out-root and --gate")
    val, val_stats = clean_val(args.pai_dir, args.gate, args.eval_subset)
    print(f"\nshared val: {val_stats['before']} -> {val_stats['after']} "
          f"({val_stats['dropped']} dropped as (c')-flagged); "
          f"overlap after: {val_stats['overlap_after']['samples_overlapping_full_eval']} samples")
    report["val"] = val_stats

    import pandas as pd
    source = pd.read_parquet(args.pai_dir / "metadata/lead_source.parquet")
    report["cells"] = {}
    # The optional decoupling cell is built last, so a veto of it leaves 1-4 untouched.
    for regime in sorted(picked, key=lambda r: len(TARGETS[r]["scales"]) == 1):
        cells, scales = picked[regime], TARGETS[regime]["scales"]
        for n in scales:
            rows = cells[f"n{n}"]
            name = f"lead-alpamayo-pai_matrix_{regime}_{n}"
            overlap = eval_overlap(rows, source, "train", args.gate, args.eval_subset)
            optional = len(scales) == 1
            meta = {
                "cell": name, "regime": regime, "n": n, "seed": args.seed,
                "optional": optional,
                "source": str(args.pai_dir), "source_pool": len(pool),
                "sample_stride_s": 0.4,
                "determinism": "sha1 order of (seed, clip_id, t0_relative); no RNG",
                "targets": TARGETS[regime],
                "allocation": alloc[regime][f"n{n}"].tolist(),
                "stationary_allocation": alloc[regime]["stationary"].tolist() if n == scales[0] else None,
                "realised": composition(rows),
                "nested_in": f"lead-alpamayo-pai_matrix_{regime}_{scales[0]}" if n != scales[0] else None,
                "val": {"shared": True, "n": len(val),
                        **{k: v for k, v in val_stats.items() if k != "overlap_before"}},
                "train_eval_overlap": overlap,
                "note": ("Optional decoupling cell: Flooded's group mix with Golden's manoeuvre "
                         "mix and 2 % stationary. It separates group mix from the lateral + "
                         "stationary bundle, NOT lateral from stationary." if optional else None),
            }
            write_cell(args.out_root / name, args.pai_dir, rows, val, meta)
            report["cells"][name] = {
                "n": n, "optional": optional, "clips": len({s["clip_id"] for s in rows}),
                "stationary_pct": composition(rows)["flags_pct"]["stationary"],
                "train_eval_overlap": overlap}
            print(f"wrote {args.out_root / name}  ({n} train, {len(val)} val, "
                  f"{overlap['samples_overlapping_full_eval']} train samples on an eval route)"
                  + ("  [optional]" if optional else ""))

    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str) + "\n")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
