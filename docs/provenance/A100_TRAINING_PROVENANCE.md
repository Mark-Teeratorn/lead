# Training provenance reported by the A100 session (12 Nov 2026)

Report from the Claude session on the A100 training machine, produced read-only from trainer artifacts and logs under `/workspace`. The evidence bundle was copied to this machine on 12 Nov 2026 and its small text files are in `docs/provenance/a100_bundle/` (191 of 198 files; the five `annotations_train.json`, one `annotations_val.json` and one training log over 1 MB are omitted, the annotation files being the published datasets themselves). Full quoted evidence is in `a100_bundle/REPORT.md`. The values below were re-read from the bundle on this machine: the seven `trainer_state.json` files match the table, and the `config.yaml` files of the two 6,400-frame Matrix runs are identical apart from the dataset name.

The dataset build script (`scripts/build_curation_matrix.py`, in the `ad-research` / `lead2alpa` repository on another machine) was supplied by the author in conversation on 12 Nov 2026; it should be added to this folder as a file. The datasets are published on the Hugging Face Hub as `earth37815/lead-alpamayo-pai_matrix_{golden,flooded}_{1600,6400}` and `earth37815/lead-alpamayo-pai_matrix_floodedgroups_balanced_6400`.

Evidence tags: [A] trainer artifact (`trainer_state.json`, `training_args.bin`, Hydra `config.yaml`); [L] log or launch script; [C] computed by the reporting session.

## Schedules

| Run | Samples | Epochs | Per-device batch | Grad. accumulation | Optimizer steps | LR schedule, warmup | Seed | Resume events | Exported checkpoint | Dates (UTC) |
|---|---|---|---|---|---|---|---|---|---|---|
| golden_1600 | 1,600 [A] | 10 [A] | 1 [A] | 8 [A] | 2,000 [A] | cosine with min LR, 1e-4 → 1e-6, warmup 100 [A] | 42 [A] | fresh start 16 Oct 11:07; several resumes from checkpoint-800 (one CUDA OOM); final resume 21:40 ran 800 → 2,000 [L] | checkpoint-2000 | 16 Oct 11:07 → 17 Oct 01:43 |
| flooded_1600 | 1,600 | 10 | 1 | 8 | 2,000 | same, warmup 100 | 42 | fresh start 17 Oct 06:39 (log stops at step 215); resumes 08:51 / 08:53 (log missing); final 10:24 resumed at 250 → 2,000 [L] | checkpoint-2000 | 17 Oct 06:39 → 16:49 |
| golden_6400 | 6,400 | 10 | 1 | 8 | 8,000 | same, warmup 200 | 42 | none; single run 0 → 8,000 [L] | checkpoint-8000 | 17 Oct 18:49 → 18 Oct 23:05 |
| flooded_6400 | 6,400 | 10 | 1 | 8 | 8,000 | same, warmup 200 | 42 | none; single run 0 → 8,000 [L] | checkpoint-8000 | 19 Oct 07:52 → 20 Oct 12:25 |
| v3 phase 1 (historical) | 6,440 | 8 planned, stopped at epoch 4.97 [A] | 1 | 8 | 4,000 saved of 6,440 planned [A] | 1e-4 → 1e-6, warmup 200 | 42 | log ends at 4,180 / 6,440 with no exit message [L] | checkpoint-4000 | 5 Oct 13:13 → 6 Oct 03:10 |
| v3 phase 2 (historical, the evaluated "Flooded-6400 (Historical)") | 6,440 | 3 [A] | 1 | 8 | 2,415 [A] | 3.5e-5 → 1e-6, warmup 50 [A] | 42 | **not a trainer resume**: a new run initialised from checkpoint-4000 weights with a fresh optimizer, scheduler and step counter [A] | checkpoint-2415 = "Lead-Large-v3-6400-A15" [L] | 6 Oct 11:47 → 20:08 |
| v4 (not in the paper's matrix) | 16,040 [C] | 10 [A] | 1 | 8 | 20,050 [A] | 1e-4 → 1e-6, warmup 200 | 42 | none seen | checkpoint-20050 | 8 Oct 20:37 → 11 Oct 16:11 |

Common to all runs [A]: optimizer `adamw_torch_fused` (betas 0.9 / 0.999, eps 1e-8), weight decay 0, gradient-norm clip 1.0, bf16, `max_steps = -1` (steps follow from epochs), `cotrain_vlm: false` (VLM frozen), no callbacks (no EMA), 2,280,592,386 trainable parameters.

Consequences for the manuscript:
- The two 6,400-frame Matrix models share an identical schedule (10 epochs, effective batch 8, 8,000 steps, warmup 200, seed 42, uninterrupted).
- The two 1,600-frame Matrix models share a schedule (2,000 steps, warmup 100) but both were interrupted and resumed.
- 20,050 steps belongs to v4, not Golden-6400.
- The historical flooded model is a two-phase run with a restarted optimizer and learning-rate schedule; "6,415 steps" and "8 epochs" are sums (4,000 + 2,415; 4.97 + 3.0), not logged counters. There is no "checkpoint-6400".
- Training dates in Table 2 are also off (e.g. flooded_6400 trained 19–20 Oct; golden_6400 17–18 Oct).

## Archives (size, SHA-256, computed on the A100)

| Archive | Bytes | SHA-256 | Matches the copy on the 4090 |
|---|---|---|---|
| Matrix-Golden-1600-A15.tar.gz | 17,616,983,912 | `03f74a05ad0a37276a76b971010f0ebd0ef2d5427c5433d5359fa1c41ca727cf` | not checked |
| Matrix-Flooded-1600-A15.tar.gz | 17,617,076,949 | `4218edc8d71d885b7d0d936ee88a21b6db9f11ed6618d3230b39c07ff43b1eb3` | not checked |
| Matrix-Golden-6400-A15.tar.gz | 17,605,502,448 | `9b6213b4fbba66937ec3f025dde5cf73a1d2fde96365920601af3e56aeb93db9` | size matches |
| Matrix-Flooded-6400-A15.tar.gz | 17,604,928,794 | `0bd5161e32c28277204edee3f846ddfabc1333c1b5a286eb30a92338b0712a6f` | size matches |

## Datasets [A: each folder's `conversion_stats.json` and `README.md`]

- Train samples 1,600 / 1,600 / 6,400 / 6,400; one shared validation split of 1,567 samples (byte-identical annotation file). Sampling stride 0.4 s. Build seed 0, deterministic selection.
- **Both regimes are drawn from the same pool** (`lead_multirig_pai_v4`, 34,132 training samples); only the target marginals differ, each fitted by iterative proportional fitting. The dataset README states "Flooded does not mean uncurated".
- Golden targets: scenario groups A–F 27 / 18 / 17 / 14 / 14 / 10 %; straight / swerve-L / swerve-R / turn-L / turn-R 50 / 13 / 13 / 12 / 12 %; stationary 2.0 % (32 / 128 samples).
- Flooded targets: groups 35 / 14 / 22 / 10 / 9 / 10 %; manoeuvres 22 / 37 / 12 / 14.5 / 14.5 %; stationary 10.0 % (160 / 640 samples).
- Nesting [C]: golden_1600 ⊂ golden_6400 and flooded_1600 ⊂ flooded_6400; **golden_6400 ∩ flooded_6400 = 4,284 samples** (67 % of each).
- Build script `build_curation_matrix.py` is not on the A100.

## Low-speed frames: waiting versus starting [C]

Among training samples with ego speed ≤ 0.5 m/s at the current frame, the 6.4 s ground-truth future path either stays put (< 0.64 m), starts moving (≥ 2 m), or is in between:

| Dataset | Speed ≤ 0.5 m/s | Stays put | Starts moving | In between | Stays put, share of low-speed |
|---|---|---|---|---|---|
| golden_1600 | 387 | 44 | 302 | 41 | 11.4 % |
| flooded_1600 | 549 | 168 | 346 | 35 | 30.6 % |
| golden_6400 | 1,568 | 171 | 1,250 | 147 | 10.9 % |
| flooded_6400 | 2,138 | 662 | 1,339 | 137 | 31.0 % |

(Shares in the last column are computed here from the reported counts.)

## Not found on the A100

The log of flooded_1600's 08:51 / 08:53 attempts (so which attempt wrote checkpoint-250 is unknown); why flooded_1600's first attempt stopped at step 215; why v3 phase 1 stopped at 4,180; the dataset build script. `pipeline_status.json` defines "final_loss" inconsistently across runs and should not be quoted.

## Evaluation-route overlap in the training sets [A: `conversion_stats.json`, dataset `README.md`]

The training splits are **not** route-disjoint from Bench2Drive. Each dataset README says so explicitly ("Eval-route overlap in training — read this before scoring on Bench2Drive"): the eval-overlap filter is not applied to the training split.

| Dataset | Train samples on a route overlapping one of the 220 Bench2Drive eval routes | ... overlapping the 44-route main-test subset |
|---|---|---|
| golden_1600 | 114 (7.12 %) | 23 (1.44 %) |
| flooded_1600 | 117 (7.31 %) | 16 (1.00 %) |
| golden_6400 | 462 (7.22 %) | 91 (1.42 %) |
| flooded_6400 | 479 (7.48 %) | 72 (1.12 %) |

40 of 581 training routes overlap the full evaluation set and 13 overlap the 44-route subset. These are lower bounds (39 log names could not be resolved to a route). The overlapping subset routes belong to the scenarios AccidentTwoWays, ConstructionObstacleTwoWays, ControlLoss, EnterActorFlow, EnterActorFlowV2, OppositeVehicleTakingPriority, T_Junction and VehicleTurningRoute. The shared validation split has no overlap (153 samples were removed for that reason).

**Exact mapping to the 44 canonical routes** (computed on 12 Nov 2026 from `gate_validation_lead.json`, `audit_curation_matrix.route_key` and each cell's `annotations_train.json`; result in `train_eval_overlap_canonical44.json`). The gate flags 69 training routes, which touch 57 evaluation route ids, 11 of them canonical: 1852, 2513, 1825, 2286, 23901, 23695, 2790, 2283, 23771, 3464, 2164. Training samples that are actually in the Matrix cells touch seven of those:

| Canonical eval route (scenario) | golden_1600 | flooded_1600 | golden_6400 | flooded_6400 |
|---|---|---|---|---|
| 1852 (AccidentTwoWays) | 1 | 2 | 3 | 7 |
| 1825 (ConstructionObstacleTwoWays) | 2 | 4 | 6 | 13 |
| 2286 (HighwayCutIn) | 6 | 2 | 21 | 15 |
| 23901 (InterurbanActorFlow) | 1 | 1 | 4 | 4 |
| 23695 (InterurbanAdvancedActorFlow) | 1 | 1 | 4 | 4 |
| 3464 (VehicleOpensDoorTwoWays) | 5 | 7 | 23 | 38 |
| 2164 (VehicleTurningRoutePedestrian) | 4 | 2 | 17 | 6 |
| Samples touching any canonical route | 20 | 19 | 78 | 87 |

(The dataset READMEs report 91 and 72 samples for a "44-route main-test subset"; that subset file is not the canonical list used in the paper, so the counts differ.) Unresolved log names: 25 to 117 samples per cell, counted as non-overlapping.

Sensitivity of the two primary hypotheses to excluding overlapped routes:

| Routes | H2: Golden-6400 minus matched Flooded-6400, standstill (pp) | H1: Golden-1600 minus Base, Driving Score |
|---|---|---|
| all 44 | −8.06, CI [−15.08, −1.25], p = 0.00071 | +11.06, CI [2.62, 19.71], p = 0.0076 |
| without the 7 routes touched by Matrix training samples (N = 37) | −7.23, CI [−15.31, +0.66], p = 0.0065 | +13.67, CI [4.90, 23.11], p = 0.0065 |
| without all 11 gate-flagged canonical routes (N = 33) | −7.70, CI [−16.59, +1.20], p = 0.016 | +15.79, CI [7.90, 25.92], p = 0.0038 |

On non-overlapping routes the H2 point estimate is essentially unchanged and the Wilcoxon test remains significant, but the BCa interval reaches zero with the smaller N. H1 is not driven by the overlapped routes. (An earlier interim check in this file used scenario type as a proxy and is superseded by this table.)

## Other facts from the dataset READMEs and the build script

- "Flooded does not mean uncurated": all cells are curated draws from one pool (the same 1,840 clips over the same 646 routes). Nothing was over-collected.
- The regimes differ on three things at once: scenario-group mix, lateral balance and stationary share. The stationary target is applied as a within-bucket preference and moves no marginal; `brake` and `hazard` shares are observed outcomes, not targets (brake 35.4 % golden vs 41.3 % flooded at 6,400).
- Group mix and lateral balance are coupled in the pool (groups A + C hold 88 % of left swerves but 58 % of right swerves).
- A fifth dataset exists, `floodedgroups_balanced_6400`: Flooded's group mix with Golden's manoeuvre mix and 2 % stationary share. It separates group mix from the lateral-plus-stationary bundle. No model has been trained on it.
- Selection is deterministic (SHA-1 order salted by seed 0, no random number generator); the 1,600 cells are exact per-bucket quarters of the 6,400 cells.
