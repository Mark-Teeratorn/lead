# Deviations from the Confirmatory Pre-Registration and Undisclosed Protocol Facts

**Date:** 12 November 2026. Written before the primary endpoint of the matched run was computed.
Scope: the 44-route evaluation of `Matrix-Flooded-6400` (11–12 November 2026) and the comparisons that use it. Evidence files are in `docs/provenance/`.

## A. Deviations from `CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md`

| # | Pre-registered | What happened | Consequence |
|---|---|---|---|
| A1 | Rendering quality Epic | The launcher sets Low on every route outside Town02/Town03 (`scripts/common/eval_alpamayo_b2d.sh` L60–65). All 44 canonical routes are in other towns, so every model in the 44-route matrix ran at Low. | Identical across models; the pre-registration text and manuscript §3.4 are wrong and are corrected. |
| A2 | Every infrastructure failure logged in `outputs/rerun_audit_matrix_flooded_6400.log` during the run | The log was not written. It was reconstructed on 12 Nov from the progress and watchdog logs. | Reconstruction shows 45 evaluator launches, 44 results, one per route, no route scored twice. |
| A3 | Reruns only for CARLA crash or RPC timeout; sequential execution without manual intervention | Route 2534 was launched three times and route 1852 twice before the first scored run, because the model server and one evaluator process were killed during start-up; the watchdog supervisor was restarted manually once (17:21). | All restarts preceded any simulation step and any score. Disclosed as outside the permitted list. |
| A4 | "Open Maneuver routes: zero traffic signals, zero stop signs, zero pedestrians" | False; the group includes signalized and non-signalized junction routes, a bicycle-flow route and two-way routes. | Description withdrawn; strata frozen in `ANALYSIS_ADDENDUM.md` §2. |
| A5 | Document presented as a pre-registration | It was committed on 11 Nov 2026 (`013a12bd`), after the same 44 routes had been evaluated for five other models, and after the endpoint had been chosen from those results. | Reported as a pre-specified replication test on previously observed routes, not as a registration prior to all data. |

## B. Facts about the protocol that the manuscript does not state

1. **Early termination.** `scenario_manager.py` L183–192 stops a route after 4,000 ticks (200 s) or after 1,200 consecutive ticks (60 s) with ego speed below 0.1 m/s. Both appear as `Failed - TickRuntime`. The standstill fraction is therefore censored. Routes with that status among the 44 (ended by the 60 s rule / by the 4,000-tick cap): matched flooded 7 (7 / 0), Golden-6400 3 (3 / 0), historical flooded 4 (3 / 1), Golden-1600 5 (5 / 0), Flooded-1600 3 (1 / 2), Base 7 (0 / 7).
2. **The 60 s rule was introduced during data collection.** The file carrying it is dated 4 Oct 2026. By result-file dates, 38 of the 44 `Base` routes were evaluated before that date (29 Sep–3 Oct) and 6 after. `Base` was therefore measured mostly under a different termination rule from the four fine-tuned models: all seven of its `TickRuntime` routes ran to the 4,000-tick cap, where a fine-tuned model in the same situation would have been stopped after 60 s. This inflates `Base` standstill time relative to the other models and affects the `Base` rows of Tables 3–4 and the H1 comparison (Golden-1600 vs Base).
3. **Harness changes between the two arms of H2.** `leaderboard_evaluator.py`, `route_scenario.py` and the launcher were modified on 10 Nov 2026: large-map streaming settings applied only on Town12/13, synchronous mode and step set explicitly, a guard around `stop_scenario`, a guard for an empty parked-vehicle batch, and the client timeout raised from 60 s to 180 s. Golden-6400 was evaluated on 19–20 Oct, the matched flooded model on 11–12 Nov. The changes are expected to be behaviour-neutral on the canonical routes; this is tested by the replicate runs in `ANALYSIS_ADDENDUM.md` §4b.
4. **Collision counting.** The leaderboard merges repeated contacts with the same actor within 5 s or 5 m before logging. The manuscript's statement that every contact tick registers as an event is incorrect.
5. **Training schedules in Table 2 are wrong.** According to the A100 operational record (`CHAT_MATRIX_TRAINING_AND_RESUME.md`), all four Matrix models used effective batch 8 and 10 epochs: 2,000 optimizer steps at 1,600 frames and 8,000 at 6,400 frames. Table 2 lists 4,800 and 20,050 steps. The two 6,400-frame Matrix models therefore share a schedule; the historical flooded checkpoint (6,440 frames, 8 epochs, 6,415 steps) differs from them by about 20 % in steps.
6. **Controller configuration.** No controller threshold is configurable; the standstill gate keeps no internal state. What the manuscript calls a hysteretic latch is the clause `v < 0.5 m/s and L < 2.0 m` together with the holding brake.
7. **Controller tuning routes.** The PID and lookahead were tuned on canonical routes before the comparison (`docs/CONTROLLER_OPTIMIZATION_EXPERIMENT.md`); the routes and checkpoint used will be named and H2 repeated on the routes not used.

## C. Numbers in the manuscript with no generating script at the time of writing

Crashes per km (14.91, 11.57 and related), proceed-cued standstill (15.56 % vs 17.24 %), stratum p-values (0.000808, 0.0547), threshold-sweep p-values. The analysis script cited in the reproducibility statement (`scripts/common/evaluate_confirmatory_plan.py`) was never committed and compares against the historical checkpoint with a 3-test Holm family. Each number is either regenerated by a committed script or removed.
