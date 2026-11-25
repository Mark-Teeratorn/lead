# Revision checklist (second revision, after the review of 17 November 2026)

Updated 25 Nov 2026, 10:21. `[x]` = done and committed. `[ ]` = not done; the note says how far it is.

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
- [x] Stage 2, gate-off runs (ended 22 Nov 10:31 and 23 Nov 06:43): without the gate the difference in full stops is no longer established (−4.65 pp [−11.44, 3.20], against −23.54 pp with the gate; interaction +18.89 pp [11.29, 27.16]); the difference in near-stationary plans remains (−13.99 pp [−20.27, −9.52])
- [x] Stage 2, 1,600-sample pair (ended 24 Nov 13:52; tests of addendum section 31): S1 met narrowly (near-stationary plans 4.92 % against 8.34 %, −3.42 pp [−7.74, −0.11], p 0.047); S2 inconclusive (standstill −8.49 pp [−17.19, 0.46]); S3 not met (Driving Efficiency −4.47 [−16.61, 2.29]); the difference is smaller than at 6,400 on all three
- [x] Stage 2, history-swap runs with full loading (24 Nov 14:00 to 22:31; all 16 routes scored at the first launch): for Flooded-6400 the controls depend on the ego history (plans that hold speed 84.29 % with the moving history against 52.29 %; +32.00 pp [22.63, 36.04]) and no plan braked to rest (−44.76 pp); the share rose and did not fall, so the pre-fixed condition for tying stay-put plans to an at-rest history is not met and the outcome is reported as found. Golden-6400: no reading (3 usable routes)
- [x] Post hoc, descriptive: blocked-time diagnosis (addendum 28), driving efficiency (29) and Bench2Drive Driving Efficiency (30); each rule committed before computing
- [ ] Analysis script run on the new results; every number, table and figure updated

## 4. Manuscript text

Restructured on 23 and 24 November: the main text reports the fully loaded runs only (Sections 4.2 to 4.8; 4.6 is the 1,600-sample pair, 4.8 the history-swap test). The earlier runs with partly loaded models are not part of the paper (author's instruction of 24 November); their account is archived in `docs/archive/` and the runs stay in the repository. Section numbers in the items below that were written before that date are the old ones.

- [x] New title in the manuscript and the supplement (20 November: main title "The Inertia Problem in a Fine-Tuned Vision-Language-Action Driving Policy", subtitle unchanged; body text on the inertia mechanism to be aligned in the rewrite)
- [x] Section 3.4: loading fault and corrected server; Section 4.1: the two evaluation series
- [x] New Section 4.13 with Table 5: first pass of the fully loaded 6,400-sample pair (F1, F2, descriptive results)
- [x] R1: direction relative to the unadapted policy (abstract, Sections 1, 4.2 and 4.6, Figure 2; title changed)
- [x] R2: wording at the level of checkpoints; the 1,600-sample result stands beside the 6,400-sample difference in the abstract, contribution (i), new Section 4.6 and the conclusion
- [x] R3: decoupling set in Table 1, with its low-speed stay-put share; Section 4.5 compares it with the conjecture
- [x] R4: new Section 4.12 on the same-input replay (as served and loaded in full)
- [x] Restructure: first series (old 4.2 to 4.11) moved to Supplementary Section S6; new Section 4.7 with Table 6; new Figures 2 to 4 for the fully loaded runs; limitations condensed to four paragraphs; question-led wording in all of Section 4
- [x] History-swap result written in (24 November): new Section 4.8 and the sentences in the abstract, introduction, discussion and conclusion
- [x] Driving efficiency stated in the abstract, discussion and conclusion (24 November; post hoc result of Section 4.3, with the 1,600-sample test that was not met)
- [x] Qualitative same-input figure: Figure 2 in Section 4.2 (24 November, 23:08); former Figures 2 to 4 are Figures 3 to 5
- [x] Re-review (Stage 3', 24 November, simplified: the checker of the review tool could not be run): Major Revision. Required items: 6 of 12 fully addressed, 6 partly (one with a required gap, the collision table). Suggested items: 20 of 22 addressed in full or in part. New points: wording and disclosure only; no numerical inconsistency. Record in `outputs/pipeline_20261124_rereview/`
- [x] Re-revision (Stage 4', 24 November): wording fixes in the abstract, introduction, Sections 4.2 to 4.8, discussion and conclusion; Supplementary Table S2 (collision events on the routes with blocked time, addendum 35)
- [x] Decision of the author (24 November, after the re-review): the paper does not disclose the earlier evaluation series. Recorded in the addendum as a deviation from its Sections 25 and 32; this was the one point that all four seats of the re-review raised
- [ ] Not done from the re-review (minor or needing the author): table for Sections 4.5 to 4.7; naming (S5); references (S18); frame spacing at each query; trim of the main text once the journal is known
- [x] R5: H1 reported as inconclusive (Table 6, Section 4.7, Sections 1 and 6; four-test value 0.097 with Base-Rerun; harness changes named)
- [x] R6–R8: blocked time (exact tests with non-zero pairs, comparison rate 64 of 71 and collision counts in Supplementary Section S6.7; co-location wording in 4.3, S4.10, S6.10; no "not an additional cost"). Comparison rate for the fully loaded runs added 24 November (addendum 33: 91 of 119 long stops on routes with a collision record, 76.5 %)
- [x] R9, R10: history-swap test as inconclusive; outcome cannot separate a history-ignoring from a history-continuing expert; visual route not tested; conjecture as a data-side reading of inertia (4.7, 5, S4.11, S6.11)
- [x] R11, R12: decoupling overlap (86.3 %) in 3.3, 4.5 and 5; three-of-four-cells wording in 4.5, 5 and 6
- [x] Abstract, discussion, conclusion: all statements rest on the fully loaded runs; no history-swap placeholder is left (24 November)
- [x] Section 4.13 extended to both passes (Table 6, repeat rule); new Sections 4.14 (decoupling checkpoint loaded in full) and 4.15 (against the unadapted policy, post hoc)
- [x] New Section 4.16 with Table 7 (run without the gate, loaded in full); gate statements in the abstract, Sections 1, 5 and 6 now rest on the second series
- [x] Disclosure of the loading fault and of the server cache not cleared between routes (Sections 3.4, 4.1; limitations 12, 13); rendering quality of the data collection (limitation 10)
- [ ] Word files (main and supplement) and LaTeX rebuilt on 24 November, 23:30; main text 33 pages, Supplement 6 pages (LaTeX files and the author's change to the build script are not committed)
- [ ] Number check: zero unsupported numbers (24 November, 23:30: 0 of 1,153 in the main text and 0 of 90 in the Supplement; to be repeated on the final text)

- [x] Suggested review items written in on 24 November: S2 (abstract as a summary), S14, S16, S17 (query rate), S20 (Success Rate), S22, S23; LOWP cited as reference [48] after reading it
- [x] Suggested review items checked against the restructured text (24 November): S1, S2, S5, S7, S11, S13, S14, S16 to S18, S20 to S23 written in; S3, S6, S8, S10, S15 no longer apply (they concern the removed material); S4 covered by the record in Supplementary Section S4.1; S19 optional and not done
- [ ] Suggested items that need the author: S9 (trainer log of the decoupling model), S12 (weights and repository)
- [x] Independent end-to-end consistency read of the restructured text (24 November): 20 findings, all fixed (test labels N1 to N3 defined, cross-references, Table 2, leftover wording)

- [x] 24 November, at the author's request: the main text reports the runs with full loading only. Section 4.8 (first series) and Table 6 removed; H1 to H3 replaced in the introduction by the four tests of these runs; partly loaded values removed from Table 3 and Section 4.2; historical checkpoint removed from Table 1. Disclosure kept: paragraph "Earlier runs" in Sections 4.1 and 5, full account with the registered tests in Supplementary Section S6 (new Table S6). Route-subset sensitivity and pass-to-pass variation recomputed on the fully loaded runs (addendum 34). Section 4.8 is now the history-swap test

- [x] 24 November, author's instruction: the earlier runs are not mentioned in the paper. The paragraphs "Earlier runs" and Supplementary Sections S4.2 to S4.11, S5 and S6 are removed; the Supplement now holds S3.1 to S3.4 and S4.1 (6 pages). One clause in Section 4.1 and one limitation say that the tests were fixed after preliminary evaluations of the same checkpoints and routes. Removed text archived in `docs/archive/`

## 5. Rest of the pipeline

- [x] Final integrity check (24 and 25 November; see section 7)
- [ ] Formatting, including LaTeX for the supplement
- [ ] Process record: compiled on 25 November, kept outside git (`outputs/pipeline_20261124_final/paper_creation_process_en.md`); the author decides whether it is added

## 6. Needed from the author

- [ ] Target journal
- [ ] Author contributions, funding, competing interests
- [ ] Sentence on verification of AI-assisted work
- [x] Rendering quality used for data collection: Epic, from the code (lead2alpa `scripts/multirig_collect_budget.sh` passes no `--quality`; the default of `collect_multirig.py` has been `Epic` in every version). No CARLA log of the collection machine is on this machine
- [ ] DOI archive (the branch was pushed to the author's fork on 25 November at the author's request; the DOI needs a release by the author)
- [ ] Trainer log details of the decoupling model
- [ ] Whether the expert weights are released, and where the repository is hosted
- [ ] 219-route check of Golden-1600 (deferred by the author until the plan is done)

## 7. Work of 25 November (after the re-review)

- [x] Final integrity check, data and claims: about 389 statements and 16 rule verdicts checked against the result files; all numbers agree. Two points of wording and reporting corrected (collision wording; statements on pre-specification), with 12 medium and 25 minor points
- [x] Final integrity check, references: all 49 exist; one co-author added; the loading fault is now attributed to our own serving script, not to the FlashDrive release
- [x] Author's decisions: the earlier evaluation series stays out of the paper; names `Balanced` and `Hazard-heavy` replace `Golden` and `Flooded` in text, tables and figures; delivery by push to the fork
- [x] Main text shortened from about 18,000 to about 13,800 words; detail moved to Supplementary Sections S4.3 to S4.11; repeated intervals removed from the introduction, discussion and conclusion; Table 6 (means of the six checkpoints) added
- [x] Rebuilt and pushed (commit 7cfb7a61): main text 29 pages, Supplement 13 pages, 0 unsupported numbers in both
- [ ] Last consistency read of the shortened text (running), then its corrections
- [ ] Formatting: references in order of first citation, published versions of four preprints, style of the reference list
- [ ] Process record (being compiled; kept outside git because the fork is public)
- [ ] Open for the author: title (the integrity check finds "The Inertia Problem in ..." stronger than the body), target journal, statements, DOI, weights, trainer log
