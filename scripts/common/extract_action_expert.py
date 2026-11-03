#!/usr/bin/env python3
"""Extracts action_expert.safetensors from fine-tuned Alpamayo model shards

and removes redundant base shards to save ~15 GB disk space.
"""

import sys
import glob
import os
import time
from pathlib import Path
import torch
from safetensors.torch import load_file, save_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_action_expert.py <checkpoint_dir>")
        sys.exit(1)

    ckpt_dir = Path(sys.argv[1]).resolve()
    if not ckpt_dir.exists():
        print(f"Error: {ckpt_dir} does not exist.")
        sys.exit(1)

    cached_file = ckpt_dir / "action_expert.safetensors"
    if cached_file.exists():
        print(f"action_expert.safetensors already exists at {cached_file} ({cached_file.stat().st_size / (1024**3):.2f} GB).")
        return

    safetensor_files = sorted(glob.glob(f"{ckpt_dir}/model-*.safetensors"))
    if not safetensor_files:
        safetensor_files = sorted(glob.glob(f"{ckpt_dir}/*.safetensors"))
        safetensor_files = [f for f in safetensor_files if not f.endswith("action_expert.safetensors")]

    if not safetensor_files:
        print(f"Error: No safetensors found in {ckpt_dir}")
        sys.exit(1)

    print(f"Extracting Action Expert weights from {len(safetensor_files)} shards in {ckpt_dir}...")
    t0 = time.time()
    expert_weights = {}

    for idx, filepath in enumerate(safetensor_files, 1):
        print(f"  [{idx}/{len(safetensor_files)}] Loading {os.path.basename(filepath)}...")
        shard = load_file(filepath, device="cpu")
        matched = 0
        for key, tensor in shard.items():
            if any(module in key for module in ["action", "expert", "diffusion", "delta"]):
                expert_weights[key] = tensor.to(dtype=torch.bfloat16)
                matched += 1
        print(f"      Matched {matched} expert tensors (total collected: {len(expert_weights)})")
        del shard

    print(f"Saving {len(expert_weights)} expert tensors to {cached_file}...")
    save_file(expert_weights, str(cached_file))
    size_gb = cached_file.stat().st_size / (1024**3)
    print(f"Successfully saved {cached_file.name} ({size_gb:.2f} GB) in {time.time() - t0:.2f}s!")

    # Verify action_expert
    test_load = load_file(str(cached_file), device="cpu")
    print(f"Verification: Successfully verified {len(test_load)} tensors in {cached_file.name}.")
    del test_load
    del expert_weights

    # Cleanup large shards to save disk space
    print("Cleaning up redundant base shards...")
    removed_bytes = 0
    for f in safetensor_files:
        f_path = Path(f)
        removed_bytes += f_path.stat().st_size
        f_path.unlink()
        print(f"  Removed {f_path.name}")
    print(f"Freed {removed_bytes / (1024**3):.2f} GB of disk space!")

if __name__ == "__main__":
    main()
