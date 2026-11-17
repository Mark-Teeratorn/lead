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
