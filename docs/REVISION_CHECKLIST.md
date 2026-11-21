# Revision checklist (second revision, after the review of 17 November 2026)

Updated 21 November 2026, 23:58. `[x]` = done and committed. `[ ]` = not done; the note says how far it is.

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

- [x] Stage 1: two 6,400-sample checkpoints, first pass (17 Nov 23:29 to 19 Nov 15:45; 44 of 44 routes in each arm)
- [x] Stage 1 read by the rule of section 25: F1 met (stay-put plans 1.31 % against 26.80 %, −25.49 pp [−31.69, −19.63]); F2 strong (standstill 22.97 % against 46.66 %, −23.69 pp [−33.48, −15.08])
- [x] Stage 2, decoupling checkpoint (ended 20 Nov 06:46): plans like Golden (near-stationary plans 1.58 % against 28.04 % for Flooded, 1.22 % for Golden); reduces hesitation at a cost (more blocked time), not a remedy
- [x] Stage 2, second pass of both checkpoints (ended 21 Nov 22:01): repeat test R1, R2, R3 all replicated; the Driving Score lead of the first pass did not recur (+3.96 [−3.06, 11.67] over both passes)
- [ ] Stage 2, still to run: gate-off runs (Golden started 21 Nov 22:01), 1,600-sample pair, history-swap runs (queue not yet prepared)
- [ ] Analysis script run on the new results; every number, table and figure updated

## 4. Manuscript text

First part written on 19 November, from the results that no longer depend on Stage 2. The rest waits for Stage 2, because the fully loaded runs become the main result and the order of Section 4 changes with them.

- [x] New title in the manuscript and the supplement (20 November: main title "The Inertia Problem in a Fine-Tuned Vision-Language-Action Driving Policy", subtitle unchanged; body text on the inertia mechanism to be aligned in the rewrite)
- [x] Section 3.4: loading fault and corrected server; Section 4.1: the two evaluation series
- [x] New Section 4.13 with Table 5: first pass of the fully loaded 6,400-sample pair (F1, F2, descriptive results)
- [ ] R1: direction relative to the unadapted policy (done for the replay, Section 4.12; closed loop waits for Stage 2)
- [ ] R2: wording at the level of checkpoints, not of data composition
- [ ] R3: decoupling set in Table 1
- [x] R4: new Section 4.12 on the same-input replay (as served and loaded in full)
- [ ] R5: H1 reported as inconclusive
- [ ] R6–R8: blocked time (tests, chance rate, collision counts; no "not an additional cost")
- [ ] R9, R10: history-swap test as inconclusive; inertia and the conjecture not set against each other
- [ ] R11, R12: decoupling overlap; three-of-four-cells wording
- [ ] Abstract, discussion, conclusion (rewritten 22 November for the second series; the statements on the gate, the 1,600-sample pair and the motion history still rest on the first series and carry placeholders)
- [x] Section 4.13 extended to both passes (Table 6, repeat rule); new Sections 4.14 (decoupling checkpoint loaded in full) and 4.15 (against the unadapted policy, post hoc)
- [x] Disclosure of the loading fault and of the server cache not cleared between routes (Sections 3.4, 4.1; limitations 12, 13); rendering quality of the data collection (limitation 10)
- [ ] Word files and LaTeX rebuilt on 22 November with the new title (LaTeX file and the author's change to its build script are not committed)
- [ ] Number check: zero unsupported numbers (0 of 1,434 on 22 November; to be repeated on the final text)

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
