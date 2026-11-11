# Pre-Registration: Confirmatory Closed-Loop Evaluation of Contemporaneous Matched Flooded-6400

**Document Type:** Formal Pre-Registration & Confirmatory Evaluation Protocol  
**Date:** November 11, 2026  
**Authors / Affiliation:** Autonomous Intelligent Multi-Agent Systems Lab (AIMS Lab)  
**Target Manuscript:** *Distribution Curation and Closed-Loop Standstill in Continuous-Action Autonomous Driving: An Empirical Evaluation Across Scale*  
**Repository Commit Reference:** Pre-committed prior to simulator execution.

---

## 1. Prior Knowledge & Pre-Registration Scope

To ensure scientific integrity and eliminate post-hoc outcome selection, we explicitly declare the prior state of knowledge before launching this evaluation:
* **Known Historical Data:**
  * Performance of the zero-shot unadapted `Base` model ($N = 44$ routes).
  * Matched $1,600$-frame scale policies (`Flooded-1600` and `Golden-1600`, $N = 44$ routes).
  * Curated $6,400$-frame model `Golden-6400` (`Alpamayo-1.5-10B-Matrix-Golden-6400-A15`, $N = 44$ routes).
  * Historical $6,400$-frame flooded model (`checkpoint-6400`, trained Oct 7 on `large_v3` with 8 epochs / 6,415 steps, $N = 44$ routes).
* **Target of this Evaluation:**
  * Evaluation of `Alpamayo-1.5-10B-Matrix-Flooded-6400-A15` (trained Oct 20, 2026, contemporaneously with `Golden-6400`).
  * This run evaluates whether the standstill reduction observed between `Golden-6400` and the historical Oct 7 flooded checkpoint replicates when compared against a contemporaneously packaged flooded checkpoint from the same training batch.

---

## 2. Hypotheses and Endpoints

### 2.1 Primary Endpoint ($H_2$)
* **Definition:** Closed-loop standstill fraction, defined as the proportion of simulation steps where ego-vehicle velocity is below $0.10\text{ m/s}$ ($v_{\text{ego}} < 0.1\text{ m/s}$) sampled at $20\text{ Hz}$ across the $N = 44$ canonical Bench2Drive routes.
* **Comparison:** Paired head-to-head comparison between `Golden-6400` and `Matrix-Flooded-6400`.
* **Primary Statistical Test:** Two-sided paired Wilcoxon signed-rank test ($\alpha = 0.05$).
* **Confidence Interval:** Two-sided $95\%$ BCa bootstrap confidence interval ($20,000$ resamples, fixed $\text{seed} = 0$).

### 2.2 Secondary Endpoints
1. **Benchmark Composite Scores:** Composite Driving Score ($\text{DS}$) and Route Completion percentage ($\text{RC}$).
2. **Controller Short-Trajectory Gate Firing Rate:** Percentage of simulation steps where predicted trajectory extent triggers the holding-brake gate condition:
   $$(L_{\text{traj}} < 1.5\text{ m}) \lor (v_{\text{ego}} < 0.5\text{ m/s} \land L_{\text{traj}} < 2.0\text{ m})$$
   reported across all simulation steps and specifically conditioned on standstill steps.
3. **Trajectory Length:** Mean cumulative arc length of the predicted 64-waypoint horizon ($L_{\text{traj}} = \sum \lVert \mathbf{y}_k - \mathbf{y}_{k-1} \rVert_2$).
4. **Collision Disaggregation:** Total collision events disaggregated by actor type:
   * Vehicle collisions (`collisions_vehicle`)
   * Layout / infrastructure collisions (`collisions_layout`)
   * Pedestrian / vulnerable road user collisions (`collisions_pedestrian`)
5. **Stratum-Level Standstill Breakdown:** Standstill fraction evaluated across all 5 Bench2Drive abilities:
   * Open Maneuver routes ($N = 25$, zero traffic signals, zero stop signs, zero pedestrians).
   * Overtaking routes ($N = 9$, obstacle avoidance bypasses).
   * Merging routes ($N = 16$, traffic flow entries and unprotected turns).
   * Emergency Braking routes ($N = 12$, dynamic crossing actors).
   * Traffic Signs routes ($N = 5$, signalized and stop-controlled intersections).
   * Give Way routes ($N = 2$, priority yields).

### 2.3 Sensitivity Analysis
* Paired comparison between Historical `checkpoint-6400` (Oct 7) and Contemporaneous `Matrix-Flooded-6400` (Oct 20) across all 44 canonical routes to quantify training schedule and checkpoint-to-checkpoint variance under hazard flooding.

### 2.4 Multiplicity Control
* Holm-Bonferroni correction at family-wise $\alpha = 0.05$ across the 2-test primary family:
  * $H_1$: Adaptation gain (`Golden-1600` vs. `Base` Driving Score, $p_1$).
  * $H_2$: Standstill reduction (`Golden-6400` vs. `Matrix-Flooded-6400` standstill fraction, $p_2$).
* All other exploratory endpoints and stratum breakdowns are reported with unadjusted two-sided $p$-values and explicit bootstrap confidence intervals.

---

## 3. Objective Decision Rules

The reporting and manuscript framing will follow these pre-specified rules based on the primary endpoint bootstrap confidence interval:

```
                                  PRIMARY DECISION MATRIX
                                  
      [ Upper bound of 95% BCa CI on (Golden - Flooded Standstill) ]
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
     CI Upper < 0.0%                                     CI Upper ≥ 0.0%
           │                                                   │
     ┌─────┴──────────────┐                              ┌─────┴──────────────┐
     ▼                    ▼                              ▼                    ▼
 Point Est ≤ -4.0%   Point Est > -4.0%             Point Est < 0.0%      Point Est ≥ 0.0%
 [CASE A: REPLICATED] [CASE A2: PARTIAL]           [CASE B: SUGGESTIVE]  [CASE C: NOT REPLICATED]
 Strong replication; Moderate replication;         Inconclusive; frame   Attributed to schedule;
 report both models   quantify duration confound   as observation only   pivot to symmetry/safety
```

* **Case A: Confirmed Replication (CI Excludes Zero):**
  * The $95\%$ BCa bootstrap CI for $(\text{Standstill}_{\text{Golden}} - \text{Standstill}_{\text{Flooded}})$ strictly excludes zero in the negative direction (upper bound $< 0.00\%$).
  * *Sub-case A1 (Strong Replication):* Point estimate $\Delta \le -4.0\text{ percentage points}$ (at least half the historical effect size). Conclude that distribution curation robustly suppresses closed-loop standstill.
  * *Sub-case A2 (Partial Attenuation):* Point estimate $-4.0\text{ pp} < \Delta < 0.0\text{ pp}$. Conclude that curation reduces standstill, but attribute the residual historical difference to training duration/batch-size variance.
* **Case B: Inconclusive (CI Spans Zero):**
  * Point estimate indicates lower standstill for Golden ($\Delta < 0.00\%$), but the $95\%$ bootstrap CI crosses zero.
  * Report as a suggestive trend; reframe the paper around observed empirical associations rather than confirmed universal effects.
* **Case C: Not Replicated (Zero or Opposite Direction):**
  * Point estimate $\Delta \ge 0.00\%$.
  * Report plainly and honestly. The historical standstill difference is formally attributed to training schedule differences. Reframe the paper around distributional symmetry, lateral lane-drift elimination, and collision bounding under curation.

---

## 4. Execution Protocol & Run Integrity Rules

1. **Deterministic Environment:**
   * CARLA 0.9.15 executed in headless synchronous mode at $20\text{ Hz}$ ($\Delta t_{\text{sim}} = 0.05\text{ s}$).
   * Rendering quality set to Epic (`DefaultScalability.ini`).
   * Simulator client timeout fixed at $180\text{ seconds}$.
   * Controller code fixed to `alpamayo_bridge_agent.py` (verified via SHA-256 hash).
2. **Sequential Single-Pass Execution:**
   * All $N = 44$ routes are executed sequentially from index 0 to 43 without manual intervention.
3. **Strict Rerun Rules:**
   * A route may **only** be re-run in the event of documented infrastructure failure:
     * CARLA Unreal Engine process crash (`SIGSEGV` or core dump).
     * CARLA client RPC timeout (`carla::client::TimeoutException` exceeding 180s).
   * **Zero post-score reruns:** Under no circumstances will a route be re-run after a driving score or completion percentage is generated, regardless of performance.
   * Every infrastructure failure and subsequent restart must be recorded in `outputs/rerun_audit_matrix_flooded_6400.log` with timestamp, route ID, and process exit code.
4. **Data Locking:**
   * Raw simulation outputs (`predicted_trajectories.jsonl` and `checkpoint_endpoint.json`) are preserved unedited.
   * All summary tables are generated automatically via `scripts/evaluation/compute_paper_tables.py`.

