# Project summary

Written 21 November 2026, 12:09. Branch `revision-round1`. For the day-to-day state see `docs/REVISION_CHECKLIST.md`.

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
- Golden-6400, second pass: plans and standstill repeat (1.12 % and 25.05 %); Driving Score 49.01, lower than the first pass but within run-to-run variation.

## What is still running or open

| Item | Status |
|---|---|
| Flooded-6400, second pass | Running, 25 of 44 routes |
| Runs without the standstill gate (both 6,400 checkpoints) | Queued |
| 1,600-sample pair | Queued |
| History-swap test on fully loaded checkpoints | Queue not yet prepared; runs after the suite |
| Rewrite of the manuscript | Planned for about 24 to 26 Nov, after the runs |

Planned in the rewrite: fully loaded runs become the main result; all of Section 4 in the finding-first wording already used in Section 4.13; first series moved to the Supplement with a table of the registered tests kept in the main text; limitations condensed; a qualitative same-input figure (scene chosen by the rule in addendum section 27); inertia framing aligned in Sections 4.11, 5 and 6.

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
