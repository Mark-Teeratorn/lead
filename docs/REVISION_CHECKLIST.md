# Revision checklist (second revision, after the review of 17 November 2026)

Updated 17 November 2026, 21:40. `[x]` = done and committed. `[ ]` = not done; the note says how far it is.

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
- [ ] Same-input replay with the checkpoints loaded in full (running; ends about 23:30)
- [ ] Cause of the second effect of the patch step (two short diagnostics, in the same queue)
- [ ] Test of the corrected server on the GPU (after the replay)

## 2. Decision needed from the author

- [ ] Re-run the closed-loop evaluation with the corrected server, or keep the data and describe the models as partly loaded

## 3. If the re-run is chosen

- [ ] Two 6,400-sample checkpoints, first pass (about 1.5 days)
- [ ] Decoupling checkpoint; second pass; gate-off runs; 1,600-sample pair (about 5 more days in total)
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
- [ ] Rendering quality used for data collection (Epic or Low)
- [ ] Permission to push to GitHub and create a DOI archive
- [ ] Trainer log details of the decoupling model
- [ ] Whether the expert weights are released, and where the repository is hosted
- [ ] 219-route check of Golden-1600 (deferred by the author until the plan is done)
