# Revision checklist (second revision, after the review of 17 November 2026)

Updated 17 November 2026, 23:57. `[x]` = done and committed. `[ ]` = not done; the note says how far it is.

## 1. Analyses and checks

- [x] Length cut of the main text
- [x] Fresh five-seat review (decision: Major Revision, 12 required items R1–R12)
- [x] R1: reference values for the unadapted policy
- [x] R3, R11: composition of the decoupling set and its overlap with the balanced set (86.3 %)
- [x] R6: permutation tests for blocked time
- [x] R7: chance rate of the collision-position match
- [x] R8: collision counts on the routes with blocked time
- [x] R4 (supplementary): plans counted per stop
- [x] Success rates; Figure 5b with all checkpoints
- [x] New title chosen
- [x] R4: same-input replay of the models as served
- [x] Control run and weight check: the model server loaded every fine-tuned checkpoint in part (180 of 396 expert-layer tensors left at base values)
- [x] Run note 13 on this fault
- [x] Corrected model server and re-run queue written (not yet run)
- [x] Same-input replay with the checkpoints loaded in full: stay-put share 0.35 % (Golden-6400) against 17.61 % (Flooded-6400), −17.26 pp, interval [−23.78, −12.13]; the partial loading had reduced this contrast to about a third
- [x] Second effect of the patch step: not caused by the patch step. An empty loading call changes nothing; the first base-model process differs from later base-model processes (cause unknown; recorded in the addendum)
- [x] Corrected server tested on the GPU: all 416 tensors in memory, largest difference 0 from the checkpoint file; first route driving

## 2. Decision needed from the author

- [x] Decided 17 November: re-run the closed-loop evaluation with the corrected server, in stages
- [x] Rules for the re-run written and committed before any route (addendum section 25)

## 3. Re-run with the corrected server

- [ ] Stage 1: two 6,400-sample checkpoints, first pass (running since 23:30 on 17 November; ends about midday on 19 November)
- [ ] Stage 1 read by the rule of section 25 (F1, F2)
- [ ] Stage 2: second pass; gate-off runs; decoupling checkpoint; 1,600-sample pair; history-swap runs (about 5 more days)
- [ ] Analysis script run on the new results; every number, table and figure updated

## 4. Manuscript text

Items R1–R12 were drafted in a working copy before the fault was found. None of it is in the manuscript file yet, and all of it is on hold until the decision in section 2.

- [ ] R1: direction relative to the unadapted policy; new title in the manuscript
- [ ] R2: wording at the level of checkpoints, not of data composition
- [ ] R3: decoupling set in Table 1
- [ ] R4: new section on the same-input replay
- [ ] R5: H1 reported as inconclusive
- [ ] R6–R8: blocked time (tests, chance rate, collision counts; no "not an additional cost")
- [ ] R9, R10: history-swap test as inconclusive; inertia and the conjecture not set against each other
- [ ] R11, R12: decoupling overlap; three-of-four-cells wording
- [ ] Abstract, discussion, conclusion
- [ ] Disclosure of the loading fault and of the server cache not cleared between routes
- [ ] Both Word files renamed to the new title; Word and LaTeX rebuilt
- [ ] Number check: zero unsupported numbers

## 5. Rest of the pipeline

- [ ] Final integrity check
- [ ] Formatting, including LaTeX for the supplement
- [ ] Process summary

## 6. Needed from the author

- [ ] Target journal
- [ ] Author contributions, funding, competing interests
- [ ] Sentence on verification of AI-assisted work
- [x] Rendering quality used for data collection: Epic, from the code (lead2alpa `scripts/multirig_collect_budget.sh` passes no `--quality`; the default of `collect_multirig.py` has been `Epic` in every version). No CARLA log of the collection machine is on this machine
- [ ] Permission to push to GitHub and create a DOI archive
- [ ] Trainer log details of the decoupling model
- [ ] Whether the expert weights are released, and where the repository is hosted
- [ ] 219-route check of Golden-1600 (deferred by the author until the plan is done)
