#!/usr/bin/env python3
"""Same-input comparison of action experts (ANALYSIS_ADDENDUM section 21).

Replays the low-speed samples of the shared validation split through the engine of the
deployed FlashDrive model server, with one action expert patched in, and stores K sampled
plans per state. The quantized backbone is loaded once; the unadapted expert runs first, then each fine-tuned
expert is patched in with the same call the model server uses. At the end the first patched expert
is patched in again and a few states are repeated, to check that swapping experts in one process
gives the same output. Run with the FlashDrive virtual environment:

  /home/aimslab/flashdrive/.venv/bin/python scripts/evaluation/same_input_replay.py \
      --out-dir outputs/same_input --experts Golden-6400=<dir> Flooded-6400-Matched=<dir> ...
"""
import argparse
import json
import os
import sys

# Offline mode must be set before huggingface_hub is imported (as the model server does).
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import time
from pathlib import Path

sys.path.insert(0, "/home/aimslab/flashdrive/scripts")

import numpy as np
import torch


def select_states(ds: Path, max_speed: float):
    ann = json.loads((ds / "annotations_val.json").read_text())
    low = [a for a in ann if a["speed_mps"] <= max_speed]
    low.sort(key=lambda a: (a["lead_log"], a["clip_id"], a["t0_relative"]))
    return low


def extent(xyz: np.ndarray):
    """xyz: (K, 64, 3) -> (L, last-second path, first-waypoint distance) per plan."""
    xy = xyz[..., :2]
    seg = np.linalg.norm(np.diff(xy, axis=1), axis=-1)  # (K, 63)
    return seg.sum(1), seg[:, -10:].sum(1), np.linalg.norm(xy[:, 0], axis=-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experts", nargs="+", required=True, help="name=checkpoint_dir, in the order to run (after Base)")
    ap.add_argument("--ds", default="/mnt/disk2/r4_sameinput/ds")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--max-speed", type=float, default=0.5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed-base", type=int, default=1000)
    ap.add_argument("--skip-base", action="store_true")
    ap.add_argument("--n-swap-check", type=int, default=5)
    a = ap.parse_args()

    ds = Path(a.ds)
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    states = select_states(ds, a.max_speed)
    if a.limit:
        states = states[:a.limit]
    experts = [tuple(e.split("=", 1)) for e in a.experts]
    print(f"{len(states)} states; experts: Base, " + ", ".join(n for n, _ in experts), flush=True)

    import contextlib
    import gc

    import pandas as pd
    import physical_ai_av
    import flashdrive_server as fs
    from alpamayo1_5.load_physical_aiavdataset import load_physical_aiavdataset
    from safetensors.torch import load_file

    class LocalAVDI(physical_ai_av.PhysicalAIAVDatasetInterface):
        """The dataset interface reading a local copy of the published dataset, without any Hub request."""

        def __init__(self, root):
            self.root = Path(root)
            df = pd.read_csv(self.root / "features.csv", index_col="feature")
            df["clip_files_in_zip"] = df["clip_files_in_zip"].map(json.loads, na_action="ignore")
            self.features = physical_ai_av.dataset.Features(df)
            self.clip_index = pd.read_parquet(self.root / "clip_index.parquet")

        @contextlib.contextmanager
        def open_file(self, filename, maybe_stream=False):
            with open(self.root / filename, "rb") as f:
                yield f

    avdi = LocalAVDI(ds)
    t_load = time.time()
    engine = fs.FlashDriveEngine(model_path="z-lab/Alpamayo-1.5-10B", num_samples=a.k)
    fs.logger.setLevel("WARNING")
    print(f"backbone loaded in {time.time() - t_load:.0f} s", flush=True)
    holder = {}
    orig = engine.rollout

    def rollout(**kw):
        kw["num_traj_samples"] = engine.num_samples
        res = orig(**kw)
        holder["extra"] = res[2]
        return res

    engine.rollout = rollout

    def patch(ckpt_dir):
        """Same call as FlashDriveEngine (Option C): load the cached expert file and patch it into the model."""
        f = Path(ckpt_dir) / "action_expert.safetensors"
        w = load_file(str(f), device="cpu")
        n = len(w)
        missing, unexpected = engine.model.load_state_dict(w, strict=False)
        del w
        gc.collect()
        torch.cuda.empty_cache()
        # The model server only warns about these (action-space constants stored in the expert file); do the same.
        print(f"patch {f.parent.name}: {len(missing)} missing, {len(unexpected)} unexpected keys {list(unexpected)[:3]}", flush=True)
        return n

    def request(clip, t0, nav):
        d = load_physical_aiavdataset(clip, t0_us=int(t0), num_frames=4, avdi=avdi, maybe_stream=False)
        return {"images": d["image_frames"].flatten(0, 1), "camera_indices": d["camera_indices"].tolist(),
                "num_frames_per_camera": 4, "nav_text": nav,
                "ego_history_xyz": d["ego_history_xyz"].numpy(), "ego_history_rot": d["ego_history_rot"].numpy()}, d

    def run_state(i, s, name):
        t_start = time.time()
        rec = {"state": i, "clip_id": s["clip_id"], "t0": s["t0_relative"], "lead_log": s["lead_log"],
               "scenario": s["scenario"], "speed_mps": s["speed_mps"], "future_path_m": s["future_path_m"],
               "nav_text": s["nav_text"], "expert": name, "k": engine.num_samples}
        try:
            torch.manual_seed(a.seed_base + i)
            torch.cuda.manual_seed_all(a.seed_base + i)
            np.random.seed(a.seed_base + i)
            engine.reset_stream()
            # A fresh stream for every state: the model starts a new stream only when its KV cache is None
            # (flashdrive/_base.py); the server's reset_stream() resets the step counter only.
            m = engine.model
            m._past_key_values = None
            m._cached_streaming_attention_mask = None  # sized by the prefill length of the stream it was built for
            m.vlm.model.visual.reset_shape_caches()
            m.vlm.model.language_model.reset_shape_caches()
            torch.cuda.empty_cache()
            r0, _ = request(s["clip_id"], s["t0_relative"] - 100_000, s["nav_text"])
            p0 = engine.step(r0)
            r1, d1 = request(s["clip_id"], s["t0_relative"], s["nav_text"])
            holder.clear()
            p1 = engine.step(r1)
            if p1.get("status") != "ok":
                raise RuntimeError(f"step status {p1.get('status')}: {p1.get('message')}")
            xyz = np.asarray(p1["pred_xyz"], dtype=np.float64).reshape(-1, 64, 3)
            L, last, first = extent(xyz)
            h = d1["ego_history_xyz"].numpy().reshape(-1, 3)
            cot = holder.get("extra", {}).get("cot") if isinstance(holder.get("extra"), dict) else None
            rec.update({"prefill_status": p0.get("status"), "n_plans": int(xyz.shape[0]),
                        "L": [round(float(x), 4) for x in L], "last_second_path": [round(float(x), 4) for x in last],
                        "first_wp": [round(float(x), 4) for x in first],
                        "hist_speed_last": round(float(np.linalg.norm(h[-1, :2] - h[-2, :2]) / 0.1), 4),
                        "cot": [str(c) for c in np.asarray(cot, dtype=object).reshape(-1)] if cot is not None else None,
                        "seconds": round(time.time() - t_start, 2)})
        except Exception as e:  # a state that cannot be loaded or run is recorded and counted
            rec.update({"error": f"{type(e).__name__}: {e}"[:400]})
            torch.cuda.empty_cache()
        return rec

    def run_expert(name, idx=None, suffix=""):
        out = out_dir / f"{name}{suffix}.jsonl"
        done = set()
        if out.exists():
            done = {json.loads(line)["state"] for line in out.read_text().splitlines() if line.strip()}
        todo = [i for i in (idx if idx is not None else range(len(states))) if i not in done]
        print(f"{name}{suffix}: {len(todo)} states to run, {len(done)} already done", flush=True)
        with out.open("a") as fh:
            for n_done, i in enumerate(todo):
                rec = run_state(i, states[i], name)
                # Addendum 21: if K = 16 does not fit in memory, K = 8, decided on the first states of the first expert.
                if "error" in rec and "out of memory" in rec["error"].lower() and engine.num_samples > 8 and n_done < 3:
                    print(f"K = {engine.num_samples} does not fit ({rec['error'][:80]}); using K = 8", flush=True)
                    engine.num_samples = 8
                    rec = run_state(i, states[i], name)
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                if n_done % 20 == 0:
                    print(f"{name}{suffix} {n_done}/{len(todo)} state {i}: {rec.get('seconds', 'ERR')} s, K {engine.num_samples}, "
                          f"mem {torch.cuda.max_memory_allocated() / 2**30:.1f} GB {rec.get('error', '')}", flush=True)
        print(f"finished {name}{suffix} at {time.strftime('%H:%M:%S')}", flush=True)

    if not a.skip_base:
        run_expert("Base")
    for name, ckpt in experts:
        n = patch(ckpt)
        print(f"patched {n} tensors of {name} from {ckpt}", flush=True)
        run_expert(name)
    # swap check: patch the first expert in again and repeat a few states with the same seeds
    if experts and a.n_swap_check:
        name, ckpt = experts[0]
        patch(ckpt)
        chk = out_dir / f"{name}.swapcheck.jsonl"
        if chk.exists():
            chk.unlink()
        run_expert(name, idx=list(range(min(a.n_swap_check, len(states)))), suffix=".swapcheck")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
