# Editorial Decision Package

## Sprint Contract Audit (v3.6.2 Sprint Contract Synthesizer Protocol)

Contract: `reviewer/reviewer_full/v2`, mode `reviewer_full`, `panel_size` 5. Five usable Phase 2 cards in dispatch order: `eic`, `methodology`, `domain`, `perspective`, `da`. No panel shrinkage.

dimension_verdicts: [D1=block, D2=block, D3=warn, D4=warn, D5=warn, D6=warn]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

The Devil's Advocate's CRITICAL table (da.md, `#### CRITICAL`) has a header and no rows, so there are no DA CRITICAL IDs to adjudicate. The adjudication list is therefore empty and no rejection-rationale line is required.

### Step 1: Role-scoped scoring matrix

Only assessed scores from seats listed in a dimension's `eligible_roles` are counted. Every other cell is `not_assessed` in the cards and enters neither numerator nor denominator. Scores are copied from the cards on the contract's own scale (`judgement_scale: sprint_contract`); none is translated to another scale.

| Dimension | Priority | Eligible roles | Assessed eligible scores | Fatal declared | Verdict (worst assessed) |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology = block (`block_class: repairable`) | no | block |
| D2 domain_accuracy | mandatory | domain | domain = block (`block_class: repairable`) | no | block |
| D3 argumentative_coherence | mandatory | da, methodology | da = warn; methodology = warn | no | warn |
| D4 cross_disciplinary_relevance | high | perspective | perspective = warn | no | warn |
| D5 writing_and_structure | normal | eic | eic = warn | no | warn |
| D6 venue_fit_and_contribution | mandatory | eic | eic = warn | no | warn |

Every dimension has at least one assessed eligible seat, so no dimension is unassessed. No ineligible seat scored any dimension.

### Step 2: Failure-condition evaluation

All six expressions parse against the recognised vocabulary (F1 pattern 6, F2 pattern 1, F3 pattern 2, F4 pattern 1, F5 pattern 7, F0 pattern 9).

| Condition | Severity | Quantifier | Expression | Evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | Both blocks (D1, D2) are declared repairable; no seat declared a fatal block | false |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1: methodology = block (1 of 1). D2: domain = block (1 of 1) | true |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | D1: n = 1, owner at block, true. D2: n = 1, owner at block, true. D3: n = 2, both seats at warn, true. D6: n = 1, owner at warn, true. Four of four mandatory dimensions, threshold two | true |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4: perspective = warn | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | All six dimensions are at warn or worse | true |
| F0 | 10 | all | every dimension scores 'pass' | No dimension is at pass | false |

### Step 3: Precedence

Three conditions fired: F2 (90), F3 (70) and F5 (40). The highest severity is F2, whose action is major revision. F3 carries the same action. The DA-CRITICAL-versus-accept marker does not apply: the decision is not accept and the DA has no CRITICAL IDs.

### Binding conformance (unbound run)

The call is not bound to a venue (`criteria_binding_unavailable`). Four cards disclose this in words: eic.md ("No venue criteria are bound to this call, so I make no venue-fit statement"), methodology.md ("the call has no venue binding"), domain.md and perspective.md ("The call is not bound to a venue"). **Flag for the orchestrator:** da.md contains no statement on binding, and no card uses the literal token. No card makes a venue-alignment claim, and this package makes none. The synthesizer does not edit cards. Binding conformance is not a score, a failure condition or a verdict, and it does not enter the arithmetic above.

### Cross-model decision check

`ARS_CROSS_MODEL` is not set in this run, so the optional blind cross-model check (#518) was not performed and no handoff envelope is emitted.

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

[Current runtime boundary: do not upgrade this package from a candidate or prose-named profile. `PROFILE_MEASURED` remains unavailable until a closed profile artifact and replay validator bind the exact target fields to the actual completed-panel `execution_topology_sha256`.]

The eic, domain, perspective and da cards state `NOT_CALIBRATED`. The methodology card carries no calibration statement; it is treated as `NOT_CALIBRATED` at emission, as every seat is, and the omission is flagged for the orchestrator.

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Learning to Wait: Fine-Tuning Data Composition and the Stay-Put Plans of a Vision-Language-Action Driving Policy". No venue is bound to this review, so the standard applied is that of a Q2-level journal in the field, and this letter makes no claim about fit to any particular outlet. Your manuscript was reviewed through five role-separated review seats: a Journal-Fit Reviewer (EIC), Methodology, Domain, Perspective and the Devil's Advocate (DA). Their execution provenance is reported below and is not reduced to a binary independence claim. In this letter the seats are named by role; `R<n>` and `S<n>` denote roadmap items, not reviewers.

### Review Panel Provenance (#540/#740)

The dispatching layer supplied no `review-panel-provenance/1.0` artifact with this synthesis input, so its carrier cannot be verified. **Provenance artifact failure: missing.** The carrier is recorded in the closed invalid/unknown state.

| Axis | Value |
|---|---|
| role_separated | unknown |
| fresh_context (scope `within_panel_attempt_only`) | unknown |
| blind_to_peer_outputs | unknown |
| model_family_distinct | unknown |
| provider_distinct | unknown |
| human_distinct | unknown |

Correlated-error disclosure: the dispatch brief states that the five seats were run by one model family. Errors of the seats may therefore be correlated, and agreement among them is not independent confirmation. The consensus labels below count positions taken in the cards and carry no more weight than that.

### Decision: Major Revision

The decision is the mechanical result of the contract (F2, with F3 and F5 also fired). All experiments are reported as complete; the remaining `[[PENDING: …]]` placeholders are administrative items for the authors to supply, except the two noted in S9.

### Consensus Analysis

Consensus is counted per sub-claim over the four non-DA seats (Journal-Fit, Methodology, Domain, Perspective). A seat that did not speak to a sub-claim is silent, not in agreement. DA findings are reported beside the count and never enter it. The full inventory is in the appendix.

#### Points of Agreement (Consensus)

- [CONSENSUS-4] **SC-2. The title and contribution (i) attribute the difference to data composition; the design supports a statement about checkpoints.** Journal-Fit W2, Methodology W1 and Domain W2 raise it at Major band; Perspective W3 corroborates it inside a Minor-band weakness whose main subject is the purposive verbs ("'Learning' adds a causal reading of data composition that one seed per mix and the absent difference at 1,600 samples do not carry"). DA M1 makes the same point. All four seats and the DA name the same minimum remedy: word the title and contribution (i) at the level of checkpoints. No seat makes further training seeds a condition. Journal-Fit W2 leaves them "at the authors' choice", Methodology W1 writes "could consider" and "failing that" rewording, and DA M1 calls them "stronger and costlier".
- No sub-claim reached [CONSENSUS-3].
- Corroborated findings (two of four seats, no conflict; not a consensus label):
  - SC-1, direction of the effect against the unadapted policy (Journal-Fit W1, Domain W2; also DA lesser point 4).
  - SC-19, the history-swap result cannot discriminate the accounts it is used to separate and the abstract states a null as a finding (Methodology W5, Domain W1; also DA M4).
  - SC-10, the decoupling set is not described in Table 1 (Journal-Fit W9, Domain W7; also DA M2).
  - SC-17, the position match between blocked runs and collisions has no chance baseline and no time order (Methodology W4, Perspective W2).
  - SC-3, the evaluation-practice result is one sentence (Journal-Fit W3, Perspective W5).
  - SC-7, near-synonymous terms and thresholds (Journal-Fit W7, Perspective W7).
  - SC-9, the headline statistic and the tested statistic differ and the abstract does not say so (Journal-Fit W8, Perspective W7).
  - SC-11, one quantity under two aggregations, 14.00 % and 24.9 % (Journal-Fit W10, Perspective W7; also DA lesser point 5).
  - SC-21, the evaluated checkpoint weights are not among the deposited materials (Methodology W7, Perspective W6).
  - SC-27, the replanning rate is not stated (Domain W6, Perspective W7).
  - SC-33, "wait", "waited" and "pushed" name a purpose the logs cannot establish (Perspective W3; Domain review body, "Argument accuracy", and W2).
  - SC-12 and SC-13, unconfirmed facts in content positions and over-wide tables (Journal-Fit W11 and W12; Perspective, unnumbered Minor Issues).
- All other sub-claims are single-seat findings. They are kept and assessed on their anchored evidence.
- Points on which the cards agree in the manuscript's favour, and which no roadmap item asks the authors to change: the descriptive core (two 6,400-sample checkpoints differ several-fold in low-speed stay-put plans across three evaluations), the separation of model and controller by a gate-off run, the disclosure of when each rule was fixed, the reporting of results against the authors' own framing, and the absence of a trade-off curve or a "remedy" label (Journal-Fit S2, S3; Methodology S1 to S4; Domain S1, S4, S5; Perspective S3 to S5; DA "What the manuscript does well").

#### Points of Disagreement

- **SC-14. Severity and remedy for the missing same-input comparison [SPLIT].** Methodology W2 (Major) holds that every plan share is taken over states each model reached, in units of logged steps, so the quantity is occupancy and not the probability of a stay-put plan given a situation, and it regards a same-input replay "as part of the evidence for the claim made now". Domain W5 (Minor) agrees on the problem and asks for medians, per-episode onset rates and, if frames were logged, the replay, as "the addition that would most strengthen the paper". DA M5 (Major, outside the count) gives two ways out: run the comparison on a subset of routes, or keep the model-level wording out of headings and conclusions.
  - **Editor's Resolution**: Major, `must_fix` (R4). Rationale: what a rate estimates is a question of estimand, which lies in the methodology seat's field, and all three cards cite the same sentence of Section 4.6 against the Discussion's "model-level difference". On the remedy the cards do not agree that a new experiment is mandatory, so R4 can be closed in either of two ways: (a) the same-input comparison is run and reported, or (b) the model-level and per-decision reading is withdrawn from the abstract, headings, Discussion and Conclusion and episode-level rates from the existing logs are added. Unresolved dissent, stated openly: the cards do not settle whether route (b) alone clears the D1 block. The methodology card's wording indicates that the claim as now made needs route (a). This is for the re-review to judge.
- **SC-18. Severity of the reading that blocked time is "not a cost in addition to the collisions" [SPLIT].** Perspective W1 (Major) and Methodology W4 (Major, as one part of a wider finding) hold that this is a statement about harm resting on merged collision counts that cannot register sustained contact, with contact order unknown. Domain W8 (Minor) makes the same point and proposes the same rewording. DA M3 (Major, outside the count) adds that the reading presupposes that the obstacle-heavy checkpoint also collided at those sites, which is not reported.
  - **Editor's Resolution**: Major, `must_fix` (R8). Rationale: only the band differs; the remedy is the same in all four cards. The sentence stands in the third headline finding of Section 1 and recurs in Sections 4.7, 4.10 and 5 (the editor confirmed these four places in the manuscript), beside the statement that the paper makes no safety claim in either direction. Whether a sentence about harm keeps that limit lies in the perspective seat's field, and the three reasons it gives are taken from the manuscript itself. The fix is textual.
- **Whether the abstract claims only what is shown.** The Journal-Fit summary states that "the abstract and the conclusion claim only what is shown", and Perspective finds that the abstract, introduction and conclusion give the right main message. Methodology W5 and W8, Domain W1 and DA M4 find specific abstract sentences overstated: "A test that replaced the ego-motion history showed no dependence on it" and "where a pre-specified test was met". Methodology W9 questions "planned like the balanced checkpoint".
  - **Editor's Resolution**: the specific findings stand. Rationale: the editor confirmed that all three phrases are in the abstract as quoted. The Journal-Fit statement is supported by that seat's S1 for the scope limits (single seed, the 1,600-sample null, no safety claim), and the seat declares statistical detail outside what it assesses. What a null on eight routes or a same-checkpoint repeat can show lies with the methodology and domain seats. The Journal-Fit scores are unchanged; the abstract sentences are covered by R9, S13 and S14.

### Decision Rationale

The decision follows from the contract applied to the role-scoped verdicts. The methodology seat scores D1 as a repairable block and the domain seat scores D2 as a repairable block. Each alone fires F2, whose action is major revision. F3 also fires, because all four mandatory dimensions stand at warn or worse, and F5 fires on any warn. No seat declared a fatal block, so F1 does not fire.

Both blocks concern analysis and interpretation, not the measurements. The methodology seat finds that results carried by the abstract rest on analyses that need repair or on evidence that is missing: the H1 verdict, the blocked-time inference, the history-swap reading, the absence of a same-input comparison and, behind them, training-run variation that the design does not measure. The domain seat finds that two statements at the level of title, abstract and positioning say more than the measured quantities support: that the stay-put plans are not the inertia mechanism, and that fine-tuning composition taught the policy to wait. The DA's five Major challenges (D3), the perspective seat's finding on the harm reading of blocked time (D4) and the journal-fit seat's two framing findings (D6) bear on the same sentences. Every seat describes the descriptive core as supported by the reported numbers.

Of the twelve required items, eleven can be closed by editing text, six of them together with numbers recomputed from logs and records the authors already hold. One item (R4) needs a new offline experiment unless the model-level reading is withdrawn. A revised version requires re-review.

### Devil's Advocate Critical Issues

The DA card lists no CRITICAL issue, so there is nothing to adjudicate and the adjudication list in the audit is empty. Its five MAJOR challenges are not adjudicated as CRITICAL items; each is carried into the roadmap as follows.

| DA finding | Corroborated by | Roadmap item |
|---|---|---|
| M1, composition credited in the contribution statement and withdrawn in the discussion | Journal-Fit W2, Methodology W1, Domain W2, Perspective W3 | R2 |
| M2, the third checkpoint cannot yet carry the weight placed on it | Journal-Fit W9, Domain W7 (dataset description and overlap); Methodology W9 (one pass against two-pass means) | R3, R11, R12; related S14 |
| M3, blocked time declared not to be an additional cost | Methodology W4, Domain W8, Perspective W1 | R8 |
| M4, the history-swap test does not discriminate | Methodology W5, Domain W1 | R9, R10 |
| M5, a model-level difference inferred from self-generated rates | Methodology W2, Domain W5 | R4 |

### Blocking Issues (0–3, immutable source order)

The three rows group the required items that underlie the two block verdicts (D1, D2). Grouping is by subject, in source order, and is not a ranking.

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---------------|----------------|--------------------|-----------------|------------------------|
| R1 | Title, motivation and contribution (i) state a direction ("learning to wait") and a cause (data composition) that the paper's own values and its one-run-per-mix design do not carry | Journal-Fit W1, W2; Methodology W1; Domain W2; Perspective W3; DA M1 | `table: Table S2, column Standstill with L under 0.64 m, rows Base-Rerun 8.29, Flooded-6400 7.93, Golden-6400 0.75, Decoupling-6400 1.17`; `text: Section 4.1 "Each condition is one trained checkpoint (seed 42), so every test compares two specific checkpoints across routes"` | R1, R2 |
| R4 | Results carried by the abstract rest on analyses that need repair: plan shares measure occupancy and not a per-decision rate, the H1 verdict is fragile, and the blocked-time result and its reading as no additional cost go beyond the evidence | Methodology W2, W3, W4; Domain W5, W8; Perspective W1, W2; DA M3, M5 | `text: Section 4.6 "none compares the two experts on identical inputs, so none is a measure of propensity"`; `text: Supplementary Section S4.3 "the Holm-adjusted values are 0.0228, 0.0028, 0.0556 and 0.1587"`; `text: Section 1, third finding "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"` | R4, R5, R6, R7, R8 |
| R9 | The history-swap test is reported as showing no dependence and is used to set the stay-put plans apart from inertia; its outcome cannot separate the accounts | Methodology W5; Domain W1; DA M4 | `text: Abstract "A test that replaced the ego-motion history showed no dependence on it."` | R9, R10 |

R3, R11 and R12 are required items that underlie the D3 warn (DA M2), not a block.

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to (e.g. `SC-1`), so the decomposed granularity survives to the output boundary. A pre-decomposition / DA-CRITICAL item that has no sub-claim id uses `—`.

Conventions used in both tables:

- **Order.** Items stand in immutable source order: by the first card that raised the sub-claim, in dispatch order (eic, methodology, domain, perspective, da), then by finding number. The order is not a rank and not a work order.
- **Severity** is transported from the cards and never re-rated. Where seats gave different bands, each band is shown with its source.
- **Obligation class.** `must_fix`: a finding tagged Major by any seat, including the DA MAJOR table, after arbitration of the two splits. `should_fix`: a Minor-band finding. `consider`: a finding its own seat holds at the lowest band with the field norm unverified. Three `should_fix` items are named by a seat in the basis of a mandatory-dimension verdict and so bear on re-scoring: S13 (Methodology, D3), S15 and S16 (Domain, D2, "lesser instances").
- **Fix type.** `text`: editing only. `text + re-analysis`: editing plus numbers recomputed from logs, datasets or records the authors already hold; no new run. `new experiment`: new inference or simulator runs. Optional stronger remedies that a card offers are named as optional and do not change the fix type.

### Required Revisions (Must Fix)

> **Ordinal contract (#576/#670):** `R<n>` follows immutable roadmap source order filtered to `obligation_class == must_fix`; author-selected display order and triage never enter the derivation. Blocks are exactly `R1..Rn`. Each Acceptance criteria value is a single-line `- **Acceptance criteria**: <text>` bullet. The machine artifact is the closed `revision-roadmap/1.0` core, not an author-editable work list.

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|--------|------------------|------------|---------------------|
| R1 | State the direction of the effect against the unadapted policy; remove "learning to wait" from title and motivation | SC-1 | Major (Journal-Fit W1; Domain W2) | `text: §4.6 "and it is the low outlier among the six"` | 4 — editorial reading of the framing against values the paper itself reports | Journal-Fit W1; Domain W2; DA lesser point 4 | must_fix | re_analysis: Base-Rerun rows for Table 4 and Figure 5; title, Abstract, Section 1 | claim_scope_unsupported; claim: title "Learning to Wait" |
| R2 | Word the title and contribution (i) at the level of checkpoints, not data composition | SC-2 | Major (Journal-Fit W2; Methodology W1; Domain W2); Minor-band parent (Perspective W3); Major (DA M1) | `text: §1 "a controlled measurement of how two fine-tuning data compositions, with the model, loss, schedule and controller held fixed, changed the low-speed behaviour"` | 4 — contribution scoping is the core of this seat; whether more seeds are required is for the methodology seat | Journal-Fit W2; Methodology W1; Domain W2; Perspective W3; DA M1 | must_fix | section: title, Section 1 contribution list, Conclusion | claim_scope_unsupported; claim: contribution (i) |
| R3 | Describe the decoupling dataset in Table 1, including its low-speed stay-put share | SC-10 | Minor (Journal-Fit W9; Domain W7); Major (DA M2) | `absence: Table 1 and §3.3 — expected the realised composition of the decoupling mix and its stay-put share among low-speed samples; checked Table 1, §3.3, §4.10, Table S1, S3.3 and S4.10` | 5 — searched every occurrence of the dataset in both parts | Journal-Fit W9; Domain W7; DA M2 | must_fix | re_analysis: Table 1, new column | evidence_gap_remains; table: Table 1 |
| R4 | Compare the two experts on the same inputs, or withdraw the model-level and per-decision reading | SC-14 | Major (Methodology W2; DA M5); Minor (Domain W5); arbitrated Major | `text: Section 4.6 "none compares the two experts on identical inputs, so none is a measure of propensity"` | 4 — estimand definition under state-dependent sampling; the feasibility judgement rests on the manuscript's description of its logs | Methodology W2; Domain W5; DA M5 | must_fix | new_data: offline replay of one common set of low-speed states through each expert | claim_scope_unsupported; claim: "model-level difference" (Section 5) |
| R5 | Report H1 with its committed rule, its test-family history and its harness confound; do not state it as met without these | SC-15 | Major (Methodology W3) | `text: Supplementary Section S4.3 "the Holm-adjusted values are 0.0228, 0.0028, 0.0556 and 0.1587"` | 4 — multiplicity and signed-rank inference; the adjusted value I derive is inferred from printed values and should be checked by the authors | Methodology W3; related: Journal-Fit W4, DA lesser point 1 | must_fix | section: Abstract, Section 4.3, S4.3, Conclusion | claim_scope_unsupported; claim: H1 met at p = 0.048 |
| R6 | Re-test blocked time with an exact or permutation test and report the number of non-zero pairs | SC-16 | Major (Methodology W4) | `text: Section 4.7 "The definition was committed after a per-episode listing of long stops had been seen and before any per-route value was computed."` | 4 — zero-inflated paired outcomes and small-sample signed-rank behaviour; the count of non-zero pairs is my inference from the stated software defaults | Methodology W4 | must_fix | re_analysis: Section 4.7, blocked-time rows of Table 4 | evidence_gap_remains; claim: rule R3 (blocked time) met |
| R7 | Give a chance baseline for the position match between blocked runs and collisions | SC-17 | Major (Methodology W4); Minor-band parent (Perspective W2) | `text: Section 4.7 "The definition was committed after a per-episode listing of long stops had been seen and before any per-route value was computed."` | 4 — zero-inflated paired outcomes and small-sample signed-rank behaviour; the count of non-zero pairs is my inference from the stated software defaults | Methodology W4; Perspective W2 and question 5 | must_fix | re_analysis: Section 4.7, 10 m match | evidence_gap_remains; claim: blocked runs lie at collision sites |
| R8 | Remove the reading that blocked time is not an additional cost or harm | SC-18 | Major (Methodology W4; Perspective W1; DA M3); Minor (Domain W8); arbitrated Major | `text: Section 1, third finding "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"` (Perspective W1, DA M3); Methodology W4 anchor as in R6; Domain W8 anchor is the same sentence | 4 — safety-assurance practice on post-collision behaviour and on what collision counts can and cannot show (Perspective W1); 4 (Methodology W4); 4 (Domain W8) | Methodology W4; Domain W8; Perspective W1; DA M3 | must_fix | re_analysis: collision events of both checkpoints on the blocked routes, per pass; Sections 1, 4.7, 4.10, 5 | claim_scope_unsupported; claim: blocked time "not a cost in addition to the collisions" |
| R9 | Restate the history-swap result as inconclusive | SC-19 | Major (Methodology W5; Domain W1; DA M4) | `text: Abstract "A test that replaced the ego-motion history showed no dependence on it."` | 3 — the argument is about what the outcome can identify, but it depends on how this action space behaves, which is near my stated blind spot (Methodology W5); 4 (Domain W1) | Methodology W5; Domain W1; DA M4 | must_fix | section: Abstract, Section 1 first finding, Section 4.11, Section 5, Conclusion | claim_scope_unsupported; claim: "showed no dependence" |
| R10 | Stop presenting inertia and the sampling conjecture as rival accounts that the swap test decides between; limit the non-attribution to the history tokens | SC-24 | Major (Domain W1) | `text: Abstract "A test that replaced the ego-motion history showed no dependence on it."` | 4 — published work on inertia and causal confusion in CARLA imitation policies | Domain W1 | must_fix | section: Sections 1, 3.2, 4.11, 5 | interpretive_ambiguity_remains; claim: stay-put plans are not the inertia mechanism |
| R11 | Report the sample overlap of the decoupling set with the other 6,400-sample sets | SC-28 | Minor (Domain W7); Major (DA M2) | `absence: Table 1 and Sections 3.3, 4.10, S3.3, S4.10 — expected the realised composition of the decoupling dataset (group, manoeuvre and stationary shares, low-speed stay-put share, samples shared with the two Matrix 6,400 sets, samples touching evaluation routes); checked Table 1, Table S1, Sections 3.3 and 4.10, Supplementary S3.3 and S4.10` | 4 — dataset construction for CARLA imitation learning | Domain W7; DA M2 | must_fix | re_analysis: overlap counts, Table 1 or Section 3.3 | evidence_gap_remains; claim: the third checkpoint as evidence against a run-specific outcome |
| R12 | Restrict the wording on the third checkpoint to what three of four design cells allow | — | Major (DA M2) | `absence: Table 1 and Sections 3.3, 4.10, S3.3, S4.10 — expected the realised low-speed stay-put share of the decoupling set and its sample overlap with the balanced 6,400 set; checked Table 1, Table S1, Sections 3.3, 3.4, 4.10, S3.3, S3.4, S4.10 and the data availability statement` | 4/5 (absence checked on every listed surface; size of the overlap unknown) | DA M2 | must_fix | sentence: Abstract, Section 4.10, Conclusion | claim_scope_unsupported; claim: "not with the scenario-group mix" |

### Required Item Details

#### R1 — Direction of the effect against the unadapted policy (SC-1)
- What must change: the title and the opening motivation say that the policy learned to wait from obstacle-heavy data. Journal-Fit W1 and Domain W2 show from the manuscript's own values that the unadapted policy already stands where the obstacle-heavy checkpoint stands, and that two of three 6,400-sample fine-tunes lost the stay-put plans. Retitle, rebuild the first two paragraphs of the motivation around the pretrained reference, and add a paragraph on the pretrained prior.
- Where: title; Abstract (reference value beside the headline pair); Section 1; Table 4 and Figure 5 (reference row for `Base-Rerun` with the per-route at-rest share); Discussion.
- Note from the cards: use `Base-Rerun`, not the pooled 33.3 % of the original `Base` run, which was made mostly under the earlier termination rule (Domain W2; Journal-Fit W1 and question 2).
- Fix type: text + re-analysis (the `Base-Rerun` logs exist).
- **Acceptance criteria**: The title no longer asserts learning to wait; the Abstract, Table 4 and Figure 5 carry the `Base-Rerun` value on the same definition as the headline pair; Section 1 states which checkpoints moved relative to the unadapted policy.

#### R2 — Attribution to data composition (SC-2)
- What must change: contribution (i) says that two data compositions "changed the low-speed behaviour", and the title pairs composition with the stay-put plans, while Section 5 says the mix cannot be separated from the training run. Word both at the level of checkpoints. DA M1 adds: state the 1,600-sample null next to the 6,400-sample difference wherever the latter is given. Journal-Fit W2 adds: lead the contribution list with (ii) and (iii), which do not depend on attribution.
- Where: title; Section 1, contribution list; first sentence of the Conclusion.
- Optional stronger remedy, at the authors' choice: further training seeds for the 6,400-sample pair (Journal-Fit W2, Methodology W1, DA M1). This would be a new experiment and would let the composition wording stand if the result recurs. No seat requires it.
- Fix type: text.
- **Acceptance criteria**: The title, contribution (i) and the Conclusion describe a comparison of specific checkpoints trained once each; no sentence states that composition changed the behaviour without the qualifier that variation between training runs is untested; the 1,600-sample null stands beside each statement of the 6,400-sample difference.

#### R3 — Decoupling dataset in Table 1 (SC-10)
- What must change: the third checkpoint carries a statement in the abstract, yet its dataset is described in one sentence. Add a Table 1 column with the same rows as for the other two mixes, including the stay-put share among low-speed samples, which is the quantity the conjecture of Section 3.2 is about.
- Where: Table 1; Section 3.3.
- Fix type: text + re-analysis (shares computed from the existing dataset).
- **Acceptance criteria**: Table 1 has a column for the decoupling set with realised group, manoeuvre and stationary shares and the low-speed stay-put share, and Section 4.10 says whether that share agrees with the conjecture.

#### R4 — Same-input comparison (SC-14)
- What must change: every plan share is measured over the states each checkpoint put itself into, in units of logged steps, so one long stop is counted many times. The ratio of 14.00 % to 2.08 % is therefore an occupancy ratio, not a rate per decision, and the Discussion's "model-level difference" does not follow from it. Arbitrated split; see Points of Disagreement.
- Route (a): replay one common set of low-speed states (pooled from both models' logs, or the low-speed samples of the shared validation split) through each expert with many noise draws, and compare stay-put probabilities paired by state (Methodology W2; Domain question 3; DA M5, on a subset of routes).
- Route (b): withdraw the model-level and per-decision reading from the Abstract, headings, Section 5 and the Conclusion, state the shares as occupancy, and add episode-level statistics from the existing logs: per-route medians, per-episode onset rates (Domain W5) or the time from reaching rest to the first plan of 2 m or more, analysed as a censored duration (Methodology W2).
- Where: Sections 4.3, 4.6, 5; Abstract; Conclusion.
- Fix type: new experiment for route (a) (offline inference, no simulator run). Text + re-analysis for route (b). The cards do not settle whether route (b) alone clears the D1 block.
- **Acceptance criteria**: Either a same-input comparison of the two experts is reported with its state set, number of noise draws and paired result, or no heading, abstract or concluding sentence states a model-level or per-decision difference and the step shares are accompanied by episode-level rates.

#### R5 — H1 verdict (SC-15)
- What must change: H1 is reported as met at p = 0.048 with an interval that includes zero. Methodology W3 gives four reasons the verdict is fragile: the decision rule committed for H1 is not stated; the Holm value printed for the earlier four-test family uses the p-value against the set-aside `Base` run, and the reduction of the family to two tests is not explained; the two arms were evaluated on either side of the harness change of 10 November; and the gain is not established on the 24 routes not used to tune the controller. Report H1 as inconclusive or state these facts beside it, give the four-test value with the designated comparator, and remove the adjusted p-value from the abstract or give it with its interval.
- Where: Abstract; Section 4.3; Supplementary Section S4.3; Conclusion.
- Optional stronger remedy: re-run the 1,600-sample balanced checkpoint on the current harness (new experiment; Methodology W3 offers it as an alternative to the abstract edit).
- Fix type: text. The methodology seat asks the authors to check its derived value of about 0.096.
- **Acceptance criteria**: The committed rule for H1 and the history of the test family are stated; the adjusted value for the four-test family is given with the designated comparator; the harness change is discussed for H1; the abstract no longer gives the H1 p-value without the interval that includes zero.

#### R6 — Blocked-time test (SC-16)
- What must change: blocked time is non-zero on 6 routes for one model and 1 for the other, so the test of rule R3 is a normal approximation on at most seven pairs, and the same p = 0.028 is printed for three contrasts. The bootstrap interval of a mean with about 38 structural zeros is not reliable. Use an exact or permutation test and report the number of non-zero pairs for each blocked-time test; say that the inference concerns a handful of scenario types.
- Where: Section 4.7; blocked-time rows of Table 4; Supplementary Section S4.7.
- Fix type: text + re-analysis.
- **Acceptance criteria**: Each blocked-time contrast reports the number of non-zero pairs and an exact or permutation p-value, and the text states the number of routes that carry the result.

#### R7 — Position match with collisions (SC-17)
- What must change: a blocked run counts as at a collision site if it starts within 10 m of a recorded collision position, on routes with about 100 m of progress each, with no chance rate for such a match and no time order. Give a chance baseline, for example the match rate of long stops that are not blocked (Methodology W4; Perspective W2 and question 5).
- Where: Section 4.7; Supplementary Section S4.7.
- Fix type: text + re-analysis.
- **Acceptance criteria**: The match rate of blocked runs is reported beside a stated chance or comparison rate for the same window.

#### R8 — Blocked time as "not an additional cost" (SC-18)
- What must change: the statement that blocked time is not a cost, or not a harm, in addition to the collisions. Collision events are merged by actor, so the count cannot register sustained or repeated contact; the order of contact and blocked run is unknown; the study is not powered to show equal collision rates. Say that blocked time is co-located with recorded collisions and that whether it adds harm beyond the recorded contact cannot be measured from these logs, without ranking the two behaviours. DA M3 adds: report the collision events of both checkpoints on the routes with blocked time, per pass.
- Where: Section 1, third finding; Sections 4.7, 4.10 ("not as an additional harm") and 5.
- Optional stronger remedy: re-run the six or seven affected routes with the collision sensor logged per tick (new experiment; Perspective W1 offers it only "if the authors want to say more").
- Fix type: text + re-analysis (collision counts per route from existing records).
- **Acceptance criteria**: No sentence states that blocked time is not an additional cost or harm; the four places listed use the co-location wording; collision events of both checkpoints on the blocked routes are tabulated per pass.

#### R9 — History-swap result (SC-19)
- What must change: the abstract states a null as a finding ("showed no dependence"), and Section 4.11 concludes that the model issues such plans "whatever the history says". The test has 8 and 7 routes and p = 0.38. Its primary outcome counts a plan that keeps cruising at the injected 4 m/s as holding speed, so an expert that ignores its history and one that continues the motion its history reports predict the same result. Restate the result as inconclusive ("did not detect") and say that the primary outcome cannot separate these two cases.
- Where: Abstract; Section 1, first finding; Section 4.11; Section 5; Conclusion.
- Optional stronger remedy: a redesigned test with graded history speeds, an outcome defined relative to the scene, and an image-side or camera-window manipulation (new experiment; Methodology W5, Domain W1).
- Fix type: text.
- **Acceptance criteria**: The Abstract and Conclusion say that no dependence was detected in a small test; Section 4.11 states that the primary outcome does not separate a history-ignoring from a history-continuing expert; the phrase "whatever the history says" is removed or qualified.

#### R10 — Inertia and the sampling conjecture as rivals (SC-24)
- What must change: Domain W1 holds that the inertia problem as the Introduction defines it and the sampling conjecture are the same statement about the training data, differing in the head that reproduces it, and that the swap test changed only the 48 ego-history tokens while the camera window, which also tells the network the vehicle is at rest, was left unchanged. Present the conjecture as a data-side reading of the inertia problem for a sampling head, and limit the non-attribution to the history tokens.
- Where: Sections 1, 3.2, 4.11 and 5.
- Fix type: text.
- **Acceptance criteria**: No sentence states that the stay-put plans are not inertia; the text says that the visual route to the same shortcut was not tested and that the swap test does not separate inertia from the alternatives.

#### R11 — Overlap of the decoupling set (SC-28)
- What must change: the statement that `Golden-6400` is not alone rests on the third checkpoint, which shares seed, schedule, step count and pool with it. The number of samples the decoupling set shares with the balanced and the obstacle-heavy 6,400 sets is not reported; the two original sets already share 67 %.
- Where: Table 1 or Section 3.3; Section 4.10.
- Fix type: text + re-analysis (overlap counted from the dataset manifests).
- **Acceptance criteria**: The overlap of the decoupling set with each of the two other 6,400-sample sets is reported as a count and a share, and Section 4.10 states what that overlap implies for reading the third checkpoint as a separate run.

#### R12 — Wording on the third checkpoint (—; DA M2)
- What must change: the design fills three of four cells; no checkpoint has the balanced scenario-group mix with the obstacle-heavy manoeuvre mix and stationary share. The statement that the difference lies "not with the scenario-group mix" therefore holds only at the balanced manoeuvre level.
- Where: Abstract; Section 4.10; Conclusion.
- Fix type: text.
- **Acceptance criteria**: Each statement that assigns the difference to the manoeuvre mix and stationary share names the missing cell or is limited to the three cells run.

### Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|--------|------------------|------------|---------------------|
| S1 | State the evaluation-practice result as a named contribution with its implications | SC-3 | Minor | `text: §5 "For evaluation practice, the standstill fraction should be reported split by command and next to collisions"` | 4 — judgement of reader interest from running closed-loop evaluation tracks | Journal-Fit W3; Perspective W5 | should_fix | section: Section 5, Abstract, Conclusion | reader_traceability_reduced; section: Section 5 |
| S2 | Rewrite abstract and conclusion as summaries, not runs of values | SC-4 | Minor | `text: Abstract "Once slow, the obstacle-heavy checkpoint planned to stay put in 14.00 % of steps and the balanced one in 2.08 %."` | 4 — standard editorial criterion for abstracts | Journal-Fit W4 | should_fix | section: Abstract, Conclusion | editorial_conformance_unmet; section: Abstract |
| S3 | Keep in the supplement only what the main text does not contain | SC-5 | Minor | `text: Supplement preamble "Some statements of the main text are repeated here so that each section can be read on its own."` | 5 — direct comparison of the two parts of the supplied file | Journal-Fit W5 | should_fix | section: Supplement S3.2 to S4.11 | reader_traceability_reduced; manuscript: Supplement |
| S4 | Reproduce the pre-specified rule texts with commit times as an appendix | SC-6 | Minor | `text: §4.1 "they were not time-stamped by a third party"` | 4 — presentation and verifiability from the reader's side; the statistical weight of the record is for other seats | Journal-Fit W6; related remedy in Methodology W8 | should_fix | section: new supplementary appendix | reader_traceability_reduced; manuscript: ANALYSIS_ADDENDUM pointers |
| S5 | One name per object; add the dataset term "stationary" to Table 2 | SC-7 | Minor | `text: §3.3 "All four Matrix datasets are drawn from one verified training pool"` | 4 — terminology audit over the full text | Journal-Fit W7; Perspective W7 | should_fix | section: whole text, Table 2 | interpretive_ambiguity_remains; table: Table 2 |
| S6 | Align hypothesis numbering and reporting order; present the adaptation result as context in one place | SC-8 | Minor | `text: §4.3 "The three hypotheses are reported in order of their weight in this paper, not of their numbering."` | 3 — structural reading; the status of each test is for the methodology and coherence seats | Journal-Fit W8 | should_fix | section: Section 4.3, Abstract, Conclusion | reader_traceability_reduced; section: Section 4.3 |
| S7 | Say in the abstract which statistic the pre-specified test used and that the headline pair is a different, post hoc measure | SC-9 | Minor | `text: §4.3 "The three hypotheses are reported in order of their weight in this paper, not of their numbering."` | 3 — structural reading; the status of each test is for the methodology and coherence seats | Journal-Fit W8; Perspective W7 | should_fix | sentence: Abstract, Section 1 findings | interpretive_ambiguity_remains; claim: "a pre-specified test was met" |
| S8 | Use one aggregation for the low-speed stay-put share, or give both and explain the gap | SC-11 | Minor | `figure: Figure 5 caption, panels (a) and (b)` | 4 — values compared across abstract, Table 4 and Section 4.6; the figure itself was not available | Journal-Fit W10; Perspective W7; DA lesser point 5 | should_fix | re_analysis: Section 4.6, Figure 5 | interpretive_ambiguity_remains; claim: "the low outlier among the six" |
| S9 | Confirm from logs the two facts that sit in content positions | SC-12 | Minor | `table: Table S1, row Decoupling-6400, columns Resume events and Training (UTC)` | 5 — read directly from the table and limitation 10 | Journal-Fit W11; Perspective Minor Issues, third point `[CONFIDENCE-SOURCE: report-level]` | should_fix | sentence: Table S1, Sections 3.3 and 3.4, Limitation 10 | reporting_requirement_unmet; table: Table S1 |
| S10 | Split Tables 3 and S2; drop or explain columns no sentence uses | SC-13 | Minor | `table: Table 3 (main text, §4.2), thirteen columns` | 4 — layout judgement from the supplied tables | Journal-Fit W12; Perspective Minor Issues, second point `[CONFIDENCE-SOURCE: report-level]` | should_fix | section: Table 3, Table S2 | editorial_conformance_unmet; table: Table 3 |
| S11 | Name one estimand per endpoint; add a paired permutation test of the mean; analyse the two passes jointly | SC-20 | Minor | `text: Section 4.4 "The interval includes zero, so the second pass alone does not meet the rule of Section 4.3."` | 4 — paired non-parametric and bootstrap inference | Methodology W6 | should_fix | re_analysis: Sections 4.3 to 4.10 | interpretive_ambiguity_remains; claim: decision rules that pair a mean interval with a rank test |
| S12 | State whether the evaluated checkpoint weights, the controller file and the repository are released, and where | SC-21 | Minor | `absence: Section 6 Data availability and Code availability statements — expected a statement that the fine-tuned action-expert weights of the evaluated checkpoints are deposited; checked Section 6, Section 3.4, Supplementary Section S3.4 and Table S1` | 4 — reproducibility requirements for single-checkpoint claims | Methodology W7; Perspective W6 | should_fix | section: Section 6 | reporting_requirement_unmet; section: Section 6 |
| S13 | Label each analysis by a three-level scheme; qualify "a pre-specified test was met" | SC-22 | Minor | `text: Abstract "where a pre-specified test was met"` | 4 — pre-specification practice | Methodology W8; DA lesser point 3 | should_fix | section: Abstract, Table 4 caption, Section 4.1 | interpretive_ambiguity_remains; claim: "pre-specified" for H3, R2 and R3 |
| S14 | Report the decoupling arm's similarity as an estimate with interval or against a stated margin | SC-23 | Minor | `text: Section 4.10 "The comparator is the per-route mean of the two default-controller passes of each of the other two models."` | 3 — equivalence reasoning; I have not seen the committed rule of the addendum | Methodology W9; related: DA M2 | should_fix | section: Abstract, Section 4.10 | claim_scope_unsupported; claim: "planned like the balanced checkpoint" |
| S15 | Describe H3 as recurrence of gate-held standstill; move the plan-level weight to the at-rest and gate-off rows | SC-25 | Minor | `text: Section 4.3 "H3 therefore shows that a controller-coupled plan statistic recurred when the same checkpoints were evaluated again"` | 4 — arithmetic on the manuscript's own tables | Domain W3 | should_fix | sentence: Abstract, Section 4.3 | interpretive_ambiguity_remains; claim: H3 as the plan-level test |
| S16 | Remove the conjecture's conclusion from the Introduction; state the aliasing assumption; discuss overwriting of the pretrained prior | SC-26 | Minor | `text: Section 1 "For a policy that samples from the futures it was shown, this share matters"` | 3 — flow and diffusion planners; the aliasing argument is conceptual and not tested here | Domain W4 | should_fix | section: Sections 1 and 3.2 | interpretive_ambiguity_remains; section: Section 3.2 |
| S17 | State the replanning rate | SC-27 | Minor | `absence: Sections 3.1, 3.4 and S3.4 on inference and control — expected the replanning rate, that is how many 20 Hz simulator steps one sampled plan is executed and logged for; checked Sections 3.1, 3.4, 4.1, 4.6 and Supplementary S3.4, S4.1, S4.6` | 4 — system description of sampling-based planners | Domain W6; Perspective W7 and question 2 | should_fix | sentence: Section 3.1 or 3.4 | reporting_requirement_unmet; section: Section 3.4 |
| S18 | Correct and extend four related-work attributions | SC-29 | Minor | `text: Section 2 "find that the style of the expert significantly affects the trained policy"` | 3 — from memory of the cited papers, without online checking in this session | Domain W9 | should_fix | section: Section 2, reference list | reader_traceability_reduced; section: Section 2 |
| S19 | Comparison with established remedies for the same symptom | SC-30 | Minor `[FIELD-NORM UNVERIFIED]` | `text: Section 5, Limitation 6 "We did not compare against controller-side anti-stall rules or model-side remedies such as history dropout"` | 3 — field practice known from experience, not sourced here | Domain W10 | consider | new_data: baseline runs, only if the authors choose | evidence_gap_remains; claim: how the plan-level difference compares with known remedies |
| S20 | Report the Bench2Drive Success Rate per checkpoint | SC-31 | Minor | `absence: Table 3 and Sections 4.2, 4.3, S4.3 — expected the Bench2Drive Success Rate per checkpoint next to Driving Score and route completion; checked Tables 2, 3, 4, S2, S3 and Sections 4.2 to 4.10 with their supplementary counterparts` | 4 — Bench2Drive evaluation | Domain W11 | should_fix | re_analysis: Table 3 | reporting_requirement_unmet; table: Table 3 |
| S21 | Name "blocked time" for what is observed, or validate the name; tell the reader its tie to the start-assist floor | SC-32 | Minor | `text: Section 4.7 "This is inferred from the command log, not from a contact sensor."` | 4 — metric validity review in scenario-based testing | Perspective W2 | should_fix | section: Table 2, Section 4.7 | interpretive_ambiguity_remains; claim: the name "blocked time" |
| S22 | Replace "waited" and "pushed" by terms that do not name a purpose | SC-33 | Minor | `text: Section 5 "In scenarios the policy cannot solve, one checkpoint waited and the others pushed."` | 4 — reading of behavioural terms from a safety-assurance standpoint | Perspective W3; Domain review body ("Argument accuracy") and W2 | should_fix | sentence: title, Section 5 | interpretive_ambiguity_remains; claim: "waited" and "pushed" |
| S23 | Present waiting and contact as two separately measured quantities; replace "at a cost" | SC-34 | Minor | `text: Section 1, second paragraph "and one that never waits meets the obstacle"` | 3 — what a trade-off statement needs in validation practice | Perspective W4 | should_fix | sentence: Section 1 second paragraph, Section 4.10 | interpretive_ambiguity_remains; section: Section 1 |

> Transported metadata reaches the emitted package ON EVERY ROW, never dies in the Step 1b working inventory (#574 A2/A3): each item carries the driving sub-claim's transported Severity (fallback tags like `[SEVERITY-SOURCE: letter-fallback]` travel with it), the finding's typed Evidence Anchor, and its per-finding Confidence — for every roadmap item, not only the ≤3 Top Blocking rows. Schema 7 `RoadmapItem` carries the same three optional fields for machine consumers.

### Suggested Item Details

Each line gives what to change, where, how to show it is done, and the fix type.

- **S1 (SC-3).** Change: state as a contribution that standstill fraction counts a waiting vehicle and a vehicle commanded to move that does not move as the same thing, and that Driving Score did not register a several-fold difference in plans; add a short paragraph with the minimum logging needed, what the reported reliability implies for runs per scenario, the absence of a reference for required stops, and the non-recommendation on choosing a mix. Where: Section 5, Abstract, Conclusion. Done when: the paragraph exists and the abstract and conclusion carry the result. Fix type: text.
- **S2 (SC-4).** Change: question, design, findings in words with three or four numbers, then limits; define "once slow" and "the gate" or avoid them. Where: Abstract, Conclusion. Done when: the abstract states in one sentence what the reader should conclude and leaves intervals to the body. Fix type: text.
- **S3 (SC-5).** Change: remove main-text paragraphs repeated word for word; introduce each remaining part by one sentence pointing to the result it extends. Where: Supplement S3.2, S3.3, S4.3, S4.5 to S4.7, S4.10, S4.11. Done when: no paragraph appears in both parts. Fix type: text.
- **S4 (SC-6).** Change: reproduce the rule texts (H2, H3, the two secondary rules, the decoupling and history-swap readings) with commit times as an appendix and cite appendix items; Methodology W8 asks for one table giving, for each analysis, the commit, its time and the data then in existence. Where: new appendix; main-text pointers. Done when: every pre-specification pointer resolves inside the submission. Fix type: text.
- **S5 (SC-7).** Change: one name per dataset and checkpoint; define "Matrix"; add the dataset-side definition of stationary to Table 2 and say why it differs from the stay-put threshold; give the two plan thresholds in the abstract. Where: whole text, Table 2, Abstract. Done when: each object has one name and Table 2 lists every state term used. Fix type: text.
- **S6 (SC-8).** Change: renumber the hypotheses by weight or report them in numbered order; present the adaptation result once, as context. Where: Sections 4.1 and 4.3, Abstract, Conclusion. Done when: numbering and reporting order agree. Fix type: text.
- **S7 (SC-9).** Change: name one primary plan-level statistic and say in the abstract that the pre-specified test used near-stationary plans (below 1.5 m, all steps) while the headline pair is the post hoc stay-put share at 0.5 m/s or less. Where: Abstract, Section 1 findings. Done when: the abstract signals the change of measure. Fix type: text.
- **S8 (SC-11).** Change: use one aggregation in both panels of Figure 5, or give both for the matched pair and say which routes drive the gap; DA lesser point 5 asks that "the low outlier among the six" be given on the per-route scale with intervals. Where: Section 4.6, Figure 5, Table 4. Done when: the 14.00 % and 24.9 % values are reconciled in the text. Fix type: text + re-analysis.
- **S9 (SC-12).** Change: confirm the rendering quality of data collection and the resume events and training end time of the decoupling checkpoint from logs, and make the dependent sentences unconditional. Where: Table S1, Sections 3.3 and 3.4, Limitation 10. Done when: neither placeholder remains in a content position. Fix type: text.
- **S10 (SC-13).** Change: split Table 3 into leaderboard outcomes and kinematics, move per-ability strata of Table S2 to their own table, and drop or explain unused columns (hard-brake share and steer jerk are never discussed). Where: Table 3, Table S2. Done when: each table fits a journal page without rotation. Fix type: text.
- **S11 (SC-20).** Change: name one estimand per endpoint; add a paired permutation test of the mean and a robust location estimate; analyse the two passes together with route as a random effect and pass as a factor, labelled post hoc. Where: Sections 4.3, 4.4, 4.9, 4.10. Done when: the four places where interval and rank test disagree are each explained by a named estimand. Fix type: text + re-analysis.
- **S12 (SC-21).** Change: state whether the fine-tuned expert weights are deposited (or why not), where the repository is, that it holds the hashed bridge controller, the gate-off variant and the harness, and what one evaluation pass costs; seed and log sampler noise in any further run. Where: Section 6. Done when: Section 6 names the weights and the repository location. Fix type: text (plus the deposit itself).
- **S13 (SC-22).** Change: use three labels consistently (pre-specified before any data of the comparison; repeat test on the same checkpoints; exploratory); qualify the abstract phrase; correct the Table 4 caption for R2 and R3. Where: Abstract, Table 4 caption, Section 4.1. Done when: no repeat test on the same checkpoints is called pre-specified without the qualifier. Fix type: text. Named by the methodology seat in its D3 basis.
- **S14 (SC-23).** Change: state a margin for "planned like the balanced checkpoint", or report the similarity as an estimate with its interval and the share of the gap closed; say that one pass is set against two-pass means. Optional: a second pass for the decoupling checkpoint (new experiment). Where: Abstract, Section 4.10. Done when: the similarity statement carries an interval or a margin. Fix type: text.
- **S15 (SC-25).** Change: say that 95 to 97 % of the steps H3 counts are gate-held standstill steps, describe H3 as recurrence of gate-held standstill, and rest the plan-level claim on the at-rest and gate-off rows, stated as post hoc. Where: Abstract (parenthesis), Section 4.3. Done when: H3 is no longer presented as a separate plan-level test. Fix type: text. Named by the domain seat as a lesser instance of its D2 trigger.
- **S16 (SC-26).** Change: remove the assertion from the Introduction; state that the 31.0 % and 10.9 % are marginal shares and that the conjecture needs stay and start contexts to be indistinguishable to the frozen backbone; discuss progressive overwriting of the pretrained prior as an alternative that predicts the 1,600-sample result. Where: Sections 1 and 3.2. Done when: the conjecture appears only as a conjecture and the alternative is discussed. Fix type: text. Named by the domain seat as a lesser instance of its D2 trigger.
- **S17 (SC-27).** Change: state whether the expert is queried at every 20 Hz step with fresh noise or a plan is held for several steps. Where: Section 3.1 or 3.4. Done when: the rate is stated. Fix type: text.
- **S18 (SC-29).** Change: extend the summary of reference [37]; cite the journal version of TransFuser for the creeping rule; attribute the freezing robot problem to its 2010 source; check what [40] says on controller heuristics; connect the persistence part of the conjecture to work on re-sampling action chunks. Where: Section 2, reference list. Done when: the four attributions are corrected. Fix type: text. The domain seat gave these from memory and asks the authors to verify each reference before citing.
- **S19 (SC-30), consider.** Change: none required; the authors already state the limit. If pursued, a history-dropout or creep-rule baseline would be a new experiment. Fix type: new experiment, optional.
- **S20 (SC-31).** Change: add the per-route Success Rate defined by the benchmark. Where: Table 3. Done when: Table 3 has the column. Fix type: text + re-analysis ("It needs no new runs", Domain W11).
- **S21 (SC-32).** Change: name the measure for what is observed (for example, commanded-acceleration standstill) or keep the name and validate it; say in the main text that 0.35 is the controller's start-assist floor, which applies only to plans of 2.5 m or more. Where: Table 2, Section 4.7. Done when: the name or its stated validity matches the command-level definition. Fix type: text. Optional validation by a contact-sensor re-run would be a new experiment.
- **S22 (SC-33).** Change: say that one checkpoint held and the others commanded a start; state that whether a stop was required is unknown. Where: Section 5; the title is covered by R1 and R2. Done when: "waited" and "pushed" are gone from summary sentences. Fix type: text. Optional: a reference run of the privileged expert on the 44 routes (new experiment).
- **S23 (SC-34).** Change: present the two failure modes as two separately measured quantities with no assumed relation; replace "at a cost" by the statement that the second pre-specified condition was not met. Where: Section 1, second paragraph; Section 4.10. Done when: the introduction no longer places waiting and contact on one axis. Fix type: text.

### Items by fix type

| Fix type | Required items | Suggested items |
|---|---|---|
| Text only | R2, R5, R9, R10, R12 | S1 to S7, S9, S10, S12 to S18, S21 to S23 |
| Text + re-analysis of existing logs or records | R1, R3, R6, R7, R8, R11 | S8, S11, S20 |
| New experiment | R4, route (a); route (b) is text + re-analysis and its sufficiency is unresolved | S19 (optional, `consider`) |

Optional stronger remedies that would need new experiments, none of them required by any card: further training seeds (R2), a re-run of the 1,600-sample balanced checkpoint on the current harness (R5), a contact-sensor re-run of the affected routes (R8, S21), a redesigned history test (R9), a second pass for the decoupling checkpoint (S14), a reference run of the privileged expert (S22).

### Source-Traceability Checklist

> Preserve source order and do not suggest a work order. Author triage is
> collected later as an explicit, complete sidecar.

- [ ] R1 — obligation `must_fix`: State the direction of the effect against the unadapted policy; retitle (SC-1; Journal-Fit W1, Domain W2)
- [ ] R2 — obligation `must_fix`: Word title and contribution (i) at the level of checkpoints (SC-2; Journal-Fit W2, Methodology W1, Domain W2, Perspective W3, DA M1)
- [ ] S1 — obligation `should_fix`: Evaluation-practice result as a named contribution (SC-3; Journal-Fit W3, Perspective W5)
- [ ] S2 — obligation `should_fix`: Abstract and conclusion as summaries (SC-4; Journal-Fit W4)
- [ ] S3 — obligation `should_fix`: Supplement without repetition (SC-5; Journal-Fit W5)
- [ ] S4 — obligation `should_fix`: Rule texts as an appendix (SC-6; Journal-Fit W6)
- [ ] S5 — obligation `should_fix`: One name per object; Table 2 completed (SC-7; Journal-Fit W7, Perspective W7)
- [ ] S6 — obligation `should_fix`: Hypothesis numbering and reporting order (SC-8; Journal-Fit W8)
- [ ] S7 — obligation `should_fix`: Tested statistic named in the abstract (SC-9; Journal-Fit W8, Perspective W7)
- [ ] R3 — obligation `must_fix`: Decoupling dataset in Table 1 (SC-10; Journal-Fit W9, Domain W7, DA M2)
- [ ] S8 — obligation `should_fix`: One aggregation for the stay-put share (SC-11; Journal-Fit W10, Perspective W7)
- [ ] S9 — obligation `should_fix`: Two unconfirmed facts confirmed (SC-12; Journal-Fit W11)
- [ ] S10 — obligation `should_fix`: Tables 3 and S2 split (SC-13; Journal-Fit W12)
- [ ] R4 — obligation `must_fix`: Same-input comparison, or model-level reading withdrawn (SC-14; Methodology W2, Domain W5, DA M5)
- [ ] R5 — obligation `must_fix`: H1 verdict (SC-15; Methodology W3)
- [ ] R6 — obligation `must_fix`: Blocked-time test (SC-16; Methodology W4)
- [ ] R7 — obligation `must_fix`: Chance baseline for the position match (SC-17; Methodology W4, Perspective W2)
- [ ] R8 — obligation `must_fix`: Blocked time as "not an additional cost" (SC-18; Methodology W4, Domain W8, Perspective W1, DA M3)
- [ ] R9 — obligation `must_fix`: History-swap result as inconclusive (SC-19; Methodology W5, Domain W1, DA M4)
- [ ] S11 — obligation `should_fix`: One estimand per endpoint; joint analysis of the passes (SC-20; Methodology W6)
- [ ] S12 — obligation `should_fix`: Release of weights, controller and repository (SC-21; Methodology W7, Perspective W6)
- [ ] S13 — obligation `should_fix`: Three-level labels for pre-specification (SC-22; Methodology W8)
- [ ] S14 — obligation `should_fix`: Decoupling similarity with interval or margin (SC-23; Methodology W9)
- [ ] R10 — obligation `must_fix`: Inertia and the conjecture not presented as rivals (SC-24; Domain W1)
- [ ] S15 — obligation `should_fix`: H3 as recurrence of gate-held standstill (SC-25; Domain W3)
- [ ] S16 — obligation `should_fix`: Conjecture not asserted in the Introduction (SC-26; Domain W4)
- [ ] S17 — obligation `should_fix`: Replanning rate (SC-27; Domain W6, Perspective W7)
- [ ] R11 — obligation `must_fix`: Sample overlap of the decoupling set (SC-28; Domain W7, DA M2)
- [ ] S18 — obligation `should_fix`: Related-work attributions (SC-29; Domain W9)
- [ ] S19 — obligation `consider`: Comparison with established remedies (SC-30; Domain W10)
- [ ] S20 — obligation `should_fix`: Bench2Drive Success Rate (SC-31; Domain W11)
- [ ] S21 — obligation `should_fix`: Name and validity of "blocked time" (SC-32; Perspective W2)
- [ ] S22 — obligation `should_fix`: "Waited" and "pushed" (SC-33; Perspective W3)
- [ ] S23 — obligation `should_fix`: One-axis framing in the introduction (SC-34; Perspective W4)
- [ ] R12 — obligation `must_fix`: Wording on the third checkpoint limited to three cells (—; DA M2)

### Response Letter Template

Please answer every item above, R1 to R12 and S1 to S23, in the format of `templates/revision_response_template.md`. For each item, state the change made and its location, or give the reason for declining. A declined `must_fix` item remains visible and unresolved for the re-review; it is neither forbidden nor silently changed. For R4, state which route was taken.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Recommendation: no decision; preliminary signal of minor revision on its two dimensions (D5 warn, D6 warn) | Confidence: 4 of 5
- Key Point: The abstract and conclusion keep their limits, but the title, the motivation and contribution (i) present an effect of data composition, in the direction "obstacle-heavy data teach waiting", that the six-checkpoint values and the one-run-per-mix design do not carry.

### Reviewer 1 (Methodology) Summary
- Recommendation: none stated; D1 block (repairable), D3 warn | Confidence: 4 of 5
- Key Point: The central descriptive result is sound, but the H1 verdict, the blocked-time inference, the history-swap reading and the absence of a same-input comparison need repair, and one training run per mix cannot carry an attribution to composition.

### Reviewer 2 (Domain) Summary
- Recommendation: none stated; D2 block (repairable) | Confidence: 4 of 5 for domain content, lower for statistical inference
- Key Point: The measurements stand; the statements that the stay-put plans are not inertia and that fine-tuning composition taught the policy to wait say more than the measured quantities support.

### Reviewer 3 (Perspective) Summary
- Recommendation: none stated; D4 warn | Confidence: 4 of 5 on measure validity and safety wording, 2 of 5 on anything that depends on the sampler
- Key Point: The scope limit on safety is stated early and repeated, but the reading that blocked time is no additional cost or harm is a statement about harm that the merged collision counts cannot support.

### Devil's Advocate Summary
- Recommendation: N/A — findings only (D3 warn)
- Key Challenge: No unresolved Critical challenge. Five Major challenges: composition credited and then withdrawn, the weight on the third checkpoint, blocked time as no additional cost, a history-swap test that does not discriminate, and a model-level difference inferred from self-generated rates.

---

## Appendix: Synthesis Working Record

### Step 1a — Reviewer Summary Matrix

| Dimension | Journal-Fit Reviewer | Methodology | Domain | Perspective |
|-----------|----------------------|-------------|--------|-------------|
| Overall recommendation | Signal only: minor revision on D5 and D6 | None stated; D1 block (repairable), D3 warn | None stated; D2 block (repairable) | None stated; D4 warn |
| Confidence / scope disclosure | 4 of 5; statistics and controller internals not assessed; figures seen as captions only; earlier review not seen | 4 of 5; driving-domain plausibility a possible blind spot, bearing mainly on W5 | 4 of 5; no web access, later references unchecked; statistics left to the methodology seat | 4 of 5 on validity and wording, 2 of 5 on the sampler; figures seen as captions only |
| Key strengths | S1 to S5: limits carried through; model and controller separated; rules applied against the authors | S1 to S5: status of every rule stated; noise measured by a full repeat; gate-off intervention; internal consistency | S1 to S5: planner and controller separated; speed dependence handled; prior work accurate; disconfirming results reported | S1 to S6: scope limit repeated; measures defined by level; reliability disclosed; trade-off curve declined |
| Key weaknesses | (→ Step 1b) 2 Major, 10 Minor | (→ Step 1b) 5 Major, 4 Minor | (→ Step 1b) 2 Major, 9 Minor | (→ Step 1b) 1 Major, 6 Minor |
| # of questions | 4 | 3 | 7 | 5 |
| # of minor issues | 10 Minor-band weaknesses | 4 Minor-band weaknesses | 9 Minor-band weaknesses | 6 Minor-band weaknesses and 3 unnumbered minor points |

The Devil's Advocate card has 0 Critical and 5 Major entries, five lesser points below the Major band, four alternative explanations and one unexamined premise.

Criterion judgements on the narrative scale are copied without conversion. Methodology, statistical reporting: effect sizes with intervals MEETS; accounting of exclusions MEETS; delimitation of test families PARTLY_MEETS; match between test, estimand and distribution PARTLY_MEETS; a priori power or minimum detectable effect DOES_NOT_MEET. Devil's Advocate, D3 only: consistency of the thesis PARTLY_MEETS; conclusions follow from evidence PARTLY_MEETS; rival explanations addressed PARTLY_MEETS; scope MEETS for abstract and conclusion and PARTLY_MEETS for title and contribution list; contrary evidence reported MEETS; limitations carried into conclusions PARTLY_MEETS. The methodology card's arithmetic receipts AR1 to AR12 report no inconsistency (five consistent, seven not computable inside the bounded procedures).

### Step 1b — Weakness Sub-Claim Inventory

One row per position taken. A seat not listed for a sub-claim is `not-mentioned` (silent). Severity and confidence are transported from the parent weakness. Convention on bands: where the same sub-claim sits inside parent weaknesses of different bands, a seat's position is `disputed` only if its weakness is solely or mainly about that sub-claim (SC-14, SC-18); otherwise it is `corroborated` and the difference of band is shown (SC-2, SC-17, SC-33). DA rows are listed for traceability and are outside the count.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|--------------|-----------------|-------------|----------|------------------|----------|------------|
| SC-1 | Title and motivation point the wrong way | Journal-Fit W1 | raised | `text: §4.6 "and it is the low outlier among the six"` | Major | 4 |
| SC-1 | Direction relative to the pretrained policy | Domain W2 | raised | `table: Table S2, column Standstill with L under 0.64 m, rows Base-Rerun 8.29, Flooded-6400 7.93, Golden-6400 0.75, Decoupling-6400 1.17` | Major | 4 |
| SC-1 | Lesser point 4, title direction | DA | outside count | `text: §4.6` "the stay-put share at low speed was 33.3 % for" | below Major | 3 |
| SC-2 | Contribution (i) and title attribute to composition | Journal-Fit W2 | raised | `text: §1 "a controlled measurement of how two fine-tuning data compositions, with the model, loss, schedule and controller held fixed, changed the low-speed behaviour"` | Major | 4 |
| SC-2 | One training run per mix | Methodology W1 | raised | `text: Section 4.1 "Each condition is one trained checkpoint (seed 42), so every test compares two specific checkpoints across routes"` | Major | 5 |
| SC-2 | Causal verb in contribution (i) | Domain W2 | corroborated | as Domain W2 above | Major | 4 |
| SC-2 | "Learning" adds a causal reading | Perspective W3 | corroborated | `text: Section 5 "In scenarios the policy cannot solve, one checkpoint waited and the others pushed."` | Minor | 4 |
| SC-2 | M1 | DA | outside count | `text: §1 contribution (i)` against `§5 "we cannot separate the effect of the mix from that of the training run"` | Major | 4 |
| SC-3 | Transferable result is one sentence | Journal-Fit W3 | raised | `text: §5 "For evaluation practice, the standstill fraction should be reported split by command and next to collisions"` | Minor | 4 |
| SC-3 | Implications for evaluation practice | Perspective W5 | raised | same sentence | Minor | 4 |
| SC-4 | Abstract and conclusion are runs of values | Journal-Fit W4 | raised | `text: Abstract "Once slow, the obstacle-heavy checkpoint planned to stay put in 14.00 % of steps and the balanced one in 2.08 %."` | Minor | 4 |
| SC-5 | Supplement repeats the main text | Journal-Fit W5 | raised | `text: Supplement preamble "Some statements of the main text are repeated here so that each section can be read on its own."` | Minor | 5 |
| SC-6 | Repository pointers used as citations | Journal-Fit W6 | raised | `text: §4.1 "they were not time-stamped by a third party"` | Minor | 4 |
| SC-7 | Near-synonymous names and thresholds | Journal-Fit W7 | raised | `text: §3.3 "All four Matrix datasets are drawn from one verified training pool"` | Minor | 4 |
| SC-7 | Abstract mixes state terms; dataset term missing from Table 2 | Perspective W7 | corroborated | `text: Abstract "Once slow, the obstacle-heavy checkpoint planned to stay put in 14.00 % of steps"` | Minor | 3 |
| SC-8 | Hypothesis numbering and reporting order | Journal-Fit W8 | raised | `text: §4.3 "The three hypotheses are reported in order of their weight in this paper, not of their numbering."` | Minor | 3 |
| SC-9 | Headline statistic is not the tested statistic | Journal-Fit W8 | raised | as SC-8 | Minor | 3 |
| SC-9 | Two different plan measures, change not signalled | Perspective W7 | corroborated | as Perspective W7 above | Minor | 3 |
| SC-10 | Decoupling mix not in Table 1 | Journal-Fit W9 | raised | `absence: Table 1 and §3.3 — expected the realised composition of the decoupling mix and its stay-put share among low-speed samples; checked Table 1, §3.3, §4.10, Table S1, S3.3 and S4.10` | Minor | 5 |
| SC-10 | Decoupling dataset described only in words | Domain W7 | raised | `absence: Table 1 and Sections 3.3, 4.10, S3.3, S4.10` (full anchor in R11) | Minor | 4 |
| SC-10 | M2 | DA | outside count | `absence: Table 1 and Sections 3.3, 4.10, S3.3, S4.10` (full anchor in R12) | Major | 4 |
| SC-11 | Two aggregations, 14.00 % and 24.9 % | Journal-Fit W10 | raised | `figure: Figure 5 caption, panels (a) and (b)` | Minor | 4 |
| SC-11 | Reason for the gap not given | Perspective W7 | corroborated | as Perspective W7 above | Minor | 3 |
| SC-11 | Lesser point 5 | DA | outside count | `table: Table 4, stay-put row` | below Major | 3 |
| SC-12 | Two unconfirmed facts in content positions | Journal-Fit W11 | raised | `table: Table S1, row Decoupling-6400, columns Resume events and Training (UTC)` | Minor | 5 |
| SC-12 | Limitation 10 depends on a pending confirmation | Perspective, Minor Issues | corroborated | Minor Issues, third point | Minor | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-13 | Tables 3 and S2 too wide | Journal-Fit W12 | raised | `table: Table 3 (main text, §4.2), thirteen columns` | Minor | 4 |
| SC-13 | Table 3 columns never discussed | Perspective, Minor Issues | corroborated | Minor Issues, second point | Minor | 4 `[CONFIDENCE-SOURCE: report-level]` |
| SC-14 | No same-input comparison; shares weighted by dwell time | Methodology W2 | raised | `text: Section 4.6 "none compares the two experts on identical inputs, so none is a measure of propensity"` | Major | 4 |
| SC-14 | Step shares weighted by duration | Domain W5 | disputed (severity and remedy) | same sentence | Minor | 4 |
| SC-14 | M5 | DA | outside count | `text: §5 "The model-level difference holds under both controllers, in both passes and among steps at rest."` | Major | 4 |
| SC-15 | H1 verdict | Methodology W3 | raised | `text: Supplementary Section S4.3 "the Holm-adjusted values are 0.0228, 0.0028, 0.0556 and 0.1587"` | Major | 4 |
| SC-15 | Lesser point 1 | DA | outside count | `text: S5 item 4` "moved by 7.40 points" | below Major | 4 |
| SC-16 | Blocked-time test on six or seven routes | Methodology W4 | raised | `text: Section 4.7 "The definition was committed after a per-episode listing of long stops had been seen and before any per-route value was computed."` | Major | 4 |
| SC-17 | Position-only match, no chance rate | Methodology W4 | raised | as SC-16 | Major | 4 |
| SC-17 | 10 m match with no time order or chance rate | Perspective W2 | corroborated | `text: Section 4.7 "This is inferred from the command log, not from a contact sensor."` | Minor | 4 |
| SC-18 | Claim about cost goes beyond the match | Methodology W4 | raised | as SC-16 | Major | 4 |
| SC-18 | Harm-accounting reading breaks the no-safety-claim limit | Perspective W1 | raised | `text: Section 1, third finding "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"` | Major | 4 |
| SC-18 | No additional cost is a judgement the logs cannot support | Domain W8 | disputed (severity) | `text: Section 1 "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"` | Minor | 4 |
| SC-18 | M3 | DA | outside count | same sentence, with `§4.7 "Whether a run began before or after the recorded contact cannot be established from these records."` | Major | 4 |
| SC-19 | History-swap outcome cannot discriminate | Methodology W5 | raised | `text: Abstract "A test that replaced the ego-motion history showed no dependence on it."` | Major | 3 |
| SC-19 | Swap test cannot carry "not inertia" | Domain W1 | raised | same sentence | Major | 4 |
| SC-19 | M4 | DA | outside count | same sentence, with `§4.11 "The inertia account predicts a lower share under a moving history."` | Major | 3 |
| SC-20 | Intervals and rank tests disagree; passes not analysed jointly | Methodology W6 | raised | `text: Section 4.4 "The interval includes zero, so the second pass alone does not meet the rule of Section 4.3."` | Minor | 4 |
| SC-21 | Checkpoints not among deposited materials | Methodology W7 | raised | `absence: Section 6 Data availability and Code availability statements` (full anchor in S12) | Minor | 4 |
| SC-21 | Checkpoint-specific claims without stated release | Perspective W6 | raised | `absence: Section 6 availability statements` | Minor | 3 |
| SC-22 | Repeat test given confirmatory weight | Methodology W8 | raised | `text: Abstract "where a pre-specified test was met"` | Minor | 4 |
| SC-22 | Lesser point 3 | DA | outside count | `text: §4.1` | below Major | 4 |
| SC-23 | Similarity inferred from non-rejection | Methodology W9 | raised | `text: Section 4.10 "The comparator is the per-route mean of the two default-controller passes of each of the other two models."` | Minor | 3 |
| SC-24 | Inertia and conjecture presented as rivals; visual route untested | Domain W1 | raised | as SC-19 | Major | 4 |
| SC-25 | H3 statistic is nearly gate-held standstill | Domain W3 | raised | `text: Section 4.3 "H3 therefore shows that a controller-coupled plan statistic recurred when the same checkpoints were evaluated again"` | Minor | 4 |
| SC-26 | Conjecture asserted as fact; marginal against per-context shares | Domain W4 | raised | `text: Section 1 "For a policy that samples from the futures it was shown, this share matters"` | Minor | 3 |
| SC-27 | Replanning rate not stated | Domain W6 | raised | `absence: Sections 3.1, 3.4 and S3.4 on inference and control` (full anchor in S17) | Minor | 4 |
| SC-27 | Inference rate not stated | Perspective W7 | corroborated | as Perspective W7 above | Minor | 3 |
| SC-28 | Sample overlap of the decoupling set not reported | Domain W7 | raised | as SC-10, Domain W7 | Minor | 4 |
| SC-28 | M2 | DA | outside count | as SC-10, DA | Major | 4 |
| SC-29 | Related-work attributions | Domain W9 | raised | `text: Section 2 "find that the style of the expert significantly affects the trained policy"` | Minor | 3 |
| SC-30 | No comparison with established remedies | Domain W10 | raised | `text: Section 5, Limitation 6 "We did not compare against controller-side anti-stall rules or model-side remedies such as history dropout"` | Minor `[FIELD-NORM UNVERIFIED]` | 3 |
| SC-31 | Success Rate not reported | Domain W11 | raised | `absence: Table 3 and Sections 4.2, 4.3, S4.3` (full anchor in S20) | Minor | 4 |
| SC-32 | Name of "blocked time" | Perspective W2 | raised | `text: Section 4.7 "This is inferred from the command log, not from a contact sensor."` | Minor | 4 |
| SC-33 | Purposive verbs | Perspective W3 | raised | `text: Section 5 "In scenarios the policy cannot solve, one checkpoint waited and the others pushed."` | Minor | 4 |
| SC-33 | Path length cannot tell a wait from a missing start | Domain W2 and review body | corroborated | review body, "Argument accuracy"; W2 anchor as above | Major (parent W2) | 4 |
| SC-34 | One-axis framing in the introduction | Perspective W4 | raised | `text: Section 1, second paragraph "and one that never waits meets the obstacle"` | Minor | 3 |
| — | M2, three of four cells | DA | outside count | as SC-10, DA | Major | 4 |

### Disposition summary (over the 4 non-DA seats)

| Disposition | Sub-claims |
|---|---|
| [CONSENSUS-4] (agree 4, conflict 0) | SC-2 |
| [CONSENSUS-3] (agree 3, conflict 0) | none |
| [SPLIT] (conflict ≥ 1) | SC-14 (agree 1, conflict 1; silent: Journal-Fit, Perspective); SC-18 (agree 2, conflict 1; silent: Journal-Fit) |
| Corroborated finding (agree 2, conflict 0) | SC-1, SC-3, SC-7, SC-9, SC-10, SC-11, SC-12, SC-13, SC-17, SC-19, SC-21, SC-27, SC-33 |
| Single-seat finding (agree 1, conflict 0) | SC-4, SC-5, SC-6, SC-8, SC-15, SC-16, SC-20, SC-22, SC-23, SC-24, SC-25, SC-26, SC-28, SC-29, SC-30, SC-31, SC-32, SC-34 |

The self-reported confidence values are carried as disclosure only. They were not totalled, averaged or used to resolve any sub-claim.

### Points passed through without a roadmap item

These points have no numbered weakness in their card. They are recorded so that nothing in the cards is lost; none is a new comment by the synthesizer.

- Perspective, Minor Issues, first point: the related-work heading "Idling, freezing and over-caution" and the keyword class "caution" are the remaining uses of the word; a half-sentence that the class is a text label would close the point.
- DA lesser point 2: H2 is reported as met, but the only comparison free of the harness change is the one that does not meet the rule; the hypothesis list and Section 4.3 lead with "met". The methodology card credits the manuscript for stating the second-pass failure in the abstract; the two cards do not conflict on the facts.
- DA, unexamined premise: with every control at its training mean a plan from rest has an extent of 0.59 m, so the stay-put class at rest may contain a default output and not a sampled waiting mode. Related to S16 and S22.
- DA, alternative explanation 3: fine-tuning erodes a stopping behaviour of the pretrained policy at a rate that depends on run length. Related to R1 and S16.
- Questions for authors: Journal-Fit 1 to 4, Methodology (three, in the review body), Domain 1 to 7, Perspective 1 to 5. Each should be answered in the response letter.
- Suggested references: Domain gives three from memory and one search lead, all unverified by that seat; Perspective gives ISO 21448:2022 and ISO 34502:2022 and one unverified search lead. The authors should verify each before citing.
- No card reports text in the manuscript addressed to reviewers or to an AI; the perspective card states that it found none.


## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 8: RC (the initials before its parentheses do not spell it)
- Body, line 83: VLA (the initials before its parentheses do not spell it)
- Body, line 83: VLM (the initials before its parentheses do not spell it)
- Body, line 442: ICLR (the initials before its parentheses do not spell it)
- Body, line 444: CoRL (the initials before its parentheses do not spell it)
- Body, line 466: SFT (the initials before its parentheses do not spell it)
- Body, line 480: RSS (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 1 | Not defined | NOTES | 2 |
| Body | 4 | Not defined | AND | 2 |
| Body | 4 | Not defined | FILLS | 1 |
| Body | 4 | Not defined | LEFT | 1 |
| Body | 4 | Not defined | THEM | 1 |
| Body | 4 | Not defined | WHAT | 1 |
| Body | 5 | Not defined | FILLED | 7 |
| Body | 8 | Not defined | DS | 5 |
| Body | 8 | Not defined | ICC | 1 |
| Body | 16 | Not defined | PMLR | 4 |
| Body | 20 | Not defined | CUT | 1 |
| Body | 20 | Not defined | LENGTH | 1 |
| Body | 22 | Not defined | CLAIMS | 1 |
| Body | 22 | Not defined | OR | 1 |
| Body | 22 | Not defined | WHY | 1 |
| Body | 27 | Not defined | IPF | 1 |
| Body | 27 | Not defined | README | 8 |
| Body | 38 | Not defined | CFM | 2 |
| Body | 38 | Not defined | OT | 2 |
| Body | 49 | Not defined | CARLA | 19 |
| Body | 51 | Not defined | CVF | 15 |
| Body | 52 | Defined after first use | ICCV | 5 |
| Body | 53 | Not defined | MDP | 3 |
| Body | 53 | Not defined | NVIDIA | 6 |
| Body | 53 | Defined after first use | CVPR | 11 |
| Body | 55 | Not defined | BEV | 1 |
| Body | 55 | Not defined | LiDAR | 2 |
| Body | 56 | Not defined | NEW | 1 |
| Body | 56 | Defined after first use | ICML | 2 |
| Body | 57 | Not defined | BibTeX | 1 |
| Body | 59 | Not defined | FILES | 1 |
| Body | 59 | Not defined | IN | 1 |
| Body | 59 | Not defined | THE | 1 |
| Body | 63 | Not defined | LEAD | 5 |
| Body | 63 | Not defined | OPEN | 1 |
| Body | 69 | Not defined | END | 1 |
| Body | 136 | Not defined | VL | 1 |
| Body | 161 | Not defined | AV | 1 |
| Body | 187 | Not defined | GB | 1 |
| Body | 187 | Not defined | GPU | 1 |
| Body | 197 | Not defined | PID | 3 |
| Body | 199 | Not defined | FIGURE | 5 |
| Body | 207 | Not defined | RTX | 1 |
| Body | 217 | Not defined | BCa | 5 |
| Body | 400 | Not defined | W4A8 | 1 |
| Body | 415 | Not defined | CRediT | 1 |
| Body | 423 | Not defined | AI | 3 |
| Body | 434 | Not defined | BC | 1 |
| Body | 434 | Not defined | IEEE | 13 |
| Body | 436 | Not defined | VAD | 1 |
| Body | 438 | Not defined | ECCV | 3 |
| Body | 440 | Defined again | CVPR | 11 |
| Body | 446 | Defined again | CVPR | 11 |
| Body | 448 | Defined again | CVPR | 11 |
| Body | 450 | Defined again | ICCV | 5 |
| Body | 454 | Not defined | LLM | 1 |
| Body | 462 | Defined again | CVPR | 11 |
| Body | 468 | Defined again | CVPR | 11 |
| Body | 470 | Defined again | ICCV | 5 |
| Body | 474 | Defined again | CVPR | 11 |
| Body | 486 | Defined again | CVPR | 11 |
| Body | 494 | Not defined | CoT | 1 |
| Body | 502 | Not defined | KING | 1 |
| Body | 504 | Not defined | CAPS | 1 |
| Body | 506 | Defined again | ICCV | 5 |
| Body | 520 | Not defined | TITS | 1 |
