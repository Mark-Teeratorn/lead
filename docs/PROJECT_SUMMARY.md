# Project summary

Written 21 November 2026, 12:09; results updated 24 Nov 2026, 22:40. Branch `revision-round1`. For the day-to-day state see `docs/REVISION_CHECKLIST.md`.

## What the project is

A paper on the **inertia problem** in a fine-tuned vision-language-action driving policy: a vehicle that has slowed or stopped and then restarts too rarely.

Current title: *The Inertia Problem in a Fine-Tuned Vision-Language-Action Driving Policy: A Closed-Loop Comparison of Checkpoints Trained on Different Data Mixes*.

The question: when the action expert of Alpamayo 1.5 is fine-tuned on different mixes of driving data, does the mix change how often the policy plans to stay put at low speed, and what does that do on the road?

## Setup

| Part | What we use |
|---|---|
| Policy | Alpamayo 1.5: frozen, quantized vision-language model plus a flow-matching action expert (the part we fine-tune) |
| Training data | One verified pool of 34,132 CARLA expert samples; each fine-tuning set is drawn from it |
| Data mixes | **Golden** (balanced), **Flooded** (obstacle-heavy, more stationary samples), **Balanced / decoupling** (Flooded's scenario mix with Golden's manoeuvre mix and stationary share) |
| Sizes | 1,600 and 6,400 samples; one training seed per mix |
| Evaluation | CARLA 0.9.15, 44 Bench2Drive routes (one per scenario type), our own bridge controller with a standstill gate |
| Statistics | Paired by route, 95 % BCa interval, Wilcoxon test; rules written and committed before each run or analysis (`docs/ANALYSIS_ADDENDUM.md`) |

Main measures: share of steps with a near-stationary plan (planned path shorter than 1.5 m), standstill time, blocked time (commanded to accelerate but not moving), Driving Score, route completion, collision events.

## What happened

1. **First evaluation series (to 17 Nov).** The registered tests H1 to H3 were run. Golden-6400 planned to stay put less often than Flooded-6400, but the differences were modest and the Driving Score did not favour Golden.
2. **Review (17 Nov).** A five-seat simulated review returned Major Revision with 12 required items.
3. **Loading fault found (17 Nov).** The model server had loaded every fine-tuned checkpoint only in part: 180 of 396 expert-layer tensors stayed at their base values. The whole first series therefore describes partly loaded models.
4. **Corrected server.** A wrapper that loads all tensors and refuses to start otherwise (`scripts/evaluation/flashdrive_server_fullpatch.py`). The stock server and the default agent are unchanged.
5. **Second evaluation series (running).** All closed-loop runs are being repeated with the checkpoints loaded in full. The two series are never pooled.

6. **Main text on the corrected runs only (24 Nov, author's decision).** The first series is no longer used for any statement in the main text. By the author's instruction it is not mentioned in the paper; the paper says only that the tests were fixed after preliminary evaluations of the same checkpoints and routes. The old account is archived in `docs/archive/`.

## Results so far, checkpoints loaded in full

**Same-input replay** (384 logged states, 16 plans each): stay-put share 0.35 % for Golden-6400 against 17.61 % for Flooded-6400 (−17.26 pp, interval [−23.78, −12.13]). The unadapted model lies between them at 3.28 %.

**Closed loop, first pass, 44 routes:**

| | Golden-6400 | Flooded-6400 | Balanced-6400 | Base |
|---|---|---|---|---|
| Near-stationary plans | 1.31 % | 26.80 % | 1.58 % | 13.24 % |
| Standstill time | 22.97 % | 46.66 % | 27.79 % | 36.28 % |
| Blocked time | 12.69 % | 0.00 % | 15.39 % | — |
| Route completion | 71.55 | 63.19 | 71.46 | 71.93 |
| Driving Score | 54.02 | 43.51 | 47.69 | 42.60 |
| Collision events | 28 | 28 | 37 | 49 |

- The primary test is met: near-stationary plans −25.49 pp, interval [−31.69, −19.63]. Standstill time −23.69 pp, interval [−33.48, −15.08].
- Golden-6400 against the unadapted model (post hoc): Driving Score +11.42, interval [2.83, 21.62]; 28 against 49 collision events.
- The decoupling checkpoint behaves like Golden, not like Flooded. This points to the manoeuvre mix and stationary share, not the scenario mix (single-pass look; final reading pending).
- Cost: the checkpoints that wait less have more blocked time.
- **Second pass (added 22 Nov).** The repeat test is met on all three measures: near-stationary plans 1.12 % against 29.28 % (−28.16 pp, interval [−34.81, −21.75]). Over both passes Golden-6400 stood still about half as long (−23.54 pp) and completed more of each route (+6.84 pp, interval [0.80, 13.29]).
- **The Driving Score lead did not repeat.** Second pass 49.01 against 51.60; over both passes +3.96, interval [−3.06, 11.67]. Collision events per kilometre driven: ratio 1.29, interval [0.90, 1.92]. The table above shows the first pass only.
- Decoupling checkpoint, final reading: it closes 98.7 % of the gap in near-stationary plans, with more blocked time; by the rule fixed in advance it reduces hesitation at a cost and is not called a remedy.

- **Without the standstill gate (added 23 Nov).** The difference in full stops is no longer established (18.76 % against 23.41 %; −4.65 pp, interval [−11.44, 3.20]; with the gate −23.54 pp). The difference in near-stationary plans remains (0.60 % against 14.58 %; −13.99 pp, interval [−20.27, −9.52]). So the plans carry the difference and the gate turns it into held stops. For Flooded-6400, removing the gate gave more route completion (+10.95 pp) and more collision events (+0.42 per route) at an unchanged Driving Score; it is not a remedy.

- **Efficiency (added 23 Nov, post hoc).** Golden-6400 is about twice as fast: 45.62 s against 76.51 s on the routes both completed, and a Bench2Drive Driving Efficiency of 102.50 and 102.25 against 77.18 and 81.98 (+22.89 points, interval [6.14, 34.89]). Faster is not reported as better: blocked time and, in the second pass, the infraction penalty go the other way.
- **Blocked time (post hoc).** Nearly all blocked steps lie at a recorded collision position, with forward plans, so a controller rule would not remove them.

- **1,600-sample pair (added 24 Nov).** The difference in near-stationary plans is present by a small margin (4.92 % against 8.34 %; −3.42 pp, interval [−7.74, −0.11], p 0.047) and is smaller than at 6,400 samples. Standstill time is inconclusive (−8.49 pp, interval [−17.19, 0.46]) and Driving Efficiency does not differ detectably (97.83 against 102.30). So at 1,600 samples the difference in plans is not shown to reach the motion of the vehicle.

- **History-swap test (added 24 Nov, exploratory).** At low speed the ego history of Flooded-6400 was replaced by one that reports motion at 4 m/s. It then planned to hold its speed more often (84.29 % against 52.29 %; +32.00 pp, interval [22.63, 36.04]) and never planned to brake to rest. So its controls depend on the ego history. The rule fixed in advance ties stay-put plans to an at-rest history only if the hold-speed share falls; it rose, so the paper reports the dependence without claiming the mechanism is demonstrated. Golden-6400 was too rarely at low speed for a reading.
- **Efficiency wording (24 Nov).** The abstract, discussion and conclusion now say that Golden-6400 was more efficient at a Driving Score that was not detectably different; labelled post hoc.

## What is still running or open

| Item | Status |
|---|---|
| Second pass of both 6,400 checkpoints; decoupling checkpoint | Done (21 Nov) |
| Runs without the standstill gate (both 6,400 checkpoints) | Done (23 Nov) |
| 1,600-sample pair | Done (24 Nov 13:52) |
| History-swap test on fully loaded checkpoints | Done (24 Nov 22:31) |
| Rewrite of the manuscript | All results written in (24 Nov): Sections 4.2 to 4.8 report the fully loaded runs only. Open: qualitative figure, re-review, final checks |

Tests for the 1,600-sample pair are fixed in addendum section 31 (near-stationary plans as the primary test, standstill time and Driving Efficiency as secondary tests).

## Limits that will remain

- One training seed per mix, so the effect of the data mix cannot be separated from that of the training run.
- 44 routes and our own controller; the scores are not comparable with published 220-route results.
- The mixes differ in several factors at once; the decoupling checkpoint separates only one.
- Closed-loop runs are not deterministic, and two server processes of the same model do not return identical plans (cause not found).

## Decisions needed from the author

- Target journal.
- Extra run after Stage 2: a second training seed, the 220-route run, or neither.
- Whether the subtitle changes to "Plan Sampling, Controller Amplification, and Data Composition" (decide after the gate-off runs).
- Author contributions, funding, competing interests; sentence on AI-assisted work.
- Permission to push to GitHub and create a DOI archive; whether the weights are released.

## Where things are

| What | File |
|---|---|
| Manuscript source | `docs/manuscript_revision_draft.txt` |
| Supplement source | `docs/manuscript_supplement.txt` |
| Word files | `docs/The Inertia Problem in a Fine-Tuned Vision-Language-Action Driving Policy - *.docx` |
| LaTeX and PDF | `docs/latex/manuscript.tex`, `docs/latex/manuscript.pdf` |
| Rules fixed before each analysis, and their outcomes | `docs/ANALYSIS_ADDENDUM.md` |
| Deviations and run notes | `docs/CONFIRMATORY_DEVIATIONS.md` |
| Checklist | `docs/REVISION_CHECKLIST.md` |
| Result files | `docs/provenance/` |
| Main analysis code | `scripts/evaluation/paper_reanalysis.py`, `fullload_analysis.py`, `fullload_vs_base.py` |
| Evaluation queue and its log | `scripts/common/run_fullload_suite.sh`, `outputs/fullload_suite_audit.log` |
| Number check | `scripts/paper/check_manuscript_numbers.py` |
