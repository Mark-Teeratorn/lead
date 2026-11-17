#!/usr/bin/env python3
"""FlashDrive model server with the fine-tuned action expert loaded in full.

The stock server (/home/aimslab/flashdrive/scripts/flashdrive_server.py, left unchanged) loads a fine-tuned
checkpoint by patching its expert tensors into the base model with strict=False. The engine has by then fused
the q/k/v projections and the gate/up projections of every expert layer (flashdrive.setup_expert_fusion, called
inside flashdrive.from_pretrained), so the 180 tensors of those projections have no matching name and are
dropped without a message: 5 of the 11 tensors of each of the 36 expert layers stay at their base values
(ANALYSIS_ADDENDUM section 24; docs/provenance/expert_patch_check_golden_6400.json).

This wrapper serves the same protocol with the same engine code. The only difference is the loading of a
fine-tuned checkpoint: the base model is loaded without the stock patch step, the checkpoint's q/k/v and
gate/up tensors are concatenated in the order of the fusion and loaded into the fused weights, and all other
tensors are loaded under their own names. The server refuses to start if any expert tensor is left unpatched
or if any loaded tensor differs from the checkpoint file, and it writes a report of that check.

Usage: as flashdrive_server.py, plus
    --patch-report <json>   where to write the loading report (default: /tmp/flashdrive_fullpatch_report.json)
Without --model-path (or with a z-lab path) the base model is served exactly as by the stock server.
"""
import argparse
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/home/aimslab/flashdrive/scripts")

import torch  # noqa: E402

import flashdrive_server as fs  # noqa: E402

BASE_MODEL = "z-lab/Alpamayo-1.5-10B"
FUSED = (("self_attn", "qkv_proj", ("q_proj", "k_proj", "v_proj")), ("mlp", "gate_up_proj", ("gate_proj", "up_proj")))
PATCH_REPORT = {"path": "/tmp/flashdrive_fullpatch_report.json"}


def fused_state_dict(weights, n_layers):
    """Checkpoint tensors under the names of the served model: fused projections concatenated in fusion order."""
    w = dict(weights)
    out = {}
    for i in range(n_layers):
        for sub, fused_name, parts in FUSED:
            pre = f"expert.layers.{i}.{sub}."
            out[pre + fused_name + ".weight"] = torch.cat([w.pop(pre + f"{p}.weight") for p in parts], dim=0)
            assert not any((pre + f"{p}.bias") in w for p in parts), "fused projections with a bias are not handled"
    out.update(w)
    return out


def full_patch(model, checkpoint_dir):
    from safetensors.torch import load_file

    f = Path(checkpoint_dir).resolve()
    f = f if f.is_file() else f / "action_expert.safetensors"
    if not f.exists():
        raise FileNotFoundError(f"{f} not found: extract the action expert of the checkpoint first")
    t0 = time.time()
    weights = load_file(str(f), device="cpu")
    n_file = len(weights)
    mapped = fused_state_dict(weights, len(model.expert.layers))
    del weights
    missing, unexpected = model.load_state_dict(mapped, strict=False)
    prefixes = ("expert.", "action_in_proj.", "action_out_proj.")
    left = sorted(k for k in missing if k.startswith(prefixes))
    sd = model.state_dict()
    worst, n_checked = 0.0, 0
    for k, v in mapped.items():
        if k in sd:
            worst = max(worst, float((sd[k].float().cpu() - v.float()).abs().max()))
            n_checked += 1
    report = {"checkpoint_file": str(f), "tensors_in_file": n_file, "tensors_given_after_fusion": len(mapped),
              "tensors_checked_in_memory": n_checked, "largest_difference_memory_vs_file": worst,
              "not_taken_by_the_model": sorted(unexpected), "expert_tensors_left_unpatched": left,
              "seconds": round(time.time() - t0, 1), "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    Path(PATCH_REPORT["path"]).write_text(json.dumps(report, indent=1) + "\n")
    fs.logger.info(f"[full patch] {json.dumps(report)}")
    # the model keeps seven constants outside its state dict (action-space statistics and Fourier frequencies);
    # they are equal in the base model and in the checkpoints
    allowed = ("action_space.", "action_in_proj.sinus.", "action_in_proj.timestep_fourier_encoder.")
    bad = [k for k in unexpected if not k.startswith(allowed)]
    if left or bad or worst != 0.0:
        raise RuntimeError(f"full patch incomplete: left {left[:5]}, not taken {bad[:5]}, largest difference {worst}")
    del mapped
    gc.collect()
    torch.cuda.empty_cache()


class FullPatchEngine(fs.FlashDriveEngine):
    def __init__(self, model_path, expert_checkpoint=None, **kw):
        ckpt = expert_checkpoint
        if ckpt is None and not model_path.lower().startswith("z-lab/"):
            ckpt = model_path
        # base model without the stock patch step
        super().__init__(model_path=BASE_MODEL if ckpt else model_path, expert_checkpoint=None, **kw)
        self.model_path = model_path
        if ckpt and not self.dummy:
            full_patch(self.model, ckpt)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--patch-report", default=PATCH_REPORT["path"])
    a, rest = ap.parse_known_args()
    PATCH_REPORT["path"] = a.patch_report
    sys.argv = [sys.argv[0]] + rest
    fs.FlashDriveEngine = FullPatchEngine
    fs.main()


if __name__ == "__main__":
    main()
