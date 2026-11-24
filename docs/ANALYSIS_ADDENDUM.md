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
An episode that both begins at the first logged step and runs to the last one is classed as terminal, not as start (clarification added 13 November, 22:50, before any episode statistic was computed). Standstill steps outside any episode (runs under 1 s) are reported as *brief*. Per route and model, standstill time in each class is expressed as a percentage of the route's logged steps, so the classes add up to the standstill fraction of Section 1. Also reported: episodes per route, median episode duration, and within each class the share of steps with L < 0.64 m (the plan itself is to stay), 0.64 ≤ L < 2.0 m, and L ≥ 2.0 m (the plan is to move while the vehicle does not).

Comparisons: paired Golden − Flooded difference of standstill time per class (mean, BCa interval), for the default controller (run 1; run 2 and the two-run mean when available) and for the gate-off controller.

**Reading fixed in advance.** With Δ the default-controller Golden − Flooded standstill difference (run 1):
- *freeze-type*: the classes *resumed, long* and *terminal, 60 s* together account for at least two thirds of Δ, and the interval of their summed difference excludes 0;
- *wait-type*: the classes *start*, *resumed, short* and *brief* together account for at least two thirds of Δ, and the interval of their summed difference excludes 0;
- otherwise *mixed*.

Duration and ending are proxies. The logs contain no record of whether a hazard was ahead, so this analysis cannot say that a stop was justified; it separates stops the vehicle recovers from quickly from stops it does not. Every reading is set against the test–retest spread of Section 5a.

## 8. Driven standstill ("blocked" time), written 14 November 2026, 05:25 (UTC+7)

Post hoc and exploratory. No new runs; existing per-step logs only (speed, throttle and brake as finally sent to the vehicle). The confirmatory record of Section 1 is not changed.

**What had been seen when this was written.** The complete gate-off result for both models (analysis P, 44 routes each) and analysis T with its gate-off row. For stop episodes of 200 steps or longer in four arms (both models, default controller run 1 and gate-off), one line per episode: its length, the median throttle, the share of its steps with throttle and with brake, the median predicted extent, the most frequent rationale texts, the route's final status and its number of collision records. In that listing most long stops of Golden-6400 had throttle near the 0.6 cap on every step and no brake. Also seen earlier: the pooled command classes of analysis E (default controller, run 1, gate-inactive steps only). Not computed or viewed: any per-route value of the classes defined below, any paired statistic on them, or their totals per arm.

**Definition.** Every standstill step (speed < 0.1 m/s) gets one class from the logged final command:
- *blocked*: the step lies in a run of at least 100 consecutive standstill steps (5 s) that all have throttle ≥ 0.35 and brake = 0. The controller is asking for clear acceleration and the vehicle does not move. (0.35 is the controller's own start-assist throttle; 0.6 is its cap.)
- *driven, transient*: throttle ≥ 0.35 and brake = 0, but not in such a run (for example pulling away from rest).
- *not driven*: every other standstill step (brake applied, or throttle below 0.35). This holds the gate's holding brake, PID braking, and low requested acceleration.
Per route and arm, time in each class is a percentage of the route's logged steps, so the three classes add up to the standstill fraction of Section 1. Derived endpoint: *standstill without blocked time* (standstill fraction minus the blocked class).

**Comparisons.** Paired Golden − Flooded difference per class and for the derived endpoint (mean, BCa interval, Wilcoxon test as in Section 1) for the default controller (run 1; run 2 and the two-run mean when available) and the gate-off controller; gate-off minus default per model; the model × controller difference of differences. Descriptive: number of routes with any blocked time, and how many of them have at least one collision record, against the same share among routes without blocked time.

**Sensitivity, fixed here.** Run length 40 and 200 steps instead of 100; throttle threshold 0.2 instead of 0.35.

**Reading.** No decision rule. "Blocked" is inferred from the command log, not from a contact sensor: it says the vehicle was commanded to accelerate and did not move, which is what happens when it rests against another vehicle or an obstacle, but the logs do not record contact at each step. If the Golden − Flooded difference in standstill without blocked time has an interval that excludes 0 under both controllers while the difference in blocked time does not favour Golden, the manuscript will say that the standstill endpoint mixes two things (stops the controller commands, and time spent held in place while driving) and that the curated mix reduces the first only. Every reading is set against the test–retest spread of Section 5a.

**8a. Extension to the other models, added 14 November 2026, 05:35 (UTC+7), before it was computed.** The same three classes for the other four models of the main results table (Base, Flooded-1600, Golden-1600, the historical flooded checkpoint), default controller, existing run-1 logs: mean per class, number of routes with blocked time and how many of them have a collision event. Paired contrasts on blocked time and on standstill outside blocked time: Golden-1600 − Flooded-1600; Golden-6400 − historical flooded checkpoint; the two size contrasts (Golden-6400 − Golden-1600, Flooded-6400 − Flooded-1600); and each 1,600-sample model against Base. (The last four were added at 05:40, still before anything in this subsection was computed.) Purpose: to see whether the pattern found for the matched 6,400-sample pair is specific to that pair. Descriptive; no decision rule. Not seen when this was written: any blocked-time value for these four models.

## 9. Replication test of the plan-level findings on the second pass, written 14 November 2026, 12:35 (UTC+7)

Sections 7 and 8 were defined after their data had been seen, so their run-1 and gate-off results are exploratory. The second pass of Section 5a is new data for them. This section fixes a decision rule for that pass before any of its plan-level or command-class values exist for the comparison. The confirmatory record of Section 1 and hypothesis H2 are not changed, and these tests do not replace H2.

**What had been seen when this was written.** All run-1 and gate-off results of Sections 7 and 8. Of the second pass: the route status lines of the audit log and the standstill fraction of the first 14 routes of `model_matrix_golden_6400_run2` (noted in `CONFIRMATORY_DEVIATIONS.md`, run note 6). Not computed or viewed for any second-pass route: predicted extent, near-stationary plan rate, stop episodes, throttle, brake, or any class of Section 8. `model_matrix_flooded_6400_run2` had not started.

**Data.** Run 2 only: `model_matrix_golden_6400_run2` and `model_matrix_flooded_6400_run2`, 44 routes each, default controller, paired by route. Definitions, code and thresholds exactly as in Sections 7a and 8 (analyses T and U of `paper_reanalysis.py` as committed in `9a8f27ee`). Test and interval as in Section 1: paired mean difference Golden − Flooded, 95 % BCa interval, two-sided Wilcoxon signed-rank test.

**R1 (primary).** Near-stationary plan rate, share of logged steps with L < 1.5 m. *Replicated* if the mean difference is negative, the interval lies entirely below 0 and p < 0.05. Otherwise *not replicated*.

**R2 and R3 (secondary, Holm-adjusted over the two).** R2: standstill without blocked time; replicated if the difference is negative, the interval lies below 0 and the adjusted p < 0.05. R3: blocked time; replicated if the difference is positive (more for Golden), the interval lies above 0 and the adjusted p < 0.05.

**Reporting.** Each of R1–R3 is reported as replicated or not replicated, whatever the outcome, in the same paragraph as the run-1 result. The same three contrasts on the 37 routes without training overlap (Section 5c) and with the sensitivity settings of Section 8 are reported as sensitivity rows without a decision. Two-run means are reported as in Sections 7a and 8 and carry no decision, because they contain run 1. If a route of either run has no score after the rerun rule, the tests use the routes scored in both.

## 10. Three further analyses of the existing step logs, written 14 November 2026, 12:45 (UTC+7)

Post hoc and exploratory. No new runs. Written before any value below was computed for any model or run. The confirmatory record of Section 1 is not changed.

**Why these three.** Each follows from a property of the training sets recorded in `docs/provenance/A100_TRAINING_PROVENANCE.md`: among low-speed training frames 31 % stay put in the Flooded sets against 11 % in the Golden sets (10a); the manoeuvre targets differ, with 37 % leftward swerves and 22 % straight driving in Flooded against 13 % and 50 % in Golden (10c). 10b uses the rationale text, which comes from the frozen backbone and is therefore produced by the same weights in every model.

**What had been seen when this was written.** Everything in the manifest at commit `9a8f27ee`, including: standstill time by rationale class (analysis J), standstill time by extent band (analysis D), and inside stop episodes the share of steps per extent band (analysis T, descriptives). Not computed or viewed for any model or run: the lateral coordinate of any predicted waypoint; plan extent conditioned on speed over all steps; plan extent conditioned on rationale class. Of the second pass, nothing beyond what Section 9 lists.

**10a. Plans at low speed and while moving.** Definitions copied from the training-set table. Among logged steps with speed ≤ 0.5 m/s: share with L < 0.64 m (*stays put*), with L ≥ 2.0 m (*starts moving*), and in between. Among logged steps with speed > 0.5 m/s: share with L < 1.5 m (*plans a stop while moving*).

**10b. Plan given the stated reason.** Rationale classes exactly as in analysis J (keyword heuristic, patterns unchanged). Among steps of class *proceed*, and separately among steps of class *caution*: share with L < 1.5 m.

**10c. Lateral plans.** y_end is the lateral coordinate of the last (64th) predicted waypoint as logged, in the model's frame, positive to the left (the controller negates it for CARLA). Among logged steps with L ≥ 2.0 m: share with y_end ≥ 1.0 m (*left*), share with y_end ≤ −1.0 m (*right*). Sensitivity: 0.5 m and 2.0 m. Reported on all 44 routes and on the nine obstacle-bypass routes already listed in the script (`BYPASS_SINGLE` and `BYPASS_TWOWAY`: 2534, 2513, 1790, 1773, 1852, 1825, 3436, 2664, 3464).

**Comparisons, the same for all three.** Per route, each share is a percentage of the conditioning steps of that route; a route enters a paired comparison only if both arms have at least 20 conditioning steps on it, and the number of routes used is reported. Paired Golden-6400 − Flooded-6400-Matched difference with the BCa interval and Wilcoxon test of Section 1, for the default controller (run 1) and the gate-off controller. Pooled shares over all steps of the 44 routes are reported for all six models of the main table (default controller, run 1) next to the training-set values, as description only.

**Second pass.** The same paired comparisons on run 2 alone are reported when both second passes are complete. A run-1 difference whose interval excludes 0 is called *replicated* if the run-2 difference has the same sign and its interval excludes 0. No adjustment for multiplicity; these stay exploratory, below R1–R3 of Section 9.

**Reading.** No decision rule. The two models visit different states in closed loop, so conditioning on speed or on rationale class narrows the comparison but does not make it a same-input comparison. The rationale classes are a keyword heuristic. A lateral offset of the plan is not a completed manoeuvre.

## 11. Motion-history swap test, written 14 November 2026, 16:13 (UTC+7), before the modified agent was run on any route

New runs, exploratory, with a reading rule fixed here. The confirmatory record of Section 1 is not changed, and these runs enter no other analysis.

**Question.** At low speed the flooded model plans to stay put more often than the curated one (Section 10a). The inertia account [Codevilla et al., 2019] says that such plans follow the model's own recent motion, not the scene. The only non-visual motion input of the model is the ego history (16 poses over the last 1.5 s). This test replaces that input on a fixed subset of steps and reads the plan.

**What had been seen when this was written.** Everything in the manifest at commit `236aa3d3` (first passes, gate-off runs, 14 of 44 routes of the Golden second pass as in run note 6). No model has been queried with a replaced history.

**Agent.** `alpamayo_bridge_agent_histswap.py` is a copy of the default agent (gate active) with three changes and no others. (i) On a *swap step* the two history arrays sent to the model are replaced as described below; camera frames (four per camera) and the navigation command are sent unchanged. (ii) The plan returned on a swap step is logged but not acted on: the vehicle receives the command of the previous step, and the controller's state is not updated. (iii) Each log line carries `hist_kind` (`true`, `moving` or `stationary`) and `controller_variant = histswap`.

**Swap steps.** Step index ≥ 60, and the SHA-256 digest of the decimal step index, read as an integer, is divisible by 5 (about one step in five). The schedule is the same for every route and model.

**Replacement.** If the measured speed is ≤ 0.5 m/s: *moving history*, 16 positions on a straight line behind the vehicle at a constant 4.0 m/s (x = 4.0 m/s × offset for offsets −1.5 s to 0 s, y = z = 0), identity rotations. If the speed is > 0.5 m/s: *stationary history*, all positions zero, identity rotations.

**Runs.** `Golden-6400` and `Flooded-6400-Matched`, one pass each on the eight replicate routes of Section 4b (2534, 3561, 1790, 23695, 28087, 2664, 17563, 26458), tags `model_matrix_golden_6400_histswap` and `model_matrix_flooded_6400_histswap`. They start after the decoupling arm of Section 6 has finished. The first route (2534, flooded model) serves as the check that the agent runs; it is that route's run and is not repeated. No route is relaunched once it has a score.

**Outcomes, per model.** Thresholds as in Section 10a.
- **W1 (primary).** Among steps at ≤ 0.5 m/s: share of plans with L < 0.64 m (*stays put*) on swap steps (moving history) minus the same share on the other steps (true history).
- **W2.** Among steps at > 0.5 m/s: share of plans with L < 1.5 m on swap steps (stationary history) minus the same share on the other steps.
- Also reported: the share with L ≥ 2.0 m at low speed under both histories, and pooled shares with step counts.

Per route, a share is a percentage of the steps of that condition; a route is used only if it has at least 20 steps in both conditions. Paired over routes, BCa interval and Wilcoxon test as in Section 1. With eight routes the smallest two-sided Wilcoxon p-value is 0.0078.

**Reading rule.** For one model, stay-put plans are called *history-dependent* if the W1 difference is negative and its interval lies entirely below 0. Otherwise the result is *no detectable dependence on the ego history*. For W2, a stationary history is said to *induce stop plans* if the difference is positive and its interval lies entirely above 0. Fewer than five usable routes for a model: no reading, the pooled shares are reported only.

**What the paper may say.** If W1 is history-dependent for `Flooded-6400-Matched`, the paper may state that this model's stay-put plans depend on the ego-history input, which is the mechanism described as the inertia problem. If not, the paper states that the test did not show this, and keeps or removes "consistent with". The result is reported whatever it is. The comparison between the two models under a moving history is descriptive.

**Limits.** A moving history together with camera frames that show no motion is an input the model was not trained on, and so is the reverse. A single replaced step measures the immediate plan, not how long a stop lasts. Holding the previous command on one step in five alters the closed loop, so scores and standstill time of these runs are not comparable with any other run and are not analysed. Eight routes, one pass, unseeded sampling.

## 12. Wording rule for contact claims, and time at crawling speed, written 14 November 2026, 16:23 (UTC+7)

Exploratory. No new runs. The confirmatory record of Section 1 is not changed.

**12a. What the paper may say about collisions after the second pass.** Section 5 already lists collision events (merged by actor id, as in analysis F) as a secondary outcome of the second pass, on run 2 alone and on the per-route mean of runs 1 and 2 (analysis O). This section adds only a wording rule, fixed before any collision count of a second pass was computed or viewed. Known when written: first pass 44 events (`Golden-6400`) against 36 (`Flooded-6400-Matched`), rate ratio 1.12 with interval 0.80 to 1.68; gate-off runs 51 against 51.
- The paper may state that one model had *more collisions* than the other only if, on the per-route mean of the two passes (44 routes), the paired difference has a BCa interval that excludes 0.
- Otherwise it states that collision counts did not differ detectably, and gives both counts.
- In neither case does the paper state that one model is *safer*. Collisions in these runs are simulator contact events of any severity, the routes are 44 short scenarios, and no hazard exposure is measured.
- Blocked time (Section 8) is reported as time spent commanded to accelerate without moving, on routes with a collision event. It is not reported as a collision count.

**12b. Time at crawling speed.** Share of logged route steps with speed ≥ 0.1 m/s and < 1.0 m/s (*crawl*); sensitivity: ≥ 0.1 and < 0.5 m/s. Paired `Golden-6400` − `Flooded-6400-Matched` difference per route, BCa interval and Wilcoxon test of Section 1, for the default controller (run 1), the gate-off controller, and the second pass when complete; the per-model means for all six models of the main table are reported as description. This is a re-expression of values that analysis P already holds (shares of steps below 0.1, 0.5 and 1.0 m/s): from the gate-off means seen when this was written, crawl is 12.75 % for the curated model and 16.93 % for the flooded one. No paired test of this quantity had been run. No decision rule; second-pass wording as in Section 10.

## 11-A. Correction to the outcomes of Section 11, written 14 November 2026, 17:19 (UTC+7), before any history-swap run existed

No history-swap run has started (queue part 4 waits for part 3). Nothing from any swap run has been seen. Section 11 is left as committed; this section replaces its outcomes W1 and W2 and nothing else.

**What was found.** Checking the equations of Section 3.1 against the model's code (`unicycle_accel_curvature.py`, `action_to_traj`) showed that the predicted waypoints are integrated from an initial speed v_0 that the model estimates from the same ego history that the test replaces (`estimate_t0_states`). A replaced history therefore changes L mechanically, whatever the learned controls say. Numerical check (run once, CPU, the model's own action space, controls fixed at the training means): from a moving history of 4.0 m/s the estimated v_0 is 3.9998 m/s and L = 25.79 m; from a stationary history v_0 = 0 and L = 0.59 m; from v_0 = 0.4 m/s L = 3.11 m. W1 as written (share of plans with L < 0.64 m under a moving history) could hardly be met under a 4.0 m/s history for a mechanical reason, and would then read as history dependence of the model whatever the model does.

**Replacement outcomes.** Plan end speed: v_end = (path length between waypoint 54 and waypoint 64) / 1.0 s, in m/s, from the logged waypoints. A plan *ends at rest* if v_end < 0.5 m/s. This does not depend on v_0 except through the controls that reach rest.
- **W1' (primary).** Among steps at ≤ 0.5 m/s: share of plans that end at rest on swap steps (moving history) minus the same share on the other steps (true history).
- **W2'.** Among steps at > 0.5 m/s: share of plans that end at rest on swap steps (stationary history) minus the same share on the other steps.
Per-route rule, pairing, intervals, reading rule, limits and what the paper may say are as in Section 11, with *ends at rest* in place of *stays put* and *stop plans*. The shares with L < 0.64 m and L ≥ 2.0 m of Section 11 are reported as description only and carry no reading.

**Agent and queue.** Unchanged: the agent logs the full waypoint array, from which v_end follows.

## 13. Plans at rest and at slow speed (sensitivity of Section 10a to the initial speed), written 14 November 2026, 17:19 (UTC+7), before computing

Post hoc, exploratory, existing step logs only. The confirmatory record of Section 1 is not changed.

**Why.** The extent L is integrated from the vehicle's current speed v_0 (Section 11-A). Among steps at ≤ 0.5 m/s, a plan that keeps v_0 = 0.4 m/s has L ≈ 3 m, whereas a plan from rest with the mean training controls has L ≈ 0.6 m. The stay-put share of Section 10a can therefore differ between two models partly because they spend different shares of their low-speed steps near zero speed. This section removes that possibility by conditioning on speed more tightly.

**What had been seen when this was written.** The results of Sections 10a and 10b for both controllers; no value of the quantities below for any model.

**Strata and outcomes.** Strata: *at rest* (speed < 0.1 m/s) and *slow* (0.1 ≤ speed ≤ 0.5 m/s). Outcomes in each stratum: share of plans with L < 0.64 m (*stays put*) and share of plans that end at rest (v_end < 0.5 m/s, Section 11-A).

**Comparison.** As Section 10: per route a percentage of that stratum's steps, a route used only if both arms have at least 20 steps in the stratum, paired `Golden-6400` − `Flooded-6400-Matched`, BCa interval and Wilcoxon test of Section 1; default controller (run 1), gate-off controller, and run 2 when complete. Pooled shares for all six models are reported as description.

**Reading.** No decision rule. If, among steps at rest, the stay-put share is lower for the curated model with an interval below 0 under both controllers, the paper says the difference in Section 10a is not an artefact of the speed distribution inside the 0.5 m/s band. If it is not, the paper says so and weakens the statement of Section 10a to match.

## 11-B. Second correction to the outcomes of Section 11, written 14 November 2026, 18:25 (UTC+7), before any history-swap run existed

No history-swap run has started and no swap log exists. Sections 11 and 11-A are left as committed. This section replaces the outcomes and the reading rule of Section 11-A.

**What was wrong in 11-A.** An independent review of the code pointed out that the plan end speed also depends on the initial speed: the integration is v_k = v_0 + Σ a_j Δt with no clamp, so for identical controls v_end shifts with v_0. Section 11-A said otherwise. The reviewer applied v_0 = 4.0 m/s to the plans already logged in the first pass on the eight replicate routes: the share of plans that end at rest becomes 0.0 % for both models on every route, against 7–61 % (flooded) and 1.5–29 % (curated) under the true history. W1' as written would therefore be met by a network that ignores the ego history completely, and would be read as dependence on it.

**What the action space implies.** The expert outputs accelerations and curvatures. A plan that stays put at rest is a plan without acceleration from v_0 = 0. The same controls from v_0 = 4.0 m/s keep the vehicle moving. Stopping from motion needs a braking plan. The two questions are therefore separate, and each gets its own outcome.

**Outcomes, per model, among steps at ≤ 0.5 m/s.** From the logged waypoints: v_start = |first waypoint| / 0.1 s; v_end as in 11-A; planned speed change Δv = v_end − v_start. A plan *holds speed* if |Δv| < 0.5 m/s, *accelerates* if Δv ≥ 0.5 m/s, *decelerates* if Δv ≤ −0.5 m/s. Δv depends on the learned controls and not on v_0, except where a braking plan passes through zero speed.
- **W-a (primary; do the learned controls depend on the ego history?).** Share of plans that hold speed, on swap steps (moving history) minus on the other steps (true history).
- **W-b (are stay-put plans matched by braking plans?).** Share of plans that end at rest (v_end < 0.5 m/s), on swap steps minus on the other steps. Under the true history this is the stay-put share; under the moving history it is the share of plans that brake to rest.
- Reported as description: the three-way split (holds, accelerates, decelerates) under both histories; the same quantities for steps at > 0.5 m/s with the stationary history; the L-based shares of Section 11.

Per-route rule, pairing, intervals and limits as in Section 11.

**Reading rule.**
- W-a: if the interval excludes 0, *the learned controls depend on the ego history*; the sign and the three-way split say how. Otherwise *no detectable dependence of the controls on the ego history*.
- W-b: if the difference is negative with the interval below 0, *stay-put plans are not matched by braking plans*: in the situations where the model stays put when at rest, it does not plan to brake to rest when told it is moving. This is expected from the action space if the controls do not change, and it is not by itself evidence that the model uses the history.

**What the paper may say.**
- If W-a shows dependence for `Flooded-6400-Matched` and the hold-speed share is lower under the moving history: the model's no-acceleration plans at rest are tied to an ego history that says it is at rest, which is the dependence the inertia account describes.
- If W-a shows no dependence and W-b is negative: the stay-put plans are plans without acceleration that the model issues whatever the history says; the paper states that the test did not show a dependence on the ego history, and does not attribute the stops to the inertia mechanism.
- Any other outcome is reported as found, without the word inertia.

**Sensitivity, fixed now.** The same review found, by reading the streaming server's code, that the key-value cache may let one step's reasoning and action tokens be visible to the next step's trajectory-start token. This was not measured. Every outcome above is therefore also computed with the true-history steps that directly follow a swap step left out. If the two versions differ in reading, both are reported and no reading is given.

**Agent, routes, schedule.** Unchanged. The queue's log check is strengthened (first-waypoint distance about 0.4 m on moving-history steps and below 0.05 m on stationary-history steps, which shows that the server used the replaced history), and the queue now waits for parts 2 and 3. If a route never scores, the analysis uses the routes that exist once the queue has ended.

**A rule that was applied but not written down.** In analyses V, X and Y a paired comparison is computed only if at least five routes meet the 20-step rule. Sections 10 and 13 do not state this. It has not been triggered (40 to 44 routes in every comparison so far).

## 14. H1 on the routes not used to tune the controller, written 15 November 2026, 02:41 (UTC+7), before computing

Post hoc sensitivity analysis, existing results only. The confirmatory record of Section 1 is not changed.

**Why.** The PID gains and the lookahead were tuned on 20 of the 44 evaluation routes with a fine-tuned checkpoint (`model_v4`), not with the pretrained model. The controller may therefore suit the plans of fine-tuned models better than those of `Base`, which would favour H1. Section 3 fixed this sensitivity analysis for H2 only.

**What had been seen when this was written.** H1 on 44 routes and on the 37 routes without training overlap, against the original `Base` run. No H1 value restricted to the non-tuning routes.

**Analysis.** `Golden-1600` − `Base` and, for comparison, `Flooded-1600` − `Base`, on Driving Score and route completion, restricted to the 24 canonical routes outside the tuning list of analysis H; paired, BCa interval and Wilcoxon test of Section 1. Against the original `Base` run now, and against `base_run2` when it is complete. No decision rule: if the point estimate keeps its sign and the interval excludes 0, the paper says H1 does not depend on the tuning routes; otherwise it reports the 24-route result next to the 44-route one and says the two differ.

## 15. Plan-level reading of the decoupling arm, and when it counts as a remedy, written 15 November 2026, 11:40 (UTC+7), before the model had run any route

Extends Section 6, which fixed a reading for standstill time only. The model `Matrix-FloodedGroups-Balanced-6400` is trained; none of its 44 evaluation routes has been run. The confirmatory record of Section 1 is not changed.

**What had been seen when this was written.** Everything in the manifest at commit `86dc79c6`, and the partial look at both second passes recorded as run note 8. Nothing from the decoupling model.

**Comparators.** As in Section 6: for `Flooded-6400-Matched` and `Golden-6400`, the per-route mean of the two default-controller passes. The decoupling model has one pass.

**Outcomes** (definitions of Sections 7a, 8, 10a and 13, unchanged):
- **D1 (primary).** Share of steps with a plan shorter than 1.5 m: Balanced − Flooded.
- **D2.** The same share: Balanced − Golden.
- Supporting: stay-put share at ≤ 0.5 m/s and among steps at rest; blocked time; standstill outside blocked time; Driving Score; route completion; collision events. Each as Balanced − Flooded and Balanced − Golden.
Paired over the 44 routes, BCa interval and Wilcoxon test of Section 1.

**Reading, which ingredient.**
- D1 negative with its interval below 0, and D2 with an interval that includes 0: near-stationary planning follows the manoeuvre mix and the stationary share, not the scenario-group mix.
- D2 positive with its interval above 0, and D1 with an interval that includes 0: it follows the scenario-group mix.
- Both intervals exclude 0 with the Balanced value in between: both contribute. Anything else: inconclusive.
The fraction of the Flooded − Golden gap that the Balanced model closes is reported as description.

**Reading, remedy.** The mix is called a *candidate remedy for hesitation* only if all three hold against `Flooded-6400-Matched`: D1 is negative with its interval below 0; the blocked-time difference has an interval that includes 0 or lies below it; and the Driving Score difference has an interval that includes 0 or lies above it. If D1 holds and either of the other two fails, the paper says that the mix reduces hesitation at a cost, and names the cost. The word remedy is not used in any other case.

**Limits.** One training seed and one evaluation pass for this model, against two-pass means for the comparators, so its values carry more run-to-run noise. The Balanced mix differs from the Flooded mix in two factors at once (manoeuvre mix and stationary share), which this arm cannot separate. A candidate remedy on 44 routes with one controller is not a demonstrated one.

## 16. Route-level agreement between the two passes, written 15 November 2026, 15:32 (UTC+7), after the values had been computed

Descriptive only, no test and no decision. These quantities were first computed in an exploratory session on 15 November, after both second passes were complete, and are written down here afterwards; they are labelled post hoc wherever they are reported.

For standstill time and for the share of steps with a plan shorter than 1.5 m: the per-route `Golden-6400` − `Flooded-6400-Matched` difference in pass 1 and in pass 2; the number of routes on which it is negative in both passes, positive in both, or of different sign; the Spearman rank correlation between the two sets of per-route differences; and, per model, the largest absolute change of a route's value between the passes.

## 17. Braking plans while moving (correction of the "plans a stop while moving" measure of Section 10a), written 15 November 2026, 15:49 (UTC+7), before computing

Post hoc, existing step logs only. The confirmatory record of Section 1 is not changed.

**What was wrong.** Section 10a measured "plans a stop while moving" as the share of steps at more than 0.5 m/s whose plan is shorter than 1.5 m, and the manuscript concluded that neither model plans a stop from motion in more than 0.3 % of steps. An independent consistency read pointed out that the plan is integrated from the current speed (Section 11-A): a plan that brakes to rest from ordinary driving speed covers more than 1.5 m, so the measure is close to zero by construction at all but the lowest speeds. The conclusion drawn from it is withdrawn.

**What had been seen when this was written.** The values of Section 10a and of Section 13 (plans that end at rest, for steps at or below 0.5 m/s only). No value of the quantity below for steps above 0.5 m/s.

**Replacement.** Among logged steps in a speed stratum, the share of plans that end at rest (v_end < 0.5 m/s, v_end as in Section 11-A). Strata: 0.5 < speed ≤ 2 m/s, and speed > 2 m/s. Comparison as in Section 10: per route a percentage of the stratum's steps, routes with at least 20 steps in the stratum in both arms, paired `Golden-6400` − `Flooded-6400-Matched`, BCa interval and Wilcoxon test of Section 1; default controller in pass 1 and in pass 2, and the gate-off controller. Pooled shares for all six models (default controller, pass 1) as description.

**Reading.** No decision rule. The manuscript's statement about stopping from motion is rewritten to say what these values show, whichever way they come out, and the sentence that the difference between the models "is one of restarting, not of stopping" is kept only if the braking-plan shares of the two models do not differ in either stratum (intervals including 0 in both passes).

## 18. Two analyses requested by the review panel, written 15 November 2026, 21:27 (UTC+7), before computing

Post hoc, existing step logs and result records only. Requested as required revisions R11 and R13 of the Stage 3 review of 15 November 2026. The confirmatory record of Section 1 is not changed.

**What had been seen when this was written.** All results in the manifest at commit `a7aba9fd`. From them it can be derived that about three in ten of the balanced model's standstill steps are blocked steps (7.75 of 25.71 in pass 1). No value of the quantities below.

**18a. Where blocked runs lie relative to recorded collisions.** For every blocked run (definition of Section 8) of `Golden-6400` and `Flooded-6400-Matched` in the two default-controller passes and the gate-off pass: (i) the distance travelled when the run starts, d_b = Σ speed × Δt over the logged steps before it; (ii) for each collision record of the same route and run, the arc length s_c of its recorded position projected onto the route's keypoint polyline, rescaled by route length / polyline length; (iii) the gap, the smallest |d_b − s_c| over the route's collision records. A run is *at a recorded collision position* if the gap is at most 10 m (sensitivity: 5 m and 20 m). Reported: the number of blocked runs and the share of blocked steps at a recorded collision position, per model and run, with a per-route listing; and blocked time recomputed without the runs at a recorded collision position, as a paired difference with the interval and test of Section 1.
Limits known in advance: collision records carry a position and an actor but no time, so whether a run began before or after the contact cannot be established; the distance travelled approximates the position along the route; steps before the first logged plan are missing.
Reading: if most blocked steps lie at a recorded collision position, the paper states that blocked time is time spent commanded to accelerate at the site of a recorded collision, that it follows from a contact already counted in the collision events, and that it is not an additional, independent cost. Otherwise it reports the split as found.

**18b. Stay-put shares without blocked steps.** Among steps at rest (speed < 0.1 m/s): the share that belongs to a blocked run, the share for which the gate condition holds (L < 1.5 m, or speed < 0.5 m/s and L < 2.0 m) outside blocked runs, and the rest. Then the stay-put share (L < 0.64 m) among steps at rest that are not in a blocked run, and the same among steps at ≤ 0.5 m/s that are not in a blocked run. Per route with at least 20 conditioning steps in both models, paired `Golden-6400` − `Flooded-6400-Matched`, interval and test of Section 1; pass 1, pass 2, gate-off.
Reading: no decision rule. If the stay-put difference without blocked steps keeps its sign with an interval below 0 in both passes and without the gate, the paper says the low-speed difference is not produced by blocked steps in the denominator; otherwise it reports the reduced difference.


## 19. Low-speed stay-put plans in the 1,600-sample pair, written 15 November 2026, 22:30 (UTC+7), before computing

Post hoc, existing step logs only; suggested in review (S23). What had been seen: the pooled stay-put shares of all six models (Section 10a; 19.77 % for `Flooded-1600`, 16.41 % for `Golden-1600`). Not computed: any per-route paired comparison for this pair. Analysis: the paired per-route comparison of Section 10a (stay-put share at ≤ 0.5 m/s, and at rest < 0.1 m/s), `Golden-1600` − `Flooded-1600`, default controller, one pass; routes with at least 20 conditioning steps in both models; BCa interval and Wilcoxon test of Section 1. No decision rule; reported next to the 6,400-sample result.

## 20. Blocked runs of the decoupling model relative to recorded collisions, written 17 November 2026, 12:35 (UTC+7), after the Section 15 values were seen

Post hoc, existing step logs and result records only. The confirmatory record of Section 1 and the readings of Sections 6 and 15 are not changed.

**What had been seen when this was written.** The complete Section 6 and Section 15 results for `Matrix-FloodedGroups-Balanced-6400` on 44 routes (near-stationary plan rate, stay-put shares, blocked time, standstill, Driving Score, route completion, collision events, each against both comparators), and the Section 18a result for `Golden-6400` and `Flooded-6400-Matched`. No value of the quantities below for the decoupling model.

**Why.** Section 15 names blocked time as the cost when the blocked-time interval lies above 0. Section 18a found that, for the two original models, blocked runs lie at recorded collision positions, so that blocked time follows from contacts already counted. Whether the same holds for the decoupling model decides how its blocked time may be described.

**Analysis.** The definition of Section 18a, unchanged (gap of at most 10 m; sensitivity 5 m and 20 m), applied to the one default-controller pass of the decoupling model: number of blocked runs, number of routes with blocked time, share of blocked steps at a recorded collision position, and blocked time recomputed without the runs at a recorded collision position. The recomputed value is compared, paired over the 44 routes with the interval and test of Section 1, with the per-route mean of the two default-controller passes of each comparator, as in Section 15.

**Reading.** No decision rule, and the Section 15 reading stands as computed. If most of the decoupling model's blocked steps lie at a recorded collision position, the paper describes its blocked time as it does for the balanced model: time commanded to accelerate at the site of a recorded collision, not an independent cost. Otherwise it reports the split as found. The limits of Section 18a apply.

## 21. Same-input comparison of the action experts (offline replay), written 17 November 2026, 15:13 (UTC+7), before any inference of this analysis was run

Requested by the review of 17 November 2026 (required item R4, route (a)) and, in an earlier form, by the review of 15 November (item R10). New inference on existing checkpoints; no simulator, no training. The confirmatory record of Section 1 and all earlier readings are not changed.

**What had been seen when this was written.** All results reported in the manuscript up to commit `1daeeeda`, including the closed-loop plan shares of every checkpoint, and the review of 17 November. Of the validation data: the annotation file only (1,567 samples in 117 clips from 40 source logs; 384 samples with annotated speed of 0.5 m/s or less, in 67 clips from 31 logs; among these 384 the demonstrated future stays within 0.64 m in 15, reaches 2 m or more in 332 and lies between in 37). No output of any checkpoint on any validation sample.

**Why.** Every plan share in the manuscript is a closed-loop rate in the states each checkpoint reached, counted per logged step. It cannot say whether two experts differ when they are given the same input.

**State set.** All samples of the shared validation split (file `annotations_val.json`, the same for every dataset cell; held out by route from every training set) whose annotated ego speed at the current frame is 0.5 m/s or less: 384 states. A state that cannot be loaded is dropped and counted.

**Procedure.** Inputs are built by the model's own dataset loader (four cameras, four frames each, 16-pose ego history) with the navigation text of the annotation, and passed through the engine of the deployed model server (same quantized backbone, same sampler of eight Euler steps with four expert evaluations). For each state the engine receives the full window at 0.1 s before the sample time (prefill) and then the streaming window at the sample time, and returns K = 16 trajectories in one call. The random seed is set to 1000 plus the state index before the prefill call, for every expert, and the rationale texts are stored, so that it can be checked whether the backbone output was the same for the experts compared. If 16 trajectories do not fit in memory, K = 8 is used; this is decided on the first states of the first expert, without looking at trajectories.

**Experts.** Primary pair: `Golden-6400` and `Flooded-6400-Matched`. Secondary: `Matrix-FloodedGroups-Balanced-6400` (the decoupling model), the unadapted model (`Base`), `Golden-1600` and `Flooded-1600`.

**Outcomes per state and expert.** With L the path length from the first to the last waypoint (as in the manuscript): p_stay, the share of the K plans with L < 0.64 m; p_start, the share with L of 2 m or more; and the mean of L.

**Primary comparison (SI-1).** p_stay of `Golden-6400` minus p_stay of `Flooded-6400-Matched`, per state; averaged within each source log, because states of one log are dependent; then paired over the logs: mean of the per-log differences, two-sided 95 % BCa interval (20,000 resamples, seed 0) and two-sided Wilcoxon signed-rank test, as in Section 1. The pooled means over the 384 states are reported as description.

**Reading, fixed now.**
- Difference negative with the interval below 0: on identical inputs the obstacle-heavy expert returns stay-put plans more often than the balanced one. The manuscript may then say that the two experts differ, for low-speed states reached by the demonstrator and replayed offline; it still may not attribute this to data composition across training runs.
- Interval includes 0: a difference between the experts on identical inputs is not shown. The manuscript withdraws every model-level or per-decision reading of the closed-loop shares and describes them as occupancy (route (b) of item R4).
- Difference positive with the interval above 0: reported as contrary to the closed-loop pattern, with the same withdrawal.
In every case the size of the same-input difference is printed next to the closed-loop shares, and the manuscript states that the closed-loop ratio also reflects how long each checkpoint stays in the states concerned.

**Secondary, descriptive, no rule.** The same comparison for the decoupling model against each of the primary pair, for `Base` against each 6,400-sample checkpoint, and for the 1,600-sample pair; the primary comparison on the states with speed below 0.1 m/s; on p_start; with L < 1.5 m in place of 0.64 m; p_stay of each expert by the class of the demonstrated future (stays put, starts, between) and against the demonstrated stay-put share of the state set; and a sign test over states that ignores the clustering.

**Limits known in advance.** The states are those a privileged expert driver reached, so states after a collision and other states that only the learned policies reach are absent. Each state is one prefill and one streaming step, not a long stream. The validation split was not drawn to the target mix of either training regime, and it holds few demonstrated stay-put futures (15 of 384).

## 22. Analyses requested by the review of 17 November 2026, written 17 November 2026, 15:13 (UTC+7), before computing

Post hoc; existing logs, result records and dataset annotation files only. No decision rule is attached to any of them, and no earlier decision is changed.

**What had been seen.** Everything in the manuscript up to commit `1daeeeda`; the review of 17 November. Not computed or viewed: any quantity below.

**(a) Reference values for the unadapted policy (item R1).** The plan-level and motion-level measures of manuscript Table 4 (near-stationary plans; stay-put plans at 0.5 m/s or less and at rest; plans ending at rest above 2 m/s; standstill outside blocked time; blocked time; crawling; standstill), as means of per-route percentages, for `Base run2` (the re-evaluated unadapted policy), with the paired difference to the two-pass mean of `Golden-6400`, of `Flooded-6400-Matched` and to the decoupling model, each with the interval of Section 1.

**(b) Composition and overlap of the decoupling dataset (items R3 and R11).** From the published annotation files: realised scenario-group, manoeuvre and stationary shares of `floodedgroups_balanced_6400`; its samples at 0.5 m/s or less by class of future (stays put, starts, between), with the definitions of manuscript Table 1; and the number of training samples it shares with `golden_6400` and with `flooded_6400`, as counts and shares.

**(c) Tests of blocked time (item R6).** For every blocked-time contrast printed in the manuscript: the number of routes with a non-zero paired difference, and a sign-flip permutation test of the mean paired difference (all sign assignments over the non-zero pairs when there are at most 20, otherwise 100,000 random assignments with seed 0), two-sided. The values are printed next to the existing ones; the outcome of rule R3 of Section 9 is not re-decided.

**(d) Chance rate of the position match (item R7).** The 10 m rule of Section 18a applied (i) to runs of at least 100 consecutive standstill steps that are not blocked runs, for the same models and passes, and (ii) as a placement rate: for each route with a blocked run, the share of the distance travelled on that route that lies within 10 m of a recorded collision position, averaged over blocked runs.

**(e) Collision events on the routes with blocked time (item R8).** For each checkpoint and pass, the collision events on the routes on which either model of the comparison has blocked time.

**(f) Plans per stop episode (item R4, supplementary to Section 21).** A stop episode is a run of at least 20 consecutive steps below 0.1 m/s (Section 7b). For each episode: whether the plan at its first step is a stay-put plan (L < 0.64 m), and the number of steps from the start of the episode to the first plan with L of 2 m or more (censored at the end of the episode). Per route: the share of episodes that begin with a stay-put plan and the median delay. Paired over the routes with at least three episodes for both models, `Golden-6400` against `Flooded-6400-Matched`, in each pass and without the gate. This counts each stop once, whatever its length.

**(g) Success rate (suggested item S20).** The share of routes completed in full without an infraction, per checkpoint and pass, as description.

## Correction note on heading times, written 17 November 2026, 18:15 (UTC+7)

Two section headings give a time that is later than the commit that first contained the section. The commit times are the record: Section 6 is headed 23:40 on 12 November 2026 and was committed at 23:32:16 (`c56dbdee`); Section 7 is headed 22:30 on 13 November 2026 and was committed at 21:19:48 (`845e061d`). The headings were written as estimates before the commit was made. Neither difference changes the order of a rule and the data it refers to. The headings are left as they were, so that earlier citations of them remain valid.

## 23. Control for the same-input replay: the unadapted expert loaded through the patch route, written 17 November 2026, 20:23 (UTC+7), before the control was run

Post hoc; a diagnostic of the replay of Section 21, not a new hypothesis. The primary result of Section 21 and its reading are not changed by it.

**What had been seen.** All results of Section 21 (`docs/provenance/same_input_results.json`). The primary difference is −5.25 pp with interval [−7.22, −3.75]. One check of the set-up did not come out as expected: the sampled rationale text is the same for the five fine-tuned experts in 381 to 384 of the 384 states, but the same as that of `Base` in only 208 to 210 states. The backbone weights are the same in all six processes, the 416 patched tensors are all expert tensors (`expert.*`, `action_in_proj.*`, `action_out_proj.*`, `action_space.*`), and the four `action_space` values are equal in the base model and in the checkpoints. The cause of the text difference is therefore not known. The only difference in set-up is that `Base` is served without the patch step, in the replay as in the closed-loop evaluation.

**Control.** A seventh process, `Base-SelfPatch`: the same base model, with the 416 expert tensors of the base model itself (copied unchanged from the published base model files) loaded through the patch step that serves the fine-tuned checkpoints. Same 384 states, same seeds, same 16 plans per state, same script.

**Reading, fixed now.**
- If the texts and the plans of `Base-SelfPatch` equal those of `Base` (allowing the 0 to 3 states in which two fine-tuned processes differ from each other), the patch step is neutral. The text difference then comes from the expert weights, and the route by which they reach the text decoder is looked for and reported.
- If they differ from `Base`, the serving route itself changes the output of the model. The contrasts of `Base` with the fine-tuned checkpoints, in closed loop (Section 22a) and in the replay, then contain a component that is not fine-tuning. The manuscript then reports `Base-SelfPatch` next to `Base`, with p_stay(`Base-SelfPatch`) − p_stay(`Base`) under the statistics of Section 21, and says that the comparison with the unadapted policy is confounded by the serving route.
- Contrasts among the fine-tuned checkpoints share one serving route and are not affected in either case.

## 24. The patch step of the model server loads the checkpoints in part; replay with the checkpoints loaded in full, written 17 November 2026, 21:01 (UTC+7), before any fully loaded checkpoint was run

**Finding (a fact about the serving code, not an analysis).** The engine fuses the q/k/v projections and the gate/up projections of each of the 36 expert layers when the base model is loaded (`flashdrive/__init__.py`, `setup_expert_fusion`, unchanged since 29 September 2026). The server then loads the fine-tuned expert tensors with `strict=False` (`scripts/flashdrive_server.py`, lines 132 to 181). The 180 tensors of the fused projections no longer have a matching name and are dropped without a message. Checked in memory for `Golden-6400` (`scripts/evaluation/check_expert_patch.py`, `docs/provenance/expert_patch_check_golden_6400.json`): the output projection, the down projection and the action output projection equal the checkpoint file (largest difference 0); the fused q/k/v and gate/up weights equal the base model (largest difference 3 × 10⁻⁸) and differ from the checkpoint file (largest difference 0.049). Every fine-tuned checkpoint in every closed-loop evaluation of this study, and in the replay of Section 21, was therefore served with base values in 180 of its 396 expert-layer tensors. `Base` is not affected by this, but see Section 23: the control `Base-SelfPatch` differs from `Base` in the rationale text in 176 of 384 states and in the plans in all states, so the patch step also changes the served model in a second way whose cause is not yet known.

**What had been seen.** All results of Sections 21 and 23; the weight check above.

**Replay with full loading.** The five fine-tuned checkpoints again, same 384 states, seeds, 16 plans and script, with every tensor of the checkpoint loaded: the q/k/v and gate/up tensors are concatenated in the order of the fusion and loaded into the fused weights, and the script stops if any expert tensor is left unpatched (`same_input_replay.py --full-patch`). Names `<checkpoint>-Full`.

**Statistic and reading, fixed now.** SI-1F: p_stay(`Golden-6400-Full`) − p_stay(`Flooded-6400-Matched-Full`), with the unit and the statistics of Section 21.
- Negative with the interval below 0: the fully loaded experts differ on identical inputs in the direction seen for the served models.
- Interval includes 0: the difference seen for the served models is not shown for the fully loaded experts.
- Positive with the interval above 0: the fully loaded experts differ in the opposite direction.

**Secondary, descriptive, no rule.** Each fully loaded checkpoint against its served version (p_stay, p_start, mean extent); the decoupling checkpoint against each of the pair; the 1,600-sample pair; each fully loaded checkpoint against `Base-SelfPatch` and `Base`.

**Limit.** The replay says nothing about the closed-loop behaviour of the fully loaded checkpoints. All closed-loop results of the study come from the partly loaded models.

**Follow-up to Section 23, written 17 November 2026, 21:10 (UTC+7), before the two runs below.** Outcome of the control: `Base-SelfPatch` has the rationale text of the fine-tuned processes in 382 to 384 of 384 states and that of `Base` in 208; its plans equal those of `Base` in no state; p_stay 4.23 % against 3.28 % (+0.95 pp, interval [0.36, 2.20]). By the reading fixed above, the serving route changes the output. A check in memory (`docs/provenance/expert_patch_check_base.json`) found no tensor shared between the expert and the rest of the model, and the expert tensors of the unpatched model equal the base files up to 3 × 10⁻⁸. Two diagnostics on the first 24 states, to find the cause: `Base-Repeat`, a second `Base` process (does `Base` reproduce itself across processes?), and `Base-EmptyLoad`, the base model after a loading call with an empty dictionary (does the call itself change the model?). They are checks of the serving code, with no decision rule.

## 25. Closed-loop evaluation of the checkpoints loaded in full, written 17 November 2026, 22:17 (UTC+7), before any closed-loop route of a fully loaded checkpoint was run

**Why.** Section 24: every closed-loop result of a fine-tuned checkpoint so far describes a model with base values in 180 of its 396 expert-layer tensors. The author decided on 17 November to evaluate the checkpoints again with a server that loads every tensor (`scripts/evaluation/flashdrive_server_fullpatch.py`; queue `scripts/common/run_fullload_suite.sh`).

**What had been seen when this was written.** Every result of the partly loaded models, including all of the manuscript; the replay of Section 21 and the control of Section 23. Not computed or viewed: any plan of a fully loaded checkpoint. The replay files of Section 24 for `Golden-6400-Full` and `Flooded-6400-Matched-Full` existed on disk and had not been opened or analysed. No closed-loop route had been run with the new server.

**Status of the earlier results.** The confirmatory record of Section 1 and all follow-up results are kept unchanged as results for the models as served. They are no longer the main results of the paper. The tests below are new tests on new data for the checkpoints as trained; they do not replace or re-run the registered tests, and the paper states both.

**Harness.** As in the second pass (Section 5a): the same agent file (SHA-256 `082c6ecc…10d3`), launcher, 44 routes, termination rule and rerun rule. Two differences. The model server is the full-loading server, which refuses to start unless all 416 tensors of the checkpoint are in memory with largest difference 0 from the checkpoint file; its loading report is stored with every route. A route counts only if that server served it from start to end; otherwise its output is moved aside and the route is launched again within the limit of three attempts. The stream cache of the server is still not cleared between routes, as in all earlier runs; this is unchanged on purpose and is disclosed.

**Stage 1.** `Golden-6400` and `Flooded-6400` (schedule-matched), 44 routes each, default controller, in this order (tags `model_matrix_golden_6400_full`, `model_matrix_flooded_6400_full`). Paired by route; paired mean difference Golden − Flooded; 95 % BCa interval with 20,000 resamples and seed 0; two-sided Wilcoxon signed-rank test; code of `paper_reanalysis.py` with the definitions of Sections 7a, 8 and 10 unchanged. If a route has no score after the rerun rule, the tests use the routes scored in both.

- **F1 (plans; primary).** Share of logged steps with predicted extent L < 1.5 m. *Met* if the difference is negative, the interval lies entirely below 0 and p < 0.05. Otherwise *not met*.
- **F2 (standstill time).** Share of route time below 0.1 m/s, read by the cases of the pre-specification of H2: interval below 0 and point estimate at most −4.0 pp (strong); interval below 0 and point estimate above −4.0 pp (partial); negative point estimate with an interval that includes 0 (inconclusive); point estimate 0 or positive (not shown).
- F1 and F2 are reported with unadjusted and Holm-adjusted p-values over the two.
- **Descriptive, no rule:** stay-put share at 0.5 m/s or less and at rest; standstill outside blocked time; blocked time with the permutation test of Section 22c; crawling; Driving Score, route completion, collision events; each next to the value of the partly loaded model.

**Reading, fixed now.**
- F1 met: the plan-level difference holds for the checkpoints as trained. Stage 2 follows.
- F1 not met: the plan-level difference reported for the served models is not shown for the checkpoints as trained. The paper reports this as its result for the pair, and Stage 2 is decided with the author before any further run.
- Whatever the outcome, the paper reports the earlier results as results for partly loaded models and does not pool them with the new runs.

**Stage 2 (only after Stage 1 is read).** Second pass of both checkpoints (repeat test with the rule of Section 9, R1 to R3, applied to the fully loaded runs), gate-off runs (Section 5b), decoupling checkpoint (Sections 6 and 15), 1,600-sample pair, history-swap runs (Section 11). Their rules are those sections' rules, applied to the new runs; any change is written here before the run concerned starts.

**Order of the replay of Section 24.** The replay queue (five fully loaded checkpoints, then the two diagnostics of Section 23) is left to finish before the first closed-loop route starts; its primary statistic SI-1F is read after this section is committed.

### Outcome of sections 23 (diagnostics) and 24 (full-loading replay), recorded 17 Nov 2026, 23:29

Source: `docs/provenance/same_input_results.json`, keys `full_loading` and `diagnostics_section_23`. All five fully loaded checkpoints ran the 384 states without error; in each, the three repeated states reproduced the first run exactly (largest difference of L 0.0 m, same rationale text); each loading printed 308 tensors given, the seven constants not taken, no expert tensor left unpatched.

**SI-1F (primary of section 24).** Per-log mean stay-put share: Golden-6400-Full 0.35 %, Flooded-6400-Matched-Full 17.61 %; difference −17.26 pp, BCa 95 % interval [−23.78, −12.13], Wilcoxon p = 5.6e-6; lower in 27 logs, higher in 0, tied in 4. By the rule of section 24 the fully loaded experts differ on identical inputs in the direction seen for the served models. Pooled over states: 0.63 % against 22.71 %.

**Secondary (descriptive).** Full against served: Golden-6400 −1.64 pp [−2.82, −0.93]; Flooded-6400-Matched +10.37 pp [6.65, 15.10]; Balanced-6400 −1.85 pp [−3.40, −0.93]; Golden-1600 −2.36 pp [−3.99, −1.15]; Flooded-1600 −1.74 pp [−3.71, 0.26]. The partial loading therefore changed the plans of every checkpoint and reduced the contrast of the 6,400 pair to about a third. Among fully loaded checkpoints: Balanced-6400 0.99 %, against Flooded-6400-Matched −16.62 pp [−22.78, −11.74], against Golden-6400 +0.63 pp [0.24, 1.44]; Golden-1600 2.59 % against Flooded-1600 5.34 %, −2.75 pp [−4.71, −1.53]. Against Base (3.28 %) and Base-SelfPatch (4.23 %): the values are in the results file.

**Diagnostics of section 23 (first 24 states, no decision rule).** Base-EmptyLoad equals Base-Repeat in every plan and every rationale text of the 24 states, so an empty loading call does not change the served model. Base-Repeat, a second process of the unchanged base model with the same code and seeds, differs from the first Base process in the rationale text and the plans of 8 of the 24 states, and has the same rationale text as Base-SelfPatch in all 24. The difference between Base and Base-SelfPatch reported in section 23 is therefore not an effect of the patch step. It is a difference between processes: the first Base process sampled other rationale texts than every later process on a subset of the states. A smaller case of the same kind is Flooded-1600-Full, whose text differs from the served Flooded-1600 in 29 of 384 states, most of them states in which the first Base process also differed. The cause is not known. Within a process the output is reproducible (reset checks). Consequences: (i) comparisons with Base in the replay carry a process-level uncertainty of about 1 pp of stay-put share (Base 3.28 % against Base-SelfPatch 4.23 %); (ii) in the closed-loop evaluation one server process serves all routes of a job, so a process-level difference is part of the difference between two jobs; the second pass of section 25 (Stage 2) is the available check on it.

### Outcome of section 25, Stage 1, recorded 19 Nov 2026, 15:47

Queue run from 17 Nov 23:29 to 19 Nov 15:45; 44 of 44 routes scored in each arm, all with a clean loading report (416 tensors, none left unpatched, largest difference 0). One relaunch under the rerun rule: route 28099 of `Flooded-6400` ended without a score at attempt 1 (exit 134, 3 min in; output moved aside) and was scored at attempt 2 (status `Failed - TickRuntime`). No route was invalid. Results: `docs/provenance/fullload_stage1_results.json`, from `scripts/evaluation/fullload_analysis.py`.

- **F1: met.** Share of steps with L < 1.5 m: 1.31 % (Golden-6400) against 26.80 % (Flooded-6400), −25.49 pp, BCa [−31.69, −19.63], Wilcoxon p = 1.1e-13 (Holm 2.3e-13), n = 44. Partly loaded models on the same routes: −10.56 pp [−16.02, −6.77].
- **F2: strong.** Standstill time: 22.97 % against 46.66 %, −23.69 pp, BCa [−33.48, −15.08], p = 3.3e-6 (Holm 3.3e-6). Partly loaded: −8.06 pp [−15.08, −1.25].
- Descriptive: standstill outside blocked time −36.38 pp [−45.55, −28.16]; blocked time +12.69 pp [6.10, 22.48] (Golden 10 routes with blocked time, Flooded none; sign-flip p = 0.002); crawling −5.46 pp [−8.58, −2.90]; stay-put share at 0.5 m/s or less 1.06 % against 26.44 % (35 routes with 20 conditioning steps in both); Driving Score 54.02 against 43.51, +10.52 [2.59, 19.09]; route completion 71.55 % against 63.19 %, +8.36 [1.76, 16.29]; collision events 28 against 28; completed routes 21 against 16.
- Full minus partly loaded, same routes: Golden-6400 standstill −2.75 pp [−10.97, 6.82], route completion −10.83 [−19.85, −3.10]; Flooded-6400 standstill +12.88 pp [3.46, 21.81], route completion −11.46 [−20.44, −3.47]. Full loading moves the flooded checkpoint much further towards stay-put plans and standstill than the golden one; route completion is lower for both.

Reading by the rule above: the plan-level difference holds for the checkpoints as trained, and it is larger than for the partly loaded models. Stage 2 follows. These are first-pass results; the second pass of Stage 2 is the check on run-to-run and process-level variation.

## 26. Fully loaded 6,400-sample checkpoints against the unadapted model in closed loop (post hoc, descriptive), written 19 Nov 2026, 21:18 (UTC+7), before any of these values was computed

**Why.** The author asked on 19 November what the paper can say about performance. Section 4.12 of the manuscript gives the direction relative to the unadapted model only for the replay. This section adds the same comparison in closed loop, from runs that exist; no new run.

**What had been seen when this was written.** The Stage 1 results of section 25 (both fully loaded checkpoints against each other and against the partly loaded models) and all results of `Base-Rerun` (tag `base_run2`, 15–16 Nov) against the partly loaded models. Not computed: any comparison of a fully loaded checkpoint with `Base-Rerun`.

**Comparison.** `Golden-6400` loaded in full (tag `model_matrix_golden_6400_full`) minus `Base-Rerun`, and `Flooded-6400` loaded in full (tag `model_matrix_flooded_6400_full`) minus `Base-Rerun`, paired over the 44 routes, with the statistics of section 25 (paired mean difference, 95 % BCa interval with 20,000 resamples and seed 0, two-sided Wilcoxon signed-rank test). Measures, all listed now: Driving Score, route completion, standstill time, share of steps with L < 1.5 m, stay-put share at 0.5 m/s or less, collision events, mean speed; and the totals of completed routes and collision events. Code: `scripts/evaluation/fullload_vs_base.py`, which imports the definitions of `paper_reanalysis.py`.

**Status.** Post hoc and descriptive; no decision rule; p-values unadjusted. It is not H1 (H1 is `Golden-1600` against `Base-Rerun` in the first series) and does not replace it. `Base-Rerun` was run with the stock server, which loads the base model correctly, on the same harness as the second pass, three days before Stage 1. The two arms are therefore runs of different dates and server processes, each with one pass. The Driving Scores are on 44 routes with a custom controller and are not comparable with published 220-route results.

### Outcome of section 26, recorded 19 Nov 2026, 21:18

44 of 44 routes in every arm. Results: `docs/provenance/fullload_vs_base_results.json`. All values descriptive, p unadjusted.

- **`Golden-6400` loaded in full minus `Base-Rerun`:** Driving Score 54.02 against 42.60, +11.42 [2.83, 21.62], p = 0.057; route completion 71.55 % against 71.93 %, −0.38 pp [−9.78, 9.53]; standstill time 22.97 % against 36.28 %, −13.31 pp [−23.90, −3.35], p = 0.0041; steps with L < 1.5 m 1.31 % against 13.24 %, −11.93 pp [−17.95, −7.65]; stay-put share at 0.5 m/s or less −13.50 pp [−19.46, −9.07] (35 routes); collision events 28 against 49 in total, −0.48 per route [−0.91, −0.11], p = 0.014; mean speed 2.17 against 1.54 m/s; completed routes 21 against 23.
- **`Flooded-6400` loaded in full minus `Base-Rerun`:** Driving Score 43.51 against 42.60, +0.91 [−9.31, 9.97]; route completion 63.19 % against 71.93 %, −8.74 pp [−19.46, 1.46]; standstill time +10.38 pp [−0.07, 20.42]; steps with L < 1.5 m +13.56 pp [6.70, 20.64]; collision events 28 against 49, −0.48 per route [−0.86, −0.11], p = 0.014; mean speed 0.96 against 1.54 m/s; completed routes 16 against 23.

Reading (descriptive): both fully loaded checkpoints had fewer collision events than the unadapted model. The obstacle-heavy checkpoint had them with more near-stationary plans and less progress; the balanced checkpoint had them with fewer near-stationary plans, less standstill and the same route completion. For the Driving Score of `Golden-6400` the interval lies above 0 and the Wilcoxon test does not reject at 0.05. One pass per arm; the second pass of Stage 2 does not repeat `Base-Rerun`.

### Interim look at the fully loaded decoupling checkpoint, recorded 20 Nov 2026, 15:54

The job `model_matrix_fgbalanced_6400_full` ended on 20 Nov 2026 at 06:46: 44 of 44 routes scored at the first attempt, each with a clean loading report. The readings of Sections 6 and 15 use the per-route mean of two default-controller passes of each comparator; the second passes of the fully loaded pair are still running, so those readings are not made yet. What was looked at now is the single-pass sensitivity row that Section 6 provides for (Balanced against the first fully loaded pass of each comparator, 44 routes, same statistics). No rule is changed.

- Against Flooded-6400 (first pass): share of steps with L < 1.5 m 1.58 % against 26.80 %, −25.23 pp [−31.44, −19.58]; standstill 27.79 % against 46.66 %, −18.87 pp [−28.90, −9.12]; blocked time 15.39 % against 0.00 %, +15.39 pp [8.78, 24.42]; Driving Score 47.69 against 43.51, +4.18 [−2.56, 12.83]; route completion +8.28 [2.98, 14.48]; collision events 37 against 28.
- Against Golden-6400 (first pass): L < 1.5 m +0.26 pp [−0.54, 1.57]; standstill +4.82 pp [−4.77, 15.05]; blocked time +2.69 pp [−5.36, 11.45]; Driving Score −6.33 [−14.26, 0.87]; route completion −0.08 [−4.84, 5.23]; collision events 37 against 28.

## 27. Choice of the scenes for a qualitative figure of the same-input replay (illustrative), written 20 Nov 2026, 17:26 (UTC+7), before any scene was looked at for this purpose

**Why.** A figure that shows, for one input, the 16 plans of each fully loaded 6,400-sample checkpoint (Golden, Flooded, decoupling). A scene chosen by eye would be a selected example, so the choice is fixed here by a rule. The figure is illustrative; no test is attached to it and no number in the text depends on it.

**What had been seen when this was written.** The aggregate replay results of Sections 21 and 24. Of single records: the first record of `outputs/same_input/Golden-6400-Full.jsonl` (state 0, printed to inspect the fields of the file). No per-state comparison between checkpoints.

**Rule.** Source: the fully loaded replays `Golden-6400-Full` and `Flooded-6400-Matched-Full` (384 states, 16 plans each). Candidate states: speed of 0.5 m/s or less. For each candidate, d = number of Flooded plans with L < 0.64 m minus number of Golden plans with L < 0.64 m.
- Panel A, the typical state: the candidate whose d is closest to the mean of d over the candidates; ties go to the lowest state index.
- Panel B, the largest difference: the candidate with the largest d; ties go to the lowest state index. The caption says that this is the largest difference of the set and gives the mean.
The decoupling checkpoint (`Balanced-6400-Full`) is shown for the same two states and plays no part in the choice. If a chosen state lacks 16 plans for any of the three checkpoints, the next state by the same rule is taken and this is reported.

**Drawing.** The replay stored the length of each plan, not its waypoints. The figure shows the camera frames of the state next to the 16 plan lengths of each checkpoint. If plan paths are drawn, the three checkpoints are run again on the chosen states only, with the replay code and seeds unchanged, after the closed-loop queue has ended (one GPU job at a time); the lengths of the new plans are compared with the stored lengths, and a mismatch is reported in the caption.

### Interim look at the second pass of the fully loaded Golden-6400, recorded 20 Nov 2026, 20:57

The job `model_matrix_golden_6400_run2_full` ended on 20 Nov 2026 at 20:25: 44 of 44 routes scored, each with a clean loading report; route 26458 ended without a score at its first launch (exit 134) and was scored at its second. When this look was taken, the second pass of Flooded-6400 had one route scored and none of its values had been computed or viewed. The repeat test (Section 9, R1 to R3, applied to the fully loaded second passes) is not made yet and its rule is unchanged. Looked at: the second pass of Golden-6400 against its own first pass, paired over 44 routes, descriptive.

- Share of steps with L < 1.5 m: 1.12 % against 1.31 % (−0.19 pp [−0.68, 0.17]). Standstill: 25.05 % against 22.97 % (+2.08 pp [−4.76, 9.70]). Standstill outside blocked time: 9.15 % against 10.28 %. Blocked time: 15.90 % against 12.69 % (+3.21 pp [−1.80, 10.76]); 11 against 10 routes.
- Driving Score: 49.01 against 54.02 (−5.01 [−12.25, 1.33]). Route completion: 70.94 % against 71.55 %. Collision events: 36 against 28. Routes completed: 19 against 21.

### Partial look at the second pass of the fully loaded Flooded-6400, recorded 21 Nov 2026, 15:05

Taken at the author's request while the job `model_matrix_flooded_6400_run2_full` was running: 30 of its 44 routes were scored. The script `scripts/evaluation/fullload_repeat_test.py` was committed (94e647f8) before the look; after it, only its printout was changed (a comparison in which every difference is 0 has no interval, which the printout did not handle). The rule of Section 9 is unchanged, and the decisions R1 to R3 are made only on the 44 routes. Values on the 30 routes scored in both second passes, Golden minus Flooded, second pass alone:

- Share of steps with L < 1.5 m: 0.80 % against 28.45 %, −27.65 pp [−35.99, −19.55]. Standstill outside blocked time: 7.31 % against 47.21 %, −39.90 pp [−51.63, −28.55]. Blocked time: 17.92 % against 0.00 %, +17.92 pp [8.32, 31.41]. Standstill time: −21.98 pp [−34.99, −7.72].
- Driving Score: 55.20 against 54.15, +1.05 [−10.24, 12.74]. Route completion: +7.05 pp [−0.84, 15.56]. Collision events per route: 0.80 against 0.33, +0.47 [0.17, 0.90].
- On these 30 routes the second pass of Flooded-6400 had a higher Driving Score than its first pass (54.15 against 43.40, +10.75 [3.22, 19.56]) and fewer collision events (10 against 23).

### Outcome of the repeat test on the fully loaded second passes (Sections 9 and 25), recorded 21 Nov 2026, 23:46

The job `model_matrix_flooded_6400_run2_full` ended on 21 Nov 2026 at 22:01: 44 of 44 routes scored at the first attempt, each with a clean loading report. Results: `docs/provenance/fullload_repeat_test_results.json` (script `scripts/evaluation/fullload_repeat_test.py`). Second pass alone, Golden-6400 minus Flooded-6400, 44 routes.

- **R1, replicated.** Share of steps with L < 1.5 m: 1.12 % against 29.28 %, −28.16 pp [−34.81, −21.75], p = 1.1e-13.
- **R2, replicated.** Standstill outside blocked time: 9.15 % against 48.44 %, −39.29 pp [−48.36, −30.34].
- **R3, replicated.** Blocked time: 15.90 % against 0.00 %, +15.90 pp [8.06, 26.85].
- No decision attached. Standstill time on the second pass alone: 25.05 % against 48.44 %, −23.39 pp [−34.18, −12.11] (case A1 of Section 1); on the mean of the two passes −23.54 pp [−32.98, −14.89] (case A1).
- Benchmark outcomes, second pass alone: Driving Score 49.01 against 51.60, −2.59 [−11.94, 6.51]; route completion 70.94 % against 65.62 %, +5.32 pp [−1.67, 12.25]; collision events 36 against 15, +0.48 per route [0.23, 0.77]. Mean of the two passes: Driving Score 51.52 against 47.55, +3.96 [−3.06, 11.67]; route completion +6.84 pp [0.80, 13.29]; collision events per route 0.73 against 0.49, +0.24 [0.00, 0.43].
- Second pass against first pass. Golden-6400: no measure with an interval that excludes 0. Flooded-6400: Driving Score 51.60 against 43.51, +8.09 [1.93, 15.16]; collision events 15 against 28, −0.30 per route [−0.61, −0.11]; plan and standstill measures with intervals that include 0.

**Consequence for Sections 25 and 26.** The Driving Score difference of the first pass (+10.52, reported there as an observation of one pass) did not recur: on the second pass the point estimate has the opposite sign, and on the two-pass mean the interval includes 0. The comparison of Section 26 with the unadapted model rests on one pass of each arm and is to be read with the same reservation.

### Collision events per distance driven, fully loaded pair, recorded 21 Nov 2026, 23:48 (descriptive, after the repeat test was read)

The measure of manuscript Table 3 (collision events per odometer kilometre; ratio with a percentile interval from 20,000 route resamples, seed 0), applied to the two default-controller passes of each fully loaded checkpoint together. Computed because the author asked whether the result can be described as a trade-off that includes collisions. Golden-6400: 64 events in 7.93 km, 8.07 per km (first pass 7.00, second pass 9.15). Flooded-6400: 43 events in 6.90 km, 6.23 per km (first pass 8.22, second pass 4.30). Ratio 1.29 [0.90, 1.92]. The interval includes 1, so a higher collision rate per distance is not shown; the two passes of Flooded-6400 differ by about a factor of two.

### Extension of section 26 and final decoupling reading: what is computed, written 21 Nov 2026, 23:53, before computing

Script `scripts/evaluation/fullload_stage2_readings.py`, committed with this note before it was run. (a) The readings of Sections 6 and 15 for the fully loaded decoupling checkpoint, rules unchanged, with the two-pass means of the fully loaded pair as comparators. Seen before: the single-pass look recorded on 20 Nov and the repeat test. (b) Collision events per odometer kilometre, as recorded above, now written to a result file. (c) Extension of Section 26, post hoc and descriptive, no rule: the second pass and the two-pass mean of each fully loaded 6,400-sample checkpoint, and the one pass of the decoupling checkpoint, against `Base-Rerun` (one pass), with the measures of Section 26 and blocked time. Reason: the first-pass comparison of Section 26 rests on one pass per arm, and the repeat test showed that the Driving Score varies between passes. `Base-Rerun` has one pass, so its own pass-to-pass variation is not averaged out.

### Outcome: decoupling reading and extension of section 26 on the fully loaded runs, recorded 21 Nov 2026, 23:54

Results: `docs/provenance/fullload_stage2_readings.json`.

- **Section 15.** D1, Balanced minus Flooded (two-pass mean): share of steps with L < 1.5 m 1.58 % against 28.04 %, −26.47 pp [−32.42, −20.84]. D2, Balanced minus Golden: +0.36 pp [−0.33, 1.74]. Reading: near-stationary planning follows the manoeuvre mix and the stationary share, not the scenario-group mix. The Balanced checkpoint closes 98.7 % of the gap. Remedy rule: blocked time against Flooded +15.39 pp [8.78, 24.42] (interval above 0), Driving Score +0.14 [−5.90, 6.50]; the mix reduces hesitation at a cost, more blocked time. The word remedy is not used.
- **Section 6.** Standstill time: Balanced minus Flooded −19.76 pp [−28.97, −10.71]; Balanced minus Golden +3.78 pp [−3.86, 12.53]. Reading: follows the manoeuvre mix and stationary share, not the group mix.
- Supporting, against Flooded: route completion +7.06 pp [2.37, 11.80]; collision events per route +0.35 [0.06, 0.69] (37 events against 28 and 15 in the two passes of Flooded). Against Golden: no measure with an interval that excludes 0.
- **Against Base-Rerun** (descriptive). Golden-6400, mean of the two passes: Driving Score 51.52 against 42.60, +8.92 [0.96, 18.04], p = 0.058; route completion −0.68 pp [−10.02, 8.51]; standstill −12.27 pp [−21.55, −3.85]; share of steps with L < 1.5 m −12.02 pp [−18.04, −7.75]; blocked time +13.93 pp [7.37, 23.77]; collision events per route −0.39 [−0.78, −0.09]. Second pass alone: Driving Score +6.41 [−2.07, 15.89]. Flooded-6400, mean of the two passes: Driving Score +4.95 [−5.26, 14.44]; standstill +11.27 pp [1.00, 20.86]; share with L < 1.5 m +14.80 pp [7.95, 21.62]; collision events per route −0.62 [−1.00, −0.31]. Balanced-6400: Driving Score +5.09 [−4.73, 15.00]; share with L < 1.5 m −11.66 pp [−17.66, −7.48].

## 28. Where and how the fully loaded checkpoints are blocked (post hoc, descriptive), written 22 Nov 2026, 00:37 (UTC+7), before computing

**Why.** The repeat test showed that the checkpoints with few stay-put plans have blocked time and that this is the cost that remains. The author asked whether the problem can be fixed; what kind of fix is plausible depends on what a blocked run is. No rule; description only.

**What had been seen when this was written.** The route-level blocked time of the fully loaded runs (Sections 25 and the repeat test), and the Section 18a and Section 20 results of the first series. Nothing below for the fully loaded runs.

**Analysis.** For the fully loaded `Golden-6400` (both passes) and the decoupling checkpoint (one pass), default controller: (a) the Section 18a measure, unchanged (number of blocked runs, share of blocked steps within 10 m of a recorded collision position, sensitivity 5 m and 20 m, blocked time without those runs); (b) per blocked run: route, scenario type, actor types of the route's collision records, duration, route status; (c) the plans during blocked steps: share with L < 1.5 m, share with L of 2.0 m or more, median L; (d) blocked steps by scenario type. Script `scripts/evaluation/fullload_blocked_diagnosis.py`, result `docs/provenance/fullload_blocked_diagnosis.json`.

### Outcome of section 28, recorded 22 Nov 2026, 00:37

Result file `docs/provenance/fullload_blocked_diagnosis.json`.

- **At recorded collision positions.** Share of blocked steps within 10 m of a recorded collision position: Golden-6400 first pass 91.4 % (31 runs, 10 routes), second pass 100.0 % (17 runs, 11 routes), decoupling checkpoint 97.0 % (59 runs, 15 routes). Blocked time without those runs: 1.32 %, 0.00 % and 0.59 % of steps.
- **Plans while blocked.** The checkpoints keep planning to drive on: plans of 2.0 m or more in 97.7 %, 99.7 % and 96.4 % of blocked steps (median plan length 11.8 m, 20.0 m and 13.0 m); plans shorter than 1.5 m in 0.8 %, 0.1 % and 1.6 %.
- **Where.** Mostly at another vehicle (routes with blocked time whose collision records name a vehicle: 8 of 10, 11 of 11, 12 of 15), in scenarios with an obstacle in the lane (door opening, accident, parked or construction obstacle, hard braking of a lead vehicle) and at junction turns. Most of these routes then end by the time limit (6 of 10, 8 of 11, 10 of 15).
- **Reading (descriptive).** In these runs a blocked run is a vehicle that has made contact and keeps commanding forward motion against the obstacle. The decoupling checkpoint, trained on the obstacle-heavy scenario mix, is blocked on more routes than Golden-6400, so a larger share of obstacle scenarios did not by itself prevent it.

### Partial look at the gate-off runs of the fully loaded pair, recorded 22 Nov 2026, 21:03

Taken at the author's request. `model_matrix_golden_6400_nogate_full` ended on 22 Nov 2026 at 10:31 (44 of 44 routes; route 28099 scored at its second launch). `model_matrix_flooded_6400_nogate_full` was running with 22 of 44 routes scored. The script `scripts/evaluation/fullload_gateoff_analysis.py` was committed before any gate-off value was computed. The reading of Section 4c is made only on the 44 routes.

- Golden-6400, gate-off against the mean of its two default passes (44 routes): standstill 18.76 % against 24.01 %, −5.24 pp [−9.21, −1.57]; Driving Score 51.45 against 51.52; route completion 72.36 % against 71.24 %; blocked time 12.62 % against 14.29 %; collision events per route 0.73 against 0.73.
- Flooded-6400, gate-off against the mean of its two default passes (22 routes): standstill 18.49 % against 37.85 %, −19.36 pp [−30.44, −11.41]; route completion 85.38 % against 74.05 %, +11.33 pp [5.26, 21.38]; share of steps with L < 1.5 m 12.23 % against 22.76 %; crawling 20.43 % against 12.54 %; Driving Score 54.99 against 52.23, +2.75 [−11.98, 14.56].
- Golden minus Flooded without the gate (22 routes): standstill 15.94 % against 18.49 %, −2.55 pp [−14.36, 11.99]; share with L < 1.5 m 0.77 % against 12.23 %, −11.46 pp [−22.47, −5.58]; standstill outside blocked time −13.22 pp [−25.50, −6.19]; blocked time 10.67 % against 0.00 %; crawling −12.92 pp [−19.01, −8.93]; route completion 77.66 % against 85.38 %, −7.73 pp [−19.46, 2.72]; Driving Score 55.75 against 54.99.
- Interaction on standstill, default = mean of the two passes (22 routes): +16.10 pp [5.34, 28.22]; noise reference between the two default passes +4.27 pp [−7.24, 18.72].

### Outcome of the gate-off runs of the fully loaded pair (Section 4c), recorded 23 Nov 2026, 22:05

`model_matrix_flooded_6400_nogate_full` ended on 23 Nov 2026 at 06:43 (44 of 44 routes; route 28087 scored at its second launch, its first attempt had no score). Both gate-off runs count on all 44 routes with a clean loading report. Result file: `docs/provenance/fullload_gateoff_results.json`, written by the script committed before any gate-off value was computed. Exploratory, as all of Section 4. This reading was made after the partial look recorded above; the script was not changed between the two.

- **Golden minus Flooded without the gate.** Standstill below 0.1 m/s: 18.76 % against 23.41 %, −4.65 pp [−11.44, 3.20] (Wilcoxon p = 0.0048; the interval includes 0). With the default controller, mean of the two passes, same routes: 24.01 % against 47.55 %, −23.54 pp [−32.98, −14.89].
- **Interaction** (gate-off difference minus default difference): +18.89 pp [11.29, 27.16] with the two-pass mean as the default, +19.04 pp [11.03, 28.18] with the first pass. Noise reference, second-pass difference minus first-pass difference: +0.30 pp [−8.75, 9.62].
- **What persists without the gate.** Share of steps with L < 1.5 m: 0.60 % against 14.58 %, −13.99 pp [−20.27, −9.52]. Time below 0.5 m/s −12.33 pp [−19.04, −4.32]; below 1.0 m/s −21.40 pp [−28.67, −12.77]. Standstill outside blocked time −16.92 pp [−25.59, −10.81]. Crawling 7.42 % against 24.18 %, −16.76 pp [−22.07, −12.68]. Mean speed 2.28 against 1.38 m/s, +0.90 [0.64, 1.11].
- **Per checkpoint, gate-off against the mean of its two default passes.** Flooded-6400: standstill 23.41 % against 47.55 %, −24.14 pp [−32.75, −17.05]; crawling 24.18 % against 11.49 %, +12.69 pp [8.41, 18.42]; share with L < 1.5 m 14.58 % against 28.04 %, −13.46 pp [−19.34, −8.65]; route completion 75.35 % against 64.40 %, +10.95 pp [3.97, 18.02]; Driving Score 45.69 against 47.55, −1.87 [−10.16, 5.41]; collision events per route 0.91 against 0.49, +0.42 [0.14, 0.72] (40 events against 28 and 15 in the two default passes; with the road layout +0.20 [0.06, 0.36]); routes completed 24 against 16 and 18; routes ended by the 60 s rule 4 against 10 and 7. Golden-6400: standstill 18.76 % against 24.01 %, −5.24 pp [−9.21, −1.57]; Driving Score 51.45 against 51.52; route completion 72.36 % against 71.24 %; blocked time 12.62 % against 14.29 %; collision events per route 0.73 against 0.73.
- **Other outcomes without the gate, Golden minus Flooded.** Driving Score 51.45 against 45.69, +5.77 [−1.68, 13.84]; route completion 72.36 % against 75.35 %, −2.99 pp [−9.92, 4.16]; collision events per route 0.73 against 0.91, −0.18 [−0.45, 0.05]; blocked time 12.62 % against 0.35 %, +12.27 pp [5.14, 22.77].
- **Reading by the rule of Section 4c.** Both parts of the rule apply, to different measures. The difference in standstill below 0.1 m/s shrinks to an interval that includes 0, and the interaction lies well outside the noise reference: the gate amplifies the difference in full stops. The difference in short plans and in time at low speed persists without the gate: its origin is in the plans. Without the gate Flooded-6400 crawls where it stood still before.
- **Not expected in advance.** Without the gate the share of short plans of Flooded-6400 is about half of its value with the gate (14.58 % against 28.04 %). The plans depend on the state, and the gate keeps the vehicle at rest, where short plans are most frequent. The closed-loop share of short plans is therefore not a property of the model alone.

## 29. Driving efficiency of the fully loaded checkpoints (post hoc, descriptive), written 23 Nov 2026, 22:17 (UTC+7), before computing

**Why.** Over both passes the Driving Score of the two 6,400-sample checkpoints did not differ detectably, while standstill time and mean speed did. The author asked whether the checkpoints can be compared by time or efficiency of driving. Mean speed over all logged steps is already reported (Section 25); the measures below were not computed before this section was committed.

**Runs.** `model_matrix_golden_6400_full`, `model_matrix_flooded_6400_full`, their second passes (`…_run2_full`) and `model_matrix_fgbalanced_6400_full`; 44 routes, default controller, clean loading report. No gate-off run.

**Measures (per route).**
- **E1, time to complete.** Game time of the route in seconds (`duration_game`), only on routes that every compared run completed (status Completed or Perfect). On these routes both vehicles covered the same distance, so the time is comparable.
- **E2, progress rate.** Route distance completed per second of route time: route completion × route length / `duration_game`, in m/s, on all 44 routes. It includes routes that ended early, so it depends on the termination rules.
- **E3, speed while moving.** Mean speed over the logged steps at 0.1 m/s or more, on routes with at least 20 such steps in every compared run. It separates driving faster from waiting less.

**Comparisons.** Golden minus Flooded on the per-route mean of the two passes, and on each pass alone; decoupling checkpoint (one pass) minus the two-pass mean of each of the other two. Paired by route, 95 % BCa interval (20,000 resamples, seed 0), two-sided Wilcoxon signed-rank test, as in `paper_reanalysis.py`. The number of routes is reported with every comparison; a comparison with fewer than 5 routes is reported as not computable.

**Reading.** Descriptive, no decision rule and no adjustment. A higher value of E2 or E3, or a lower E1, is described as faster or as more progress per unit time, not as better driving, and is reported next to blocked time and collision events per distance. If the Driving Scores are similar while route completion differs, the infraction penalty differs in the other direction; the mean penalty factor of each checkpoint is reported for that reason.

**Script.** `scripts/evaluation/fullload_efficiency.py`, result file `docs/provenance/fullload_efficiency.json`.

### Outcome of Section 29, recorded 23 Nov 2026, 22:18

Result file `docs/provenance/fullload_efficiency.json`; the script was not changed after the rule was committed.

- **E1, time to complete** (routes completed by all compared runs). Golden minus Flooded, two-pass mean, 11 routes: 45.62 s against 76.51 s, −30.89 s [−60.44, −19.98]. First pass (14 routes) −41.33 s [−66.13, −28.44]; second pass (15 routes) −29.62 s [−50.70, −17.36].
- **E2, progress rate** (44 routes). Two-pass mean 1.83 against 0.92 m/s, +0.91 [0.70, 1.15]; first pass +1.01 [0.78, 1.26]; second pass +0.81 [0.54, 1.07].
- **E3, speed while moving** (43 routes). Two-pass mean 2.82 against 1.76 m/s, +1.06 [0.93, 1.21]. Golden-6400 is therefore faster while moving as well, not only waiting less.
- **Penalty factor** (lower = larger infraction penalty). Two-pass mean 0.72 against 0.78, −0.06 [−0.12, 0.01]; first pass 0.75 against 0.75; second pass 0.69 against 0.81, −0.12 [−0.20, −0.04].
- **Decoupling checkpoint.** Against Flooded-6400: E1 −34.82 s [−48.95, −27.79] (14 routes), E2 +0.96 m/s [0.69, 1.17], E3 +1.13 m/s [0.97, 1.25], penalty factor 0.66 against 0.78, −0.12 [−0.20, −0.03]. Against Golden-6400 no measure differed with an interval excluding 0 (E1 −3.86 s [−9.48, 2.25], 16 routes).
- **Reading (descriptive).** The two checkpoints that wait less are about twice as fast by progress per unit time. E1 rests on the routes that all runs completed (11 to 16 of 44), which are the easier routes. The penalty factor points the other way in the second pass and for the decoupling checkpoint, so faster is not reported as better.

## 30. Driving Efficiency as defined by Bench2Drive (post hoc, descriptive), written 23 Nov 2026, 22:23 (UTC+7), before computing

**Why.** The author asked whether Bench2Drive has a built-in measure of efficiency that can be used in place of, or next to, the measures of Section 29. It has: the Driving Efficiency of the official tool `tools/efficiency_smoothness_benchmark.py`. The evaluation harness places 20 checkpoints along each route (`MinimumSpeedRouteTest`, `checkpoints=20`); each time the ego vehicle passes one, it records the ego speed as a percentage of the mean speed of the background vehicles since the previous checkpoint. These records are in every `checkpoint_endpoint.json` of our runs (`min_speed_infractions`). No value of them was computed before this section was committed; one route file was opened to see the format.

**Definition (that of the official tool, unchanged).** Per route: the mean of the recorded percentages, leaving out values above 1000; a route without any record is left out. Per run: the mean over the routes that remain.

**Runs.** The five fully loaded default runs of Section 29, the two gate-off runs (`…_nogate_full`) and `base_run2` (no loading report required for the unadapted model).

**Reported.** Per run: Driving Efficiency, the number of routes that enter it and the mean number of records per route. Paired by route (95 % BCa interval, Wilcoxon), on the routes with at least one record in every compared run: Golden minus Flooded on the two-pass mean and on each pass; decoupling checkpoint against each; each fully loaded checkpoint (two-pass mean, decoupling one pass) against `base_run2`; gate-off against the two-pass default mean per checkpoint, and Golden minus Flooded gate-off.

**Limits known in advance.** (i) A record is written only when a checkpoint is passed, so the time a vehicle spends in its last, unfinished segment (a final stop, a blocked vehicle) is not counted, and a vehicle that stops early contributes few records. The measure is therefore conditional on progress and understates waiting. (ii) 44 routes and our controller, so the value is not comparable with published 220-route values. (iii) The Driving Smoothness of the same tool needs per-step vehicle kinematics (`metric_info.json`), which our agent did not save; it is not computed.

**Reading.** Descriptive, no decision rule. Script `scripts/evaluation/fullload_b2d_efficiency.py`, result file `docs/provenance/fullload_b2d_efficiency.json`.

### Outcome of Section 30, recorded 23 Nov 2026, 22:25

Result file `docs/provenance/fullload_b2d_efficiency.json`; the script was not changed after the rule was committed.

- **Per run** (Driving Efficiency; routes with a record; mean records per route). Golden-6400: 102.50 (43; 12.86) and 102.25 (43; 12.68). Flooded-6400: 77.18 (41; 11.25) and 81.98 (42; 11.73). Decoupling: 102.45 (43; 12.89). Base-Rerun: 88.56 (43; 13.11). Gate-off: Golden 103.99 (43; 13.16), Flooded 83.76 (43; 13.50).
- **Golden minus Flooded.** Two-pass mean, 41 routes: 103.08 against 80.19, +22.89 [6.14, 34.89]; first pass +26.27 [4.58, 37.70]; second pass +20.78 [4.95, 34.97] (42 routes).
- **Decoupling checkpoint.** Against Flooded +22.63 [6.26, 37.53] (41 routes); against Golden +0.07 [−6.16, 6.53] (43 routes).
- **Against Base-Rerun.** Golden +13.82 [6.32, 22.13] (43 routes); decoupling +13.89 [6.17, 21.68]; Flooded −8.54 [−21.96, 9.33] (41 routes; Wilcoxon p = 0.010, interval includes 0).
- **Gate-off.** Against the default mean of the same checkpoint: Golden +1.61 [−1.79, 6.99], Flooded +1.44 [−14.13, 14.79]. Golden minus Flooded without the gate: +20.23 [3.39, 32.06] (43 routes).
- **Reading (descriptive).** The benchmark's own measure gives the order of Section 29: Golden-6400 and the decoupling checkpoint drive at about the speed of the surrounding traffic, Flooded-6400 at about 80 % of it, the unadapted model in between. The difference between the checkpoints stays without the gate, as expected of a measure that leaves out the unfinished last segment (limit (i)). The intervals are wide and skewed, because a few routes with few records carry large differences.

## 31. The 1,600-sample pair loaded in full: tests and reading, written 23 Nov 2026, 22:29 (UTC+7), before any value of these runs was computed

**Why.** Section 25 lists the 1,600-sample pair in Stage 2 with "the rules of the earlier sections", but no earlier section has a decision rule for this pair: in the first series it appeared only in the 2 × 2 contrasts (exploratory, unadjusted) and, for `Golden-1600`, in H1. This section fixes the tests. It is written after the runs started, which Section 25 did not intend: `model_matrix_golden_1600_full` ended on 23 Nov 2026 at 20:58 (44 routes) and `model_matrix_flooded_1600_full` was running with 4 of 44 routes scored.

**What had been seen when this was written.** Of these two runs: the route status lines of the audit log as they passed (two of them read: one `Failed - TickRuntime`, one `Failed - Agent deviated from the route`, both of `Flooded-1600`) and the count of scored routes. No plan, speed, score or infraction value of either run was computed or viewed. Known from other work: in the first series (partly loaded) the two mixes did not differ detectably at 1,600 samples; on identical replayed inputs the fully loaded `Golden-1600` returned stay-put plans in 2.59 % and `Flooded-1600` in 5.34 % (−2.75 pp [−4.71, −1.53], Section 25 outcome); all results of the 6,400-sample pair, including the efficiency measures of Sections 29 and 30, which are post hoc for that pair.

**Runs and statistics.** `Golden-1600` minus `Flooded-1600`, 44 routes, one pass each, default controller, clean loading report required. Paired by route, 95 % BCa interval (20,000 resamples, seed 0), two-sided Wilcoxon signed-rank test, code of `paper_reanalysis.py`. If a route has no score after the rerun rule, the tests use the routes scored in both.

- **S1 (plans; primary).** Share of logged steps with L < 1.5 m. *Met* if the difference is negative, the interval lies below 0 and p < 0.05; otherwise *not met*. Same rule as F1.
- **S2 (standstill time).** Share of route time below 0.1 m/s, read by the four cases of F2 (strong, partial, inconclusive, not shown).
- **S3 (Driving Efficiency, Bench2Drive definition of Section 30).** On the routes with a record in both runs. *Met* if the difference is positive, the interval lies above 0 and the Holm-adjusted p < 0.05; otherwise *not met*.
- S2 and S3 are reported with unadjusted p-values and with Holm-adjusted p-values over the two. S1 is tested alone.
- **Descriptive, no rule.** The other measures of Sections 25 and 29 (standstill outside blocked time, blocked time with the sign-flip test, crawling, Driving Score, route completion, collision events, mean speed, time to complete, progress rate, speed while moving, penalty factor); each 1,600 checkpoint against `base_run2`, including the Driving Score of `Golden-1600` against `base_run2` (the comparison of H1, here on the fully loaded checkpoint, one pass, not a registered test); and the size contrast: the difference of the 6,400 pair (per-route mean of its two passes) minus the difference of the 1,600 pair, for S1, S2 and S3.

**Reading, fixed now.**
- S1 met: the plan-level difference between the mixes is present at 1,600 samples as well. With the size contrast it is reported as smaller than, similar to or larger than at 6,400 only if the interval of the size contrast excludes 0; otherwise as not distinguishable in size.
- S1 not met: at 1,600 samples a difference in near-stationary plans is not shown in closed loop. Together with the replay value above, the paper then reports that the difference on identical inputs did not carry over to a detectable closed-loop difference at this size.
- Each checkpoint has one seed and one pass, and the 1,600-sample training runs were interrupted and resumed; the paper says so with either outcome. No pass-to-pass variation is available for this pair, so a Driving Score difference in one pass is not interpreted (Section 25, second pass: the first-pass difference of the 6,400 pair did not recur).

**Script.** `scripts/evaluation/fullload_pair1600.py` (to be committed before it is run on the complete pair), result file `docs/provenance/fullload_pair1600_results.json`.

**Outcome of Section 31 (24 Nov 2026, 13:55).** `model_matrix_flooded_1600_full` ended on 24 Nov 2026 at 13:52; all 44 routes of both runs have a score at the first launch and a clean loading report. The script was committed (`5cfed292`, 24 Nov 13:54) after a test of its code path on the 6,400-sample pair only, and then run once on the pair. Result file `docs/provenance/fullload_pair1600_results.json`.

- **S1: met, narrowly.** Share of steps with L < 1.5 m 4.92 % (`Golden-1600`) against 8.34 % (`Flooded-1600`): −3.42 pp, interval [−7.74, −0.11], p = 0.047. The upper end of the interval and the p-value are both close to their thresholds.
- **S2: inconclusive.** Standstill time 24.93 % against 33.41 %: −8.49 pp, interval [−17.19, 0.46], p = 0.015 (Holm 0.030). Negative point estimate, interval includes 0.
- **S3: not met.** Driving Efficiency 97.83 against 102.30 on the 43 routes with a record in both: −4.47, interval [−16.61, 2.29], p = 0.188 (Holm 0.188). The sign is opposite to that of the 6,400-sample pair.
- **Size contrast (6,400 difference minus 1,600 difference).** S1 −23.41 pp [−31.39, −15.49]; S2 −15.05 pp [−26.97, −4.16]; S3 +26.99 [10.56, 40.03] (41 routes). All three intervals exclude 0: by the reading fixed above, the difference between the mixes is smaller at 1,600 samples than at 6,400.
- **Descriptive.** Blocked time 1.26 % against 1.90 % (−0.64 pp [−3.72, 2.24]; 6 non-zero pairs, sign-flip p = 0.78). Standstill outside blocked time −7.84 pp [−16.79, 1.02]. Crawling −0.46 pp [−2.44, 0.89]. Driving Score 52.83 against 46.56 (+6.27 [−3.21, 17.69]). Route completion 69.92 against 74.33 (−4.40 pp [−12.46, 3.14]). Collision events 29 against 38 (−0.20 per route [−0.55, 0.14]). Mean speed 2.07 against 1.79 m/s (+0.28 [0.01, 0.54]). Routes completed 20 and 20. Time to complete on the 15 routes both completed 48.97 s against 54.55 s (−5.59 s [−19.00, −0.65], p = 0.42). Progress rate +0.13 m/s [−0.10, 0.35]. Speed while moving +0.12 m/s [0.00, 0.25]. Penalty factor 0.74 against 0.61 (+0.13 [0.04, 0.24]).
- **Against `base_run2` (descriptive).** `Golden-1600`: Driving Score 52.83 against 42.60, +10.23, interval [1.06, 21.69], Wilcoxon p = 0.19 (interval and test disagree; not a registered test and one pass, so not interpreted beyond this line); near-stationary plans −8.32 pp [−13.98, −3.90]; standstill −11.35 pp [−20.67, −2.17]; collision events 29 against 49; Driving Efficiency +9.27 [2.31, 16.85]. `Flooded-1600`: Driving Score +3.96 [−7.65, 13.99]; near-stationary plans −4.90 pp [−11.43, 1.02]; standstill −2.86 pp [−13.90, 7.85]; collision events 38 against 49; Driving Efficiency +13.74 [6.03, 28.32].

**Reading by the rule fixed above.** S1 is met, so the paper reports that the plan-level difference between the mixes is present at 1,600 samples as well, and that it is smaller than at 6,400 samples (size contrast). It also reports that S1 is met by a small margin, that standstill time is inconclusive and that Driving Efficiency does not differ detectably, so that at 1,600 samples the difference in plans is not shown to reach the motion of the vehicle. One seed and one pass per checkpoint; the 1,600-sample training runs were interrupted and resumed.

## 32. Motion-history swap test with the checkpoints loaded in full, written 24 Nov 2026, 13:59 (UTC+7), before any such run existed

Section 25 lists the history-swap runs in Stage 2 with the rules of Section 11. This section names the runs and states that nothing in those rules changes. No history-swap run with a fully loaded checkpoint exists when this is written, and no fully loaded checkpoint has been queried with a replaced history.

**What had been seen.** The first-series outcome (partly loaded models, Section 11-B applied): no detectable dependence of the controls on the ego history for either model (W-a +5.32 pp [−2.40, 13.97] for the obstacle-heavy model, +4.79 pp [−1.89, 11.75] for the balanced one). Every result of the second series to date, including the 1,600-sample pair (Section 31).

**Runs.** `Flooded-6400` and `Golden-6400`, loaded in full by the corrected server, one pass each on the eight replicate routes (2534, 3561, 1790, 23695, 28087, 2664, 17563, 26458) with `alpamayo_bridge_agent_histswap.py` unchanged (SHA-256 `7a23d87d…8192`). Tags `model_matrix_flooded_6400_histswap_full` and `model_matrix_golden_6400_histswap_full`. Queue: `scripts/common/run_fullload_suite.sh` with these two jobs added, its rerun rule and its loading check unchanged. The first route (2534, obstacle-heavy checkpoint) serves as the check that the server used the replaced history (first-waypoint distance, as in Section 11-B); it is that route's run and is not repeated.

**Outcomes, reading rule, sensitivity, limits.** Those of Section 11-B, with the per-route rule and the statistics of Section 11: W-a (primary) and W-b per checkpoint among steps at ≤ 0.5 m/s, the descriptive splits, and the sensitivity version without the true-history steps that directly follow a swap step. Code: the functions of analysis W in `paper_reanalysis.py`, imported by `scripts/evaluation/fullload_histswap.py`; a route counts only with a score and a clean loading report. Result file `docs/provenance/fullload_histswap_results.json`.

**What the paper may say.** As in Section 11-B. In addition, fixed now after the review of 17 November: whatever the outcome, the paper states that the test replaced the ego-history tokens only and left the camera window unchanged, so a visual route to the same shortcut is not tested; and that an outcome without detectable dependence cannot separate an expert that ignores its history from one that continues the motion its history reports. The first-series outcome is reported beside the new one; the two are not pooled.

## 33. Two descriptive additions for the fully loaded runs asked for by the review of 17 November, written 24 Nov 2026, 14:01 (UTC+7), before computing

Post hoc, descriptive, no decision rule, no new runs. Neither quantity has been computed or viewed for any fully loaded run.

**(a) Comparison rate of the position match (review item R7).** Section 28 reports that nearly all blocked steps of the fully loaded checkpoints lie within 10 m of a recorded collision position. Section 22(d) gave the comparison rate for the first series only. The same function (`position_match` of `paper_reanalysis.py`, unchanged) is applied to the fully loaded runs: both passes of `Golden-6400` and `Flooded-6400`, the decoupling checkpoint, the two runs without the gate and the 1,600-sample pair. Reported per run and pooled: (i) of the runs of at least 100 consecutive standstill steps that are not blocked runs, the share within 10 m of a recorded collision position, over all such runs and over those on a route with a collision record; (ii) the placement rate of Section 22(d). The paper states the pooled comparison rate beside the share of Section 28 and words the co-location accordingly.

**(b) Bench2Drive Success Rate (suggested item S20).** Share of the 44 routes that were completed without an infraction other than a minimum-speed record (definition of `tools/merge_route_json.py` of the benchmark, as coded in `paper_reanalysis.py` for the first series), for the same runs and for `base_run2`. Reported per run as a count and a percentage; for the 6,400-sample pair also the paired difference of the two-pass mean with its BCa interval. No test.

Script `scripts/evaluation/fullload_review_additions.py`, result file `docs/provenance/fullload_review_additions.json`.

**Outcome of Section 33 (24 Nov 2026, 14:02).** Result file `docs/provenance/fullload_review_additions.json`.

- **(a) Comparison rate.** Over the nine fully loaded runs there are 224 runs of at least 100 standstill steps that are not blocked runs; 91 of them lie within 10 m of a recorded collision position (40.6 %), and 91 of the 119 on a route with a collision record (76.5 %). Per run, on routes with a collision record: `Golden-6400` 2 of 2 and 3 of 3; `Flooded-6400` 13 of 27 and 9 of 14; decoupling checkpoint 2 of 2; without the gate `Flooded-6400` 25 of 28 (no such run for `Golden-6400`); `Golden-1600` 19 of 21; `Flooded-1600` 18 of 22. Placement rate of the blocked runs (share of the distance travelled on the route within 10 m of a collision position): 34.6 % and 30.9 % (`Golden-6400`), 43.7 % (decoupling), 28.2 % (`Golden-6400` without the gate), 27.3 % and 54.5 % (1,600-sample pair), 83.0 % for the two blocked runs of `Flooded-6400` without the gate. Reading (descriptive): the share of blocked steps at a collision position (91.4 % to 100 %, Section 28) is well above the placement rate, but long stops that are not blocked also lie at collision positions in about three of four cases on routes with a collision record. The co-location is therefore not specific to blocked time.
- **(b) Success Rate.** Routes of 44 completed without an infraction other than a minimum-speed record: `Golden-6400` 9 and 6 (20.5 % and 13.6 %); `Flooded-6400` 3 and 5 (6.8 % and 11.4 %); decoupling checkpoint 3 (6.8 %); without the gate 5 (`Golden-6400`) and 6 (`Flooded-6400`); `Golden-1600` 8 (18.2 %); `Flooded-1600` 7 (15.9 %); `base_run2` 6 (13.6 %). `Golden-6400` minus `Flooded-6400`, mean of the two passes: 17.05 % against 9.09 %, +7.95 pp, interval [−2.27, 17.05]. Not detectably different.

### Scene choice by the rule of Section 27, recorded 24 Nov 2026, 14:39

Computed from the stored replays `Golden-6400-Full`, `Flooded-6400-Matched-Full` and `Balanced-6400-Full` (384 states, 16 plans each for all three). All 384 states are candidates (speed of 0.5 m/s or less). Mean of d over the candidates: 3.53 plans of 16.
- **Panel A (typical state):** state 7 (d = 4; scenario `SignalizedJunctionLeftTurnEnterFlow`, speed 0.0 m/s, instruction "Turn left in 14m"). Stay-put plans of 16: Golden 0, Flooded 4, decoupling 0; median plan length 5.68 m, 1.10 m and 5.96 m.
- **Panel B (largest difference):** state 120 (d = 16, the only state with this value; scenario `PedestrianCrossing`, speed 0.03 m/s, instruction "Turn right in 25m"). Stay-put plans of 16: Golden 0, Flooded 16, decoupling 8; median plan length 1.50 m, 0.23 m and 0.64 m.
- Not chosen by eye, and reported as found: Panel B is a pedestrian-crossing scenario, in which staying put may be the required behaviour. The caption says so. No state had to be skipped.
- The camera frames and, if drawn, the plan paths are produced after the history-swap queue has ended (one GPU job at a time; no dataset loading while routes run).

## 34. Sensitivity and pass-to-pass variation of the fully loaded 6,400-sample pair, written 24 Nov 2026, 15:27 (UTC+7), before computing

Post hoc, descriptive, no decision rule, no new runs. Reason: at the author's request of 24 November the main text reports the runs with full loading only, and the first series is kept as a disclosure in the Supplement. The main text so far took three items from the first series that have a direct counterpart in the fully loaded runs. None of the values below has been computed or viewed.

**(a) Route subsets.** The contrasts F1 (share of steps with L < 1.5 m) and F2 (standstill time), `Golden-6400` minus `Flooded-6400`, on the first pass, the second pass and the per-route mean of the two passes, (i) on the 37 routes not touched by training samples (Section 2 list of seven routes left out) and (ii) on the 24 routes not used to tune the controller (the route list of analysis Z, manifest key `H.tuning_routes_union`). Paired, BCa interval and Wilcoxon test as in Section 25. Reported as sensitivity rows; the decisions of F1 and F2 are not changed by them.

**(b) Pass-to-pass variation.** For each fully loaded 6,400-sample checkpoint: the standard deviation over the 44 routes of the difference between its two passes, and the intraclass correlation ICC(1,1) of analysis N (`icc_1_1`, unchanged), for standstill time, the share of steps with L < 1.5 m and Driving Score.

Script `scripts/evaluation/fullload_sensitivity.py`, result file `docs/provenance/fullload_sensitivity.json`.

**Outcome of Section 34 (24 Nov 2026, 15:28).** Result file `docs/provenance/fullload_sensitivity.json`.

- **(a) 37 routes not touched by training samples**, mean of the two passes: near-stationary plans 1.32 % against 28.01 %, −26.69 pp [−33.09, −20.67]; standstill time 21.05 % against 48.17 %, −27.13 pp [−37.35, −17.19]. First pass −25.13 pp [−31.62, −19.06] and −27.53 pp [−38.14, −17.91]; second pass −28.25 pp [−35.51, −21.48] and −26.72 pp [−38.97, −13.21].
- **(a) 24 routes not used to tune the controller**, mean of the two passes: near-stationary plans 1.20 % against 27.46 %, −26.27 pp [−34.35, −18.56]; standstill time 18.46 % against 46.58 %, −28.12 pp [−41.62, −16.15]. First pass −24.87 pp [−33.63, −17.17] and −27.12 pp [−41.40, −14.34]; second pass −27.67 pp [−36.02, −19.57] and −29.12 pp [−43.59, −14.40].
- Both contrasts keep their sign and size on both subsets, with intervals below 0 in every row.
- **(b) Pass-to-pass variation.** Standard deviation of the per-route difference between the two passes: standstill time 24.73 pp (`Golden-6400`) and 18.29 pp (`Flooded-6400`); Driving Score 23.36 and 22.43 points; near-stationary plans 1.42 pp and 13.92 pp. ICC(1,1): standstill 0.67 and 0.84; Driving Score 0.70 and 0.68; near-stationary plans 0.68 and 0.80.
