# Academic Integrity Verification Report: Stage 2.5 re-verification (round 2)

Run: 15 Nov 2026, after 16:45 (UTC+7). Agent: `integrity_verification_agent`, re-verification of the round-1 findings in `stage2_5_data_claims_report.md` and `stage2_5_references_report.md`, a scan of the text changed for new problems, an internal-consistency check, and the 7-mode checklist run again.

Manuscript checked: `docs/manuscript_revision_draft.txt`, SHA-256 `7fe110fb924e596d6904494d9ee6a563185e13be75e1cf1a64e4647a477e0df9`, last changed in commit `cd8e28aa` (15 Nov 16:13:43). HEAD is `1b8d228c` (16:45:07), which changes only `CONFIRMATORY_DEVIATIONS.md` (run note 9). Line numbers below refer to this file. `docs/latex/manuscript.tex` contains the same text, and the same fixes apply there (tex lines given where they matter).

Read-only. No project file was changed, and the GPU queue was not touched. The only file written is this report.

## Verification mode

Re-verification after corrections (Mode 1, Stage 2.5, correction loop round 2). In line with "re-verify the corrected items, plus the whole C2 check when a correction changed findings, numbers or scope": every new number in the changed text was traced to a manifest key, and the whole changed text was scanned.

## Verdict

**FAIL (correctable): one MEDIUM item remains.** IL-SERIOUS-1 is resolved, and ten of the eleven round-1 MEDIUM items are resolved. IL-MEDIUM-1 (when H3 was fixed relative to its data) is only partly resolved. The sentence that round 1 flagged is still in the text unchanged (L287). The new abstract, the limits paragraph and the conclusion use a shorter wording that makes the same overstatement again (L72, L103, L460). These are four sentence edits, listed exactly below. Once they are made, the expected verdict is **PASS WITH NOTES**, and only those lines need to be checked again.

The 7-mode checklist does not block any more. Modes 1, 5 and 6 are now CLEAR. Mode 4 is still SUSPECTED, which is flag-only at Stage 2.5.

Mapping of verdict terms: the protocol's "PASS WITH NOTES" corresponds to the dispatch's "PASS WITH MINOR ITEMS".

## Blocking item (exact fix)

IL-MEDIUM-1 residual. Addendum §9 (`a1a2f96e`, 14 Nov 12:35:56) records that when H3 was written, 14 of the 44 `Golden-6400` second-pass routes had been run and their standstill had been looked at (run note 6). Their step logs, which contain the plans, existed. Only plan-level values had not been computed. Section 4.1 (L241), L89 and the first sentence of L287 now say exactly that. Four sentences still say that the data did not exist:

| Line (tex) | Current text | Replace with |
|---|---|---|
| L287 (tex 300) | "H3 was specified later than H1 and H2 and is tested once, on data that did not exist when it was written;" | "H3 was specified later than H1 and H2 and is tested once, on second-pass data whose plan-level values had not been computed when it was written (Section 4.1);" |
| L72 (tex 32) | "The difference held without the gate and in the second pass (11.74 % vs 1.86 %), where a test specified before its data was met." | "The difference held without the gate and in the second pass (11.74 % vs 1.86 %), where a test of near-stationary plans, fixed before any plan-level value of that pass was computed, was met." (This also says which test is meant. H3 is the share of plans under 1.5 m over all steps, not the stay-put share quoted just before it.) |
| L103 (tex 69) | "and H3 before the second-pass data it is tested on;" | "and H3 before the obstacle-heavy model's second pass started and before any second-pass plan-level value was computed;" |
| L460 (tex 489) | "a test of near-stationary plans specified before the second-pass data it used was met" | "a test of near-stationary plans specified before any plan-level value of the second pass was computed was met" |

Recommended at the same time (MINOR): L434 "under rules fixed in advance (H3 and rules R2 and R3)" should become "under rules fixed before any plan-level or command-class value of the second pass was computed (H3 and rules R2 and R3)". R3 is standstill outside blocked time, and the balanced model's second-pass standstill on 14 routes had been seen.

---

## Task 1: status of every round-1 finding

### Data/claims report

| ID | Status | Current line and text (short) |
|---|---|---|
| IL-SERIOUS-1 | **RESOLVED** | All four statements are gone ("0.3 %", "restarting, not of stopping", "the pattern the inertia account predicts", old L356). They are replaced by L362: "An earlier version of this analysis counted plans shorter than 1.5 m at more than 0.5 m/s; that count is close to zero by construction … and is withdrawn. We use the planned end speed instead". The values come from the project script (manifest `braking`, see Task 2) and agree with my round-1 preview from separate code to 0.01 pp. The §17 rule was applied: the sentence "restarting, not stopping" was not kept, because the shares differ in both strata and all three arms. |
| IL-MEDIUM-1 | **PARTLY RESOLVED (blocking)** | Fixed at L89, L241(ii), L287 (first sentence), L322 ("fixed on 14 November 2026, before any collision count of a second pass was computed"), L356 and L399 ("fixed together with H3 … Section 4.1"). The three partial looks are now in Section 4.1 (L241). The manifest label is corrected (`second_pass_decisions.label`). Not fixed: L287 (last sentence), L72, L103 and L460; see the table above. |
| IL-MEDIUM-2 | RESOLVED | L89: "H1 stands in the same document, but its result against the original `Base` run was already known." L241(i) uses the same wording. L103: "Only H2 was specified before its comparison was evaluated". This agrees with L243. |
| IL-MEDIUM-3 | RESOLVED (minor residual, N-7) | L94: "Analyses added after the first results are labelled post hoc; Section 4.1 states for each group when it was written down". L241(iii)–(iv) list §7a (looked at first), §16 (after computing), and the first re-analysis analyses without an addendum entry. |
| IL-MEDIUM-4 | RESOLVED | The word "registered" no longer appears in the body. L241: "they were not time-stamped by a third party, and the repository is released with the paper." L285: "the original pre-specification (repository commit `013a12bd`)". |
| IL-MEDIUM-5 | RESOLVED (minor residual, N-10) | L427: "In the first pass the balanced model had 44 collision events and the matched obstacle-heavy model 36 (logged entries 46 and 37) … Over both passes the counts did not differ detectably". L405: "Where the balanced model is commanded to accelerate without moving, on routes that have a collision event". L440: "the time it spends commanded to accelerate without moving, on routes that have a collision event". |
| IL-MEDIUM-6 | RESOLVED | L101: "fine-tuned on an A100 machine, is served and evaluated in closed loop on a single 24 GB GPU". L193: "Fine-tuning ran on an NVIDIA A100 machine; inference and closed-loop evaluation ran on one 24 GB GPU." |
| IL-MEDIUM-7 | RESOLVED (minor residual, N-3) | Title: "… Low-Speed Hesitation … A Matched-Pair, Single-Seed Study". L72: "In this matched pair the mix changed …"; "At 1,600 samples no difference between the mixes was detected." L101: "alone" is dropped. L442: "In this matched pair, the fine-tuning mix moved …". L360: "is ordered as its training sets are". L436: "rises with" replaces "tracks". "Progress" is gone from the title; L442 says "we did not observe more progress". |
| IL-MEDIUM-8 | RESOLVED | L436: "It resembles the behaviour described as the inertia problem … [12]". "That is the pattern the inertia account predicts" is deleted. The keyword "inertia problem" is replaced by "low-speed planning" (L74). |
| IL-MEDIUM-9 | RESOLVED | L460: "[[PENDING: H1 result on Base-Rerun, sentence to be written from the result]]". |
| IL-MEDIUM-10 | RESOLVED (minor residual, N-6) | L155: "This conjecture is not one of the three hypotheses tested. It was formulated on 12 November 2026, after the primary result and the band decomposition of Section 4.5 were known; their agreement with it is not a test of it." |
| IL-MEDIUM-11 | RESOLVED (minor residual, N-14) | L356: 37-route R1 is −7.81 pp [−12.00, −5.23]. L399: 37 routes, −12.65 [−21.94, −6.31] and +7.34 [2.07, 16.80]; §8 settings for R3, +7.66 [1.60, 15.59], +6.54 [2.35, 14.11], +6.85 [−0.06, 14.81], with "The last interval includes zero, so the second-pass replication of blocked time depends on the throttle threshold." Also "All of these first-pass and gate-off intervals exclude zero." All values match `second_pass_decisions.sensitivity_no_decision`. |
| IL-MINOR-1 | RESOLVED | L72 "(means of per-route shares)"; L97 "(means of per-route shares; pooled over steps, 24.9 % and 2.3 %)"; L436 "(means of per-route shares)". |
| IL-MINOR-2 | RESOLVED | L72: "in two passes with the default controller and one pass without its standstill gate". |
| IL-MINOR-3 | RESOLVED | L72: "two-pass Driving Score was 5.67 points lower (rank test p = 0.11)". L99: "CI of the difference [−12.10, −0.46], Wilcoxon p = 0.11, no rule fixed in advance". |
| IL-MINOR-4 | RESOLVED | L346: "gave p = 0.045 and 0.025, with the balanced model lower on 30 and 31 routes". This matches `P.(2) Golden minus Flooded, gate-off`. |
| IL-MINOR-5 | RESOLVED | L231: "For one route of that run (23687) … the script counted its standstill as 0 %, which gives 40.32 % in the confirmatory record. This paper reports 40.45 %". |
| IL-MINOR-6 | RESOLVED | L358: "Both differences have the same sign as in the first pass and intervals that exclude zero". |
| IL-MINOR-7 | RESOLVED | L209: "In the server code we ran, the integrator is forward Euler and the velocity is reused … (zero-based indices 3 to 6), so the expert is evaluated four times per call". |
| IL-MINOR-8 | NOT ADDRESSED (deferred) | L213–215 still does not describe the no-waypoint fallback (throttle 0.35, brake 0). **Deferral acceptable before peer review.** In round 1 no logged step had fewer than five waypoints. It is one sentence and is required at 4.5. |
| IL-MINOR-9 | PARTLY RESOLVED | L356 adds: "This share is taken over all steps, so it also reflects how much time each model spends slow (Section 3.1)". L336 ("mean predicted extent was 5.75 m longer") and the rationale-conditioned shares of plans under 1.5 m (L383) still have no speed caveat. |
| IL-MINOR-10 | PARTLY RESOLVED | The equation check is now stored: `docs/provenance/action_space_equation_check.txt` gives a maximum of 5.6 × 10⁻⁶ m (supports "within 10⁻⁵ m"), and L = 0.59 / 3.11 m (supports L139). I verified the 416 tensors myself from the safetensors header of `Matrix-Golden-6400-A15/action_expert.safetensors`: 416 tensors. That is not yet stored in `docs/provenance`, and the manuscript attributes it to "the trainer artifacts". There are still no trainer artifacts for the decoupling model in `docs/provenance`, and `A100_TRAINING_PROVENANCE.md` L108 still says "No model has been trained" on it. Run note 3 records the training. |
| IL-MINOR-11 | RESOLVED (small residual) | L474 now covers analysis and queue scripts, controller variants, decision rules, the literature search and checks, number checks and drafting. "Most commits of the revision were made with AI assistance." The attestation is replaced by "[[PENDING: authors' statement …]]". Not named: the AI session that wrote the A100 training-provenance report, and the launching and monitoring of runs. Add them when the authors write their statement. |
| IL-MINOR-12 | NOT ADDRESSED | The headings of addendum §6 ("23:40", commit 23:32:16) and §7 ("22:30", commit 21:19:48) are unchanged, with no dated correction note. The same pattern appears in run note 7 (states 21:45, commit `b3c80f88` 21:42:51) and run note 8 (states 10:55, commit `13454b8c` 10:53:58). In each case the commit is earlier than the stated time, so no claim is weakened. |
| IL-MINOR-13 | NOT ADDRESSED | Notes block L8, L12 and L13 still list as pending test–retest, the noise reference and the run-2 rows, all of which are filled. Housekeeping only; the block is stripped before submission. |

### References report

| ID | Status | Current text |
|---|---|---|
| Ref IL-MEDIUM-1 [5] | RESOLVED | L487 "pp. 8340–8350". |
| Ref IL-MEDIUM-2 [20] | PARTLY RESOLVED | L517 "recipe `alpamayo1_5_sft`, configuration `sft_stage2_nav`". Still no commit hash or access date, so the version is not pinned (MINOR). |
| Ref IL-MEDIUM-3 | RESOLVED (grammar, N-11) | L83: "training on generated safety-critical scenarios has been reported to improve collision avoidance [38], re-weighting rare samples to raise closed-loop benchmark scores [39]". |
| Ref IL-MEDIUM-4 | RESOLVED | L193: "quantized to 4-bit weights with pairwise rotation quantization (ParoQuant) [14] and run with 8-bit activations in the FlashDrive streaming server [15] (W4A8)". |
| Ref MINOR-1 [35] | RESOLVED | L547 "ReMix", "C. A. Bhateja". |
| Ref MINOR-2 [13] | RESOLVED (kept, as allowed) | L503 pp. 11698–11709. |
| Ref MINOR-3 [38] | NOT RESOLVED | L553 "vol. 13698" is still unconfirmed on a primary page and needs a check by hand. |
| Ref MINOR-4 [47] | RESOLVED | L571 "vol. 23, no. 11, pp. 20538–20552". |
| Ref MINOR-5 | RESOLVED | Pages added to [40] L557, [41] L559 (with DOI), [36] L549, [22] L521, [24] L525, [28] L533 and [10] L497. |
| Ref MINOR-6 | NOT ADDRESSED (optional) | [26], [39] and [45] are still cited as preprints. |
| Ref MINOR-7, -8 | no action needed | — |
| Ref MINOR-9 | RESOLVED | L111 "straighter paths are obtained with additional procedures such as …". |
| Ref MINOR-10 | RESOLVED | L209 "In the server code we ran …". |
| Ref MINOR-11 | RESOLVED | L193 "20 Fourier features, maximum frequency 100". |
| Ref MINOR-12 | RESOLVED | L83 "the loss or the weighting of training frames [12, 27, 28]"; L113 adds the controller-side remedies without a citation (see N-11). |
| Ref MINOR-13 | RESOLVED | L121 "Errors of an imitation policy compound in closed loop [16], and open-loop planning metrics do not show this [17, 18]." |
| Ref MINOR-14 | NOT ADDRESSED (optional) | L113 unchanged. |
| Advisory 1 (FlowDrive stationary cluster) | NOT ADDRESSED (deferred) | L119 unchanged. **Deferral acceptable.** It is an advisory, not an issue. One clause ("whose balancing mainly down-weights a dominant stationary cluster") would answer a reviewer before they ask. |
| Advisory 3 (flow-time distribution) | RESOLVED | L143: "[2] describes a shifted beta distribution; we did not verify the distribution in the recipe version we ran". |
| B55 (48 history tokens) | unchanged, COULD-NOT-CHECK | L131. |

### Other items deferred on purpose

| Item | Status | Acceptable before peer review? |
|---|---|---|
| Revision-history remarks in the body: L151, L195, L215, L229, L235, L362, L415, L421, L427, L464 | NOT ADDRESSED | **Yes**, except **L421** "called H3 in earlier versions". The current H3 is a different hypothesis, so a reviewer will be misled. Remove that phrase now (N-12). The rest are transparency notes, not errors, but they belong in a response letter and must be removed before journal submission. |
| IL-MINOR-8 | see above | Yes. |
| FlowDrive advisory | see above | Yes. |
| Third-party time-stamping | Disclosed at L241 | **Yes.** It cannot be done after the fact. Archive the repository with its history under a DOI at submission so that the commit times can at least be checked against a fixed copy. |

---

## Task 2: new-issue scan of the changed text

### Numbers in the changed text, traced to the manifest

| Text | Value | Manifest key | Result |
|---|---|---|---|
| L72 | 5.67 lower; p = 0.11 | `O.comparisons.(ii) …/44 routes/driving_score`: −5.674, p 0.108 | match |
| L72, L99 | 8.13 % vs 0.43 % | `U.golden_minus_flooded.default controller, mean of run1 and run2.time_blocked_pct`: 8.131 / 0.435 | match |
| L97, L362, Table 6 | above 2 m/s: 0.99/2.17 (−1.18 [−1.79, −0.83]); 0.99/2.16 (−1.17 [−2.07, −0.76]); 1.02/2.26 (−1.25 [−1.76, −0.84]). 0.5–2 m/s: 0.35/0.78, 0.22/0.65, 0.22/0.74, all CIs below 0 | `braking.golden_minus_flooded.{default controller, run1 / run2 / gate-off controller}.{moving_above_2, moving_0.5_to_2}`: n = 43 above 2 m/s and 44 at 0.5–2 m/s; 0.5–2 CIs [−0.71, −0.21], [−0.64, −0.28], [−0.75, −0.34] | match |
| L362 | "last second covers less than 0.5 m" | script L2273: v_end = path between waypoints 54 and 64 over 1.0 s; `braking.definition` "v_end < 0.5 m/s" | same definition |
| L356 | 37 routes, −7.81 [−12.00, −5.23] | `second_pass_decisions.sensitivity_no_decision.37 routes….R1` | match |
| L399 | −12.65 [−21.94, −6.31]; +7.34 [2.07, 16.80]; +7.66 [1.60, 15.59]; +6.54 [2.35, 14.11]; +6.85 [−0.06, 14.81] | `sensitivity_no_decision.37 routes….R2/R3`; `…section 8 settings, 44 routes.{run>=40, run>=200, throttle>=0.2}.time_blocked_pct` | match |
| L427 | 1.07 / 1.05; 1.03 / 0.93 (+0.10 [−0.10, 0.28]) | `O.(i)….collision_events` 1.068 / 1.045; `O.(ii)…` 1.034 / 0.932, CI [−0.102, 0.284] | match |
| L235, L322 | 16.25 / 35.20; 22.53 / 21.34; ICC 0.57/0.63, 0.51/0.36, 0.58/0.55 | `N.models.*.run_to_run_differences.rep1 - run1…sd`; `N.models.*.test_retest_44.*.icc_1_1` | match |
| L346 | noise reference +2.97 [−6.05, 12.63] | `P.(4) noise reference….standstill_pct_v<0.1` 2.974 | match |
| L448 | DS moved 7.40 | `N.models.Golden-6400.test_retest_44.driving_score.run2_minus_run1` −7.397 | match |
| Table 6, all 24 cells | — | Equal to the text values in L356, L358, L362, L364, L393, L399 and L346. Row sums check: standstill outside blocked time + blocked = total in every column (17.97 + 7.75 = 25.72 ≈ 25.71; 33.59 + 0.18; 19.50 + 8.51; 32.41 + 0.69; 13.36 + 14.05; 21.68 + 2.89) | consistent |

Number checker (`check_manuscript_numbers.py`): 13,578 source values; supported 1,347, unsupported 0, ignored 317. Round 1 found this check permissive. The manuscript no longer cites it as verification.

### Timing statements in the changed text

| Statement | Record | Result |
|---|---|---|
| L241(i) H2 committed on 11 Nov (`013a12bd`) before `Flooded-6400` was evaluated | commit 17:05:00; run started 17:20:06 | accurate |
| L241(ii), L287, L89: H3 and R2/R3 committed 14 Nov 12:35, before the Flooded pass 2 started and before any plan-level second-pass value; 14 Golden routes run and their standstill looked at | `a1a2f96e` 12:35:56; §9 "what had been seen"; run note 6; Flooded pass 2 started 21:35 | accurate |
| L241(ii) "Two further looks … the completed second pass of `Golden-6400` alone, and, on 15 November, both models on 31 of 44 routes, including plan-level values" | run notes 7 (14 Nov 21:45) and 8 (15 Nov 10:55) | accurate |
| L241(ii) "No rule was changed after any of these looks" | §9, §10, §12a, §13 committed before notes 7 and 8 and unchanged. §17 replaced the §10a moving-step measure after look 8 (disclosed in L362). | true for decision rules; see N-7 |
| L241(iii) §12a, §10, §13, §17, §12b "written down before their values were computed" | §10 12:45:33 "before any value below was computed"; §12a 16:23:27; §13 17:19:39; §17 15:49:37, manifest regenerated about 16:11. **§12b records that the gate-off crawl means (12.75 / 16.93) had already been seen**; only the paired test had not been run. | accurate except §12b (N-7) |
| L322 collision rule "before any collision count of a second pass was computed" | §12a text and commit | accurate |
| L155 conjecture formulated 12 Nov, after the primary result and the band decomposition | round-1 record (analysis D 13:14, first draft with the hypothesis 15:15) | accurate |
| L287 last sentence; L72; L103; L460 | see the blocking item | **stronger than the record** |

### Wording rules

- **Safety claim:** none. L72, L99 and L460 say "we make no safety claim". L81 only says that a safety case depends on where a policy sits.
- **"More collisions":** none. L440 says "we do not say that the balanced model collides more". L427 gives both counts, as §12a requires.
- **Inertia mechanism claimed as shown:** none. L436 says "resembles", and the mechanism is explicitly not claimed until the swap test is done.
- **Claim wider than one matched pair and one seed:** the title, L72, L442 and L460 are scoped. Two generic headline sentences remain (N-3).

### New issues, most serious first

| ID | Severity | Line | Issue | Fix |
|---|---|---|---|---|
| N-1 | **MEDIUM** (IL-MEDIUM-1 residual) | L287, L72, L103, L460 | Statements that H3 was fixed before its data existed. | See the blocking item. |
| N-2 | MINOR (recommended now) | L362 | §17 commits to "Pooled shares for all six models (default controller, pass 1) as description". They are not reported, and they bear on how the result is read. Pooled share of plans ending at rest above 2 m/s: Base 1.50, Flooded-1600 1.80, Golden-1600 1.99, Hist 1.59, Flooded-6400 1.79, **Golden-6400 0.82**. At 0.5–2 m/s: 1.35, 0.88, 0.55, 0.65, 0.73, 0.38 (`braking.pooled_all_models_default_run1`). The matched obstacle-heavy model is typical of the others. The balanced 6,400 checkpoint is the outlier, and at 1,600 samples the order is reversed above 2 m/s. | Add one sentence like L360: "Pooled over all steps, the share above 2 m/s was 1.50–1.99 % for the other five models and 0.82 % for `Golden-6400`; at 1,600 samples the balanced model's share was the higher one." |
| N-3 | MINOR | L97, L434 | Generic causal headlines: "Data composition shifts what the model plans once it is slow." and "Fine-tuning data composition changed what the policy planned once it was slow". The title and abstract are now scoped; these two are not. | "In the matched pair, the data mix shifted …" and "In this matched pair, the fine-tuning mix changed …". |
| N-4 | MINOR | L299, L366 | Table 5 and Table 6 are not cited anywhere in the running text. Table 5 lost its only citation when L173 changed "(Table 5)" to "(Sections 4.3 and 4.4)". | Cite Table 5 in Section 4.4 (e.g. L320) and Table 6 in Section 4.6 (e.g. L354 or L362). |
| N-5 | MINOR | L366–377 | The Table 6 caption says rows are post hoc "except where a hypothesis or rule is named". The pass-2 cells of "Standstill outside blocked time" and "Blocked time" are the pre-specified R2 and R3, but they are not named, so the caption marks them as post hoc. The rows for plans ending at rest above 2 m/s use 43 routes, while the caption says "on 44 routes" (§10 and §17 require the number of routes to be reported). | Add "(R2 in pass 2)" and "(R3 in pass 2)" to those rows and "(43 routes)" to the braking row. |
| N-6 | MINOR | L336, L358, L436 vs L147/L155 | Section 3.2 now calls the idea a "Conjecture … not one of the three hypotheses". L336, L358 and L436 still call it "the stay-put sampling hypothesis", next to H1–H3. L336 "This is the pattern the … hypothesis … predicts" repeats the circular reading that L155 retracts. | Use "conjecture" throughout. L336: "This is the pattern the conjecture of Section 3.2 was formulated to account for." |
| N-7 | MINOR | L241(ii)–(iii), L94, L354 | (a) §12b is listed among the analyses written before their values were computed, but §12b states that the gate-off crawl means had been seen. (b) "No rule was changed" is true of decision rules; the §10a moving-step measure was replaced after look 8 (§17). (c) L94 and L354 say Section 4.1 gives the timing "for each group", but §7b, §8, §8a and §14 are not in the list (§7b and §8 are covered locally at L395 and L397). | (a) "… and the crawling analysis (§12b), whose gate-off means had been seen; no paired test had been run". (b) "No decision rule was changed …". (c) Add §7b, §8 and §8a ("written after a per-episode listing had been seen, before any per-route value"), and §14 ("before computing"). |
| N-8 | MINOR | L241(ii) | "the two secondary rules for blocked time": R2 is standstill outside blocked time. | "the two secondary rules (standstill outside blocked time, blocked time)". |
| N-9 | MINOR | L97, L362 | L97: "(above 2 m/s, 2.17 % against 0.99 % of steps)" is a share of steps above 2 m/s, in pass 1, and neither is said. "About twice" understates the 0.5–2 m/s ratio in pass 2 and gate-off (3.0× and 3.4×). | "(first pass, steps above 2 m/s: …)"; "two to three times". |
| N-10 | MINOR | L342 | "when the vehicle is held in place": §12a says to describe this only as commanded to accelerate without moving. | "… when it is commanded to accelerate and does not move". |
| N-11 | MINOR | L83, L113 | L83 is ungrammatical ("… [38], re-weighting rare samples to raise … [39], and rebalancing has been shown … [33], and Alpamayo 1.5 …"). L113 adds an uncited factual claim: "Many closed-loop CARLA agents also include controller-side anti-stall rules, such as creeping forward after a fixed time at rest". | L83: "… [38] and that re-weighting rare samples raises closed-loop benchmark scores [39]; rebalancing …". L113: cite an agent that has a creep rule, or write "Some closed-loop CARLA agents …". |
| N-12 | MINOR | L421 | "called H3 in earlier versions" now names a different hypothesis H3. | Delete the parenthesis. |
| N-13 | MINOR | L399 | §9 promised R2 with the §8 settings as sensitivity rows too. They are not reported. They support the result: −12.75 [−20.30, −7.25], −11.63 [−19.60, −5.57], −11.94 [−18.79, −6.00]. | Add half a sentence. |
| N-14 | MINOR | L517 [20] | No commit hash or access date for a repository that is still being changed. | Add the commit or the access date. |

Claim-strength drift (E6, informal; no Revision-Evidence Bundle was supplied, so no schema artifact was produced): every changed claim either moved down the ladder (title, abstract, L101, L436, L442, L460) or was reversed as §17 requires (stopping from motion). None was strengthened without authorization. Result: none detected by this semantic review.

---

## Task 3: internal consistency

- **Main finding.** The title (low-speed hesitation, matched pair, single seed), the abstract ("the mix changed what the policy planned once it was slow"), Section 1 (H3 "main finding"; the first of the three findings), the discussion (L434, L436) and the conclusion (L460) all lead with the same finding: plans at low speed, with the controller deciding how they appear on the road, at a cost in blocked time. Consistent.
- **H1, H2 and H3 definitions.** L90 and L293: Golden-1600 vs Base on Driving Score. L91 and L289: Golden-6400 has less standstill than Flooded-6400 at a matched schedule. L92, L287 and L356 (R1): share of plans under 1.5 m in pass 2 is lower for Golden-6400; the decision criterion (interval below 0, p < 0.05) is given at L287 and L356. Consistent. The role labels are the same at L90–92 and L287–293.
- **Table 6 against the text.** All 24 cells equal the text values (see Task 2). No discrepancy.
- **Cross-references.** There are 6 tables and 5 figures, each with a caption or placeholder. Figures 1–5 are each cited once (L213, L249, L336, L346, L358). Tables 1–4 are cited in the text; **Tables 5 and 6 are cited only in their own captions** (N-4). Every "Section x.y" reference points to the right section (checked one by one: 3.1, 3.2, 3.3, 3.4, 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, "4.3 and 4.4", "4.5 to 4.7", "4.6 and 4.7"). Every addendum § cited exists (5a, 6, 7, 7a, 7b, 8, 8a, 9, 10, 11-B, 12a, 12b, 13, 14, 16, 17).
- **Citations.** All 47 references are cited. There are no orphans and no dangling numbers ("[0,1]" at L141 is an interval).
- **Abstract vs body.** The two-pass Driving Score (5.67, p = 0.11), blocked time over both passes (8.13 / 0.43), H2 pass 1 and pass 2, and the 1,600-sample null all agree with the body.

---

## Task 4: the 7-mode checklist after corrections

| Mode | Round 1 | Round 2 | Evidence |
|---|---|---|---|
| 1. Implementation bug passing self-review | SUSPECTED | **CLEAR** | (a) The measure that was near zero by construction is withdrawn and replaced; the new values come from the committed `analysis_braking` and agree with the round-1 values from separate code to 0.01 pp. (b) The route scored 0 % without a step log is disclosed (L231). The equation check is stored (5.6 × 10⁻⁶ m). 416 tensors confirmed from the weight header. The permissive number checker is no longer cited as verification. Remaining, not a finding: `except Exception: pass` in the registered loader, which stays unmodified by design. |
| 2. Hallucinated citation | INSUFFICIENT EVIDENCE | **CLEAR** | All 47 references exist (references report). All four MEDIUM corrections and MINOR 1, 4, 5, 9–13 are applied. No ghost citations. Remaining: the volume of [38] is unconfirmed (MINOR, check by hand) and [20] has no version pin. |
| 3. Hallucinated experimental result | CLEAR | **CLEAR** | Every new number traced to a manifest key; the braking values reproduced independently. |
| 4. Shortcut reliance | SUSPECTED (flag only) | **SUSPECTED (flag only, not blocking)** | Unchanged. There is no same-input comparison, the decoupling model and the swap test are pending, and there is one seed. New supporting evidence: the pooled braking-plan shares (N-2) and stay-put shares (L360) show the balanced 6,400 checkpoint as the outlier among six models, which is what an idiosyncratic checkpoint would produce. Re-check at 4.5. |
| 5. Bug reframed as insight | SUSPECTED | **CLEAR** | "restarting, not stopping" is removed under the §17 rule. Contact is no longer stated as fact (L405, L440). Residual wording at L342 (N-10, MINOR). |
| 6. Methodology fabrication | SUSPECTED | **CLEAR** | The training hardware is corrected (L101, L193); the cache convention now comes from the server code (L209). The Methods numbers checked against artifacts: 416 tensors, 10⁻⁵ m, 0.59 / 3.1 m. Gaps that are not fabrication: the fallback branch is not described (IL-MINOR-8), there are no trainer artifacts for the decoupling model (its result is pending), and the collection rendering quality is open and not claimed. |
| 7. Frame-lock | INSUFFICIENT EVIDENCE | **CLEAR** | The frame now matches the design: the title and abstract are scoped to one matched pair and one seed, the 1,600-sample null is in the abstract, the inertia keyword is removed, the conjecture is labelled post hoc, and "progress" is dropped. Residual generic headlines (N-3) are wording, not frame. |

Block condition: no mode is SUSPECTED except Mode 4, which is flag-only at Stage 2.5. Modes 1, 3, 5 and 6 are not INSUFFICIENT EVIDENCE. **The checklist does not block.** At 4.5, Mode 4 must be CLEAR or overridden with reasoning.

---

## What could not be verified

- That nothing was computed before the commits that say so. Commit times are local, which Section 4.1 now discloses.
- The 4.1 statement that the second directory for route 23687 has "identical" result records. I did not compare the two directories.
- Training of the decoupling model (no trainer artifacts in `docs/provenance`).
- The volume of [38]; the content of B55 (48 history tokens).
- Figures 1–5, which are placeholders in the text file.
- Originality against external sources (not in scope; use iThenticate before submission).
- The authors' statement in the AI disclosure, which is still pending.
- The gap of 34 elements between the parameter count in the weight header (2,280,592,420) and the trainer's trainable count (2,280,592,386) is presumably a non-trainable buffer, which I did not trace. The manuscript reports the trainer's trainable count.

## Audit trail

Read: the role file (§ re-verification, verdict criteria, E6), `ai_research_failure_modes.md`, both round-1 reports, the manuscript in full, `git diff cd8e28aa~1 cd8e28aa` of the manuscript (old lines compared one by one), addendum §6–§17, `CONFIRMATORY_DEVIATIONS.md` §D, `action_space_equation_check.txt`, `A100_TRAINING_PROVENANCE.md` (by search), `paper_reanalysis.py` (`analysis_braking`, `second_pass_sensitivity`, v_end definition), and the manifest keys `braking`, `second_pass_decisions` (with `sensitivity_no_decision`), `pass_agreement`, `O`, `U`, `N` and `P`.

Commands: the number checker; read-only `git log`, `git diff`, `git show`, `git status`; `grep`, `sed`, `awk`, `ls`, `find`; `nice python3` snippets that read JSON and one safetensors header (8-byte length plus JSON). No GPU use, no process control, no project file written.

---

# Round 3 (narrow scope): commit 7fc39915

Manuscript: SHA-256 `974a1ad92e986ba11c3feb1251c8cce0208e61de018d15b7dbaad79545ca2433`, commit `7fc39915` (15 Nov 16:56:31). Scope: only the text that `git diff cd8e28aa 7fc39915 -- docs/manuscript_revision_draft.txt` shows as changed (18 lines). Read-only, as in the earlier rounds.

## Verdict: **PASS WITH NOTES**

No SERIOUS or MEDIUM issue remains. The blocking item (IL-MEDIUM-1) is resolved. The 7-mode checklist does not block; Mode 4 is still SUSPECTED, which is flag-only at this stage. The MINOR notes below go forward to Stage 4.5, where MINOR items must be fixed.

## Checks

| Item | Result | Current text |
|---|---|---|
| (a) IL-MEDIUM-1, four sentences | **RESOLVED** | L72: "a test of near-stationary plans, fixed before any plan-level value of that pass was computed, was met". L103: "H3 before the obstacle-heavy model's second pass started and before any second-pass plan-level value was computed". L287: "on second-pass data whose plan-level values had not been computed when it was written (Section 4.1)". L460: "specified before any plan-level value of the second pass was computed". Every statement agrees with addendum §9 and run note 6. "did not exist" is gone from both the .txt and the .tex. |
| (b) "called H3 in earlier versions" | **RESOLVED** | L421: "**Dataset size (exploratory, `Golden-6400` vs `Golden-1600`).**" |
| (c) N-2, pooled braking shares | **RESOLVED** | L362 gives 1.50 / 1.80 / 1.99 / 1.59 / 1.79 / 0.82. These equal `braking.pooled_all_models_default_run1.*.moving_above_2` (1.496, 1.800, 1.994, 1.587, 1.794, 0.819). "Golden-6400 is the low outlier": true, it is the lowest of the six. "At 1,600 samples the order is reversed": true, Golden-1600 1.99 against Flooded-1600 1.80. |
| (d) N-3, scoped headlines | **RESOLVED** | L97: "**In this matched pair, the data composition shifted what the model planned once it was slow.**" L434: "In this matched pair of checkpoints, the fine-tuning data composition changed …". |
| (e) Section 4.1 (iii)/(iv) | **RESOLVED except one MINOR item** | §14 is correctly placed in (iii): the addendum says "before computing" and lists what had been seen (H1 on 44 and 37 routes, nothing restricted to the non-tuning routes). §12b in (iv) agrees with §12b ("from the gate-off means seen when this was written"). §8 and §8a in (iv) agree with the addendum: the per-episode listing was seen before §8 was written (05:25), and §8a (05:35) came after it. "No decision rule was changed" is now precise. **§7b is misplaced (R3-1, below).** |
| (f) N-4 | RESOLVED | Table 5 is cited at L320 ("Table 5 collects these sensitivity analyses") and in its caption; Table 6 is cited at L287. |
| (f) N-5 | RESOLVED | L366: "All rows are post hoc except H3 (pass 2), H2 (pass 1) and the pass-2 values of standstill outside blocked time and blocked time, which are the pre-specified rules R2 and R3. … so the braking row uses 43 routes." |
| (f) N-6 | RESOLVED | L157 "implies"; L336 "conjecture … describes"; L358 "stay-put conjecture"; L436 "conjecture of Section 3.2". The one remaining "hypothesis" (L287) correctly refers to H3. |
| (f) N-8 | RESOLVED | L241: "two secondary rules, for standstill outside blocked time and for blocked time". |
| Also changed | RESOLVED | N-10 (L342): "commanded to accelerate and does not move". N-11, second part (L113): "Closed-loop agents can also include controller-side anti-stall rules". |
| (g) Number checker | 0 unsupported | 1,357 supported, 0 unsupported, 333 ignored. |
| (g) New problems | one MINOR | See R3-1. No new safety, collision or inertia wording, and no claim of wider scope. `CONFIRMATORY_DEVIATIONS.md` changed only by run note 9. |

## R3-1 (MINOR, new)

L241(iv) puts §7b in the group "written down after a per-episode listing of long stops had been seen". The record says otherwise. Addendum §7 (commit `845e061d`, 13 Nov 21:19) states: "Not computed or viewed for any model: the number, duration or ending of stop episodes (Section 7b)". The per-episode listing was seen only before §8 (14 Nov 05:25). L395 says, correctly, "By a rule fixed before the episode statistics were computed", so Sections 4.1 and 4.7 now contradict each other. The error makes the record look worse than it is, not better, so it does not block.

Fix: in (iv), write "the blocked-time analyses (§8, §8a) were written down after a per-episode listing of long stops had been seen". In (iii), add "the stop-episode classes (§7b), written after part of the gate-off run had been seen but before any episode statistic was computed".

## Notes carried to Stage 4.5 (MINOR items, all must be fixed there)

1. R3-1: §7b placement in Section 4.1 (iv).
2. L434 "under rules fixed in advance" (recommended in round 2, not yet changed): write "fixed before any plan-level or command-class value of the second pass was computed".
3. L97: the braking share does not name its pass (first pass).
4. N-7(c) in part: §7b and §8 are now in the 4.1 record; §8a and §14 are also covered.
5. N-9: "about twice" understates the 0.5–2 m/s ratio in pass 2 and gate-off (3.0× and 3.4×).
6. N-11, first part: L83 is still ungrammatical.
7. N-13: R2 sensitivity rows with the §8 settings are not reported.
8. N-14 and ref [20]: the recipe has no commit hash or access date.
9. Ref [38]: the volume number is unconfirmed.
10. Optional ref items MINOR-6 and MINOR-14.
11. IL-MINOR-8: the controller's no-waypoint fallback is not described.
12. IL-MINOR-9: the mean-L comparison (L336) and the rationale-conditioned shares (L383) have no speed caveat.
13. IL-MINOR-10: the 416-tensor count and the decoupling-model trainer artifacts are not stored in `docs/provenance`.
14. IL-MINOR-11: the AI disclosure needs the authors' statement, the A100 provenance session, and the run monitoring.
15. IL-MINOR-12: addendum heading times and run-note times are later than their commits.
16. IL-MINOR-13: notes-block housekeeping.
17. Revision-history remarks in the body: move them to the response letter.
18. FlowDrive advisory.
19. Archive the repository with a DOI, since its commit times are not third-party time-stamped.
20. Mode 4 (shortcut reliance), SUSPECTED: must be CLEAR or overridden with reasoning at 4.5.
