# LEAD: Deployment, Evaluation & Transfer Guide

This document details the complete end-to-end instructions for deploying, transferring, and running **LEAD** with **Alpamayo 1.5** and the **Bench2Drive** closed-loop benchmark on a new machine or cluster.

---

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 20.04 / 22.04 / 24.04 LTS)
- **GPU**: NVIDIA GPU with 24 GB+ VRAM (RTX 4090, RTX 6000 Ada, A100, H100)
- **NVIDIA Driver**: 550+ (CUDA 12.x compatible)
- **Storage**:
  - ~100 GB for CARLA 0.9.15, environments, and checkpoints
  - Recommended: A dedicated SSD or high-speed NVMe mount (e.g. `/data` or `/home`)
- **Python Versions**:
  - **Python 3.10** for LEAD, CARLA 0.9.15 PythonAPI, and Leaderboard Evaluator
  - **Python 3.12** for the FlashDrive model server

---

## 2. Directory Layout & Overview

Recommended directory layout:
```
/home/<user>/
├── lead/                           # This repository (LEAD + Bench2Drive)
│   ├── 3rd_party/
│   │   ├── CARLA/fail2drive_0915/  # CARLA 0.9.15 Simulator binary
│   │   └── leaderboard/bench2drive/# Bench2Drive Leaderboard & Scenario Runner
│   ├── scripts/common/             # Evaluation and execution scripts
│   └── src/lead/                   # Agent bridge, routes, and controllers
├── flashdrive/                     # FlashDrive VLA model server repository
└── checkpoints/                    # Checkpoint storage
    ├── checkpoint-6400/            # Full sharded checkpoints (optional / symlinked)
    └── action_experts/             # Standalone Action Expert weights (~4.25 GB each)
        ├── action_model_1/         # Ckpt 600
        ├── action_model_2/         # Ckpt 640
        ├── action_model_3/         # Ckpt 600-3
        ├── action_model_4/         # Ckpt 1730 Non-EMA
        ├── action_model_4_ema/     # Ckpt 1730 EMA
        └── checkpoint-6400/        # Ckpt 6400 (v3 curated)
```

---

## 3. Installation Step-by-Step

### Step 1: Clone the Repository & Submodules

```bash
git clone git@github.com:Mark-Teeratorn/lead.git
cd lead
git submodule update --init --recursive
```

### Step 2: Set Up Python 3.10 Virtual Environment for LEAD

```bash
# Install uv package manager if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create Python 3.10 environment
uv venv .venv --python 3.10
source .venv/bin/activate

# Install LEAD dependencies
uv pip install -e .
uv pip install setuptools<81 packaging pyyaml shapely ephem tabulate
```

### Step 3: Install CARLA 0.9.15 (Fail2Drive Build)

CARLA 0.9.15 is the official simulator engine for the Bench2Drive benchmark:

```bash
mkdir -p 3rd_party/CARLA
cd 3rd_party/CARLA

# Download and unpack CARLA 0.9.15 Fail2Drive release
wget https://github.com/autonomousvision/carla_garage/releases/download/v0.1/fail2drive_0915.tar.gz
mkdir -p fail2drive_0915
tar -xzf fail2drive_0915.tar.gz -C fail2drive_0915
rm fail2drive_0915.tar.gz
cd ../..
```

Verify that the CARLA Python egg exists:
`3rd_party/CARLA/fail2drive_0915/PythonAPI/carla/dist/carla-0.9.15-py3.10-linux-x86_64.egg`

### Step 4: Set Up FlashDrive Model Server

In a sibling directory, clone and set up `flashdrive`:

```bash
cd ..
git clone git@github.com:Mark-Teeratorn/flashdrive.git
cd flashdrive

uv venv --python 3.12
source .venv/bin/activate
uv sync
cd ../lead
```
*(See `flashdrive/TRANSFER_GUIDE.md` for full model server configuration).*

---

## 4. Checkpoints & Action Expert Weights

Bench2Drive evaluates fine-tuned Action Expert weights on top of the 4-bit quantized base model. Only the standalone `action_expert.safetensors` (~4.25 GB) is needed for evaluation:

1. Unpack or download the checkpoint directory (e.g. `checkpoint-6400`).
2. Extract the Action Expert weights using the extraction utility:
```bash
/home/<user>/flashdrive/.venv/bin/python /home/<user>/flashdrive/scripts/extract_action_expert.py \
    --checkpoint /path/to/checkpoint-6400 \
    --output-dir /home/<user>/checkpoints/action_experts/checkpoint-6400
```
3. Symlink shortcuts (optional):
```bash
ln -s checkpoint-6400 /home/<user>/checkpoints/action_experts/action_model_5
```

---

## 5. Running Evaluations

All evaluation scripts automatically manage launching CARLA 0.9.15 headless, starting the FlashDrive model server, bridging IPC via `/tmp/alpamayo_flashdrive.sock`, and cleaning up resources upon completion.

### A. Full 44-Scenario Bench2Drive Evaluation (Detached Mode)

> [!IMPORTANT]
> Because evaluating all 44 routes takes 16–20 hours, **always execute via `setsid` in detached background mode** so your session will not terminate if your SSH terminal disconnects:

```bash
mkdir -p outputs
setsid bash scripts/common/eval_batch_44scenarios.sh 6400 </dev/null >> outputs/eval_44_model_6400.log 2>&1 &
```

#### Monitor Progress:
```bash
# View live tail of the master log:
tail -f outputs/eval_44_model_6400.log

# Print live comparison scorecard anytime:
bash scripts/common/eval_batch_44scenarios.sh 6400 --summary-only
```

### B. Model Shortcuts

`eval_batch_44scenarios.sh` supports convenient shortcuts:
- `1` : Action Model 1 (`checkpoints/action_experts/action_model_1`, Ckpt 600)
- `2` : Action Model 2 (`checkpoints/action_experts/action_model_2`, Ckpt 640)
- `3` : Action Model 3 (`checkpoints/action_experts/action_model_3`, Ckpt 600-3)
- `4` : Action Model 4 Non-EMA (`checkpoints/action_experts/action_model_4`, Ckpt 1730 Non-EMA)
- `4_ema` : Action Model 4 EMA (`checkpoints/action_experts/action_model_4_ema`, Ckpt 1730 EMA)
- `6400` : Action Model v3 (`checkpoints/action_experts/checkpoint-6400`, Ckpt 6400)
- `/path/to/dir` : Custom action expert path

### C. Options & Flags

```bash
# Evaluate only a specific scenario type (e.g. HighwayExit)
bash scripts/common/eval_batch_44scenarios.sh 6400 --scenario HighwayExit

# Force re-evaluation of completed routes
bash scripts/common/eval_batch_44scenarios.sh 6400 --force

# Launch CARLA with visual spectator display
bash scripts/common/eval_batch_44scenarios.sh 6400 --gui

# Run 5 Canonical benchmark subset
bash scripts/common/eval_batch_5canonical.sh 6400

# Run 5 Stress Test subset
bash scripts/common/eval_batch_5stresstest.sh 6400
```

---

## 6. Critical Reliability Fixes Implemented

The following critical stability patches have been integrated directly into this repository:

1. **Town13 Hybrid Physics Segfault Protection**:
   - *File*: `3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/leaderboard_evaluator.py:221`
   - *Fix*: `traffic_manager.set_hybrid_physics_mode(False)` is enforced. Enabling hybrid physics in Town13 causes null pointer dereferences (`SIGSEGV` Signal 11) in the CARLA C++ engine.
2. **60-Second Standstill Timeout Watchdog**:
   - *File*: `3rd_party/leaderboard/bench2drive/leaderboard/leaderboard/scenarios/scenario_manager.py:186`
   - *Fix*: Detects vehicles trapped in gridlock (>1,200 ticks at 0 km/h) and raises a graceful `TickRuntimeError` to log the distance completed without hanging the entire batch.
3. **Approach-Aware 6-Token Navigation Prompting**:
   - *File*: `src/lead/evaluation/agents/alpamayo/alpamayo_bridge_agent.py:268`
   - *Fix*: All navigation strings (`"Go straight along the road."`, `"Turn left at the intersection."`, etc.) are constrained to exactly 6 tokens to preserve static FlashDrive KV-cache tensor dimensions.
4. **Validation Check in Batch Evaluator**:
   - *File*: `scripts/common/eval_batch_44scenarios.sh:245`
   - *Fix*: Verifies that `checkpoint_endpoint.json` contains valid `"scores_mean"` before skipping routes, automatically re-running any corrupted or zero-byte runs.

---

## 7. Migration Verification Checklist

When setting up on a new server, verify each component in order:

- [ ] `nvidia-smi` confirms driver version 550+ and 24 GB+ GPU memory.
- [ ] Python 3.10 virtual environment activates with `import carla` working.
- [ ] Python 3.12 virtual environment activates in `flashdrive` with `import flashdrive` working.
- [ ] `action_expert.safetensors` exists in `checkpoints/action_experts/checkpoint-XXXX/`.
- [ ] Run a test route:
  ```bash
  bash scripts/common/eval_alpamayo_b2d.sh src/lead/routes/benchmark_routes/bench2drive/2534.xml
  ```
- [ ] Verify score output in `outputs/local_evaluation/alpamayo_2534/checkpoint_endpoint.json`.
