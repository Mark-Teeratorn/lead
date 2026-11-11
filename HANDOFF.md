# AI AGENT HANDOFF & PROJECT CONTINUATION GUIDE
**Project Title:** Distribution Curation and Closed-Loop Standstill in Continuous-Action Autonomous Driving: An Empirical Evaluation Across Scale  
**Repository Path:** `/home/aimslab/lead`  
**Current Date/Time:** November 11, 2026 — 18:25 +07:00  
**Latest Git Commit:** `ff21075f` (branch `main`)  
**Hardware:** Single NVIDIA GeForce RTX 4090 (24 GB VRAM), Ubuntu 22.04 LTS (Kernel 6.8, CUDA 13.4)  

---

## 1. Executive Summary & Context

This repository contains the codebase, empirical evaluation harness, and academic paper evaluating continuous-action Vision-Language-Action (VLA) models—specifically **Alpamayo 1.5 (10B hybrid with 2.28B Flow-Matching Action Expert)**—in closed-loop autonomous driving on CARLA 0.9.15 and the Bench2Drive benchmark suite.

### The Research Question
Does naive edge-case demonstration gathering ("hazard flooding") induce imitation-learning inertia / causal confusion freezing in continuous Flow-Matching action experts, and does distribution curation ($2\%$ stationary frame cap + $50{:}25{:}25$ steering symmetry) resolve this standstill at scale ($6,400$ frames)?

### Current Milestone
- **Phase 1 (Zero-Compute / Text & Tables):** **100% COMPLETE & COMMITTED** to git (`84b3eb3e`). All reviewer critiques (overclaim language, Table 2 premature labeling, missing strata columns, missing gate accounting, missing 0.5m collapse stress test) are fully addressed.
- **Phase 2 (GPU Compute / 44-Route Confirmatory Rerun):** **ACTIVELY RUNNING IN BACKGROUND.** Evaluating the contemporaneous `Matrix-Flooded-6400` checkpoint across all 44 canonical Bench2Drive routes.

---

## 2. Real-Time System & Process Status

### 2.1 Live GPU & Service State (NVIDIA RTX 4090)
| Process | PID | Function | VRAM Usage |
| :--- | :--- | :--- | :--- |
| **FlashDrive Server** | `580518` | Model inference server running `extracted_matrix_flooded_6400` on socket `/tmp/alpamayo_flashdrive.sock` | **$\approx 14.3\text{ GB}$** |
| **CARLA Simulator** | `582570` | CARLA 0.9.15 (`CarlaUE4-Linux-Shipping`) running synchronously at 20 Hz | **$\approx 5.5\text{ GB}$** |
| **Supervisor Watchdog** | Background daemon | Monitors `run_full_44_matrix_flooded_6400.sh`, auto-recovers if frozen | Negligible CPU |

*Total GPU VRAM:* $\approx 19.9\text{ GB} / 24.56\text{ GB}$ ($81\%$ load, leaves clean headroom).

### 2.2 Evaluation Progress
- **Harness:** Bench2Drive 44 Canonical Routes (`CANONICAL_44`).
- **Log File:** `/home/aimslab/lead/outputs/full_44_matrix_flooded_6400_progress.log`
- **Supervisor Log:** `/home/aimslab/lead/outputs/watchdog_supervisor_matrix_flooded_6400.log`
- **Progress Snapshot:**
  - Route 1/44 (`RouteScenario_2534: Accident`, Town01): **COMPLETED** ($\text{DS}=60.00, \text{RC}=100.0\%$, 1 collision).
  - Route 2/44 (`RouteScenario_1852: AccidentTwoWays`, Town01): **COMPLETED** ($\text{DS}=60.00, \text{RC}=100.0\%$, 1 collision).
  - Remaining: Routes 3 to 44 running sequentially. Runtime is $\sim 15\text{--}20$ minutes per route ($\approx 14\text{ hours}$ remaining).

---

## 3. Key Model & Code Provenance (Cryptographic Hashes)

All model weights and evaluation files have verified SHA-256 checksums to ensure perfect reproducibility:

1. **Target Action Expert Checkpoint (`Matrix-Flooded-6400`):**
   - Path: `/home/aimslab/checkpoints/action_experts/extracted_matrix_flooded_6400/action_expert.safetensors`
   - Size: $4,561,232,672\text{ bytes}$ ($4.25\text{ GiB}$, 416 parameter tensors)
   - **SHA-256:** `5707c517e2a39f8bd2d5bf2840966fd1b5ecb59ddc3d4fd308dffa7401214940`
   - Shard Source: `/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Flooded-6400-A15` (5 shards, recorded in `source_shards_sha256.json`)

2. **Reference Champion Checkpoint (`Golden-6400`):**
   - Path: `/home/aimslab/checkpoints/action_experts/Alpamayo-1.5-10B-Matrix-Golden-6400-A15/action_expert.safetensors`
   - **SHA-256:** `641287335d43877349cc633611ac85fe28628d0e4130eb59d055402926e8a2bf`

3. **Tracking Controller & Bridge Agent:**
   - Path: `/home/aimslab/lead/src/lead/evaluation/agents/alpamayo/alpamayo_bridge_agent.py`
   - **SHA-256:** `082c6ecc079e8424ac7d3b7bab3b9cbd4883440098f02e4f12a644eff7b610d3`
   - Standstill Gate Threshold: $(L_{\text{traj}} < 1.5\text{ m}) \lor (v_{\text{ego}} < 0.5\text{ m/s} \land L_{\text{traj}} < 2.0\text{ m})$.

4. **Git Pre-Registration Document:**
   - Path: `/home/aimslab/lead/docs/CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md`
   - Committed at commit `013a12bd`. Pre-registers H2 endpoint, Wilcoxon signed-rank test, 20,000-resample BCa bootstrap CI, and pre-specified Decision Rules.

---

## 4. Completed Phase 1 Fortifications (Manuscript Defenses)

The manuscript text (`.txt`) and Word document (`.docx`) are located at:
- Text: `/home/aimslab/lead/docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.txt`
- Word: `/home/aimslab/lead/docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.docx`

### Specific Items Resolved & Verified in the Paper:
1. **Defused Premature Pre-Registration Claim in Table 2:**
   - The row for `Flooded-6400 (Contemporaneous)` now lists:  
     `| Flooded-6400 (Contemporaneous) | large_v3 | 6,400 | TBD | TBD | TBD | 1.0e-6 | Oct 20, 2026 | Pending Rerun | Target of pre-registered protocol (git 013a12bd) |`
2. **Purged All Overclaim Wording:**
   - §4.3: Removed *"proves conclusively... directly diagnosing imitation-learning paralysis"*; replaced with *"This observation indicates that `Flooded-6400`'s excess standstill occurs on open roads with zero signals and zero pedestrians, supporting the imitation-learning inertia hypothesis."*
   - §3.2: Replaced *"reinforce these low-velocity attractors"* with *"fail to alleviate these low-velocity attractors"*.
   - §6 Conclusion: Replaced *"generalizes consistently to 175 unseen routes"* with *"demonstrates operational out-of-sample route completion across 175 unseen Bench2Drive routes within a wide 95% bootstrap confidence interval ([-11.81, +7.75] DS)"*.
3. **Complete 5-Strata Breakdown Added (Table 4):**
   Table 4 now reports all 5 Bench2Drive ground-truth functional abilities partitioning all 44 routes:
   - *Open Maneuver ($N=25$):* `Base` $= 43.67\%$, `Flooded-1600` $= 31.05\%$, `Golden-1600` $= 30.23\%$, `Flooded-6400` $= 37.79\%$, `Golden-6400` $= \mathbf{24.66\%}$
     - *Overtaking ($N=9$):* `Flooded-6400` $= 50.11\%$ vs. `Golden-6400` $= \mathbf{32.52\%}$ ($\Delta = -17.59\%$)
     - *Merging ($N=16$):* `Flooded-6400` $= 30.86\%$ vs. `Golden-6400` $= \mathbf{20.24\%}$ ($\Delta = -10.62\%$)
   - *Emergency Braking ($N=12$):* `Flooded-6400` $= 26.38\%$ vs. `Golden-6400` $= 31.86\%$ (yielding to pedestrians preserved)
   - *Traffic Signs ($N=5$):* `Flooded-6400` $= 40.41\%$ vs. `Golden-6400` $= \mathbf{22.20\%}$ ($\Delta = -18.20\%$, green-light freezing eliminated)
   - *Give Way ($N=2$):* `Flooded-6400` $= 14.34\%$ vs. `Golden-6400` $= \mathbf{10.85\%}$
4. **Gate Accounting Added to §4.3:**
   - Documented that on **$73.73\%$ of Flooded standstill steps** and **$86.30\%$ of Golden standstill steps**, the gate does NOT fire ($L_{\text{traj}} \ge 2.0\text{ m}$).
   - The gate explains $\approx 5.39$ of the $8.19$ percentage-point gap; the remaining $2.80$ percentage points ($34\%$) occur without the gate firing at all.
5. **0.5 m Extreme Trajectory Collapse Stress Test Added to §4.3:**
   - Under $L_{\text{traj}} < 0.5\text{ m}$, `Flooded-6400` collapses on **$4.75\%$** of steps vs. only **$0.54\%$** for `Golden-6400` (an **$8.8\times$ divergence**, $p = 1.0 \times 10^{-6}$).
6. **Correct Table Numbering Maintained:**
   - Table 1: $2 \times 2$ Factorial Curation Matrix
   - Table 2: Training Provenance and Checkpoint Details
   - Table 3: Overall 5-Model Closed-Loop Benchmark ($N=44$)
   - Table 4: 20 Hz Standstill Decomposition & Complete Strata Breakdown

---

## 5. How to Monitor the Ongoing Run (Cheat Sheet)

You do **NOT** need to restart anything; the run is actively executing. Use these commands to inspect progress:

### 1. View Live Step Telemetry
```bash
tail -f /home/aimslab/lead/outputs/full_44_matrix_flooded_6400_progress.log
```

### 2. View Supervisor Watchdog Log
```bash
tail -n 25 /home/aimslab/lead/outputs/watchdog_supervisor_matrix_flooded_6400.log
```

### 3. Check Count of Completed Routes
```bash
python3 -c "
import glob, json
routes = glob.glob('/home/aimslab/lead/outputs/local_evaluation/model_matrix_flooded_6400_*/checkpoint_endpoint.json')
completed = [p for p in routes if 'scores_mean' in json.load(open(p)).get('_checkpoint',{}).get('global_record',{})]
print(f'Completed routes: {len(completed)} / 44')
"
```

### 4. Check GPU Memory & Power
```bash
nvidia-smi
```

---

## 6. What to Do Once the 44 Routes Finish (Next AI Action Items)

When all 44 routes reach `Completed` status in `outputs/watchdog_supervisor_matrix_flooded_6400.log`:

### Step 1: Run Deterministic Table Computation
Execute the committed table computation script:
```bash
python3 /home/aimslab/lead/scripts/evaluation/compute_paper_tables.py
```
This automatically parses all 44 `checkpoint_endpoint.json` and `predicted_trajectories.jsonl` files for both models and writes a verified JSON manifest:
`/home/aimslab/lead/outputs/paper_tables_unified_manifest.json`.

### Step 2: Compare Golden-6400 vs Contemporaneous Flooded-6400
Check the output from the manifest:
1. Mean Standstill ($v < 0.1\text{ m/s}$): Golden-6400 ($25.71\%$) vs. new Flooded-6400.
2. Paired Wilcoxon Signed-Rank $p$-value and 20,000-resample BCa bootstrap 95% CI.
3. Apply the Pre-Registered Decision Rules from [`CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md`](file:///home/aimslab/lead/docs/CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md):
   - **Case A (Confirmed Curation Advantage):** Standstill reduction $\ge 5.0$ percentage points, Wilcoxon $p < 0.05$. (Confirms primary hypothesis H2).
   - **Case B (Attenuated / Schedule Confound):** Standstill reduction $< 5.0$ percentage points. (Honestly report training schedule impact).
   - **Case C (Sensitivity Analysis):** Compare the historical Oct 7 Flooded-6400 ($33.91\%$) against the contemporaneous Oct 20 Flooded-6400 to quantify multi-seed / schedule variance.

### Step 3: Update Table 2 in Manuscript
Edit `/home/aimslab/lead/docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.txt`:
- Update the `Flooded-6400 (Contemporaneous)` row in Table 2: replace `TBD` with the actual metrics and update the status from `Pending Rerun` to `Completed confirmatory evaluation`.
- Add the paired Wilcoxon and bootstrap result alongside the historical comparison.

### Step 4: Recompile Word Document (.docx)
Run the automated OMML docx builder:
```bash
python3 /home/aimslab/.gemini/antigravity/brain/a4159320-cec9-4e6d-beb7-b31a0168afce/scratch/build_manuscript_docx.py
```
Verify that the output file `/home/aimslab/lead/docs/Distribution-Curated Fine-Tuning Reduces Closed-Loop Standstill at Scale in Continuous-Action Autonomous Driving.docx` is cleanly updated.

### Step 5: Git Commit & Finalization
```bash
git -C /home/aimslab/lead commit -am "docs: integrate contemporaneous Flooded-6400 confirmatory evaluation results"
```

---

## 7. Important Architectural Details & Caveats

1. **FlashDrive Boot Time:** The server takes $\sim 3\text{--}4$ minutes to boot because it initializes the 8B Qwen-VL language backbone, loads the W4A8 quantized Pairwise Rotation Quantization (PARO) weights, and initializes the DFlash speculative drafting model. Once loaded, patching the 416 action expert tensors takes only **1.15 seconds**. Do not kill the server while it is in this 3-minute warm-up window.
2. **Controller File Invariance:** The controller script `alpamayo_bridge_agent.py` has SHA-256 `082c6ecc079e8424ac7d3b7bab3b9cbd4883440098f02e4f12a644eff7b610d3`. Under no circumstances should this file be modified during evaluation, as holding it invariant guarantees that all behavioral differences stem strictly from the action expert weights.
3. **Preservation of Historical Oct 7 Model:** Never delete or overwrite `model_6400` data. The paper reports both the historical model (Oct 7) and the contemporaneous model (Oct 20) to maintain full transparency and measure training run variability.
