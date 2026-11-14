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

