# Analysis Addendum to the Confirmatory Pre-Registration (Matrix-Flooded-6400)

**Date:** 12 November 2026
**Status:** written and committed **after** the 44-route evaluation of `Matrix-Flooded-6400` finished and **before** its primary endpoint (standstill fraction, Golden-6400 vs Matrix-Flooded-6400) was computed or viewed.
**What had been seen when this was written:** route statuses and their counts, run durations, logged-step counts, launch/result marker lines with scores masked, and the Driving Score of routes 2534 and 1852 (printed in `HANDOFF.md`). No standstill, speed, gate or trajectory statistic of the matched run had been computed.

This addendum does not change the primary endpoint, test, interval or decision rule in `CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md`. It fixes choices that document left open, corrects one factual error in it, and pre-specifies one new exploratory experiment.

## 1. Primary analysis: fixed details

- The primary result is the output of `scripts/evaluation/compute_paper_tables.py` at commit `84b3eb3e` (identical to the pre-registration commit `013a12bd` except for one blank line), run unmodified with the system `python3` (SciPy 1.18.1, NumPy 2.5.4). Its manifest is saved untouched as the confirmatory record before any script change.
- Wilcoxon: `scipy.stats.wilcoxon(x, y)` with library defaults (two-sided, `zero_method="wilcox"`, `method="auto"`). The extended report will additionally give the statistic, the number of zero differences, the exact and the asymptotic p-value, and the matched-pairs rank-biserial correlation. The decision rule uses the BCa interval and point estimate only, as pre-registered.
- Holm over the 2-test family (H1, H2) is reported as pre-registered. H1's p-value was known before the family was declared, so the correction adds no protection for H2; this will be stated. The earlier 4-test family is reported alongside.
- Decision rule (unchanged): A1 if CI upper < 0 and Δ ≤ −4.0 pp; A2 if CI upper < 0 and −4.0 < Δ < 0; B if Δ < 0 and the CI includes 0; C if Δ ≥ 0.

## 2. Strata: correction and frozen definitions

The pre-registration and the manuscript describe the 25 "Open Maneuver" routes as having "zero traffic signals, zero stop signs, zero pedestrians". That is not true: the group contains `SignalizedJunctionLeftTurn`, `SignalizedJunctionRightTurn`, `SignalizedJunctionLeftTurnEnterFlow`, three `NonSignalizedJunction*` routes, `CrossingBicycleFlow`, and five `*TwoWays` routes with oncoming traffic. The description is withdrawn. The following definitions are frozen now:

1. **Primary-ability strata (unchanged membership).** Each route is assigned the first ability, in the order Overtaking, Merging, Emergency_Brake, Give_Way, Traffic_Signs, whose official scenario list in `Bench2Drive/tools/ability_benchmark.py` contains its scenario. This reproduces `STRATA_MAP` in the script (9 / 16 / 12 / 2 / 5). The union of Overtaking and Merging (25 routes) is renamed **"Overtaking + Merging"**.
2. **Official multi-label abilities.** The same tables are also reported with the official overlapping lists (a route counts under every ability that lists its scenario).
3. **No junction control by scenario type (17 routes, post hoc).** The 9 Overtaking routes plus `HighwayCutIn` 2286, `HighwayExit` 23687, `InterurbanActorFlow` 23901, `InterurbanAdvancedActorFlow` 23695, `MergerIntoSlowTraffic` 2283, `MergerIntoSlowTrafficV2` 23771, `ParkingExit` 1956, `SequentialLaneChange` 17563. Defined from scenario type only; not verified against the map.
4. **Static-obstacle bypass, split by oncoming flow (post hoc, descriptive only).** Single-direction: 2534, 2513, 1790, 1773 (N = 4). Two-way: 1852, 1825, 3436, 2664, 3464 (N = 5).

All stratum results are exploratory and unadjusted.

## 3. Sensitivity analyses for the primary endpoint

- **Termination censoring.** The harness ends a route after 4,000 ticks or after 60 s continuously below 0.1 m/s (`scenario_manager.py` L183–192). H2 is repeated (a) on a common tick window per route (the first `min(n_Golden, n_Flooded)` logged steps of each route) and (b) with standstill counted as seconds per route instead of a fraction. The number of routes ended by the 60 s rule is reported per model.
- **Historical comparator.** Golden-6400 vs historical `checkpoint-6400`, and historical vs matched flooded, as pre-registered.
- **Thresholds.** Standstill at v < 0.05, 0.1, 0.2, 0.5 m/s.

## 4. Controller question: pre-specified exploratory work

**4a. Offline decomposition (existing logs).** Standstill steps of each model are split by predicted trajectory extent L: L < 0.64 m (the trajectory's own planned speed L / 6.4 s is below the 0.1 m/s standstill threshold, so the gate cannot be the cause); 0.64 ≤ L < 1.5 m (gate overrides a planned crawl); 1.5 ≤ L < 2.0 m with v < 0.5 m/s (hysteresis clause only); L ≥ 2.0 m (gate inactive). Reported per model and for the Golden − Flooded difference.

**4b. Replicates (noise floor and harness check).** Routes chosen by rule, every fifth entry of `CANONICAL_44` from index 0: 2534, 3561, 1790, 23695, 28087, 2664, 17563, 26458. Golden-6400 and Matrix-Flooded-6400 are re-run on these with the unmodified controller on the current harness, under new tags (`*_rep1`). Stored and replicate runs are compared step by step. If they are identical, the pipeline is deterministic and the 10 November harness changes are behaviour-neutral on these routes. If not, the replicate-to-replicate spread of each endpoint is reported as the noise floor and paired differences are read against it.

**4c. Gate-off run.** Both models, all 44 routes, with `alpamayo_bridge_agent_nogate.py`: the hashed controller with two changes only, the forced `target_speed_kmh = 0` and the holding brake under the standstill-gate condition are removed. Speed cap, curve limit, PID gains, lookahead, smoothing and start-assist are unchanged. Tags `model_matrix_golden_6400_nogate`, `model_matrix_flooded_6400_nogate`.
- Endpoints: standstill fraction at v < 0.1, 0.5 and 1.0 m/s; mean speed; route completion; distance travelled within a common tick window; routes ended by the 60 s rule; collisions by class.
- Analyses: Golden − Flooded difference under the gate-off controller (paired Wilcoxon, BCa interval); the model × controller interaction as the paired difference of differences across the 44 routes; both read against the 4b noise floor.
- Interpretation fixed in advance: with the gate removed the controller still tracks the model's planned speed, so remaining standstill is attributable to the predicted trajectories. A Golden − Flooded gap that persists gate-off supports a model-side origin; a gap that shrinks toward the noise floor indicates the gate amplifies it. Either result is reported.
- Rerun rule: a route is re-launched only if no `checkpoint_endpoint.json` with a score exists for it; the runner writes its audit log during the run and records model path, checkpoint SHA-256 and agent SHA-256 per route.

All of Section 4 is exploratory.

## 5. Additional runs decided on 12 November 2026 (after the primary endpoint was known)

Written before any of these runs started. The primary confirmatory record of Section 1 is not changed by anything below.

**Why.** Three facts emerged after the primary analysis: (i) a replicate of one route with the same checkpoint and controller differed from the stored run from the first step (Driving Score 4.1 vs 60.0, standstill 81 % vs 9 %), so the pipeline is not deterministic, the model server sets no seed; (ii) 38 of the 44 `Base` routes were evaluated before the 60 s standstill termination rule existed; (iii) training samples in the Matrix datasets lie on routes overlapping 7 of the 44 canonical evaluation routes (1852, 1825, 2286, 23901, 23695, 3464, 2164).

**5a. Second pass of both 6,400-frame Matrix models.** All 44 routes, unmodified controller, current harness; tags `model_matrix_golden_6400_run2`, `model_matrix_flooded_6400_run2`. Reported:
- H2 on run 2 alone (same endpoint, test and interval as Section 1), labelled a replication, not a second confirmatory test.
- H2 on the per-route mean of the two runs of each model.
- Test–retest for each model: difference of the 44-route means between runs, per-route standard deviation of the run-to-run difference, and the intraclass correlation of route-level standstill, Driving Score and route completion.
- For the eight replicate routes of Section 4b, the third run is included in the per-route spread.
- The gate-off comparison of Section 4c is read against the run-1 vs run-2 difference of the default controller for the same model.

**5b. `Base` re-evaluated under the current termination rule.** All 44 routes, unmodified controller, server started without a fine-tuned action expert; tag `base_run2`. In the revised manuscript the `Base` rows and the H1 comparison (Golden-1600 vs Base, Driving Score) use `base_run2`, because it shares the termination rule of the fine-tuned models; the original `Base` results are reported beside it as a sensitivity row. H1's test and interval are as before.

**5c. Non-overlapping routes.** H1 and H2 are each reported on all 44 routes and on the 37 routes not touched by Matrix training samples (and on the 33 routes not gate-flagged at pool level), as already computed in `docs/provenance/train_eval_overlap_canonical44.json`.

All of Section 5 is exploratory or sensitivity analysis. Rerun rule and provenance recording are those of Section 4c.

## 6. Decoupling arm, decided 12 November 2026, 23:40 (UTC+7), before the model was trained

Written before the training run started. Optional: it is reported only if training finishes within the available A100 window (to 14 November) and the checkpoint can be evaluated; otherwise it is reported as not done. The confirmatory record of Section 1 is not changed.

**Why.** Golden and Flooded differ in three target marginals at once (scenario-group mix, manoeuvre mix, stationary share). The dataset `lead-alpamayo-pai_matrix_floodedgroups_balanced_6400` (built with the other four, same pool, same build seed, never trained on) has Flooded's group mix with Golden's manoeuvre mix and 2 % stationary share. A model trained on it separates the group mix from the manoeuvre-plus-stationary bundle.

**Training.** Same recipe, base weights and schedule as the two 6,400-frame Matrix models: 10 epochs, per-device batch 1, gradient accumulation 8, 8,000 optimizer steps, warmup 200, learning rate 1e-4 to 1e-6, seed 42, VLM frozen; same export procedure. Name: `Matrix-FloodedGroups-Balanced-6400`.

**Evaluation.** All 44 canonical routes, unmodified controller, current harness, one pass, tag `model_matrix_fgbalanced_6400`, after the runs of Section 5. Rerun rule and provenance recording as in Section 4c.

**Analysis (exploratory).** Endpoint: standstill fraction (v < 0.1 m/s). Paired differences Balanced − Flooded-6400-Matched and Balanced − Golden-6400 over the 44 routes, with the Wilcoxon test and BCa interval of Section 1; the comparator is the per-route mean of its two default-controller passes, and each pass separately is given as a sensitivity row. Driving Score, route completion and collision events are reported descriptively. The same comparisons are repeated on the 37 non-overlapping routes.

**Interpretation fixed in advance.**
- Balanced below Flooded (interval excludes 0) and not separable from Golden: the standstill difference follows the manoeuvre mix and stationary share, not the group mix.
- Balanced above Golden (interval excludes 0) and not separable from Flooded: it follows the group mix.
- Anything else, including a value between the two with both intervals containing 0: inconclusive, and reported as such.

One training seed and one evaluation pass; every reading is set against the test–retest spread of Section 5a. No confirmatory claim is made from this arm.

## 7. Plan-level and stop-episode analyses, written 13 November 2026, 22:30 (UTC+7)

Post hoc and exploratory. No new runs; existing per-step logs only (`predicted_trajectories.jsonl`: speed and predicted waypoints per logged step). The confirmatory record of Section 1 is not changed.

**What had been seen when this was written.** Everything in the committed manifest up to commit `49d1788a`, and, on the 18–19 gate-off routes of Golden-6400 finished by 13 November 20:50: the mean standstill fraction of both models under both controllers, and the share of steps with predicted extent L below 0.64, 1.5 and 2.0 m (Section 7a was therefore looked at before it was written down, on a partial route set). Not computed or viewed for any model: the number, duration or ending of stop episodes (Section 7b).

**7a. Near-stationary plan rate.** Per route and model: share of logged steps with L < 1.5 m (primary), and with L < 0.64 m and L < 2.0 m. Paired Golden − Flooded difference over the 44 routes with the Wilcoxon test and BCa interval of Section 1, for the default controller (run 1; run 2 and the two-run mean when available) and for the gate-off controller. Stated limitation: the two models visit different states in closed loop, so this is not a same-input comparison.

**7b. Stop episodes.** A stop episode is a maximal run of consecutive logged steps with speed < 0.1 m/s lasting at least 20 steps (1 s at 20 Hz). Each episode gets one class:
- *start*: begins at the first logged step of the route;
- *resumed, short*: ends before the route's last logged step, shorter than 200 steps (10 s);
- *resumed, long*: ends before the last logged step, 200 steps or longer;
- *terminal, 60 s*: runs to the last logged step and is at least 1,190 steps long (the route was ended by the 60 s rule);
- *terminal, other*: runs to the last logged step, shorter than 1,190 steps.
Standstill steps outside any episode (runs under 1 s) are reported as *brief*. Per route and model, standstill time in each class is expressed as a percentage of the route's logged steps, so the classes add up to the standstill fraction of Section 1. Also reported: episodes per route, median episode duration, and within each class the share of steps with L < 0.64 m (the plan itself is to stay), 0.64 ≤ L < 2.0 m, and L ≥ 2.0 m (the plan is to move while the vehicle does not).

Comparisons: paired Golden − Flooded difference of standstill time per class (mean, BCa interval), for the default controller (run 1; run 2 and the two-run mean when available) and for the gate-off controller.

**Reading fixed in advance.** With Δ the default-controller Golden − Flooded standstill difference (run 1):
- *freeze-type*: the classes *resumed, long* and *terminal, 60 s* together account for at least two thirds of Δ, and the interval of their summed difference excludes 0;
- *wait-type*: the classes *start*, *resumed, short* and *brief* together account for at least two thirds of Δ, and the interval of their summed difference excludes 0;
- otherwise *mixed*.

Duration and ending are proxies. The logs contain no record of whether a hazard was ahead, so this analysis cannot say that a stop was justified; it separates stops the vehicle recovers from quickly from stops it does not. Every reading is set against the test–retest spread of Section 5a.
