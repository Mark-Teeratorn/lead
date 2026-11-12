# Comprehensive Training Instructions: Alpamayo 1.5 Fine-Tuning on 4 Curated LEAD Matrix Datasets
## (`golden_1600`, `flooded_1600`, `golden_6400`, `flooded_6400`)

> **PRIMARY MANDATE: ACTION-ONLY FINE-TUNING (STAGE 2 SFT)**  
> This guide provides step-by-step instructions to train **Alpamayo 1.5** on the **4 Matrix Datasets** in `/workspace/datasets/`.  
> Consistent with the project's record-setting **72.2 Driving Score** on the CARLA benchmark, all 4 runs prioritize **Action-Only Fine-Tuning (Stage 2 SFT)** where the 8.8B Vision-Language Model (VLM) backbone is **completely FROZEN** (`cotrain_vlm: false`). Training targets solely the 2.28B parameter Trajectory Action Expert (Flow Matching transformer) and action projection layers.

---

## 1. Matrix Dataset Overview & Taxonomy

All 4 datasets are stored in `/workspace/datasets/` and were extracted with a fine-grained **0.4s stride** from the multi-rig CARLA collection. They share a common, leak-screened validation split of **1,567 samples** (0 overlap with CARLA benchmark test routes).

| Dataset Directory | Regime | Train Samples | Val Samples | Straight % | Lateral Balance (L : R) | Stationary % | Primary Focus / Character |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| [`lead-alpamayo-pai_matrix_golden_1600`](file:///workspace/datasets/lead-alpamayo-pai_matrix_golden_1600) | **Golden** | **1,600** | 1,567 | 50.0% (800) | 25.0% L : 25.0% R (Symmetric) | 2.0% (32) | Fast benchmark baseline, clean balanced distribution |
| [`lead-alpamayo-pai_matrix_flooded_1600`](file:///workspace/datasets/lead-alpamayo-pai_matrix_flooded_1600) | **Flooded** | **1,600** | 1,567 | 22.0% (352) | 51.5% L : 26.5% R (High Swerve) | 10.0% (160) | High manoeuvre density, obstacle & hazard stress-test |
| [`lead-alpamayo-pai_matrix_golden_6400`](file:///workspace/datasets/lead-alpamayo-pai_matrix_golden_6400) | **Golden** | **6,400** | 1,567 | 50.0% (3,200) | 25.0% L : 25.0% R (Symmetric) | 2.0% (128) | Scaled golden baseline (4× volume), deep convergence |
| [`lead-alpamayo-pai_matrix_flooded_6400`](file:///workspace/datasets/lead-alpamayo-pai_matrix_flooded_6400) | **Flooded** | **6,400** | 1,567 | 22.0% (1,408) | 51.5% L : 26.5% R (High Swerve) | 10.0% (640) | Scaled edge-case volume (4×), complex interactions |

### Detailed Manoeuvre Breakdown:

```
[Golden Regime (1600 & 6400)]
  ├── STRAIGHT:     50.0%  (Golden 1600: 800   | Golden 6400: 3,200)
  ├── SWERVE_LEFT:  13.0%  (Golden 1600: 208   | Golden 6400: 832)
  ├── SWERVE_RIGHT: 13.0%  (Golden 1600: 208   | Golden 6400: 832)
  ├── TURN_LEFT:    12.0%  (Golden 1600: 192   | Golden 6400: 768)
  └── TURN_RIGHT:   12.0%  (Golden 1600: 192   | Golden 6400: 768)
  Total Lateral:    50.0%  (Exact 25.0% Left : 25.0% Right balance)

[Flooded Regime (1600 & 6400)]
  ├── STRAIGHT:     22.0%  (Flooded 1600: 352  | Flooded 6400: 1,408)
  ├── SWERVE_LEFT:  37.0%  (Flooded 1600: 592  | Flooded 6400: 2,368)
  ├── SWERVE_RIGHT: 12.0%  (Flooded 1600: 192  | Flooded 6400: 768)
  ├── TURN_LEFT:    14.5%  (Flooded 1600: 232  | Flooded 6400: 928)
  └── TURN_RIGHT:   14.5%  (Flooded 1600: 232  | Flooded 6400: 928)
  Total Lateral:    78.0%  (High dynamic density, obstacle bypass focus)
```

### Scenario Coverage:
All 4 datasets span all 6 scenario groups across 41 CARLA scenario types:
- **Group A (Obstacle & Construction)**: 27% (Golden) vs. 35% (Flooded)
- **Group B (Junctions)**: 18% (Golden) vs. 14% (Flooded)
- **Group C (Hazards & Emergency)**: 17% (Golden) vs. 22% (Flooded)
- **Group D (Highway & Merging)**: 14% (Golden) vs. 10% (Flooded)
- **Group E (VRUs & Dynamic Conflicts)**: 14% (Golden) vs. 9% (Flooded)
- **Group F (Baseline & Signals)**: 10% (Golden) vs. 10% (Flooded)

---

## 2. Step Arithmetic & Scheduling

All calculations assume an **effective batch size of 8** (`per_device_batch_size = 1`, `gradient_accumulation_steps = 8` on 1× A100 SXM4 80GB, or `gradient_accumulation_steps = 1` on 8× A100):

| Dataset Scale | Train Samples | Steps / Epoch | 10 Epochs (Full) | 5 Epochs (Medium) | Warmup Steps | Save Checkpoints Every |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1600** (`golden_1600` / `flooded_1600`) | 1,600 | **200 steps** | **2,000 steps** | **1,000 steps** | 100 steps | Every 100 or 200 steps |
| **6400** (`golden_6400` / `flooded_6400`) | 6,400 | **800 steps** | **8,000 steps** | **4,000 steps** | 200 steps | Every 400 steps |

---

## 3. Quick-Start Commands (TL;DR)

Choose which dataset you want to train and run the corresponding command block:

### Dataset 1: `golden_1600` (1,600 samples, Balanced Baseline)

```bash
# 1. Setup Environment
export YOUR_HOME=/workspace
export RECIPE_DIR=$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft
export DATASET_DIR=$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_golden_1600
export CKPT_DIR_A1=$YOUR_HOME/Alpamayo-1.5-10B-A1-format
export CKPT_DIR_A15=$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Golden-1600-A15
export OUTPUT_DIR=output_stage2_golden_1600
export HF_HOME=$YOUR_HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export USE_WANDB=no

DATA_ARGS="data.train_dataset.local_dir=$DATASET_DIR \
  data.train_dataset.annotations_path=$DATASET_DIR/annotations_train.json \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$DATASET_DIR \
  data.val_dataset.annotations_path=$DATASET_DIR/annotations_val.json \
  data.val_dataset.chunk_ids=null"

# 2. Launch Training (10 Epochs = 2,000 steps, ~1.2 hrs on 1x A100)
cd $RECIPE_DIR
source a1_5_sft/bin/activate

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=100 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=200 \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=$OUTPUT_DIR

# 3. Convert to Alpamayo 1.5 Serving Format
cd $YOUR_HOME/alpamayo-recipes
STAGE2_CKPT=$(ls -d $RECIPE_DIR/$OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
python scripts/convert_checkpoint.py to-a15 --input "$STAGE2_CKPT" --output "$CKPT_DIR_A15" --overwrite
```

---

### Dataset 2: `flooded_1600` (1,600 samples, High Difficulty & Lateral Stress)

```bash
# 1. Setup Environment
export YOUR_HOME=/workspace
export RECIPE_DIR=$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft
export DATASET_DIR=$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_flooded_1600
export CKPT_DIR_A1=$YOUR_HOME/Alpamayo-1.5-10B-A1-format
export CKPT_DIR_A15=$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15
export OUTPUT_DIR=output_stage2_flooded_1600
export HF_HOME=$YOUR_HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export USE_WANDB=no

DATA_ARGS="data.train_dataset.local_dir=$DATASET_DIR \
  data.train_dataset.annotations_path=$DATASET_DIR/annotations_train.json \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$DATASET_DIR \
  data.val_dataset.annotations_path=$DATASET_DIR/annotations_val.json \
  data.val_dataset.chunk_ids=null"

# 2. Launch Training (10 Epochs = 2,000 steps, ~1.2 hrs on 1x A100)
cd $RECIPE_DIR
source a1_5_sft/bin/activate

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=100 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=200 \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=$OUTPUT_DIR

# 3. Convert to Alpamayo 1.5 Serving Format
cd $YOUR_HOME/alpamayo-recipes
STAGE2_CKPT=$(ls -d $RECIPE_DIR/$OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
python scripts/convert_checkpoint.py to-a15 --input "$STAGE2_CKPT" --output "$CKPT_DIR_A15" --overwrite
```

---

### Dataset 3: `golden_6400` (6,400 samples, Deep Balanced Convergence)

```bash
# 1. Setup Environment
export YOUR_HOME=/workspace
export RECIPE_DIR=$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft
export DATASET_DIR=$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_golden_6400
export CKPT_DIR_A1=$YOUR_HOME/Alpamayo-1.5-10B-A1-format
export CKPT_DIR_A15=$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Golden-6400-A15
export OUTPUT_DIR=output_stage2_golden_6400
export HF_HOME=$YOUR_HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export USE_WANDB=no

DATA_ARGS="data.train_dataset.local_dir=$DATASET_DIR \
  data.train_dataset.annotations_path=$DATASET_DIR/annotations_train.json \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$DATASET_DIR \
  data.val_dataset.annotations_path=$DATASET_DIR/annotations_val.json \
  data.val_dataset.chunk_ids=null"

# 2. Launch Training (10 Epochs = 8,000 steps, ~4.8 hrs on 1x A100; or 5 Epochs = 4,000 steps)
cd $RECIPE_DIR
source a1_5_sft/bin/activate

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=200 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=400 \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=$OUTPUT_DIR

# 3. Convert to Alpamayo 1.5 Serving Format
cd $YOUR_HOME/alpamayo-recipes
STAGE2_CKPT=$(ls -d $RECIPE_DIR/$OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
python scripts/convert_checkpoint.py to-a15 --input "$STAGE2_CKPT" --output "$CKPT_DIR_A15" --overwrite
```

---

### Dataset 4: `flooded_6400` (6,400 samples, Large-Scale Edge-Case Density)

```bash
# 1. Setup Environment
export YOUR_HOME=/workspace
export RECIPE_DIR=$YOUR_HOME/alpamayo-recipes/recipes/alpamayo1_5_sft
export DATASET_DIR=$YOUR_HOME/datasets/lead-alpamayo-pai_matrix_flooded_6400
export CKPT_DIR_A1=$YOUR_HOME/Alpamayo-1.5-10B-A1-format
export CKPT_DIR_A15=$YOUR_HOME/Alpamayo-1.5-10B-Matrix-Flooded-6400-A15
export OUTPUT_DIR=output_stage2_flooded_6400
export HF_HOME=$YOUR_HOME/.cache/huggingface
export HF_HUB_OFFLINE=1
export USE_WANDB=no

DATA_ARGS="data.train_dataset.local_dir=$DATASET_DIR \
  data.train_dataset.annotations_path=$DATASET_DIR/annotations_train.json \
  data.train_dataset.chunk_ids=null \
  data.val_dataset.local_dir=$DATASET_DIR \
  data.val_dataset.annotations_path=$DATASET_DIR/annotations_val.json \
  data.val_dataset.chunk_ids=null"

# 2. Launch Training (10 Epochs = 8,000 steps, ~4.8 hrs on 1x A100; or 5 Epochs = 4,000 steps)
cd $RECIPE_DIR
source a1_5_sft/bin/activate

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=200 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=400 \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=$OUTPUT_DIR

# 3. Convert to Alpamayo 1.5 Serving Format
cd $YOUR_HOME/alpamayo-recipes
STAGE2_CKPT=$(ls -d $RECIPE_DIR/$OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
python scripts/convert_checkpoint.py to-a15 --input "$STAGE2_CKPT" --output "$CKPT_DIR_A15" --overwrite
```

---

## 4. Unified Launch Script (`launch_matrix_training.sh`)

For convenience, a parameterized runner script is provided at [`/workspace/launch_matrix_training.sh`](file:///workspace/launch_matrix_training.sh). You can launch any dataset with a single argument:

```bash
# Usage:
./launch_matrix_training.sh golden_1600
./launch_matrix_training.sh flooded_1600
./launch_matrix_training.sh golden_6400
./launch_matrix_training.sh flooded_6400
```

To run in the background with persistent logging:
```bash
nohup ./launch_matrix_training.sh golden_1600 > train_golden_1600.log 2>&1 &
echo $! > train_golden_1600.pid
```

---

## 5. Mandatory Safeguards & Stability Protocol

> [!CAUTION]
> **Container Shared Memory (`/dev/shm`) Limit**:
> Cloud container environments typically provide only 64 MB for `/dev/shm`. Setting PyTorch `dataloader_num_workers > 0` or enabling `dataloader_pin_memory=true` will exhaust IPC shared memory and crash with `Bus error`.
> - **Must Keep**: `trainer.dataloader_num_workers=0`
> - **Must Keep**: `trainer.dataloader_pin_memory=false`
> - **Must Keep**: `trainer.dataloader_persistent_workers=false`
> - **Must Keep**: `trainer.dataloader_prefetch_factor=null`

> [!IMPORTANT]
> **Streaming Data vs. RAM Overflow (`performance.zip_cache=false`)**:
> - The container has a strict 32.0 GB memory limit (`cgroup`).
> - Setting `performance.zip_cache=true` caches decompressed frame tensors into system RAM, causing a cumulative memory leak exceeding 28 GB within 2 epochs and triggering the Linux OOM Killer.
> - Setting `performance.zip_cache=false` streams clips directly from NVMe SSD on-the-fly, locking dataset RAM under **~1.5 GB** throughout the entire training lifecycle.

> [!IMPORTANT]
> **Lossless Crash Resilience (`trainer.save_only_model=false`)**:
> - Training with `trainer.save_only_model=false` writes `optimizer.pt` (8.5 GB AdamW states) and `scheduler.pt` alongside the model weights.
> - Because RAM usage remains low (~1.5 GB), serializing `optimizer.pt` is completely safe (peaks at ~12-14 GB, well below the 32 GB limit).
> - This guarantees that training can resume losslessly without optimizer momentum resets or learning rate spikes after any power interruption.

---

## 6. How to Resume After Interruption

If a run is interrupted by container reboot, timeout, or power cut, resume it by simply appending `+trainer.resume_from_checkpoint=true`:

```bash
cd $RECIPE_DIR
source a1_5_sft/bin/activate

torchrun --nproc_per_node 1 -m alpamayo1_5_sft.train_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  model.pretrained_model_name_or_path=$CKPT_DIR_A1 \
  model.stage1_vlm_checkpoint_path=$CKPT_DIR_A1 \
  $DATA_ARGS \
  trainer.learning_rate=1e-4 \
  trainer.lr_scheduler_type=cosine_warmup_with_min_lr \
  trainer.warmup_steps=100 \
  trainer.gradient_accumulation_steps=8 \
  trainer.num_train_epochs=10 \
  trainer.save_steps=200 \
  trainer.save_total_limit=5 \
  trainer.dataloader_num_workers=0 \
  trainer.dataloader_pin_memory=false \
  trainer.dataloader_persistent_workers=false \
  trainer.dataloader_prefetch_factor=null \
  trainer.save_only_model=false \
  performance.zip_cache=false \
  paths.output_dir=$OUTPUT_DIR \
  +trainer.resume_from_checkpoint=true
```

---

## 7. Mandatory Post-Training Checkpoint Conversion

> [!WARNING]
> Raw checkpoints output by `train_hf.py` are saved in internal training format (`model_type: "alpamayo_r1"`).
> FlashDrive inference servers require serving format (`model_type: "alpamayo1_5"` with `nav_text` support).
> **Failing to convert causes runtime crash**: `TypeError: create_message() got unexpected keyword argument 'nav_text'`!

Run the converter:
```bash
cd $YOUR_HOME/alpamayo-recipes
source $RECIPE_DIR/a1_5_sft/bin/activate

STAGE2_CKPT=$(ls -d $RECIPE_DIR/$OUTPUT_DIR/checkpoint-* | sort -V | tail -1)
echo "Converting checkpoint: $STAGE2_CKPT -> $CKPT_DIR_A15"

python scripts/convert_checkpoint.py to-a15 \
  --input "$STAGE2_CKPT" \
  --output "$CKPT_DIR_A15" \
  --overwrite
```

### What this modifies:
1. `config.json`: Updates `"model_type": "alpamayo1_5"` and `"architectures": ["Alpamayo1_5"]`.
2. Remaps Hydra targets from `alpamayo_r1.*` to `alpamayo1_5.*` to enable `nav_text` keyword argument processing.

---

## 8. Symlink-Safe Deployment Packaging

`convert_checkpoint.py` links weight safetensors using relative symlinks. To bundle the checkpoint for transfer to execution environments or FlashDrive clusters without broken symlinks, package with dereferencing:

```bash
cd $YOUR_HOME

# Option A: Compressed Tarball (Dereferences symlinks)
tar -chzf $(basename $CKPT_DIR_A15).tar.gz -C $YOUR_HOME $(basename $CKPT_DIR_A15)

# Option B: Python Zipfile (Dereferences symlinks)
python3 -c "
import os, zipfile
src = '$CKPT_DIR_A15'
dst = '$YOUR_HOME/' + os.path.basename(src) + '.zip'
print(f'Archiving {src} -> {dst}...')
with zipfile.ZipFile(dst, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(src, followlinks=True):
        for f in files:
            full = os.path.join(root, f)
            zf.write(full, os.path.relpath(full, src))
print('Archive created successfully!')
"
```

---

## 9. Validation & Offline Benchmark Evaluation

Evaluate both the baseline model and the newly fine-tuned checkpoints against the common **1,567-sample validation set**:

```bash
cd $RECIPE_DIR
source a1_5_sft/bin/activate

# 1. Baseline Evaluation (Zero-Shot Base Model)
torchrun --nproc_per_node 1 -m alpamayo1_5_sft.evaluate_hf \
  --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
  evaluate.eval_ckpt=$CKPT_DIR_A1 $DATA_ARGS

# 2. Evaluate All Checkpoints in Output Directory
for CKPT in $RECIPE_DIR/$OUTPUT_DIR/checkpoint-*; do
  echo "=========================================="
  echo "Evaluating Checkpoint: $CKPT"
  echo "=========================================="
  torchrun --nproc_per_node 1 -m alpamayo1_5_sft.evaluate_hf \
    --config-path pkg://alpamayo1_5_sft/configs --config-name sft_stage2_nav \
    evaluate.eval_ckpt=$CKPT $DATA_ARGS
done
```

### Key Metrics to Monitor:
- `val/metric/min_ade`: Minimum Average Displacement Error (m) — best-of-K accuracy.
- `val/metric/ade`: Average Displacement Error across the 6.4 s future horizon (64 waypoints).
- `val/metric/corner_distance`: 4-corner bounding box orientation error.

---

## 10. Summary Matrix Cheatsheet

| Configuration / Setting | `golden_1600` | `flooded_1600` | `golden_6400` | `flooded_6400` |
| :--- | :--- | :--- | :--- | :--- |
| **Path** | `datasets/lead-alpamayo-pai_matrix_golden_1600` | `datasets/lead-alpamayo-pai_matrix_flooded_1600` | `datasets/lead-alpamayo-pai_matrix_golden_6400` | `datasets/lead-alpamayo-pai_matrix_flooded_6400` |
| **Train Samples** | 1,600 | 1,600 | 6,400 | 6,400 |
| **Val Samples** | 1,567 | 1,567 | 1,567 | 1,567 |
| **Steps / Epoch** | 200 | 200 | 800 | 800 |
| **Total Steps (10 Ep)** | **2,000** | **2,000** | **8,000** | **8,000** |
| **Total Steps (5 Ep)** | 1,000 | 1,000 | 4,000 | 4,000 |
| **Warmup Steps** | 100 | 100 | 200 | 200 |
| **Save Steps** | 200 (or 100) | 200 (or 100) | 400 | 400 |
| **Learning Rate** | `1e-4` | `1e-4` | `1e-4` | `1e-4` |
| **LR Scheduler** | `cosine_warmup_with_min_lr` | `cosine_warmup_with_min_lr` | `cosine_warmup_with_min_lr` | `cosine_warmup_with_min_lr` |
| **Grad Accumulation** | 8 | 8 | 8 | 8 |
| **Per-Device Batch** | 1 | 1 | 1 | 1 |
| **VLM Backbone** | Frozen (`cotrain_vlm: false`) | Frozen (`cotrain_vlm: false`) | Frozen (`cotrain_vlm: false`) | Frozen (`cotrain_vlm: false`) |
| **Chunk IDs** | `null` | `null` | `null` | `null` |
| **Zip Cache** | `false` | `false` | `false` | `false` |
| **Save Only Model** | `false` | `false` | `false` | `false` |
| **Dataloader Workers**| `0` | `0` | `0` | `0` |

---

## 11. Downtime & Disconnect Prevention Protocol (IMPORTANT: Antigravity & Terminal Resilience)

> [!IMPORTANT]
> **CRITICAL PRECAUTION: RUNTIME IMMUNITY & OOM QUARANTINE (MANDATORY)**  
> Long-running training jobs executed inside cloud environments and AI agents (such as Antigravity) will terminate abruptly if launched inside an interactive shell or standard agent background task. To guarantee uninterrupted execution:
> 1. **Always Use True Double-Fork Daemonization (`daemon_flooded_1600.py`)**: Detach the job completely so it is adopted directly by **`init` (`PPID: 1`)** with no controlling terminal (`TTY: ?`). This guarantees complete immunity against browser closures, Wi-Fi drops, and `agy` agent daemon restarts.
> 2. **Never Run Compression During Active Training**: The container has a strict **32 GB RAM ceiling** (`/sys/fs/cgroup/memory/memory.limit_in_bytes = 34,359,738,368`). Running heavy 21 GB `tar` or `zip` compression while PyTorch is checkpointing exhausts page cache and triggers the Linux kernel's uncatchable `SIGKILL` (OOM kill). Always run archive packaging with parallel `pigz` after training completes.

### A. Root Cause Analysis: Why Jobs Disconnect
When running long-running model training jobs (1.5 to 8+ hours) in web-based agent environments like Antigravity, jobs can be unexpectedly interrupted by three distinct failure modes:
1. **Interactive Pseudo-Terminal (`pts`) Vulnerability**: Commands started directly in an interactive terminal belong to that session's process group. When the browser tab closes, internet drops, or the web proxy refreshes, the controlling terminal closes.
2. **Antigravity CLI Daemon Session Drops**: The `agy` agent runs in a controlling shell. If `agy` restarts (e.g. `[Notice] All your subagents and background tasks have been stopped due to server restart`), it sends termination signals to all its child processes and background tasks.
3. **Container Cgroup 32 GB RAM Exhaustion (OOM Killer)**: The container environment enforces a hard 32.0 GB memory limit (`/sys/fs/cgroup/memory/memory.limit_in_bytes = 34,359,738,368`). Running heavy 21 GB compression (`tar -chzf`) concurrently with active PyTorch training and checkpoint serialization (which dumps 30 GB of safetensors and 8.5 GB AdamW state) exhausts dirty page cache and heap, triggering the kernel's uncatchable `SIGKILL` (OOM kill).

---

### B. The 4 Pillars of 100% Disconnect & Crash Immunity

#### Pillar 1: True Double-Fork Daemonization (Adoption by Init PID 1)
Standard backgrounding (`nohup ... &`) still keeps the process in the shell's process hierarchy. The gold standard for complete immunity is **Double-Fork Daemonization** with `os.setsid()`:
- **First Fork**: Intermediate parent exits immediately.
- **Session Decoupling (`setsid`)**: The child detaches from the controlling pseudo-terminal (`TTY: ?`), creating its own session.
- **Second Fork**: Creates a grandchild process that is not a session leader (cannot acquire a controlling terminal).
- **Adoption by PID 1**: The grandchild is adopted directly by `init` (`PPID: 1`). When the browser closes or `agy` restarts, the Linux kernel leaves PID 1's adopted processes completely untouched.
- **Standard I/O Redirection**: `stdin` is redirected to `/dev/null`, and `stdout`/`stderr` append directly to `/workspace/train_flooded_1600.log`.

```python
# /workspace/daemon_flooded_1600.py (Double-Forking Daemon)
pid = os.fork()
if pid > 0: sys.exit(0)
os.setsid()
pid2 = os.fork()
if pid2 > 0: sys.exit(0)
# Running as PID 1's child with no controlling TTY
```

#### Pillar 2: Signal Immunity (`trap '' HUP TERM`)
Setting signal masks to `SIG_IGN` (Ignore) prevents `SIGHUP` (Signal 1 - Hangup) and `SIGTERM` from terminating the worker processes:
```bash
trap '' HUP TERM
```
When `SIGHUP` or `SIGTERM` is generated upon terminal closure, the Linux kernel silently discards the signal, allowing `torchrun` and Python worker threads to continue computing uninterrupted.

#### Pillar 3: High-Frequency Checkpointing (`SAVE_STEPS=50`)
- **Default Issue**: At `save_steps: 200`, a checkpoint is only written once every **~40 minutes** (200 steps $\times$ 12s). If a session drops at step 942 or 997, all progress between step 800 and 997 (~35–40 minutes) is lost.
- **Optimized Setting**: Setting `SAVE_STEPS=50` writes a complete checkpoint every **~10 minutes**. Any unexpected halt rolls back at most 5–10 minutes.
- **Disk Safety**: With `save_total_limit: 5`, older checkpoints are pruned automatically, keeping disk usage bounded to ~50 GB (negligible on the 11 TB storage volume).

#### Pillar 4: I/O and RAM Quarantine (Preventing Cgroup OOM)
- **Sequential Execution**: Never run heavy 21 GB compression jobs (`tar` or `zip`) in parallel with active PyTorch training. Wait for training to complete before running archive compression.
- **Parallel Multi-Core Compression (`pigz`)**: When packaging converted checkpoints, always use parallel `pigz` across CPU cores (`tar --use-compress-program=pigz -chf ...`), which finishes in ~1.5 minutes rather than choking disk I/O and page cache for 25+ minutes.

---

### C. Self-Healing Daemon Implementation (`daemon_flooded_1600.py`)

A persistent, self-healing supervisor loop continuously monitors training until the final converted and dereferenced deployment archive is produced:

```python
#!/usr/bin/env python3
import os, sys, time, signal, subprocess, datetime

TARGET_ARCHIVE = "/workspace/Alpamayo-1.5-10B-Matrix-Flooded-1600-A15.tar.gz"
LOG_FILE = "/workspace/train_flooded_1600.log"
PID_FILE = "/workspace/flooded_1600_daemon.pid"

def run_loop():
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    while not os.path.exists(TARGET_ARCHIVE):
        with open(LOG_FILE, "a") as out:
            proc = subprocess.Popen(
                ["/workspace/launch_matrix_training.sh", "flooded_1600"],
                stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                start_new_session=True, cwd="/workspace"
            )
            with open("/workspace/train_flooded_1600.pid", "w") as pf:
                pf.write(str(proc.pid))
            proc.wait()

        if os.path.exists(TARGET_ARCHIVE):
            break
        time.sleep(10)

def main():
    if os.fork() > 0: sys.exit(0)
    os.setsid()
    if os.fork() > 0: sys.exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdin.fileno())
    run_loop()

if __name__ == "__main__":
    main()
```

---

### D. Monitoring Commands

```bash
# 1. Watch real-time training stream & step loss:
tail -f /workspace/train_flooded_1600.log

# 2. Check GPU compute & power draw (expect ~300W and ~43.5 GB VRAM):
nvidia-smi

# 3. Confirm immune daemon is running under PPID 1:
ps -ef | grep -E "daemon_flooded|train_hf"

# 4. Verify latest 50-step checkpoints:
ls -ld /workspace/alpamayo-recipes/recipes/alpamayo1_5_sft/output_stage2_flooded_1600/checkpoint-*
```

