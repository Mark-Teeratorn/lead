contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "Reporting gaps that do not threaten the headline conclusion"

The warn rests mainly on W2, W4 and W6 to W10. No D1 block trigger is met. Every confirmatory rule (H2, H3, R2, R3) is dated before its comparison data existed, the paired route-level tests respect the pairing, the H2 shortfall in the second pass is reported as such, post hoc analyses are labelled and the trade-off rests on pre-specified replications. The materials needed to recompute the headline values are described as archived, with the DOI and commit still pending, which I read as incomplete materials, not missing information.

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "limitations acknowledged but not propagated to every summary statement"

The central thesis is scoped to the matched pair and to one seed in the title, abstract and conclusion, so the block clause about generalising from a single training run is not met. The warn rests on W1, W3, W5 and W11. Caveats stated in Sections 3.2, 4.6 and 5 are missing from the summary statements of the abstract, the introduction and the discussion, and the step from less hesitation to more blocked time is asserted but not argued.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity
Peer Reviewer 1 (Methodology). Biostatistics-trained ML evaluation methodologist working on paired non-parametric inference, multiplicity, pre-specification and small-N benchmark design. Driving-domain plausibility is outside my remit and is left to the domain seat.

### Calibration Status
`NOT_CALIBRATED`

### Summary Assessment
This is a carefully reported closed-loop comparison of two fine-tuned checkpoints of one flow-matching VLA policy. The two checkpoints differ only in the fine-tuning mix, and that mix bundles three factors. Methodologically the revision is unusually candid. It dates every rule against the data it governs, lists the interim looks, withdraws earlier claims and measures, quantifies run-to-run noise (replicate SDs, ICCs, a between-pass noise reference for the interaction), and adds a second evaluation pass and a gate-off controller run. The main finding is H3 together with its speed-conditioned companions: the obstacle-heavy checkpoint produces stay-put plans several times as often. It is replicated across passes and controllers on nearly every route, and the replication was fixed before the comparison data existed. I find that result well supported as a statement about these two checkpoints.

Three things limit what the design can carry. First, with one checkpoint per cell the difference cannot be attributed to composition as opposed to this training run, and the paper's own numbers make the balanced 6,400-sample checkpoint an outlier among all six models (W1). Second, the plan comparisons are not on identical inputs, and a cheap offline test that would settle this is available (W2). Third, the cost side of the trade-off rests on blocked time on six routes, each of which has a collision, and the order of blocking and contact is not reported (W3). The pre-specified H2 comparison is confounded by a harness change between its arms (W4). The remaining points are reporting refinements. Several summary sentences need the caveats the body already states.

### S1: The pre-specified primary test is reported honestly, including where it falls short
**Evidence Anchor**: text: Section 4.3, H2 paragraph, "In the second pass alone the same rule gives case B (same direction, interval including zero; Section 4.4)."

H2 is stated with its decision rule and cases (A1, A2, B, C) and applied to both passes. The pass-2 shortfall appears in the abstract, the discussion and the conclusion. The headline was not moved to the favourable pass or to the two-pass mean, and the two-pass mean is flagged as having no decision attached.

### S2: A pre-specification record that dates rules against data and discloses the interim looks
**Evidence Anchor**: text: Section 4.1, Record of pre-specification, "Two further looks at incomplete second-pass data followed and are recorded"

Each analysis group is placed relative to its values: (i) to (iii) were written before their values were computed, and (iv) lists the exceptions. "Registered" has been replaced by "pre-specified", and the paper says that H1's p-value was known when the Holm family was declared. A reviewer can see exactly which inferences are confirmatory.

### S3: Run-to-run noise is measured and carried into the reading of the results
**Evidence Anchor**: text: Section 4.1, Non-determinism, "with intraclass correlations of 0.57 and 0.63 for standstill"

The unseeded server is disclosed, along with replicate SDs on eight routes, between-pass SDs and ICCs for three outcomes, the per-route sign agreement and rank correlation between passes (Section 4.4), and a no-change-of-controller reference for the interaction (Section 4.5). Per-route comparisons are correctly called descriptive, and the route-level paired test treats each route's single run as one draw, so run noise sits in the variance of the paired differences.

### S4: Model and controller are separated in several complementary ways
**Evidence Anchor**: table: Table 6, plan-level and motion-level measures under the default controller in both passes and under the gate-off controller

The gate-off run, the speed-conditioned stay-put shares (at 0.5 m/s or less, and at rest), the decomposition of total standstill into blocked time and the rest, and the crawling measure are shown side by side for both passes and both controllers. The table makes visible that total standstill is the sum of two components that move in opposite directions.

### S5: The dataset and training provenance are controlled and documented
**Evidence Anchor**: table: Table 2, training and evaluation provenance of every evaluated checkpoint

Both mixes come from one verified pool with deterministic salted selection, and the 1,600-sample sets are nested quarters of the 6,400-sample sets. The overlap between the two mixes (4,284 shared samples) and the overlap with the evaluation routes are reported. Schedules were rebuilt from trainer artifacts, including resume events and a correction of earlier step counts. The step counts are internally consistent (1,600/8 × 10 = 2,000; 6,400/8 × 10 = 8,000; 4,000 steps on 6,440 samples is 4.97 epochs).

### S6: Measures that are artefacts of how they are built are recognised and withdrawn
**Evidence Anchor**: text: Section 4.6, Braking plans while moving, "that count is close to zero by construction, because the plan is integrated from the current speed, and is withdrawn"

The paper sees that the extent L depends on v0 (Section 3.1) and draws the consequences. It conditions low-speed shares on speed, adds an at-rest restriction, and replaces a measure that is degenerate by construction with planned end speed.

### W1: One checkpoint per cell, so composition cannot be separated from this training run
**Severity**: Major
**Evidence Anchor**: text: Section 4.6, paragraph on pooled stay-put shares across six models, "the balanced model at 6,400 samples plans to stay put far less often than its own training data do"
**Confidence**: 4 — design of seed-replicated comparisons in ML evaluation

Within the pair, the data change is the only intervention, so the two checkpoints do differ because of it. A single checkpoint per cell cannot show whether the difference is a property of the composition, one that would recur across training runs, or of this particular optimisation path, which changes completely when the data change even with seed 42 fixed. The manuscript's own numbers keep the second reading open. The pooled low-speed stay-put share is 2.3 % for `Golden-6400`, against 16.4 % for `Golden-1600` (same mix), 14.6 % to 33.3 % for the other four models, and 10.9 % in its own training set. For braking to rest from motion, `Golden-6400` is the low outlier and the order of the mixes reverses at 1,600 samples. At 1,600 samples, conditional training shares that differ almost as much produce no standstill difference. Every headline comparison involves the same balanced checkpoint. H3 replicates the checkpoint difference across evaluation passes, not across training runs. The pass-2 tests therefore rule out evaluation noise, not training-run idiosyncrasy.

Minimum remedy: state in the abstract, the findings list and the conclusion that the replication addresses evaluation noise only, and phrase the result as a difference between these two checkpoints whose dependence on composition across training runs is untested. Stronger option, at moderate compute cost: train two or three further seeds or data-order permutations of each 6,400-sample regime and report the plan-level measures with a between-seed component. Combined with the offline test of W2 this needs no closed-loop runs.

### W2: The plan distributions are never compared on identical inputs
**Severity**: Major
**Evidence Anchor**: text: Section 4.6, Near-stationary plans, "The two models visit different states in closed loop, so this is not a same-input comparison."
**Confidence**: 4 — standard identification argument for policy comparisons under closed-loop state shift

The plan-level shares are conditioned on speed but not on the scene. The two checkpoints reach different states, and the gate's holding brake feeds back into the context, as the paper notes in Section 4.5. A checkpoint that ends up waiting behind an obstacle or a queue more often will show more stay-put plans at rest even with an identical conditional policy. The keyword-rationale split points the other way, but it rests on an unvalidated classifier. The paper names the decisive test and says it was not performed (Section 3.2). That test is cheap and needs no simulator. Run both experts on identical inputs, using the shared 1,567-sample validation split restricted to low-speed samples and, if the camera frames were stored, on low-speed states logged from both models' runs. Draw many noise samples per input and compare the per-input stay-put rate between experts with a paired test over inputs. It would also test the conjecture of Section 3.2 directly, against the conditional training shares of Table 1.

### W3: Blocked time is not separated from contact, so the cost side of the trade-off is not established as a cost of less hesitation
**Severity**: Major
**Evidence Anchor**: text: Section 4.7, Blocked time, "Every route with blocked time has at least one collision event"
**Confidence**: 3 — inference from command logs; what physically happens on these routes is driving-domain judgement outside my remit

Contribution (iii) and the heading "Less hesitation has a cost" rest on blocked time. Its pass-2 replication (R3) is pre-specified, which is a strength. In pass 1, however, blocked time comes from 22 runs on six routes, and each of those routes has a collision event. The manuscript does not report whether the blocked runs begin before or after the collision events on their routes. If they follow contact, with the vehicle pressing against or wedged on what it hit, blocked time is a consequence of a collision. The paper reports no detectable difference in collisions and makes no safety claim, so that reading would undercut the trade-off as framed. The causal step from shorter commanded stops to more blocked time is supported only by a descriptive six-route comparison (Section 4.7, last paragraph). In pass 2 the R3 interval also includes zero at a throttle threshold of 0.2. Remedy: for every blocked run, report its onset relative to the route's collision timestamps and actor (the leaderboard records carry them). Classify runs as preceding contact, following contact, or on routes without contact before the run, and report blocked time without post-contact runs, together with a per-route listing.

### W4: The arms of the pre-specified H2 comparison ran on different harness versions
**Severity**: Major
**Evidence Anchor**: text: Section 4.1, Harness changes between the H2 arms, "We expect these changes to be behaviour-neutral on these routes, but this has not been shown."
**Confidence**: 3 — confounding in sequential evaluation; whether the specific harness changes matter is a simulator question

`Golden-6400` was evaluated on 19 and 20 October and `Flooded-6400` on 11 and 12 November, after changes to the evaluator and launcher. The only like-for-like comparison is the second pass, and it is case B. Between passes `Golden-6400` moved by +2.30 pp and `Flooded-6400` by −0.68 pp, while the difference shrank by +2.97 pp. A harness effect on one arm would produce exactly this pattern, although run noise can produce it as well. With a per-route between-pass SD of about 22 pp, "no shift larger than run-to-run variation" cannot establish neutrality. The abstract reports the pass-1 value as the pre-specified comparison without this qualification. Remedy: state in the abstract and the conclusion that the pass-1 arms ran on different harness versions and that the only same-harness test did not meet the rule. Optionally, test neutrality directly by re-running a subset of `Golden-6400` routes on the old harness.

### W5: The two-pass Driving Score is described as "lower" beyond what the evidence carries
**Severity**: Minor
**Evidence Anchor**: text: Abstract, "its two-pass Driving Score was 5.67 points lower (rank test p = 0.11)"
**Confidence**: 4 — small-sample paired inference with poorly reliable outcomes

The card asks whether the Driving Score can carry the "progress" side of the trade-off. My answer is that it can support "not higher", which is what Section 5 says, but not "lower". The evidence is: in pass 1, −3.24 points with p = 0.64; on the two-pass mean, which had no rule fixed in advance, the bootstrap interval only just excludes zero while the signed-rank test does not reject; and the ICC for Driving Score is 0.36 to 0.51. The pass-2 difference alone, about −8.1 points by the printed means, is not reported with an interval. Remedy: write "not higher" in the abstract and the introduction, report the pass-2 Driving Score difference with its interval, and attribute the trade-off to blocked time (subject to W3).

### W6: The pre-specification record cannot be checked from the submission, and one look is missing from the discussion
**Severity**: Minor
**Evidence Anchor**: text: Section 4.1, Record of pre-specification, "they were not time-stamped by a third party"
**Confidence**: 4 — pre-registration practice

Git commit times in a self-held repository can be set by the author. Only one commit hash is given (`013a12bd`), the repository commit is pending, and ANALYSIS_ADDENDUM, which is cited throughout, is not part of the submission. R2 and R3 were committed after the standstill of 14 of the 44 second-pass `Golden-6400` routes had been seen. Section 4.1 says so, but Section 5 presents all three rules as "fixed in advance" without that qualifier. The probable impact is small, because the blocked-time definition was already fixed in pass 1. Remedy: supply the addendum as a supplementary file with the commit hash of each section. Give push times from a hosted remote, or a deposited snapshot, as third-party evidence of timing. Carry the 14-route qualifier into Section 5.

### W7: Mean-based intervals and signed-rank p-values address different estimands and disagree in several rows
**Severity**: Minor
**Evidence Anchor**: table: Table 5, rows for the 37 routes without training overlap, standstill in seconds, and the second pass alone
**Confidence**: 4 — non-parametric inference

In several rows p is well below 0.05 while the BCa interval for the mean difference includes zero: p = 0.0065 on 37 routes, p = 0.0088 for seconds and p = 0.0021 for the second pass. The two procedures target different quantities, the mean difference and a sign-rank (pseudo-median) location. Their divergence reflects heavy-tailed route differences driven by a few long stalls, as the paper notes in Section 4.5. Read alone, these p-values suggest a stronger result than the pre-specified rule supports. Remedy: name the estimand next to each inferential statement, keep decisions on the pre-specified interval, and consider adding the Hodges–Lehmann estimate with its interval.

### W8: Inference on zero-inflated outcomes rests on a handful of routes
**Severity**: Minor
**Evidence Anchor**: text: Section 4.7, Blocked time, "(2 runs on 1 route), a difference of +7.57 pp"
**Confidence**: 4 — small-sample rank tests and bootstrap coverage

Blocked time is non-zero on six routes for one model and one route for the other. With zero differences dropped, the signed-rank test operates on six or seven pairs under the normal approximation (Section 4.1, Statistics), and a BCa interval for a mean over 44 routes, 37 or more of them zero, has uncertain coverage. Remedy: print the number of non-zero routes next to each such p, give the per-route values, and use an exact sign or permutation test conditional on the non-zero routes. The same applies to pedestrian contacts and to the per-stratum comparisons.

### W9: The materials for an independent rerun are not yet complete
**Severity**: Minor
**Evidence Anchor**: absence: Section 6, Data availability and Code availability — expected a release statement for the six evaluated checkpoints and a fixed commit for both analysis scripts; checked Section 6 Data availability, Code availability, Section 3.4 and Table 2
**Confidence**: 4 — reproducibility standards for ML evaluation

The datasets are released, but the evaluated checkpoints are not mentioned. The archive DOI for logs and trainer artifacts and the code commit are pending. Retraining cannot reproduce the checkpoints, because training is not shown to be deterministic and W1 makes the specific checkpoint matter. Remedy: release the six checkpoints, or state why they cannot be released, and fix the commit and DOI before acceptance. For future runs, seeding the server's noise draws would make closed-loop reruns auditable.

### W10: Some secondary results have p-values but no interval
**Severity**: Minor
**Evidence Anchor**: text: Section 4.8, Strata, "Overtaking (9 routes) gave −8.28 pp (p = 0.0039) and Merging (16) −12.18 pp (p = 0.034)"
**Confidence**: 5 — reporting standard

Traffic Signs (five routes) and the 0.1 to 0.5 m/s at-rest band shares (Section 4.6) have no interval either, and the Spearman correlations of Section 4.8 are reported without intervals. Remedy: give the interval used elsewhere, or drop the p-value for strata this small.

### W11: Consistency with the conjecture is cited without the evidence against it
**Severity**: Minor
**Evidence Anchor**: text: Section 5, second paragraph, "This is consistent with the conjecture of Section 3.2"
**Confidence**: 4 — fit between claims and evidence

Section 5 cites the nearly threefold difference in training shares as fitting the conjecture. The same sentence does not mention what Section 3.2 and Section 4.6 report: the 1,600-sample pair, whose training shares differ almost as much, shows no difference; and `Golden-6400` plans to stay put far less often than its training data. The findings list in the introduction gives the braking-from-motion ratio ("two to three times") without the Section 4.6 caveat that `Golden-6400` is the low outlier and that the order reverses at 1,600 samples. Remedy: put the disconfirming observations in the same sentence as each consistency claim.

### W12: H1 has no valid test in the manuscript as it stands
**Severity**: Minor
**Evidence Anchor**: text: Section 4.1, Termination rule and censoring, "and H1 will use that run"
**Confidence**: 5 — direct reading of the reported design

The original `Base` run predates the 60 s rule on 38 routes, and the controller was tuned with a fine-tuned checkpoint. On the 24 untuned routes the interval includes zero, so the reported H1 value cannot be interpreted until `Base-Rerun` is in. This affects only H1. With two tests, the Holm-adjusted value for H2 cannot exceed 2 × 0.00071, whatever H1's p turns out to be.

### What depends on the pending results
The H3, R2, R3 and H2 results and my scores do not depend on the placeholders. H1 depends entirely on `Base-Rerun` (W12). The bundled-treatment limitation can only be narrowed by the decoupling model, which would separate the scenario-group mix from lateral balance plus stationary share, but not those two from each other. The mechanism sentence in Section 5 waits on the motion-history swap test. Reproducibility depends on the archive DOI and the commit hash (W9).

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Rules dated before their data; interim looks disclosed | Card #2 focus 1; D1 scoring plan | PARTLY_MEETS | via W6 | Full dated record, but self-timestamped, addendum not supplied, one look not carried into Section 5 | Commit times not verified | no — warn-level |
| Paired inference under run-to-run noise | Card #2 focus 2; D1 scoring plan | MEETS | via S3, W7 | Route pairing respected, noise quantified; estimand labelling incomplete | — | no |
| Multiplicity | statistical_reporting_standards.md §4.5 | MEETS | via S2 | Families declared, post hoc tests labelled unadjusted, R2/R3 Holm-adjusted | Holm over {H1, H2} gives H2 no protection, as the paper states | no |
| What the seed and bundle design permits | Card #2 focus 3; D3 scoring plan | PARTLY_MEETS | via W1, W2 | Scoped to the pair, but the replication addresses evaluation noise only, and inputs are not identical | Seed-to-seed variance unknown | yes — basis of D3 warn |
| Effect sizes and intervals | statistical_reporting_standards.md §1.2–1.3 | PARTLY_MEETS | via W10, W8 | Intervals on nearly all main results; a few secondary gaps; sparse outcomes | — | no |
| Trade-off supported on both sides | Card #2 "will particularly care about"; D3 scoring plan | PARTLY_MEETS | via W3, W5 | Hesitation side strong; cost side rests on blocked time on six routes with unknown order relative to contact; Driving Score supports "not higher" only | Contact timing not reported | yes — basis of D3 warn |
| Reproducibility affordances | D1 scoring plan | PARTLY_MEETS | via W9 | Datasets released; checkpoints, DOI and commit pending | — | no — warn-level |

### Methodological fallacies checked
Confounding: the harness change between H2 arms (W4). Uncontrolled checkpoint variance in place of an effect of the factor (W1). State-distribution shift standing in for a policy difference (W2). Reverse ordering between blocked time and contact (W3). The p-hacking and HARKing risk from choosing the endpoint after results is disclosed and handled by labelling and by replication on new data. Pooled and per-route-mean shares are both reported and diverge (Flooded-6400 24.9 % pooled against 14.00 % per route), without changing the direction. I found no Simpson-type reversal.

### Recomputation notes
The receipts below use only the bounded procedures. I also made informal checks, offered for audit and not verified. Table 4 bands and Table 6 components add to the totals within rounding (for example −15.63 + 7.57 = −8.06 and −8.31 + 11.16 = 2.85). The collision class counts in Table 3 sum to their totals. The Holm values follow from the raw p-values (2 × 0.00071 = 0.0014; 4 × 0.00071 = 0.0028; 3 × 0.0076 = 0.0228). The normal approximation of the signed-rank statistic gives about 0.0010 for W = 213 with n = 44 and about 0.0076 for W = 152 with n = 35, which matches the printed asymptotic values. The implied rank-biserial correlations are −0.57 and 0.52. The interaction values follow from the printed differences (2.85 − (−8.06) = 10.91). I found no internal inconsistency.

### Questions for Authors
1. Do the blocked runs on the six routes begin before or after the collision events on those routes (W3)?
2. Were camera frames stored for the logged low-speed states, so that both experts can be queried on identical inputs (W2)?
3. Can the six evaluated checkpoints be released (W9)?
4. Which ANALYSIS_ADDENDUM commit hash corresponds to each of §5a, §7a, §7b, §8, §9, §10, §12a, §13, §14, §16 and §17 (W6)?

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Table 1, row "Samples at ≤ 0.5 m/s, 1,600 set", Flooded column
reported_inputs: 168 / 346 / 35 of 549 (30.6 % stay put)
assumptions: proportion of 549 low-speed samples counted as stay put or not, as Table 1 gives the counts; percentage printed to one decimal; rounding rule unstated, and the paper's other printed percentages (4,284 shared samples given as 67 % of 6,400) follow round-to-nearest, not truncation
derivation: 168/549 = 0.306011, i.e. 30.6011 %, which lies inside the interval that rounds to 30.6
derived_value_or_range: 30.6011 %
rounding_interval: [30.55 %, 30.65 %)
nearest_achievable: 167/549 = 30.4189 %, 168/549 = 30.6011 %, 169/549 = 30.7832 %
comparison_rule: reported value must equal some k/549 rounded to nearest at one decimal; half-up and half-even agree because 30.6011 is not at a half boundary
status: consistent

### AR2
procedure_id: grim
evidence_anchor: table: Table 1, row "Samples at ≤ 0.5 m/s, 1,600 set", Golden column
reported_inputs: 44 / 302 / 41 of 387 (11.4 % stay put)
assumptions: proportion of 387 low-speed samples; percentage printed to one decimal; round-to-nearest as licensed by the paper's other printed percentages
derivation: 44/387 = 0.113695, i.e. 11.3695 %, which lies inside the interval that rounds to 11.4
derived_value_or_range: 11.3695 %
rounding_interval: [11.35 %, 11.45 %)
nearest_achievable: 43/387 = 11.1111 %, 44/387 = 11.3695 %, 45/387 = 11.6279 %
comparison_rule: reported value must equal some k/387 rounded to nearest at one decimal; half-up and half-even agree because 11.3695 is not at a half boundary
status: consistent

### AR3
procedure_id: grim
evidence_anchor: table: Table 1, row "Samples at ≤ 0.5 m/s, 6,400 set", Flooded column
reported_inputs: 662 / 1,339 / 137 of 2,138 (31.0 % stay put)
assumptions: proportion of 2,138 low-speed samples; percentage printed to one decimal; round-to-nearest as licensed by the paper's other printed percentages
derivation: 662/2138 = 0.309635, i.e. 30.9635 %, which lies inside the interval that rounds to 31.0
derived_value_or_range: 30.9635 %
rounding_interval: [30.95 %, 31.05 %)
nearest_achievable: 661/2138 = 30.9167 %, 662/2138 = 30.9635 %, 663/2138 = 31.0103 %
comparison_rule: reported value must equal some k/2138 rounded to nearest at one decimal; half-up and half-even agree because 30.9635 is not at a half boundary
status: consistent

### AR4
procedure_id: grim
evidence_anchor: table: Table 1, row "Samples at ≤ 0.5 m/s, 6,400 set", Golden column
reported_inputs: 171 / 1,250 / 147 of 1,568 (10.9 % stay put)
assumptions: proportion of 1,568 low-speed samples; percentage printed to one decimal; round-to-nearest as licensed by the paper's other printed percentages
derivation: 171/1568 = 0.109056, i.e. 10.9056 %, which lies inside the interval that rounds to 10.9
derived_value_or_range: 10.9056 %
rounding_interval: [10.85 %, 10.95 %)
nearest_achievable: 170/1568 = 10.8418 %, 171/1568 = 10.9056 %, 172/1568 = 10.9694 %
comparison_rule: reported value must equal some k/1568 rounded to nearest at one decimal; half-up and half-even agree because 10.9056 is not at a half boundary
status: consistent

### AR5
procedure_id: grim
evidence_anchor: text: Section 4.9, first paragraph, Golden-6400 value, "In the second pass the events per route"
reported_inputs: second-pass collision events per route 1.07 (Golden-6400), 44 routes
assumptions: unweighted mean over 44 routes of non-negative integer event counts per route; printed to two decimals; round-to-nearest as licensed by the paper's other printed values
derivation: 47/44 = 1.068182, which lies inside the interval that rounds to 1.07
derived_value_or_range: 1.068182
rounding_interval: [1.065, 1.075)
nearest_achievable: 46/44 = 1.045455, 47/44 = 1.068182, 48/44 = 1.090909
comparison_rule: reported value must equal some k/44 rounded to nearest at two decimals; half-up and half-even agree because 1.068182 is not at a half boundary
status: consistent

### AR6
procedure_id: grim
evidence_anchor: text: Section 4.9, first paragraph, Flooded-6400 value, "the events per route were 1.07 and 1.05"
reported_inputs: second-pass collision events per route 1.05 (Flooded-6400), 44 routes
assumptions: unweighted mean over 44 routes of non-negative integer event counts per route; printed to two decimals; round-to-nearest as licensed by the paper's other printed values
derivation: 46/44 = 1.045455, which lies inside the interval that rounds to 1.05 (0.000455 above its lower edge)
derived_value_or_range: 1.045455
rounding_interval: [1.045, 1.055)
nearest_achievable: 45/44 = 1.022727, 46/44 = 1.045455, 47/44 = 1.068182
comparison_rule: reported value must equal some k/44 rounded to nearest at two decimals; half-up and half-even agree because 1.045455 is not exactly at the half boundary
status: consistent

### AR7
procedure_id: grim
evidence_anchor: text: Section 4.4, Second pass paragraph, "collision events per route were 1.03 and 0.93"
reported_inputs: two-pass mean collision events per route 1.03 (Golden-6400); first-pass events 44; second-pass events per route 1.07; 44 routes, two passes
assumptions: per-route mean of two integer counts averaged over 44 routes, so the mean equals a total count divided by 88; printed to two decimals; round-to-nearest as licensed by the paper's other printed values
derivation: first-pass total 44 plus second-pass total 47 (from AR5) gives 91, and 91/88 = 1.034091, which lies inside the interval that rounds to 1.03
derived_value_or_range: 1.034091
rounding_interval: [1.025, 1.035)
nearest_achievable: 90/88 = 1.022727, 91/88 = 1.034091, 92/88 = 1.045455
comparison_rule: reported value must equal some k/88 rounded to nearest at two decimals, and k must match the first-pass and second-pass totals; half-up and half-even agree because 1.034091 is not at a half boundary
status: consistent

### AR8
procedure_id: grim
evidence_anchor: text: Section 4.9, first paragraph, "on the mean of both passes 1.03 and 0.93"
reported_inputs: two-pass mean collision events per route 0.93 (Flooded-6400); first-pass events 36; second-pass events per route 1.05; 44 routes, two passes
assumptions: per-route mean of two integer counts averaged over 44 routes, so the mean equals a total count divided by 88; printed to two decimals; round-to-nearest as licensed by the paper's other printed values
derivation: first-pass total 36 plus second-pass total 46 (from AR6) gives 82, and 82/88 = 0.931818, which lies inside the interval that rounds to 0.93
derived_value_or_range: 0.931818
rounding_interval: [0.925, 0.935)
nearest_achievable: 81/88 = 0.920455, 82/88 = 0.931818, 83/88 = 0.943182
comparison_rule: reported value must equal some k/88 rounded to nearest at two decimals, and k must match the first-pass and second-pass totals; half-up and half-even agree because 0.931818 is not at a half boundary
status: consistent

### AR9
procedure_id: p_from_test_statistic
evidence_anchor: text: Section 4.3, H2 paragraph, "no zero differences, exact two-sided"
reported_inputs: Wilcoxon signed-rank W = 213; 44 routes; no zero differences; exact two-sided p = 0.00071; asymptotic 0.00100
assumptions: two-sided as stated in Section 4.1; the statistic is a signed-rank sum, not a t, z, F or chi-square value
derivation: the bounded procedure maps a t, z, F or chi-square statistic and its df to p; a signed-rank W with an exact permutation null lies outside it, so no p is derived
derived_value_or_range: none derived
comparison_rule: not applied
tail_convention: two-tailed
status: not_computable
not_computable_reason: nonstandard_p_procedure

### AR10
procedure_id: p_from_test_statistic
evidence_anchor: text: Section 4.3, H1 paragraph, "9 zero differences, asymptotic p = 0.0076"
reported_inputs: Wilcoxon signed-rank W = 152; 44 routes; 9 zero differences; asymptotic two-sided p = 0.0076
assumptions: two-sided as stated in Section 4.1; the statistic is a signed-rank sum with zero differences dropped, not a t, z, F or chi-square value
derivation: the bounded procedure maps a t, z, F or chi-square statistic and its df to p; a signed-rank W lies outside it, so no p is derived
derived_value_or_range: none derived
comparison_rule: not applied
tail_convention: two-tailed
status: not_computable
not_computable_reason: nonstandard_p_procedure
