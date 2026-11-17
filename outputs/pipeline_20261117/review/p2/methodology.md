contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "A headline result rests on an analysis that is mis-specified yet repairable from evidence already collected or cheaply collectable"
block_class: repairable

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "The core thesis is supported, but wording in places outruns the evidence and can be corrected by editing"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This is a single-seed, 44-route closed-loop comparison of fine-tuned checkpoints of one driving policy, analysed with route-level paired tests and reported with unusual candour about what was fixed when. Its central descriptive result is sound: in three evaluations (two passes with the default controller and one gate-off run) the obstacle-heavy checkpoint produced short plans at low speed several times as often as the balanced one, on 41 to 44 of 44 routes. The route is the right unit, pairing is respected, intervals accompany nearly every contrast, and a full second pass measures evaluation noise and is reported where it hurts: H2 fails its own rule in the only same-harness comparison, and the manuscript says so in the abstract.

I score D1 as a repairable block. Several results that the abstract carries rest on analyses that need repair, or on evidence that is cheap to collect and missing: the H1 verdict (W3), the blocked-time inference (W4), the history-swap reading (W5), a same-input comparison of the two experts (W2) and, behind all of them, training-run variation that the design does not measure (W1). Nothing here is unrecoverable, and no rule was found to have been changed after its data. I score D3 as warn: the body text scopes its claims to the checkpoints tested, and the remaining overreach sits in a small number of sentences (W1, W3, W4, W5, W8) that editing can correct.

On the three foci of my configuration card. Pre-specification: the manuscript does not use the word registered. It calls H2 a pre-specified replication test and states that the endpoint, one of the two arms and the difference against the historical checkpoint were known when the rule was committed; that description matches the record as given, with the caveat that commit times are self-attested. H3, R2 and R3 are repeat tests on the same checkpoints and routes from which they were formed. The interim looks are disclosed and, with a fixed number of routes and no stopping rule, do not inflate error by themselves. Noise: because each route contributes one run per arm, run-to-run noise is contained in the route-level differences, so the paired intervals are valid for evaluation noise; they say nothing about training runs. Trade-off: the manuscript no longer asks Driving Score to carry a progress side. It reports the balanced checkpoint's score as not higher (two-pass mean −5.67, interval just excluding zero, signed-rank p = 0.11) and declines to describe a trade-off. With an intraclass correlation of 0.36 to 0.51 for Driving Score, that restraint is correct.

Statistical reporting, judged against general standards of the field (the call has no venue binding). Effect sizes with intervals: MEETS. Accounting of exclusions, reruns and missing logs: MEETS (route 23687, the 43-route conditional rows and the pre-simulation restarts are disclosed). Delimitation of test families: PARTLY_MEETS (W3, W8). Match between test, estimand and distribution: PARTLY_MEETS (W4, W6). A priori power or a minimum detectable effect: DOES_NOT_MEET; none is given for any hypothesis, which matters most for the null readings of Sections 4.9 and 4.11.

Arithmetic. The manuscript reports no t, z, F or chi-square statistic and no degrees of freedom. Its tests are Wilcoxon signed-rank tests with exact or asymptotic p-values, which lie outside the bounded procedures, and the receipts record that. Nine means of integer counts admit a GRIM check and are receipted: five are reachable under any rounding rule, and four are reachable under round-to-nearest only, which I record as not computable because the manuscript states no rounding rule. The following read-off checks are outside the bounded procedures and are therefore not verified recomputations; all agree with the printed values: the Holm values for H1 and H2 against the raw p-values; the rank-biserial correlations against the printed W and the number of non-zero pairs; the four standstill bands and the blocked plus non-blocked parts against the totals of Table 4 and Table S2; the Table 1 shares against their counts; the two-pass means against the two pass values; and the second-pass collision totals implied by 1.07 and 1.05 (47 and 46), which add to the first-pass counts (44 and 36) to give exactly the totals implied by the two-pass means (91 and 82). I found no arithmetic inconsistency. The one reporting inconsistency I found is described in W3.

Questions for the authors, beyond the remedies listed under each weakness: what decision rule was committed for H1, and when and why was the Holm family reduced from four tests to two; how many non-zero pairs enter each blocked-time test; and are the fine-tuned weights deposited.

My confidence in this review is 4 of 5. Driving-domain plausibility is a possible blind spot and bears mainly on W5.

### S1: The status of every rule is stated, with dates and with what had been seen
**Evidence Anchor**: text: Section 4.1 "This is a pre-specified replication test on routes already observed for the other models, not a registration prior to all data."
For each analysis the manuscript says when it was written down, which data existed and which had been looked at, and it lists the interim looks and the protocol deviations. It also states what the label does not mean. This lets a reader weigh each result by its actual exposure, which is the purpose of pre-specification.

### S2: Evaluation noise is measured by a full repeat and reported against the primary result
**Evidence Anchor**: text: Section 4.4 "on 15 routes the sign changed, and the rank correlation between the per-route differences of the two passes was 0.01"
Both 6,400-sample checkpoints were run twice on all 44 routes. The manuscript reports intraclass correlations, the between-pass standard deviation, the sign changes and the failure of H2 under its own rule in the second pass. Per-route comparisons and small strata are, correctly, declared descriptive.

### S3: The controller's contribution is separated by intervention as well as by accounting
**Evidence Anchor**: text: Section 4.5 "both 6,400-sample models were re-run on all 44 routes with a controller identical to the default one"
The gate-off run is a closed-loop intervention on the one controller rule that is coupled to the outcome, and the offline band decomposition is labelled as accounting and not as a causal test. Conditioning the plan shares on speed, and then on rest, addresses the artefact that plan length is integrated from the current speed. Removing blocked steps addresses a denominator artefact. These are the right checks, and they were run.

### S4: The primary comparison is stressed along every disclosed threat
**Evidence Anchor**: table: Table S3, all sensitivity rows for the H2 comparison
Routes touched by training samples, controller-tuning routes, the termination rule, the speed threshold, the unit (seconds) and the historical comparator each have a row, including those where the interval then includes zero.

### S5: Reported quantities are internally consistent wherever they can be cross-checked
**Evidence Anchor**: table: Table 4, rows Standstill outside blocked time, Blocked time and Total standstill time
Decompositions sum to their totals in all three evaluations, and the informal cross-checks listed above found no discrepancy. The analysis scripts are named, and one is said to write a manifest of every reported number.

### W1: One training run per mix cannot carry an attribution to data composition
**Severity**: Major
**Evidence Anchor**: text: Section 4.1 "Each condition is one trained checkpoint (seed 42), so every test compares two specific checkpoints across routes"
**Confidence**: 5 — replication structure and variance components are my core area
Every contrast compares two specific checkpoints, each trained once. The study's question, and the wording of its first listed contribution (a controlled measurement of how two compositions changed low-speed behaviour), concern composition. The design cannot separate composition from the idiosyncrasy of a training run, and the manuscript's own evidence cuts both ways. The 1,600-sample pair has nearly the same stay-put shares in its training data (30.6 % and 11.4 %) and shows no difference in plans (−0.68 pp, interval including zero). The balanced 6,400-sample checkpoint is the low outlier among the six original checkpoints, including the one trained on the same mix, and it plans to stay put in 2.3 % of low-speed steps against 10.9 % in its training data. In favour of a composition effect, the decoupling checkpoint and the historical obstacle-heavy checkpoint fall on the expected sides, so four checkpoints at this size split two and two. That is suggestive, but they are four datasets, one on a different schedule, not replicates. The manuscript states the limit plainly; stating it does not supply the missing variance component. The authors could consider at least two further seeds for each 6,400-sample mix. By Table S1 and Section 4.1 a seed costs roughly 28 hours of training and 16 hours of evaluation, and the plan-level effect is large enough that one pass per seed would be informative; scoring extra seeds on a fixed set of states (W2) would be cheaper still. Failing that, the first contribution should be reworded as a comparison of checkpoints.

### W2: The experts are never compared on the same inputs, and step shares are weighted by dwell time
**Severity**: Major
**Evidence Anchor**: text: Section 4.6 "none compares the two experts on identical inputs, so none is a measure of propensity"
**Confidence**: 4 — estimand definition under state-dependent sampling; the feasibility judgement rests on the manuscript's description of its logs
The main finding concerns what the models plan, but every plan share is taken over the states each model reached, in units of logged steps. A stay-put plan keeps the vehicle at rest, so the next query sees almost the same state and the same stop is counted again, many times. Route-level pairing keeps the tests valid, but the quantity estimated is occupancy, not the probability of a stay-put plan given a situation, and the ratio of 14.00 % to 2.08 % should not be read as several times as often per decision. Speed conditioning and the gate-off run narrow the gap between the two readings without closing it, as the manuscript concedes. The direct measurement appears to be within reach of materials already in hand: replay one common set of low-speed states (pooled from both models' logs, or the low-speed samples of the shared 1,567-sample validation split) through each expert with many noise draws, and compare stay-put probabilities paired by state. The history-swap agent shows that plans can be obtained without being acted on. The same state set would also score additional seeds (W1) without simulator time. An episode-level outcome from existing logs would help as well, for example the time from reaching rest to the first plan of 2 m or more, analysed as a censored duration. The manuscript lists the replay as future work; I regard it as part of the evidence for the claim made now.

### W3: The H1 verdict depends on choices the record does not fix and on a confounded comparison
**Severity**: Major
**Evidence Anchor**: text: Supplementary Section S4.3 "the Holm-adjusted values are 0.0228, 0.0028, 0.0556 and 0.1587"
**Confidence**: 4 — multiplicity and signed-rank inference; the adjusted value I derive is inferred from printed values and should be checked by the authors
H1 is reported as met at p = 0.048, with an interval that includes zero. Four things make that verdict fragile. First, the p-value is a normal approximation on 34 non-zero pairs after 10 zero differences were dropped; a different treatment of zeros or an exact conditional test could move it across 0.05, and the manuscript does not state the decision rule committed for H1 (the rule for H2 required the interval to exclude zero). Second, the value printed for H1 in the earlier four-test family, 0.0228, equals three times 0.0076, the p-value against the original Base run, which the manuscript has set aside in favour of Base-Rerun. With the designated comparator (0.048) and the two margin-test p-values implied by the printed adjusted values (0.0278 and 0.1587), the Holm-adjusted value for H1 in that family would be about 0.096. The manuscript does not say when or why the family was reduced to two tests. Third, the treatment arm was evaluated on 17 to 18 October and Base-Rerun on 15 to 16 November, on either side of the harness change of 10 November. The manuscript discusses that change for H2 only, and H1 has no same-harness repeat; the 44-route Driving Score of one unchanged checkpoint moved by 7.40 points between passes, as much as the H1 effect. Fourth, on the 24 routes not used to tune the controller the gain is not established, as the manuscript reports. The authors could consider reporting H1 as inconclusive, stating its committed rule and the history of the family, giving the four-test value with the designated comparator, and either re-running the 1,600-sample balanced checkpoint on the current harness or removing the adjusted p-value from the abstract.

### W4: The blocked-time result rests on six or seven informative routes, an approximate test and a position-only match
**Severity**: Major
**Evidence Anchor**: text: Section 4.7 "The definition was committed after a per-episode listing of long stops had been seen and before any per-route value was computed."
**Confidence**: 4 — zero-inflated paired outcomes and small-sample signed-rank behaviour; the count of non-zero pairs is my inference from the stated software defaults
In the first pass, blocked time occurs on 6 routes for one model and 1 route for the other; on the remaining routes both values are zero. Under the software defaults stated in Supplementary Section S4.1, zero differences are dropped and a normal approximation is used whenever zeros are present, so the test of rule R3 is a normal approximation on at most seven pairs. The printed p = 0.028 is the value that approximation returns for six pairs of one sign; the exact two-sided value for that configuration is 0.031, the smallest the test can attain. The same 0.028 is printed for three different blocked-time contrasts, which is the signature of a very small discrete support. The verdict probably survives an exact test, but the inference is about a handful of scenario types, with a definition written after the long stops had been inspected, and the second-pass interval includes zero when the throttle threshold is 0.2. The bootstrap interval of a mean with about 38 structural zeros is also not reliable. Separately, the reading that blocked time follows from a contact and is not an additional cost goes beyond a match on position alone: a run counts as at a collision site if it starts within 10 m of a recorded position, on routes of the order of 100 m (Table 3 gives about 4 km of progress over 44 routes at about 80 % completion), every blocked route has at least one collision, no chance rate for such a match is given, and the manuscript itself says the temporal order cannot be established. The authors could consider an exact or permutation test with the number of non-zero pairs reported, a chance baseline for the position match (for example the match rate of long stops that are not blocked), and wording that says co-located with a recorded collision, without the claim about cost.

### W5: The history-swap outcome cannot discriminate the accounts it is meant to separate
**Severity**: Major
**Evidence Anchor**: text: Abstract "A test that replaced the ego-motion history showed no dependence on it."
**Confidence**: 3 — the argument is about what the outcome can identify, but it depends on how this action space behaves, which is near my stated blind spot
The primary outcome is the share of plans whose planned speed change is small, compared between the true history and an injected 4 m/s history. Because the expert outputs accelerations, two different accounts predict the same result on this outcome: that the controls ignore the history, and that the plan simply continues whatever motion the history reports. The label holds speed covers staying at rest in one condition and continuing at 4 m/s in the other, which are different behaviours with different base rates in driving data. The secondary outcome points the same way: under the moving history no plan ended at rest and decelerating plans stayed rare, in the very situations where the model otherwise stays put. A plan that followed the scene would be expected to brake there; a plan that continues the reported motion would not. The manuscript sets that result aside as following from the action space, but the same argument applies to the primary outcome. In addition the test has 8 and 7 routes, p = 0.38, a BCa interval at a sample size where its coverage is doubtful, and an input the model was never trained on. The body text is mostly careful (did not show), but the abstract states a null as a finding, and Section 4.11 concludes that the model issues such plans whatever the history says. The authors could consider restating the result as inconclusive in the abstract and conclusion, and redesigning the test with graded history speeds, an outcome defined relative to the scene (for example, braking when the true state is a stop behind an obstacle), and an image-side intervention for comparison, on the common state set of W2.

### W6: Mean-based intervals and rank-based tests disagree repeatedly, and the two passes are never analysed jointly
**Severity**: Minor
**Evidence Anchor**: text: Section 4.4 "The interval includes zero, so the second pass alone does not meet the rule of Section 4.3."
**Confidence**: 4 — paired non-parametric and bootstrap inference
The decision rules combine a BCa interval for the mean with a signed-rank p-value, and the two point in different directions in at least four places: H2 in the second pass (p = 0.0021, interval including zero), Driving Score on the two-pass mean (interval excluding zero, p = 0.11), the decoupling stay-put contrast against the balanced model (interval excluding zero, p = 0.15) and the gate-off contrasts at 0.5 and 1.0 m/s (intervals including zero, p = 0.045 and 0.025). They target different estimands, and the per-route distributions are heavy-tailed, censored by the 60 s rule and dominated by a few long stalls; the H2 interval also includes zero when standstill is measured in seconds. The authors could consider naming one estimand per endpoint, adding a paired permutation test of the mean and a robust location estimate, and analysing the two passes together with route as a random effect and pass as a factor, labelled post hoc.

### W7: The evaluated checkpoints are not listed among the deposited materials
**Severity**: Minor
**Evidence Anchor**: absence: Section 6 Data availability and Code availability statements — expected a statement that the fine-tuned action-expert weights of the evaluated checkpoints are deposited; checked Section 6, Section 3.4, Supplementary Section S3.4 and Table S1
**Confidence**: 4 — reproducibility requirements for single-checkpoint claims
Every inference is conditional on specific checkpoints, yet the availability statements name datasets, logs, trainer artifacts and scripts, not weights. Retraining with seed 42 need not reproduce them, the more so for the two runs that were interrupted and resumed. Inference noise is unseeded, so no run can be reproduced step for step. The authors could consider depositing the weights of all evaluated checkpoints and the controller file under its full hash, and seeding and logging the sampler noise in any further run. The pending archive identifier and commit hash are administrative and I do not count them here.

### W8: The abstract gives the repeat test more confirmatory weight than a same-checkpoint repeat can carry
**Severity**: Minor
**Evidence Anchor**: text: Abstract "where a pre-specified test was met"
**Confidence**: 4 — pre-specification practice
H3 was formed from the first pass of the same two checkpoints on the same routes, where the difference held on 42 of 44 routes, so its repeat was close to certain to succeed if the first pass was not noise. It establishes robustness to evaluation noise and nothing more, as the body text says. In the abstract the phrase stands without that qualifier, next to a main finding that was promoted above the originally pre-specified H2 after the results were known. The same applies to the Table 4 caption, which calls R2 and R3 pre-specified although their quantities were defined from first-pass data. The authors could consider a three-level label used consistently (pre-specified before any data of the comparison; repeat test on the same checkpoints; exploratory) and one table giving, for each analysis, the commit, its time and the data then in existence.

### W9: The decoupling arm infers similarity from non-rejection and sets one pass against two-pass means
**Severity**: Minor
**Evidence Anchor**: text: Section 4.10 "The comparator is the per-route mean of the two default-controller passes of each of the other two models."
**Confidence**: 3 — equivalence reasoning; I have not seen the committed rule of the addendum
The statement that the decoupling checkpoint planned like the balanced one is an equivalence statement made without a margin. It rests on an interval that includes zero for one plan measure and just excludes it for another, and it sets a single noisy pass against comparators whose noise has been halved. The share of the gap closed (90 %) is the more informative summary. The authors could consider stating a margin, or reporting the similarity as an estimate with its interval, and adding a second pass for this checkpoint.

## Arithmetic Receipts

### AR1
procedure_id: p_from_test_statistic
evidence_anchor: text: Supplementary Section S4.3, H2 paragraph "no zero differences, exact two-sided"
reported_inputs: Wilcoxon signed-rank W = 213, 44 routes, no zero differences, exact two-sided p = 0.00071
assumptions: none beyond the paper's statement that the test is a two-sided Wilcoxon signed-rank test with an exact p-value
derivation: the bounded procedure recomputes p from a t, z, F or chi-square statistic with its df; the reported p comes from the exact null distribution of the signed-rank statistic, which is outside that boundary, so no recomputation is made
derived_value_or_range: none inside the bounded procedure
comparison_rule: none applied
tail_convention: two-tailed
status: not_computable
not_computable_reason: nonstandard_p_procedure

### AR2
procedure_id: p_from_test_statistic
evidence_anchor: text: Supplementary Section S4.3, H2 paragraph, value in parentheses "asymptotic 0.00100"
reported_inputs: Wilcoxon signed-rank W = 213, 44 routes, no zero differences, asymptotic two-sided p = 0.00100
assumptions: none beyond the paper's statement that the asymptotic value is a normal approximation to the two-sided signed-rank test
derivation: the paper reports W and not the z statistic from which the asymptotic p is taken, and the bounded procedure does not include a conversion from W to z, so no recomputation is made
derived_value_or_range: none inside the bounded procedure
comparison_rule: none applied
tail_convention: two-tailed
status: not_computable
not_computable_reason: missing_reported_value

### AR3
procedure_id: p_from_test_statistic
evidence_anchor: text: Supplementary Section S4.3, H1 paragraph "10 zero differences, asymptotic p = 0.048"
reported_inputs: Wilcoxon signed-rank W = 182, 44 routes, 10 zero differences dropped, asymptotic two-sided p = 0.048
assumptions: none beyond the paper's statement that zero differences are dropped and a normal approximation is used when zeros are present
derivation: the paper reports W and not the z statistic from which the asymptotic p is taken, and the tie structure of the 34 non-zero differences is not reported; the bounded procedure does not include a conversion from W to z, so no recomputation is made
derived_value_or_range: none inside the bounded procedure
comparison_rule: none applied
tail_convention: two-tailed
status: not_computable
not_computable_reason: missing_reported_value

### AR4
procedure_id: grim
evidence_anchor: text: Section 4.10 "collision events per route (1.02, against 0.93 and 1.03)"
reported_inputs: mean collision events per route 1.02 for Decoupling-6400, two decimals, n = 44 routes, one evaluation pass, integer event counts per route, Table 3 prints 45 collision events for this model
assumptions: collision events are integer counts per route and the value is the unweighted mean over the 44 routes, both as the paper states; no rounding rule is stated, so round-to-nearest (half-up and half-even) and truncation are all checked
derivation: attainable means are k/44; 44 × 1.015 = 44.66 and 44 × 1.025 = 45.10, so k = 45 is the only integer in range and 45/44 = 1.02273; under truncation 44 × 1.02 = 44.88 and 44 × 1.03 = 45.32, again k = 45; this agrees with the 45 events of Table 3
derived_value_or_range: 45/44 = 1.02273, which is reported as 1.02 under every rounding rule checked
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under each candidate rounding rule
rounding_interval: 1.015 inclusive to 1.025 exclusive for round-to-nearest, and 1.02 inclusive to 1.03 exclusive for truncation
nearest_achievable: 44/44 = 1.00000 and 45/44 = 1.02273 straddle 1.02
status: consistent

### AR5
procedure_id: grim
evidence_anchor: text: Section 4.4, first value "collision events per route were 1.03 and 0.93"
reported_inputs: mean collision events per route 1.03 for Golden-6400 on the per-route mean of the two default-controller passes, two decimals, 44 routes and 2 passes, integer event counts per route and pass
assumptions: every route has both passes, as the paper states, so the mean of per-route two-pass means equals the unweighted mean of 88 integer counts; no rounding rule is stated, so round-to-nearest and truncation are all checked
derivation: attainable means are k/88; 88 × 1.025 = 90.20 and 88 × 1.035 = 91.08, so k = 91 and 91/88 = 1.03409; under truncation 88 × 1.03 = 90.64 and 88 × 1.04 = 91.52, again k = 91
derived_value_or_range: 91/88 = 1.03409, which is reported as 1.03 under every rounding rule checked
comparison_rule: some k/88 must fall inside the rounding interval of the reported two-decimal mean under each candidate rounding rule
rounding_interval: 1.025 inclusive to 1.035 exclusive for round-to-nearest, and 1.03 inclusive to 1.04 exclusive for truncation
nearest_achievable: 90/88 = 1.02273 and 91/88 = 1.03409 straddle 1.03
status: consistent

### AR6
procedure_id: grim
evidence_anchor: text: Section 4.9, second value "on the mean of both passes 1.03 and 0.93"
reported_inputs: mean collision events per route 0.93 for Flooded-6400 on the per-route mean of the two default-controller passes, two decimals, 44 routes and 2 passes, integer event counts per route and pass
assumptions: every route has both passes, as the paper states, so the mean of per-route two-pass means equals the unweighted mean of 88 integer counts; no rounding rule is stated, so round-to-nearest and truncation are all checked
derivation: attainable means are k/88; 88 × 0.925 = 81.40 and 88 × 0.935 = 82.28, so k = 82 and 82/88 = 0.93182; under truncation 88 × 0.93 = 81.84 and 88 × 0.94 = 82.72, again k = 82
derived_value_or_range: 82/88 = 0.93182, which is reported as 0.93 under every rounding rule checked
comparison_rule: some k/88 must fall inside the rounding interval of the reported two-decimal mean under each candidate rounding rule
rounding_interval: 0.925 inclusive to 0.935 exclusive for round-to-nearest, and 0.93 inclusive to 0.94 exclusive for truncation
nearest_achievable: 81/88 = 0.92045 and 82/88 = 0.93182 straddle 0.93
status: consistent

### AR7
procedure_id: grim
evidence_anchor: text: Section 4.9, first value "In the second pass the events per route were 1.07 and 1.05"
reported_inputs: mean collision events per route 1.07 for Golden-6400 in the second pass, two decimals, n = 44 routes, integer event counts per route
assumptions: collision events are integer counts per route and the value is the unweighted mean over the 44 routes, both as the paper states; no rounding rule is stated and none is assumed
derivation: attainable means are k/44; 44 × 1.065 = 46.86 and 44 × 1.075 = 47.30, so under round-to-nearest k = 47 and 47/44 = 1.06818; under truncation 44 × 1.07 = 47.08 and 44 × 1.08 = 47.52 contain no integer; the verdict therefore depends on the unstated rounding rule
derived_value_or_range: reachable as 47/44 = 1.06818 under round-to-nearest, unreachable under truncation
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under the paper's rounding rule, which is not stated
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR8
procedure_id: grim
evidence_anchor: text: Supplementary Section S4.9, second value "the events per route were 1.07 and 1.05"
reported_inputs: mean collision events per route 1.05 for Flooded-6400 in the second pass, two decimals, n = 44 routes, integer event counts per route
assumptions: collision events are integer counts per route and the value is the unweighted mean over the 44 routes, both as the paper states; no rounding rule is stated and none is assumed
derivation: attainable means are k/44; 44 × 1.045 = 45.98 and 44 × 1.055 = 46.42, so under round-to-nearest k = 46 and 46/44 = 1.04545; under truncation 44 × 1.05 = 46.20 and 44 × 1.06 = 46.64 contain no integer; the verdict therefore depends on the unstated rounding rule
derived_value_or_range: reachable as 46/44 = 1.04545 under round-to-nearest, unreachable under truncation
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under the paper's rounding rule, which is not stated
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR9
procedure_id: grim
evidence_anchor: text: Supplementary Section S4.7, first pass, first value "With the default controller the obstacle-heavy model had more stop episodes per route"
reported_inputs: mean stop episodes per route 5.23 for Flooded-6400 in the first pass, two decimals, n = 44 routes, integer episode counts per route
assumptions: stop episodes are integer counts per route and the value is the unweighted mean over the 44 routes, with no exclusion stated for this analysis; no rounding rule is stated and none is assumed
derivation: attainable means are k/44; 44 × 5.225 = 229.90 and 44 × 5.235 = 230.34, so under round-to-nearest k = 230 and 230/44 = 5.22727; under truncation 44 × 5.23 = 230.12 and 44 × 5.24 = 230.56 contain no integer; the verdict therefore depends on the unstated rounding rule
derived_value_or_range: reachable as 230/44 = 5.22727 under round-to-nearest, unreachable under truncation
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under the paper's rounding rule, which is not stated
status: not_computable
not_computable_reason: rounding_rule_ambiguous

### AR10
procedure_id: grim
evidence_anchor: text: Supplementary Section S4.7, first pass, second value "the obstacle-heavy model had more stop episodes per route"
reported_inputs: mean stop episodes per route 2.27 for Golden-6400 in the first pass, two decimals, n = 44 routes, integer episode counts per route
assumptions: stop episodes are integer counts per route and the value is the unweighted mean over the 44 routes, with no exclusion stated for this analysis; no rounding rule is stated, so round-to-nearest and truncation are all checked
derivation: attainable means are k/44; 44 × 2.265 = 99.66 and 44 × 2.275 = 100.10, so k = 100 and 100/44 = 2.27273; under truncation 44 × 2.27 = 99.88 and 44 × 2.28 = 100.32, again k = 100
derived_value_or_range: 100/44 = 2.27273, which is reported as 2.27 under every rounding rule checked
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under each candidate rounding rule
rounding_interval: 2.265 inclusive to 2.275 exclusive for round-to-nearest, and 2.27 inclusive to 2.28 exclusive for truncation
nearest_achievable: 99/44 = 2.25000 and 100/44 = 2.27273 straddle 2.27
status: consistent

### AR11
procedure_id: grim
evidence_anchor: text: Supplementary Section S4.7, second pass, first value "the obstacle-heavy model again had more stop episodes per route"
reported_inputs: mean stop episodes per route 5.36 for Flooded-6400 in the second pass, two decimals, n = 44 routes, integer episode counts per route
assumptions: stop episodes are integer counts per route and the value is the unweighted mean over the 44 routes, with no exclusion stated for this analysis; no rounding rule is stated, so round-to-nearest and truncation are all checked
derivation: attainable means are k/44; 44 × 5.355 = 235.62 and 44 × 5.365 = 236.06, so k = 236 and 236/44 = 5.36364; under truncation 44 × 5.36 = 235.84 and 44 × 5.37 = 236.28, again k = 236
derived_value_or_range: 236/44 = 5.36364, which is reported as 5.36 under every rounding rule checked
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under each candidate rounding rule
rounding_interval: 5.355 inclusive to 5.365 exclusive for round-to-nearest, and 5.36 inclusive to 5.37 exclusive for truncation
nearest_achievable: 235/44 = 5.34091 and 236/44 = 5.36364 straddle 5.36
status: consistent

### AR12
procedure_id: grim
evidence_anchor: text: Supplementary Section S4.7, second pass, second value "again had more stop episodes per route"
reported_inputs: mean stop episodes per route 1.89 for Golden-6400 in the second pass, two decimals, n = 44 routes, integer episode counts per route
assumptions: stop episodes are integer counts per route and the value is the unweighted mean over the 44 routes, with no exclusion stated for this analysis; no rounding rule is stated and none is assumed
derivation: attainable means are k/44; 44 × 1.885 = 82.94 and 44 × 1.895 = 83.38, so under round-to-nearest k = 83 and 83/44 = 1.88636; under truncation 44 × 1.89 = 83.16 and 44 × 1.90 = 83.60 contain no integer; the verdict therefore depends on the unstated rounding rule
derived_value_or_range: reachable as 83/44 = 1.88636 under round-to-nearest, unreachable under truncation
comparison_rule: some k/44 must fall inside the rounding interval of the reported two-decimal mean under the paper's rounding rule, which is not stated
status: not_computable
not_computable_reason: rounding_rule_ambiguous
