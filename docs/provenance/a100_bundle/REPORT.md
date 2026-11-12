# Provenance report: Alpamayo 1.5 "Matrix" fine-tunes (A100), written 2026-11-12

Read-only pass. Everything in this folder is a COPY. `training_args.json` files are `TrainingArguments.to_json_string()` dumps of each checkpoint's `training_args.bin`, loaded on CPU.
Paths: R = /workspace/alpamayo-recipes/recipes/alpamayo1_5_sft, W = /workspace.

Tags: [A] = read from a trainer artifact (trainer_state.json, training_args.bin, Hydra config/overrides), [L] = training log or launch script, [N] = notes or chat file only, [C] = computed by me (method stated).

## Main table

| run | train samples | epochs | per-dev batch | grad acc | optimizer steps | LR schedule | seed | resume events | exported step | dates (UTC) |
|---|---|---|---|---|---|---|---|---|---|---|
| golden_1600 | 1,600 [A] | 10 [A] | 1 [A] | 8 [A] | 2,000 [A] | cosine_warmup_with_min_lr, peak 1e-4, min 1e-6, warmup 100 [A] | 42 [A] | yes: fresh start, then resumed from ckpt-800 (several attempts; one OOM); final attempt resumed at 800 and ran to 2000 [L] | checkpoint-2000 [A/L] | 2026-10-16 11:07 → 2026-10-17 01:43 [L] |
| flooded_1600 | 1,600 [A] | 10 [A] | 1 [A] | 8 [A] | 2,000 [A] | same, warmup 100 [A] | 42 [A] | yes: fresh start, resumed 08:51/08:53 (log missing), final attempt resumed at 250 and ran to 2000 [L] | checkpoint-2000 [A/L] | 2026-10-17 06:39 → 16:49 [L] |
| golden_6400 | 6,400 [A] | 10 [A] | 1 [A] | 8 [A] | 8,000 [A] | same, warmup 200 [A] | 42 [A] | none: one launch, 0 → 8000 [L] | checkpoint-8000 [A/L] | 2026-10-17 18:49 → 2026-10-18 23:05 [L] |
| flooded_6400 | 6,400 [A] | 10 [A] | 1 [A] | 8 [A] | 8,000 [A] | same, warmup 200 [A] | 42 [A] | none: one launch, 0 → 8000 [L] | checkpoint-8000 [A/L] | 2026-10-19 07:52 → 2026-10-20 12:25 [L] |
| hist. large_v3, phase 1 | 6,440 [A] | 8 planned, stopped at epoch 4.97 [A] | 1 | 8 | 4,000 saved of 6,440 planned [A] | peak 1e-4, min 1e-6, warmup 200 [A] | 42 | log ends at 4180/6440 with no exit message [L] | ckpt-4000 → Lead-Large-v3-Ckpt4000-A15 [L] | 2026-10-05 13:13 → 2026-10-06 03:10 (ckpt-4000) |
| hist. large_v3, phase 2 | 6,440 [A] | 3 [A] | 1 | 8 | 2,415 [A] | peak 3.5e-5, min 1e-6, warmup 50 [A] | 42 | a NEW run initialised from ckpt-4000 WEIGHTS (fresh optimizer, LR schedule and step counter), not a Trainer resume [A] | checkpoint-2415 → "Lead-Large-v3-6400-A15" [L] | 2026-10-06 11:47 → 20:08 |
| model_v4 / Lead-Large-v4 | 16,040 [A] | 10 [A] | 1 | 8 | 20,050 [A] | peak 1e-4, min 1e-6, warmup 200 [A] | 42 | none seen [L] | checkpoint-20050 [L] | 2026-10-08 20:37 → 2026-10-11 16:11 |

Common to every run [A]: optimizer adamw_torch_fused (β 0.9/0.999, ε 1e-8), weight_decay 0.0, max_grad_norm 1.0, bf16 true, max_steps -1 (step count comes from epochs), `cotrain_vlm: false` (VLM frozen), `callbacks: {}` (no EMA; the launcher calls `alpamayo1_5_sft.train_hf`, not `train_hf_ema.py`), trainable_params 2,280,592,386 (each Hydra train_hf.log), validation = the shared 1,567-sample set.

## Evidence (quoted)

### Matrix runs, trainer artifacts
- R/output_stage2_golden_1600/checkpoint-2000/trainer_state.json: L7 `"global_step": 2000,` L2814 `"max_steps": 2000,` L2816 `"num_train_epochs": 10,` L2806 `"epoch": 10.0,`. `best_model_checkpoint` null. log_history first `(step 5, loss 9.0658, lr 5e-06)`, `(10, 8.9912, 1e-05)`, `(15, 9.1772, 1.5e-05)`; last `(1990, 6.1275, 1.0068e-06)`, `(1995, 3.4336, 1.0017e-06)`, `(2000, 4.6853, 1e-06)`.
- R/output_stage2_flooded_1600/checkpoint-2000/trainer_state.json: same line numbers, 2000 / 2000 / 10 / 10.0. First `(5, 7.1845, 5e-06)`, `(10, 9.3796, 1e-05)`, `(15, 8.5577, 1.5e-05)`; last `(1990, 7.3806)`, `(1995, 3.0746)`, `(2000, 4.4364, 1e-06)`.
- R/output_stage2_golden_6400/checkpoint-8000/trainer_state.json: L7 `"global_step": 8000,` L11214 `"max_steps": 8000,` L11216 `"num_train_epochs": 10,` L11206 `"epoch": 10.0,`. First `(5, 8.7211, 2.5e-06)`, `(10, 9.3143, 5e-06)`, `(15, 8.7605, 7.5e-06)`; last `(7990, 4.0652)`, `(7995, 2.144)`, `(8000, 3.3108, 1e-06)`.
- R/output_stage2_flooded_6400/checkpoint-8000/trainer_state.json: same line numbers, 8000 / 8000 / 10 / 10.0. First `(5, 7.7563, 2.5e-06)`, `(10, 8.9164, 5e-06)`, `(15, 9.4805, 7.5e-06)`; last `(7990, 3.1947)`, `(7995, 2.9814)`, `(8000, 3.017, 1e-06)`.
- Resolved config, e.g. R/output_stage2_golden_1600/config.yaml: L71 `per_device_train_batch_size: 1`, L73 `gradient_accumulation_steps: 8`, L74 `learning_rate: 0.0001`, L75 `warmup_steps: 100`, L80 `num_train_epochs: 10`, L81 `bf16: true`, L88 `lr_scheduler_type: cosine_warmup_with_min_lr`, L90 `min_lr: 1.0e-06`, L108 `cotrain_vlm: false`, L54 `callbacks: {}`, L24 `annotations_path: /workspace/datasets/lead-alpamayo-pai_matrix_golden_1600/annotations_train.json`. The other three runs' config.yaml files differ only in dataset path, output_dir and warmup/save_steps (6400 runs: `warmup_steps: 200`, `save_steps: 400`).
- training_args.bin (runs/*/checkpoint-*/training_args.json): every run has `per_device_train_batch_size 1, gradient_accumulation_steps 8, weight_decay 0.0, max_grad_norm 1.0, optim adamw_torch_fused, seed 42, data_seed None, bf16 True`. The 1600 runs have `resume_from_checkpoint: True` and `save_steps 50`. The 6400 runs have `resume_from_checkpoint: None`.
- Hydra overrides: R/outputs/2026-10-16/11-07-44 is golden_1600's fresh start (no resume flag). 15-40-24, 18-35-45, 19-23-49, 20-36-30, 20-44-37, 21-36-48 and 21-40-20 carry `- +trainer.resume_from_checkpoint=true`. Flooded_1600: 2026-10-17/06-39-34 fresh; 08-51-19, 08-53-15 and 10-24-58 resumed. Golden_6400: 2026-10-17/18-49-10. Flooded_6400: 2026-10-19/07-52-25. All have `- trainer.gradient_accumulation_steps=8` and `- trainer.num_train_epochs=10`.

### Logs and resume events
- W/train_golden_1600.log: first attempt's tqdm runs 0 → `903/2000 [3:06:14` (line 1876 after splitting on CR), then `=== RESUMING TRAINING FROM CHECKPOINT-800 VIA TMUX ===`. The 15:40 attempt hit `torch.OutOfMemoryError: CUDA out of memory` while loading the optimizer. Then `STARTING/RESUMING MATRIX TRAINING (golden_1600): Fri Oct 16 21:39:53 UTC 2026` and `Existing checkpoints detected ... Automatically resuming...`. The first tqdm value after 0 is 801, so that attempt resumed at global step 800. Final: `100%|██████████| 2000/2000 [4:01:28<00:00, 11.47s/it] {'train_runtime': 14520.5528, ... 'train_loss': 2.633328640460968, 'epoch': 10.0}`.
- W/pipeline_matrix.log holds two more golden_1600 attempts, both resumed at 800 (first tqdm 801), reaching 942 and 828 before stopping, then `LAUNCHING IMMUNE DETACHED DAEMON (SAVE_STEPS=50): Fri Oct 16 20:44:11 UTC 2026`. Steps past 800 from these attempts were rolled back, because the final attempt restarted at 800.
- W/train_flooded_1600.log: first attempt 0 → `215/2000 [54:16` (fresh, Hydra 06:39:34). Then `STARTING/RESUMING MATRIX TRAINING (flooded_1600): Sat Oct 17 08:50:38 UTC 2026`, whose tqdm output went to `train_flooded_1600_live.log -> /root/.gemini/.../task-256.log`. That target is GONE: NOT FOUND. Then `[2026-10-17 10:24:53 UTC] [IMMUNE_DAEMON] Immune daemon active`. Its attempt's first tqdm value after 0 is 251, so it resumed at global step 250. Final: `2000/2000 [6:22:14<00:00, 12.12s/it] {'train_runtime': 22971.8378, ... 'train_loss': 3.995`. Which attempt produced checkpoint-250, and why attempt 1 stopped at 215: NOT FOUND (log gap 07:34–08:50).
- W/train_golden_6400.log: line 1 `[2026-10-17 18:49:05 UTC] [IMMUNE_DAEMON_6400] Immune daemon active`. One tqdm sequence 0 → 8000, with no resume marker. L1777 `8000/8000 [28:15:15<00:00, 12.70s/it] {'train_runtime': 101753.814, ...}`.
- W/train_flooded_6400.log: line 1 `[2026-10-19 07:52:20 UTC] [IMMUNE_DAEMON_6400_FLOODED] Immune daemon active`. One sequence 0 → 8000, with no resume marker. L1777 `8000/8000 [28:31:28<00:00, 12.48s/it] {'train_runtime': 102725.2482, ...}`.
- End times are the mtimes of the final checkpoint directories (runs/*/LISTING.txt).

### Export
- Command (W/launch_matrix_training.sh): `python scripts/convert_checkpoint.py to-a15 --input "$LATEST_CKPT" --output "$CKPT_DIR_A15" --overwrite`, with `LATEST_CKPT=$(ls -d .../checkpoint-* | sort -V | tail -1)`, then `tar --use-compress-program=pigz -chf`.
- The logs print `Converting latest checkpoint .../output_stage2_{golden_1600,flooded_1600}/checkpoint-2000` and `.../output_stage2_{golden,flooded}_6400/checkpoint-8000`.
- The A15 directories' safetensors are symlinks into exactly those checkpoints (exports/*/LISTING.txt).
- Golden-1600 caveat: its log ends with `Zip archive complete: /workspace/Alpamayo-1.5-10B-Matrix-Golden-1600-A15.zip` (02:14). The launcher's tar.gz step did not exist yet. The .tar.gz (mtime 2026-10-17 08:40) was made separately, and no log of that tar command was found (NOT FOUND). It packs the same A15 directory, which links to checkpoint-2000.

### Datasets [A: each folder's conversion_stats.json and README.md]
| cell | train | val | stride | seed | groups A–F % | Straight/SwL/SwR/TL/TR % | stationary | clips |
|---|---|---|---|---|---|---|---|---|
| golden_1600 | 1600 | 1567 (shared) | 0.4 s | 0 | 27/18/17/14/14/10 | 50/13/13/12/12 | 32 (2.0 %) | 1314 |
| flooded_1600 | 1600 | 1567 | 0.4 s | 0 | 35/14/22/10/9/10 | 22/37/12/14.5/14.5 | 160 (10.0 %) | 1072 |
| golden_6400 | 6400 | 1567 | 0.4 s | 0 | 27/18/17/14/14/10 | 50/13/13/12/12 | 128 (2.0 %) | 1534 |
| flooded_6400 | 6400 | 1567 | 0.4 s | 0 | 35/14/22/10/9/10 | 22/37/12/14.5/14.5 | 640 (10.0 %) | 1517 |
- Pool and build: README `every sample comes from lead_multirig_pai_v4's verified training pool (34,132 samples at a 0.4 s stride)`. Build command: `python scripts/build_curation_matrix.py --stage build --pai-dir <v4> --out-root <root> --seed 0 --gate <lead2hipad>/eval/gate_validation_lead.json`, `Deterministic: sha1 order of (seed, clip_id, t0_relative); no RNG`.
- Golden and flooded are drawn from the SAME pool. They differ only in the target marginals (groups, manoeuvres, stationary %). Each allocation is an IPF/RAS minimum-divergence fit, as the README says.
- The build script itself is NOT on this machine. `media.repacked_from` = `/home/earth/Documents/AD/lead2alpa/dataset/lead_multirig_pai_v4`, so the build ran on another PC.
- Nesting [C, set check on (clip_id, t0_relative)]: golden_1600 ⊂ golden_6400 and flooded_1600 ⊂ flooded_6400 are both True. golden_6400 ∩ flooded_6400 = 4,284 samples, and golden_1600 ∩ flooded_1600 = 1,071 samples.
- annotations_val.json is byte-identical across all cells (datasets/annotations_val_md5.txt).

### Item 7 [C]
Script: analysis/q7.py; output: analysis/q7_output.txt.
- Speed: |(vx, vy)| from each clip's egomotion.parquet, linearly interpolated at t0_relative.
- Path length: sum of XY segment lengths between poses interpolated at t0 + k·0.1 s, k = 0..64 (6.4 s). This matches the loader default `num_future_steps: int = 64, time_step: float = 0.1` in alpamayo/data/pai.py:43-44. No horizon was truncated.
- The annotation fields `speed_mps` / `future_path_m` agree with this recomputation to ≤ 5 mm/s and ≤ 3 cm.

| cell | speed ≤ 0.5 m/s (total) | stays put (< 0.64 m) | starts moving (≥ 2 m) | in between |
|---|---|---|---|---|
| golden_1600 | 387 | 44 | 302 | 41 |
| flooded_1600 | 549 | 168 | 346 | 35 |
| golden_6400 | 1568 | 171 | 1250 | 147 |
| flooded_6400 | 2138 | 662 | 1339 | 137 |

From the annotation fields instead, golden_6400 gives 1570 / 171 / 1251 / 148 and flooded_6400 gives 2143 / 663 / 1343 / 137. The small differences come from rounding at the 0.5 m/s threshold. The 1600 cells are identical either way.

### Historical runs
- large_v3, phase 1: R/output_stage2_lead_v3/checkpoint-4000/trainer_state.json L7 `"global_step": 4000,` L5614 `"max_steps": 6440,` L5616 `"num_train_epochs": 8,` L5606 `"epoch": 4.9689440993788825,`. Last logged `(4000, loss 4.1433, lr 3.388e-05)`. Launch: W/launch_stage2_v3.sh `Schedule: 8 Epochs = 6,440 Optimizer Steps (eff. batch 8)`. Log W/train_stage2_v3.log: `Date: Mon Oct  5 13:13:45 UTC 2026`, last line `4180/6440 [14:31:58`, with no exit message.
- large_v3, phase 2: W/resume_stage2_v3_from_4000.sh sets `model.pretrained_model_name_or_path=$LAST_CKPT` (= checkpoint-4000), `trainer.learning_rate=3.5e-5`, `trainer.warmup_steps=50`, `trainer.num_train_epochs=3`, and has no resume_from_checkpoint. R/output_stage2_lead_v3_resumed/checkpoint-2415/trainer_state.json L7 `"global_step": 2415,` L3395 `"max_steps": 2415,` L3397 `"num_train_epochs": 3,`. Its log_history restarts at step 5 with lr 3.5e-06, i.e. a fresh schedule. W/train_resumed_standalone.log: `Date: Tue Oct  6 11:47:15 UTC 2026` … `2415/2415 [8:19:39 ... 'train_loss': 3.882210149429353, 'epoch': 3.0}`. W/Alpamayo-1.5-10B-Lead-Large-v3-6400-A15 links to `output_stage2_lead_v3_resumed/checkpoint-2415`.
- No directory named checkpoint-6400 exists for v3: NOT FOUND. "6,415 total steps" = 4000 + 2415 and "≈ 8 epochs" = 4.97 + 3.0 are my arithmetic [C], not a logged counter.
- v4: R/output_stage2_lead_v4/checkpoint-20050/trainer_state.json L7 `"global_step": 20050,` L28084 `"max_steps": 20050,` L28086 `"num_train_epochs": 10,` L28076 `"epoch": 10.0,`. W/lead-alpamayo-pai_large_v4/annotations_train.json has 16,040 entries (val 1,720) [C: len()]. W/train_stage2_v4.log: `Date: Thu Oct  8 20:37:31 UTC 2026` … `20050/20050 [67:32:21 ... 'epoch': 10.0}`. Export W/Alpamayo-1.5-10B-Lead-Large-v4-A15 links to checkpoint-20050.

### Notes-only claims [N]
- W/CHAT_MATRIX_TRAINING_AND_RESUME.md and W/pipeline_status.json say "2,000 / 2,000" and "8,000 / 8,000". The artifacts above confirm both.
- pipeline_status.json `final_loss` is defined inconsistently. flooded_1600's 3.9950 is the run-mean `train_loss` of the final attempt, while golden_6400's 3.3108 and flooded_6400's 3.0170 are the last logged step-8000 loss.

### Sensitive file left out on purpose
W/alpamayo-recipes/recipes/alpamayo1_5_sft/run_env.sh is not in the bundle because it contains an HF token.

### Archives [C: stat + sha256sum, 2026-11-12]
| archive | bytes | sha256 |
|---|---|---|
| Alpamayo-1.5-10B-Matrix-Golden-1600-A15.tar.gz | 17,616,983,912 | 03f74a05ad0a37276a76b971010f0ebd0ef2d5427c5433d5359fa1c41ca727cf |
| Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.tar.gz | 17,617,076,949 | 4218edc8d71d885b7d0d936ee88a21b6db9f11ed6618d3230b39c07ff43b1eb3 |
| Alpamayo-1.5-10B-Matrix-Golden-6400-A15.tar.gz | 17,605,502,448 | 9b6213b4fbba66937ec3f025dde5cf73a1d2fde96365920601af3e56aeb93db9 |
| Alpamayo-1.5-10B-Matrix-Flooded-6400-A15.tar.gz | 17,604,928,794 | 0bd5161e32c28277204edee3f846ddfabc1333c1b5a286eb30a92338b0712a6f |
The Golden-6400 and Flooded-6400 byte sizes match the 4090 values exactly. Compare the hashes with `sha256sum` on the 4090.
