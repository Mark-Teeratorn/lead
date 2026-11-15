# Phase 2 Review Card: Journal-Fit Reviewer

contract_role: eic
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: warn
trigger: "Localised clarity or presentation problems that slow the reader but leave the content recoverable"

Basis: the line from hypotheses to results to conclusion can be followed and every central number is in a table, but the manuscript carries unresolved placeholders in the abstract, conclusion and front-matter statements, all five figures are placeholders, revision-history remnants run through the body, and Table 4 and the abstract are overloaded (W2, W6, W7, W8).

### D6: venue_fit_and_contribution
score: block
trigger: "the claimed significance materially exceeds what the evidence can bear"
block_class: repairable

Basis: the title, abstract and contribution list attribute the plan-level difference to the fine-tuning mix, but each mix is represented by one checkpoint, and the paper's own six-checkpoint data show that the balanced 6,400-sample checkpoint differs from all five others, including the balanced 1,600-sample one, by about as much as it differs from its matched comparator. Pending results and an uncitable pre-specification record add to this (W1, W2, W3). It can be repaired, either by training more seeds or by reframing the claim as a difference between two checkpoints; no venue-alignment claim is made (`criteria_binding_unavailable`).

## Review Body

### Reviewer Identity
Associate editor at a robotics and intelligent-vehicles journal who handles learning-based driving submissions and has run closed-loop CARLA evaluation tracks. Field-general judgement at the level of a Q2 journal; this call is not bound to a venue, so I make no claim about fit to any particular outlet.

### Calibration Status
`NOT_CALIBRATED`

### Summary Assessment
The manuscript fine-tunes the flow-matching action expert of Alpamayo 1.5 on two deliberately composed mixes drawn from one pool of CARLA expert data: a balanced mix and an obstacle-heavy mix with a larger share of stationary samples. Each is built at 1,600 and 6,400 samples, with one seed per condition. The models are evaluated in closed loop on 44 Bench2Drive routes. For the 6,400-sample pair it reports two passes with the default controller and one pass without the controller's standstill gate, and it analyses the logged plan of every step. The best-supported result concerns plans: the obstacle-heavy checkpoint plans to stay put far more often at low speed, with and without the gate and in both passes, and the second-pass test (H3) was fixed before its values were computed. Total standstill time, the originally pre-specified endpoint, differs only with the gate. The balanced checkpoint instead accumulates "blocked" time, and its Driving Score is not higher.

The reporting is unusually candid. It discloses when each analysis was written down, withdraws earlier claims and scopes the safety language carefully. The practical lesson that standstill fraction confounds model and controller is useful to the field. The main editorial problem is attribution. With one checkpoint per mix, and with the balanced 6,400-sample checkpoint standing apart from every other checkpoint in the study, the evidence supports "these two checkpoints differ" more firmly than "the mix changed the policy". A secondary problem is readiness: H1, the decoupling model, the figures and several required statements are still pending. The core observation survives either outcome of the pending results, but the paper as it stands is not ready for acceptance.

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D5 writing_and_structure | contract D5; Phase 1 scoring plan | PARTLY_MEETS | see W2, W6, W7, W8 | Content is recoverable from text and tables, but placeholders, missing figures, revision remnants and overloaded tables slow the reader | Figures not seen; judged from captions only | yes: requires a presentation revision before acceptance |
| D6 venue_fit_and_contribution (field-general half only) | contract D6; Phase 1 scoring plan; `criteria_binding_unavailable` | DOES_NOT_MEET as presented | see W1, W2, W3 | The causal attribution to data composition exceeds a one-checkpoint-per-arm design whose own comparison checkpoints show spread of similar size | No venue criteria bound; statistical detail is outside my remit | yes: repairable by new seeds or reframing |

### S1: Exemplary disclosure of when each analysis was fixed
Section 4.1 lists, for every analysis group, whether it was written down before or after its values were seen. It records partial looks at the data and says which analyses have no addendum entry. Few submissions in this area give readers this much to calibrate their trust.
**Evidence Anchor**: text: §4.1 Record of pre-specification "No decision rule was changed after any of these looks"

### S2: A transferable measurement lesson that separates model from controller
The comparison of plan-level and motion-level measures under the default and gate-off controllers shows that the total-standstill endpoint flips sign once the gate is removed, while the plan-level gap persists. The recommendation to report standstill split by command and alongside collisions is the part of the paper most likely to matter beyond this one policy.
**Evidence Anchor**: table: Table 6, all rows across the three controller and pass columns

### S3: The main plan-level result replicated across closed-loop passes under a rule fixed in advance
H3 was fixed before any plan-level value of the second pass was computed, and the second-pass result had an interval well away from zero (lower on 41 of 44 routes). The rules for blocked time and for standstill outside blocked time (R2, R3) were also met.
**Evidence Anchor**: text: §4.3 H3 paragraph "H3 is met."

### S4: Matched dataset construction from one pool, with the datasets released
Both mixes are drawn deterministically from one verified pool, each 1,600-sample set is nested within its 6,400-sample set, the overlap with the evaluation routes is quantified per set, and the five datasets are public with composition cards. This makes the composition contrast reproducible at the data level.
**Evidence Anchor**: table: Table 1, rows Source pool through Hugging Face dataset

### S5: Proportionate safety and benchmark language
The paper declines to make a safety claim from about 4 km of driving per model, states that it is not powered for equivalence, and reports that the lower-standstill model did not have a higher Driving Score.
**Evidence Anchor**: text: §4.9 "With about 4 km of driving per model, the study is not powered to show that the rates are equal"

### W1: The plan-level difference is attributed to the mix, but one checkpoint per mix cannot separate the mix from the training run
The abstract ("In this matched pair the mix changed what the policy planned once it was slow"), the first finding in Section 1, contribution (i) and the title all frame the result as an effect of the fine-tuning data composition. The paper's own six-checkpoint data point to another reading. Pooled stay-put shares at low speed are 33.3 % (`Base`), 19.8 % and 16.4 % (the two 1,600-sample models), 14.6 % (`Flooded-6400-Hist`), 24.9 % (`Flooded-6400`) and 2.3 % (`Golden-6400`). `Golden-6400` is also the low outlier for braking plans from motion and the high outlier for blocked time (7.75 % against at most 2.11 %). At 1,600 samples, where the conditional stay-put shares of the training sets differ almost as much, no difference was detected. And `Golden-6400` plans to stay put at about one fifth of its own training share, the opposite of what the sampling conjecture of Section 3.2 predicts. The most economical description of the data is that one checkpoint, `Golden-6400`, differs from the other five. With one seed per arm, the reader cannot tell whether that is the mix or this training run. The paper acknowledges the single seed (Limitation 1 and the title), but the headline still states a causal attribution to composition, and a Q2 readership will take it as one.
Minimum remedy: reword the title, abstract, Section 1 findings and contributions, and the Conclusion so that the claim concerns the two checkpoints. State plainly that `Golden-6400` is distinct from all five other checkpoints, and bring the six-model comparison forward as the context for the matched-pair result. Stronger option: train at least two further seeds of each 6,400-sample arm (Table 2 implies about 28 h of A100 time per run) and evaluate one pass each. If the plan-level gap holds across seeds, the composition claim becomes publishable as stated; if it does not, the measurement contribution (S2) still stands.
**Severity**: Major
**Evidence Anchor**: text: §4.6 Plans at low speed, pooled paragraph "the balanced model at 6,400 samples plans to stay put far less often than its own training data do"
**Confidence**: 4 (framing judgement from reported numbers; the statistical treatment of seed variance is the methodology seat's remit)

### W2: Results and required statements are still pending, including in the abstract and conclusion
The abstract ends with two placeholders and the Conclusion with one. H1 has no result against its specified comparator (`Base-Rerun`): Tables 2 to 4 carry empty rows, and §4.3 and the 24-route comparison are incomplete. The decoupling model, already trained, is unreported, and so is the motion-history swap test. The archive DOI, the code commit hash, the CRediT, funding and competing-interest statements, and the authors' AI-verification statement are all missing. Judged against what is in hand, the main message survives either outcome. H1 is peripheral to the plan-level finding, and the swap test bears only on a mechanism the paper explicitly does not claim. The decoupling result is different: it bears directly on how the composition effect is read (W1, Limitation 2) and may require Discussion text to be rewritten. A manuscript with unresolved placeholders in its abstract cannot be accepted.
Remedy: complete the three pending analyses, write the abstract and Conclusion sentences from their results, and supply every statement before resubmission. If the decoupling result is not ready, remove its forward references, not leave placeholders.
**Severity**: Major
**Evidence Anchor**: text: §5 Limitation 7 "so H1 awaits the re-run"
**Confidence**: 5 (directly observable in the manuscript)

### W3: The pre-specification record that carries the confirmatory claims cannot be cited or checked by a reader
The status of H3, R2, R3 and the §10 replication criterion as tests fixed in advance rests on "ANALYSIS_ADDENDUM §n", which is cited more than twenty times. The addendum is not in the reference list or the availability statements; the code commit hash is pending; and the paper says the commit times were not time-stamped by a third party. A reader therefore cannot verify the confirmatory framing that the paper relies on to rank H3 as its main finding. The AI-assistance disclosure adds that generative tools were used to propose and word these decision rules, which raises the importance of an inspectable record.
Remedy: deposit the addendum as citable supplementary material, with the commit hash and commit time for each section, and reference it formally. Consider an external timestamp for the archive.
**Severity**: Major
**Evidence Anchor**: absence: reference list and Data and Code availability statements — expected a citable, persistent copy of ANALYSIS_ADDENDUM with per-section commit identifiers; checked references 1 to 47, Data availability, Code availability, §4.1 Record of pre-specification
**Confidence**: 4 (the existence and content of the addendum are outside what I was given)

### W4: "Replicated" describes a re-run of the same checkpoints, which readers may take for replication of the composition effect
The second pass re-evaluates the same two checkpoints on the same 44 routes. It shows that the plan-level difference is stable across closed-loop runs, not across training runs, routes or mixes. Section 5 and the Conclusion use "reproduced" and "replicated" without that qualifier.
Remedy: say "reproduced across a second closed-loop pass of the same checkpoints" wherever the word appears.
**Severity**: Minor
**Evidence Anchor**: text: §5 opening paragraph "the change was reproduced in a second pass under rules fixed in advance"
**Confidence**: 4 (wording judgement)

### W5: The "cost" headline rests on a post hoc, command-inferred quantity and a Driving Score difference the test does not support
"Less hesitation has a cost" is a bold first-level finding. The cost consists of blocked time and a Driving Score that is not higher. Blocked time is inferred from the command log; its definition was written after a per-episode listing had been seen; and its second-pass replication depends on the throttle threshold. The two-pass Driving Score difference has p = 0.11. The more defensible framing is the paper's own Discussion wording, that less hesitation did not translate into a better benchmark result.
Remedy: soften the Section 1 bullet and contribution (iii) to match the Discussion.
**Severity**: Minor
**Evidence Anchor**: text: §1 third finding "Less hesitation has a cost."
**Confidence**: 4 (framing judgement)

### W6: All five figures are placeholders
Figures 1 to 5 exist only as bracketed captions. Figure 4 (gate-off standstill with blocked time) and Figure 5 (low-speed plan mix across six models) would carry the paper's argument most directly for non-specialist readers. Their quality and their consistency with the text cannot be assessed. The tables preserve the numbers, so no core claim changes.
Remedy: render all figures. Figure 5b, with the training-set share marked, is especially useful for the reading in W1.
**Severity**: Minor
**Evidence Anchor**: absence: §3.4, §4.2, §4.5 and §4.6 figure positions — expected rendered Figures 1 to 5; checked the five FIGURE caption markers and the Table 3 to 6 captions
**Confidence**: 5 (directly observable)

### W7: Revision-history remnants and response-letter material sit in the body text
The body contains numerous statements addressed to a previous round, such as withdrawn arguments, corrected settings, renamed terms, withdrawn crash-rate statements, a withdrawn 10-route subset and a never-committed script. They belong in the response letter. In the article they distract the reader and date the text.
Remedy: remove them from the manuscript and keep them in the response to reviewers; keep only the corrections a reader of the final article needs.
**Severity**: Minor
**Evidence Anchor**: text: §3.2 "The previous version of this manuscript argued the opposite; that argument treated the flow as a regressor and is withdrawn."
**Confidence**: 5 (directly observable)

### W8: Density and table width impede readers outside the subfield
The abstract packs in roughly twenty numerical results. Table 4 has 19 columns, mixing a decomposition with strata. Section 4 reports dozens of unadjusted intervals in running prose. At about 15,000 words, the paper's main line (plan-level difference, controller dependence, blocked-time offset) is harder to extract than it needs to be.
Remedy: limit the abstract to the headline numbers. Split Table 4 into a decomposition table and a strata table, moving the strata to the supplement. Move the secondary sensitivity prose of Sections 4.6 to 4.8 into supplementary tables.
**Severity**: Minor
**Evidence Anchor**: table: Table 4, standstill decomposition and frozen strata (19 columns)
**Confidence**: 4 (presentation judgement)

### W9: Contribution (iv) is engineering integration rather than a research contribution
The single-GPU serving setup integrates prior work, as the paper itself states. Presenting it beside the scientific contributions inflates the contribution list.
Remedy: move it to a reproducibility or availability paragraph.
**Severity**: Minor
**Evidence Anchor**: text: §1 contributions paragraph "an open setup in which a 10B-parameter VLA policy, fine-tuned on an A100 machine"
**Confidence**: 4 (positioning judgement)

### W10: The AI-assistance disclosure lacks the authors' statement of verification and responsibility
The disclosure reports extensive use of generative tools, including for analysis scripts, decision rules and text, and the authors' verification statement is still a placeholder. Journals at this level will require it before acceptance.
Remedy: supply a statement describing how the authors verified the scripts, the decision rules and the reported numbers.
**Severity**: Minor
**Evidence Anchor**: text: §6 AI assistance disclosure "Most commits of the revision were made with AI assistance."
**Confidence**: 5 (directly observable)

### Detailed Comments

#### Journal Fit
No venue is bound to this call, so I make no fit claim. In field-general terms, the topic (data composition and low-speed behaviour of a flow-matching VLA driving policy in closed loop) is timely for robotics and intelligent-vehicle readerships. A measurement study with no new method can be a sufficient contribution at Q2 level if its central attribution is secure; at present it is not (W1).

#### Originality
The positioning against data-mixture work [35, 36, 46], driving data rebalancing [33, 38, 39], inertia and copycat remedies [12, 25, 27, 28] and the earlier report of this model stalling in CARLA [34] is adequate. The novelty claimed is a controlled composition change measured at the plan level with the controller's share separated, and it is distinguishable from that prior work.

#### Significance
The controller-separation lesson (S2) is the most generalisable result. The composition claim would be significant if it held across seeds; as it stands, its generality is limited to one policy, one simulator, 44 routes, a controller tuned on 20 of them, and a null result at 1,600 samples.

#### Structural Coherence
The hypotheses are reported in order of weight (H3, H2, H1), not by number. This is defensible, but it should be signposted where the hypotheses are introduced as well as in §4.3. The Discussion and Conclusion follow the results and avoid over-promising on safety. The over-reach lies in the attribution (W1) and the "cost" framing (W5). The manuscript visibly withdraws several earlier claims; I cannot check those withdrawals against the earlier review, which I was not given.

#### Title & Abstract
Putting "Matched-Pair, Single-Seed" in the title is good scoping. The abstract is too dense (W8), ends in placeholders (W2) and states the attribution causally (W1).

#### Conclusion
The Conclusion matches the body numerically and keeps the safety disclaimer, but it inherits the causal phrasing ("the mix changed what the policy plans") and a pending H1 sentence.

### Questions for Authors
1. Does the plan-level gap at 6,400 samples hold for a second seed of each arm? If no further training is possible, how do you separate the effect of the mix from that of the training run, given that `Golden-6400` is distinct from all five other checkpoints?
2. Why does `Golden-6400` plan to stay put at low speed far below its own training share (2.3 % against 10.9 %), when `Golden-1600` does not? Is a difference in fit at 8,000 optimizer steps the leading explanation?
3. Will the analysis addendum be deposited as citable supplementary material, with per-section commit identifiers?
4. If the decoupling model resembles `Golden-6400`, `Flooded-6400`, or neither, how would each outcome change the Discussion?

### Minor Issues
- Section 4.6 reports p-values as "1.1 × 10^{-8}" in plain text in some places and in math notation in others; make the notation consistent.
- Table 2 gives evaluation dates in local time and training times in UTC; state both in one convention.
- Section 3.4 states that no controller threshold is configurable, yet a gate-off variant was run; say how the variant was produced, for example as a separate hashed file.

### Preliminary Signal
Major Revision (preliminary journal-fit signal for the synthesizer; the decision rests with the synthesizer). The core observation survives either outcome of the pending results. Acceptance would require the attribution to be secured or reframed (W1), the pending items to be completed (W2), and the pre-specification record to be made citable (W3).
