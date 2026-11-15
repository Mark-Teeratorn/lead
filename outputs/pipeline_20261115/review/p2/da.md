contract_role: da
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "a rival explanation is acknowledged without being tested"

The central argument holds as scoped. The two 6,400-sample checkpoints differ robustly in their closed-loop plans, under both controllers and in both passes, and the paper's own arithmetic is internally consistent. Four weaknesses (M1 to M4 below) each concern a rival reading or a framing that the paper names, or that its own numbers raise, without testing it. Each can be corrected by rewording or by a modest analysis of existing logs, so this is a warn rather than a block. M3 comes closest to the block threshold, because the logs could already separate its two readings.

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Calibration Status
`NOT_CALIBRATED`

### Criterion-Bound Judgements

No venue criteria are bound to this call (criteria_binding_unavailable). The criteria below are the contract dimension D3 and the eight challenge dimensions of the Devil's Advocate protocol. The judgements are not totalled, weighted or mapped to severity.

- D3 argumentative_coherence (contract). Judgement: PARTLY_MEETS. Anchor: table: Table 5, second-pass rows. Rationale: the pre-specified endpoint weakens on its own replication, and the thesis was rebuilt around plan-level measures. That rebuilding is coherent but leaves rivals untested (M1 to M3). Scope limit: one checkpoint per arm. Decision bearing: yes, it sets the D3 score.
- Challenge 1, core thesis. Judgement: PARTLY_MEETS. Anchor: table: Table 6, rows 1–3. Rationale: the plan-level contrast is large and stable across passes and controllers, but it is attributed to the mix and not to the checkpoint (M1). Scope limit: none identified beyond seeds. Decision bearing: yes.
- Challenge 2, evidence selection. Judgement: PARTLY_MEETS. Anchor: table: Table 4, Golden-1600 and Flooded-1600 rows. Rationale: the 1,600-sample pair is the only within-study check on generality, and it receives descriptive treatment only (m3). Scope limit: the 1,600-sample runs were resumed from checkpoints. Decision bearing: no, it supports M1.
- Challenge 3, confirmation bias. Judgement: PARTLY_MEETS. Anchor: text: §3.2 "It was formulated on 12 November 2026, after the primary result and the band decomposition of Section 4.5 were known". Rationale: the post hoc status is disclosed honestly, but the conjecture is still cited as consistent only where it fits (m2). Scope limit: none identified. Decision bearing: no.
- Challenge 4, logic chain. Judgement: PARTLY_MEETS. Anchor: text: §4.7 "The long stops of the balanced model are mostly not planned stops." Rationale: the step from command logs to blocked, and from blocked to cost, omits the temporal relation to contact (M3). Scope limit: no contact sensor. Decision bearing: yes.
- Challenge 5, overgeneralisation. Judgement: MEETS. Anchor: text: Title "A Matched-Pair, Single-Seed Study". Rationale: the title, the abstract and the limitations scope the claims to the pair; the residual overreach lies in causal verbs and normative terms (M1, M4). Scope limit: none identified. Decision bearing: no.
- Challenge 6, alternative paths. Judgement: PARTLY_MEETS. Anchor: text: §2 "We did not run a history-dropout baseline or a creep-rule controller". Rationale: the paper discloses that it cannot say how a data-side change compares with model-side or controller-side remedies. Scope limit: none identified. Decision bearing: no.
- Challenge 7, stakeholder blind spots. Judgement: MEETS. Anchor: text: Abstract "we make no safety claim". Rationale: the paper refrains from safety claims despite motivating with a safety case. Scope limit: none identified. Decision bearing: no.
- Challenge 8, so what. Judgement: PARTLY_MEETS. Anchor: text: §5 "The practical reading is narrow." Rationale: the practitioner consequence depends on whether the contrast belongs to the mixes (M1). If it belongs to one training run, the actionable content reduces to the measurement recommendation. Scope limit: none identified. Decision bearing: no.

### What the Paper Does Well

The record of what was specified before which values were seen is unusually explicit, and so are the deviations from it. Several earlier claims are withdrawn in the text rather than quietly dropped. The gate-off closed-loop run attacks the controller confound directly instead of arguing it away. The lateral-asymmetry rival is tested and comes out in the direction opposite to the training mix. The plan-at-rest analysis removes the artefact created by integrating the plan from the current speed. A braking-from-motion measure that was near zero by construction is withdrawn and replaced. No sentence in the manuscript addresses reviewers or an AI.

### Strongest Counter-Argument

A sceptic would say the paper has measured one unusual checkpoint, not an effect of data composition. Across the six evaluated models, `Golden-6400` is the outlier on every plan-level and command-level measure the paper reports:

- its pooled stay-put share at low speed is 2.3 %, against 14.6 % to 33.3 % for the other five;
- its share of plans braking to rest from motion is 0.82 %, against 1.50 % to 1.99 %;
- its gate activity is 3.73 % of steps, against 11.22 % to 20.06 %;
- its blocked time is 7.75 %, against at most 2.11 %.

`Flooded-6400`, by contrast, sits within or near the range of the other fine-tuned checkpoints. `Golden-1600` was trained on the exact first quarter of the same balanced data, yet it plans much like the obstacle-heavy models (16.4 % against 19.8 % for `Flooded-1600`). It does so although the two 1,600-sample sets differ in their conditional stay-put share almost as much as the 6,400-sample sets do. The balanced 6,400-sample model also plans to stay put at about a fifth of the rate in its own training data, the opposite of what the paper's sampling conjecture says a well-fitted expert does.

The most economical reading of the reported numbers is therefore that one training run (balanced data, 8,000 optimizer steps, seed 42) lost most of its stay-put mode. That checkpoint then keeps commanding throttle when it is blocked, which is where its blocked time, and possibly its lower two-pass Driving Score, come from. On that reading, data composition is just the label of the arm in which the anomaly happened to occur. The second pass confirms that the anomaly is stable under simulator noise, which is not in doubt for a roughly sevenfold ratio. Nothing in the paper says whether a second seed of either mix would reproduce the contrast. The paper scopes its claims to this matched pair, but its causal verb (the mix changed what the policy planned), its title and its practitioner framing all assume that the contrast belongs to the mixes and not to the run.

### Further Challenges (Minor)

- m1 (Minor). The words replicated and reproduced are used for a second closed-loop pass of the same two checkpoints. That pass guards against simulator noise, not against the training-run variance that the composition claim needs. Section 5 and the Conclusion place the word directly behind the composition claim, so a reader takes the second pass as support for it. Anchor: text: §5 "the fine-tuning data composition changed what the policy planned once it was slow, and the change was reproduced in a second pass". Confidence: 4 (wording read directly against the stated design).
- m2 (Minor). The sampling conjecture is cited as consistent with the matched pair and with the band decomposition, but its quantitative prediction fails. The prediction is a stay-put rate close to the conditional training share. None of the four models whose training share is known reproduces it: the balanced 1,600-sample model exceeds its share (16.4 % against 11.4 %), and the balanced 6,400-sample model falls to about a fifth of it (2.3 % against 10.9 %). The paper says the conjecture is untested and at most part of the explanation. The issue is therefore selective consistency in Sections 4.5 and 5, not a defect of the core claim. Anchor: text: §4.5 "This is the pattern the stay-put sampling conjecture of Section 3.2 describes." Confidence: 4 (arithmetic on the paper's own pooled shares and Table 1).
- m3 (Minor). The 1,600-sample pair is the only within-study test of whether the contrast generalises beyond one pair of checkpoints. For it, the paper reports only pooled descriptive plan shares and standstill bands, not the per-route paired comparison with BCa interval that it reports for every 6,400-sample plan measure. Reporting that comparison would make the rival in M1 partly testable with existing data. Anchor: absence: §4.6 and Table 6 — expected a per-route paired comparison of low-speed stay-put plans for Golden-1600 vs Flooded-1600 with a BCa interval; checked §4.6, Table 6, Table 4, §4.8, Figure 5 caption. Confidence: 4 (all plan-level passages read).
- m4 (Minor). The abstract presents the two-pass Driving Score difference as part of the cost reading. That difference is a single contrast with no rule fixed in advance (p = 0.11, interval barely excluding zero, unadjusted). In the first pass the difference was −3.24 (p = 0.64), and the paper itself reports intraclass correlations of 0.51 and 0.36 for Driving Score. The abstract gives this contrast more weight than the evidence carries. Anchor: text: Abstract "its two-pass Driving Score was 5.67 points lower (rank test p = 0.11)". Confidence: 4 (numbers read from Sections 4.3 and 4.4).
- m5 (Minor). The quantity under the strongest pre-specification (H3) is the least specific plan measure. It is the share of short plans over all steps, which mixes plan propensity with time spent slow and with the gate's holding feedback. The speed-conditioned shares used in the headline carry a weaker replication criterion. The ordering of the evidence does not match the ordering of the claims. Anchor: text: §4.6 "This share is taken over all steps, so it also reflects how much time each model spends slow". Confidence: 3 (depends on how the addendum criteria are weighted).
- m6 (Minor). The pre-specified endpoint (H2) weakened: it gives case B in the second pass and no detectable difference without the gate. The paper now calls a measure formed from first-pass data its main finding and calls total standstill a poor measure. The pre-specified second-pass test protects that choice against noise, but the headline was still chosen after seeing which measures held. This is disclosed, so it is a matter of emphasis. Anchor: text: §1 "plans; main finding, tested as a replication". Confidence: 3 (timing taken from the paper's own record).

### Ignored Alternative Explanations/Paths

1. Checkpoint idiosyncrasy. The matched-pair contrast is mostly a departure of `Golden-6400` from all other checkpoints, including the one trained on the same balanced data (M1, m3).
2. Different self-generated contexts. The obstacle-heavy model reaches more states in which staying is what the scene calls for, or in which the gate has just held it. Plan rates then differ without any difference in propensity on the same input (M2).
3. Post-contact pushing. Blocked time follows contact and is the same plan difference seen after a collision, not an independent cost (M3).
4. Training length interacting with mix. The contrast appears only at 8,000 optimizer steps. Longer training on the balanced set may sharpen the start mode beyond the data's share, a fitting effect rather than a composition effect. The 2 × 2 design cannot separate this from dataset size, as the paper notes.

### Missing Stakeholder Perspectives

- A safety assessor's view of whether holding, or pushing, on the six blocked routes is the safer failure. The introduction invokes this view through the safety case.
- Other road users exposed to a vehicle that commands throttle while stationary after contact.

### Unexamined Premise

The paper treats the standstill gate as a nuisance whose removal reveals the model-side difference. But there is no neutral controller. The gate-off controller is itself a design choice, made after the primary result, and every plan measure is logged in states that the controller in the loop helped produce. A model-level difference is therefore always relative to some controller. The paper says this about standstill, but not about the plan measures it calls model-level.

### Observations (Non-Defects)

- Three pending results bear on different claims. The decoupling model bears on which factor of the bundle carries the effect, and so on the stationary-share reading of the conjecture. The motion-history swap test bears on the mechanism, including the Discussion's reading that the difference concerns how often the model issues a start. Base-Rerun bears only on H1, which no longer carries the thesis. Anchor: text: §5 "until it is reported we do not claim that mechanism". Confidence: 4.
- The archive DOI, the code commit hash and the authors' responsibility statement for AI assistance are pending. These concern reproducibility and integrity, which other seats assess.

No finding meets the singleton-Critical bar. Every rival above leaves standing the scoped core claim, that these two checkpoints differ in their closed-loop plans. Each can be addressed by narrowed wording or by analysis of existing logs.

### Issue List

#### CRITICAL
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|

#### MAJOR
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| M1 | D3 | The headline causal claim, that the mix changed what the policy planned, rests on one checkpoint per arm, and the paper's other checkpoints do not order by mix. Golden-6400 is the outlier among all six models on stay-put plans (2.3 % pooled, against 14.6 % to 33.3 %), on braking plans from motion (0.82 %, against 1.50 % to 1.99 %), on gate activity and on blocked time. Flooded-6400 sits near the other fine-tuned models, and Golden-1600, trained on the first quarter of the same balanced data, plans like the obstacle-heavy models. A training-run idiosyncrasy of Golden-6400 explains the matched-pair contrast at least as well as composition. The paper acknowledges one seed as a generic limitation but never confronts this pattern. Minimum remedy: restate the causal verbs in the title, the Section 1 findings, Section 5 and the Conclusion as a contrast between two checkpoints, and state the outlier pattern there. Stronger remedy: further seeds of the 6,400-sample pair. | text: §4.6 "the shares are not reproduced: the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | 4 (direct reading of the paper's six-model numbers) | — | — |
| M2 | D3 | The plan-level rates on which the main finding rests are closed-loop rates in states that each model generated for itself. Conditioning on speed and on being at rest removes the artefact of integrating from the current speed, but not differences in scene (queue, signal, obstacle ahead, after contact). The only scene-side control is an unvalidated keyword classifier applied to the frozen backbone's text. The paper names this rival but does not test it. The direct test it describes itself, querying both experts on the same logged low-speed states, would separate a difference in propensity from a difference in context if those inputs are recoverable. Until then, the phrase what the policy planned once it was slow reads as a propensity claim that the design does not identify. Remedy: a same-input comparison on logged states, or rewording to closed-loop rates. | text: §4.6 "The two models visit different states in closed loop, so this is not a same-input comparison." | 3 (depends on what the step logs contain) | — | — |
| M3 | D3 | The cost half of the thesis (Less hesitation has a cost; contribution iii) rests on blocked time. Blocked time occurs only on routes with a collision event, on six routes for Golden-6400 with the default controller, and is inferred from the command log. The paper does not report whether blocked runs begin before or after the collision on those routes. If they follow contact, blocked time is the post-contact form of the same plan difference: a model that rarely plans to stay keeps commanding throttle against an obstacle. It is then not a separate cost, collision counts did not differ, and the trade-off counts one behavioural difference twice. The logged event timing would separate the two readings. Remedy: report when each blocked run starts relative to the nearest collision event, and restate the cost accordingly. | text: §4.7 "Every route with blocked time has at least one collision event" | 3 (inference from the stated definition and co-occurrence; timing not reported) | — | — |
| M4 | D3 | The title and the findings in Sections 1 and 5 call the obstacle-heavy model's stay-put plans hesitation. The term presupposes that the stops were unnecessary, yet the paper states that it cannot classify any stop as required or not. On the six routes where the balanced model is blocked, the obstacle-heavy model stops and holds instead, which may be the more appropriate response, and the gap-waiting analysis cannot separate correct waiting from freezing. The normative term therefore carries a conclusion the evidence does not reach, and Less hesitation has a cost turns a measured difference in rates into a value judgement. Remedy: use a descriptive term (for example stay-put planning rate) in the title and the findings, or add the required-stop classification that the paper lists as future work. | text: §4.8 "the bridge does not log signal state, actor distances or conflict-zone occupancy, so we cannot tell when stopping was required" | 3 (framing judgement grounded in the paper's own disclaimer) | — | — |
