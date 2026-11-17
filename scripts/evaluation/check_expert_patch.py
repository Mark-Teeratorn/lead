#!/usr/bin/env python3
"""Which expert tensors does the model server's patch step actually load?

Builds the engine exactly as the server does for a fine-tuned checkpoint (FlashDriveEngine with a local
checkpoint directory), then compares the expert weights held in memory with (a) the tensors of the
checkpoint's action_expert.safetensors and (b) the tensors of the base model. Writes a JSON report.

Usage: check_expert_patch.py --model-path <checkpoint dir> --base-file <base action_expert.safetensors> --out <json>
"""
import argparse
import json
import os
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.path.insert(0, "/home/aimslab/flashdrive/scripts")

import torch  # noqa: E402
from safetensors import safe_open  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--base-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import flashdrive_server as fs

    if a.model_path == "BASE":
        # The base model as served, without the patch step: are the expert tensors in memory those of the base files,
        # and does any expert tensor share its storage with a tensor outside the expert?
        engine = fs.FlashDriveEngine(model_path="z-lab/Alpamayo-1.5-10B", num_samples=16)
        m = engine.model
        base = safe_open(a.base_file, "pt")
        sd = m.state_dict()
        named = dict(m.named_parameters())
        named.update(dict(m.named_buffers()))
        ptr = {}
        for k, v in named.items():
            if v is not None and v.numel():
                ptr.setdefault(v.data_ptr(), []).append(k)
        shared = [ks for ks in ptr.values() if len(ks) > 1 and any(k.startswith(("expert.", "action_")) for k in ks)]
        diffs = {}
        for k in base.keys():
            if k in sd:
                diffs[k] = float((sd[k].float().cpu() - base.get_tensor(k).float()).abs().max())
        rep = {"model_path": "BASE (no patch step)", "n_base_file_keys": len(list(base.keys())), "n_present_in_memory": len(diffs),
               "n_identical_to_base_file": sum(v == 0.0 for v in diffs.values()),
               "keys_differing_from_base_file": {k: v for k, v in sorted(diffs.items(), key=lambda kv: -kv[1])[:40] if v > 0},
               "n_keys_differing": sum(v > 0 for v in diffs.values()),
               "storage_shared_with_expert_tensors": shared[:40], "n_shared_groups": len(shared),
               "dtypes_in_memory": sorted({str(sd[k].dtype) for k in diffs}),
               "expert_param_dtypes": sorted({str(p.dtype) for n, p in m.named_parameters() if n.startswith("expert.")}),
               "expert_param_devices": sorted({str(p.device) for n, p in m.named_parameters() if n.startswith("expert.")})}
        with open(a.out, "w") as f:
            json.dump(rep, f, indent=1)
        print(json.dumps(rep, indent=1)[:6000])
        return
    engine = fs.FlashDriveEngine(model_path=a.model_path, num_samples=16)
    m = engine.model
    ft = safe_open(os.path.join(a.model_path, "action_expert.safetensors"), "pt")
    base = safe_open(a.base_file, "pt")
    sd_keys = set(m.state_dict().keys())
    file_keys = list(ft.keys())
    rep = {"model_path": a.model_path, "n_file_keys": len(file_keys),
           "file_keys_present_in_served_model": sum(k in sd_keys for k in file_keys),
           "file_keys_absent_from_served_model": sorted(k for k in file_keys if k not in sd_keys)[:12],
           "n_file_keys_absent": sum(k not in sd_keys for k in file_keys),
           "served_expert_keys_not_in_file": sorted(k for k in sd_keys if k.startswith("expert.") and k not in set(file_keys))[:6],
           "layers": {}}

    def d(x, y):
        return float((x.float().cpu() - y.float().cpu()).abs().max())

    def cat(f, i, names, sub):
        return torch.cat([f.get_tensor(f"expert.layers.{i}.{sub}.{n}.weight") for n in names], dim=0)

    for i in range(len(m.expert.layers)):
        lay = m.expert.layers[i]
        r = {}
        if hasattr(lay.self_attn, "qkv_proj"):
            w = lay.self_attn.qkv_proj.weight.detach()
            r["qkv: served vs fine-tuned file"] = d(w, cat(ft, i, ["q_proj", "k_proj", "v_proj"], "self_attn"))
            r["qkv: served vs base"] = d(w, cat(base, i, ["q_proj", "k_proj", "v_proj"], "self_attn"))
        else:
            r["qkv"] = "not fused"
        if hasattr(lay.mlp, "gate_up_proj"):
            w = lay.mlp.gate_up_proj.weight.detach()
            r["gate_up: served vs fine-tuned file"] = d(w, cat(ft, i, ["gate_proj", "up_proj"], "mlp"))
            r["gate_up: served vs base"] = d(w, cat(base, i, ["gate_proj", "up_proj"], "mlp"))
        else:
            r["gate_up"] = "not fused"
        for sub, name in (("self_attn", "o_proj"), ("mlp", "down_proj")):
            w = getattr(getattr(lay, sub), name).weight.detach()
            k = f"expert.layers.{i}.{sub}.{name}.weight"
            r[f"{name}: served vs fine-tuned file"] = d(w, ft.get_tensor(k))
            r[f"{name}: served vs base"] = d(w, base.get_tensor(k))
        rep["layers"][str(i)] = r
    keys = sorted({k for r in rep["layers"].values() for k in r})
    rep["max_over_layers"] = {k: max(r[k] for r in rep["layers"].values() if isinstance(r.get(k), float)) for k in keys
                              if any(isinstance(r.get(k), float) for r in rep["layers"].values())}
    w = m.action_out_proj.weight.detach()
    rep["action_out_proj.weight: served vs fine-tuned file"] = d(w, ft.get_tensor("action_out_proj.weight"))
    rep["action_out_proj.weight: served vs base"] = d(w, base.get_tensor("action_out_proj.weight"))
    with open(a.out, "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "layers"}, indent=1))
    print("layer 0:", json.dumps(rep["layers"]["0"], indent=1))


if __name__ == "__main__":
    main()
