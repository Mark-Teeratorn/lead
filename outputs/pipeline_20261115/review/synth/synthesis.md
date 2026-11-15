# Editorial Decision Package

## Sprint Contract Audit (v3.6.2 Sprint Contract Synthesizer Protocol)

Contract: `reviewer/reviewer_full/v2`, mode `reviewer_full`, `panel_size` 5. Five usable Phase 2 cards: `eic`, `methodology`, `domain`, `perspective`, `da`. No panel shrinkage.

dimension_verdicts: [D1=warn, D2=warn, D3=warn, D4=warn, D5=warn, D6=block]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

The Devil's Advocate's CRITICAL table (da.md, Issue List, `#### CRITICAL`) has no rows, so there are no DA CRITICAL IDs to adjudicate. The adjudication list is therefore empty, and no rejection-rationale line is required. The DA card states: "No finding meets the singleton-Critical bar."

### Step 1: Role-scoped scoring matrix

Only assessed scores from seats in each dimension's `eligible_roles` are counted. All other cells are `not_assessed` and appear in neither numerator nor denominator.

| Dimension | Priority | Eligible roles | Assessed eligible scores | n | Verdict (worst) |
|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology=warn | 1 | warn |
| D2 domain_accuracy | mandatory | domain | domain=warn | 1 | warn |
| D3 argumentative_coherence | mandatory | da, methodology | da=warn, methodology=warn | 2 | warn |
| D4 cross_disciplinary_relevance | high | perspective | perspective=warn | 1 | warn |
| D5 writing_and_structure | normal | eic | eic=warn | 1 | warn |
| D6 venue_fit_and_contribution | mandatory | eic | eic=block (`block_class: repairable`) | 1 | block |

No seat declared a fatal block, so no dimension is `block(fatal)`.

### Step 2: Failure-condition evaluation

| Condition | Severity | Quantifier | Expression (pattern) | Evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block (pattern 6) | No fatal block on D1, D2, D3 or D6 | false |
| F2 | 90 | any | any mandatory dimension scores 'block' (pattern 1) | D6: 1 of 1 eligible seat (eic) scores block, which satisfies `any` | true |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse (pattern 2) | Per dimension, majority of assessed eligible seats: D1 n=1, owner warn, true; D2 n=1, owner warn, true; D3 n=2, both seats needed, both warn, true; D6 n=1, owner block, true. Four of four mandatory dimensions, so at least two | true |
| F4 | 60 | any | any high-priority dimension scores 'block' (pattern 1) | D4 is the only high-priority dimension and scores warn | false |
| F5 | 40 | any | any dimension scores 'warn' or worse (pattern 7) | All six dimensions are warn or worse | true |
| F0 | 10 | all | every dimension scores 'pass' (pattern 9) | No dimension is pass | false |

All six expressions parse against the recognised vocabulary. No `[EXPRESSION-UNRECOGNISED]` or `[DIMENSION-UNASSESSED]` marker applies.

### Step 3: Precedence

Three conditions fired: F2 (90), F3 (70) and F5 (40). The highest severity is F2, whose action is major revision. F3 carries the same action. The DA-CRITICAL-vs-accept marker does not apply, because the decision is not accept and the DA has no CRITICAL IDs.

### Binding conformance (unbound run)

The target is not bound to a venue (`criteria_binding_unavailable`). The protocol requires every card to disclose this. Three cards do: eic.md (D6 basis and Detailed Comments), domain.md (Reviewer Identity) and da.md (Criterion-Bound Judgements). **Flag:** methodology.md and perspective.md contain no `criteria_binding_unavailable` disclosure. Neither card makes a venue-alignment claim. The perspective card uses "the venue's readers" once, as a scope limit and not as a fit claim. The synthesizer does not edit cards, so this flag is passed to the orchestrator. Binding conformance is not a score, a failure condition or an editorial verdict, and it does not affect the arithmetic above. This package makes no venue-specific claim.

### Cross-model decision check

`ARS_CROSS_MODEL` is not set in this run, so the optional blind cross-model check (#518) was not performed and no handoff envelope is emitted.

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

[Current runtime boundary: do not upgrade this package from a candidate or prose-named profile. `PROFILE_MEASURED` remains unavailable until a closed profile artifact and replay validator bind the exact target fields to the actual completed-panel `execution_topology_sha256`.]

All five seats also report `NOT_CALIBRATED`.

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript titled "Fine-Tuning Data Composition and Low-Speed Hesitation in a Vision-Language-Action Driving Policy: A Matched-Pair, Single-Seed Study". No venue is bound to this review (`criteria_binding_unavailable`), so this letter makes no claim about fit to any particular outlet. Your manuscript was reviewed through five role-separated review seats: a Journal-Fit Reviewer, Methodology (R1), Domain (R2), Perspective (R3) and the Devil's Advocate (DA). Their execution provenance is reported below and is not reduced to a binary independence claim.

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

Family-unknown disclosure: the model family behind each seat is unknown to the synthesizer. The five seats may share one model family, in which case their errors may be correlated, and agreement among them should not be read as independent confirmation.

### Decision: Major Revision

The decision is derived mechanically from the contract. Condition F2 fired because the Journal-Fit Reviewer scored D6 (venue_fit_and_contribution, a mandatory dimension) `block`, with `block_class: repairable`. F3 (four mandatory dimensions at warn or worse) and F5 also fired. F2 has the highest severity, and its action is major revision.

### Consensus Analysis

Consensus is counted per sub-claim over the four non-DA seats (Journal-Fit Reviewer, R1, R2, R3). The full inventory is in the Appendix (Step 1b).

#### Points of Agreement (Consensus)

- [CONSENSUS-3] **SC-1: the headline attributes the plan-level difference to the fine-tuning mix, but one checkpoint per mix cannot separate the mix from the training run, and `Golden-6400` is the outlier among all six checkpoints.** Raised by the Journal-Fit Reviewer (W1), R1 (W1) and R2 (W4), all at Major severity. R3 is silent on this sub-claim. The DA corroborates independently (M1, "Strongest Counter-Argument"). The minimum remedy is the same in all three cards: reword the title, abstract, Section 1 findings and contributions, Section 5 and the Conclusion as a contrast between two checkpoints, and state the outlier pattern there.
- [CONSENSUS-3] **SC-2: further training seeds of each 6,400-sample arm would decide the attribution.** The Journal-Fit Reviewer (W1), R1 (W1) and R2 (W4) each name this as the stronger, optional route. R3 is silent.
- Corroborated findings (2 of 4, no conflict):
  - SC-17: plan distributions are never compared on identical inputs (R1 W2, R2 W1; DA M2).
  - SC-18: blocked time is not separated in time from contact (R1 W3, R3 W3; DA M3).
  - SC-11: the two-pass Driving Score supports "not higher", not "lower" (Journal-Fit W5, R1 W5; DA m4).
  - SC-23: the six evaluated checkpoints are not released and the server noise is unseeded (R1 W9, R3 W4).
- Single-reviewer findings retained on their anchored evidence. Major: SC-6 (Journal-Fit W2), SC-19 (R1 W4), SC-25, SC-26 and SC-27 (R2 W1, W2, W3), SC-35 (R3 W2; DA M4). The Minor findings are listed in Part 2.

#### Points of Disagreement

No sub-claim is disputed on substance except SC-3. The other SPLITs are severity disagreements: two seats raise the same sub-claim under parent findings with different severity tags. Every severity below is transported unchanged.

- **SC-3: the sampling conjecture is cited as consistent without the evidence against it.** The Journal-Fit Reviewer (W1, Major), R1 (W11, Minor) and R2 (W4, Major) say that Section 5 cites consistency with the conjecture of Section 3.2 without the 1,600-sample null or the fact that `Golden-6400` plans to stay put below its own training share. R3's Assumption Audit says the conjecture "is labelled post hoc and untested, and the authors note that it does not predict the 1,600-sample result. This is handled correctly."
  - **Editor's Resolution**: retained as required (R2). The two positions refer to different places in the manuscript. R3's statement is accurate for Section 3.2. The Section 5 sentence ("This is consistent with the conjecture of Section 3.2 ... and the training sets differ nearly threefold in that share") carries no such qualifier, which can be checked directly in the manuscript. The fix is to move the disconfirming observations into the same sentence. R3's assessment of Section 3.2 stands.
- **SC-4: H1 has no result against its specified comparator.** The Journal-Fit Reviewer rates this Major (W2), and R1 rates it Minor (W12: "This affects only H1").
  - **Editor's Resolution**: required (R3). Both seats ask for the result against `Base-Rerun`. Methodology is R1's domain, and R1's point that H2, H3, R2 and R3 do not depend on H1 is accepted and recorded. This is a legitimately pending result, not a defect of reporting integrity.
- **SC-5: the decoupling model and the motion-history swap test are unreported.** The Journal-Fit Reviewer rates this Major (W2, because the decoupling result bears on how the composition effect is read), and R3 rates it Minor (W7, practical lesson).
  - **Editor's Resolution**: required (R4). The work is to report the results, or else to remove their forward references (the Journal-Fit Reviewer's own fallback). Both severities stand. These results are legitimately pending.
- **SC-7: the archive DOI and code commit are pending.** The Journal-Fit Reviewer rates this Major (W2), and R1 (W9) and R3 (W4) rate it Minor.
  - **Editor's Resolution**: required (R6). All three seats state that these items are needed before acceptance, so the action is not in dispute.
- **SC-8: the pre-specification record cannot be cited or checked.** The Journal-Fit Reviewer rates this Major (W3), and R1 rates it Minor (W6: "The probable impact is small").
  - **Editor's Resolution**: required (R7). Both ask for the same deposit with per-section commit identifiers. R1's view that the impact on the inferences is small is a methodology judgement within R1's remit and is recorded. The Journal-Fit Reviewer's point concerns reader verifiability and stands separately.
- **SC-9: "replicated" describes a re-run of the same checkpoints.** The Journal-Fit Reviewer rates this Minor (W4). R1 raises it inside the Major parent W1 ("state ... that the replication addresses evaluation noise only").
  - **Editor's Resolution**: required (R8). It is a wording change, the remedies are identical, and the DA's m1 concurs.
- **SC-10: the "Less hesitation has a cost" and "trade-off" headline is stronger than one matched contrast and a post hoc quantity support.** The Journal-Fit Reviewer rates this Minor (W5), and R3 rates it Major (W1).
  - **Editor's Resolution**: required (R9) as rewording to the Discussion's scoped wording. Both minimum remedies coincide. R3's six-model frontier plot remains the author's option. R11 bears on how the cost can be stated.

### Decision Rationale

The panel agrees on what the paper does well. The pre-specification record is unusually explicit (Journal-Fit S1, R1 S2). The gate-off run separates model from controller (Journal-Fit S2, R2 S2, R3 S1). The H3 plan-level difference held across a second pass under a rule fixed in advance (Journal-Fit S3, R1 summary). Measures that were artefacts of their construction were withdrawn (R1 S6, R2 S1). The safety language is proportionate (Journal-Fit S5, R3 S3). No seat found an internal numerical inconsistency (R1 Recomputation notes), and the DA found that the scoped core claim, that these two checkpoints differ in their closed-loop plans, survives every rival it raised.

The decision rests on fired condition F2. The Journal-Fit Reviewer's D6 block is repairable and has three bases: W1 (attribution), W2 (pending results and statements) and W3 (an uncitable pre-specification record). The attribution concern is the panel's strongest consensus (SC-1, three of four seats plus the DA). Its minimum repair is rewording, not new training. F3 also fired, independently: all four mandatory dimensions are at warn or worse, and R1, R2 and the DA each identify rival readings that are not yet tested but can be tested from existing logs. These are same-input plans (SC-17), blocked-time onset relative to contact (SC-18), controller coupling of H3 (SC-26), the deployed sampler (SC-27) and at-rest denominators (SC-25). Several reviewers note that most of these need re-analysis of logs already in hand, not new closed-loop runs (R3 Overall Recommendation; DA D3 basis).

Three results are legitimately pending: H1 against `Base-Rerun`, the decoupling model and the motion-history swap test. The roadmap requires them before acceptance (or, for the latter two, removal of their forward references); their placeholders are not treated as a reporting defect. The DA raised no CRITICAL issue. Confidence scores carried no weight. The revision will be re-reviewed.

### Devil's Advocate Critical Issues

The DA's CRITICAL table is empty, so there is nothing to adjudicate (`da_critical_adjudications: []` in the audit block). The DA's four MAJOR challenges are corroborated by non-DA seats and enter the roadmap through those seats' sub-claims: M1 → SC-1 and R1; M2 → SC-17 and R10; M3 → SC-18 and R11; M4 → SC-35 and R16. The author should answer each of them in the response letter.

### Blocking Issues (0–3, immutable source order)

These are the bases of the D6 block that fired F2, in roadmap source order.

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---------------|----------------|--------------------|-----------------|------------------------|
| R1 | Composition attribution exceeds a one-checkpoint-per-arm design; `Golden-6400` is the outlier among six checkpoints | EIC (W1), R1 (W1), R2 (W4), DA (M1) | text: §4.6 Plans at low speed, pooled paragraph "the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | REV-R1 |
| R3 | Pending results, required statements and placeholders in the abstract and Conclusion | EIC (W2, W10), R1 (W9, W12), R3 (W4, W7) | text: §5 Limitation 7 "so H1 awaits the re-run" | REV-R3, REV-R4, REV-R5, REV-R6 |
| R7 | The pre-specification record behind the confirmatory claims cannot be cited or checked | EIC (W3), R1 (W6) | absence: reference list and Data and Code availability statements — expected a citable, persistent copy of ANALYSIS_ADDENDUM with per-section commit identifiers; checked references 1 to 47, Data availability, Code availability, §4.1 Record of pre-specification | REV-R7 |

---

## Part 2: Revision Roadmap

> The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) each item traces to (e.g. `SC-1`), so the decomposed granularity survives to the output boundary. A pre-decomposition / DA-CRITICAL item that has no sub-claim id uses `—`.

`schema_version: revision-roadmap/1.0`. Items appear in immutable source order: seat order EIC, R1 (Methodology), R2 (Domain), R3 (Perspective), DA; then finding ordinal; then sub-claim ordinal. Each seat's unnumbered lists (the EIC Minor Issues, the DA minor challenges) follow its numbered findings. Severity, obligation and cost do not affect the order. In the Source column, "Meth", "Dom" and "Persp" denote the R1, R2 and R3 seats, so that they are not confused with the `R<n>` transport refs. No block manifest was bound to this run, so no `proposed_targets[]` block ids are emitted. Severity and confidence are transported from the cards, one value per source finding.

### Required Revisions (Must Fix)

> **Ordinal contract (#576/#670):** `R<n>` follows immutable roadmap source order filtered to `obligation_class == must_fix`; author-selected display order and triage never enter the derivation. Blocks are exactly `R1..Rn`. Each Acceptance criteria value is a single-line `- **Acceptance criteria**: <text>` bullet. The machine artifact is the closed `revision-roadmap/1.0` core, not an author-editable work list.

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|--------|------------------|------------|---------------------|
| R1 | Restate the composition attribution as a contrast between two checkpoints; state that `Golden-6400` differs from all five other checkpoints and bring the six-model comparison forward | SC-1 | Major (EIC W1); Major (Meth W1); Major (Dom W4) | text: §4.6 Plans at low speed, pooled paragraph "the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | 4 (EIC); 4 (Meth); 4 (Dom) | EIC W1; Meth W1; Dom W4; DA M1 | must_fix | section: title, abstract, §1 findings and contributions, §5, Conclusion | claim_scope_unsupported; claim: headline attribution of the plan-level difference to the mix |
| R2 | Put the disconfirming observations (1,600-sample null; `Golden-6400` below its own training share; braking order reversed at 1,600) in the same sentence as each claim of consistency with the conjecture | SC-3 | Major (EIC W1); Minor (Meth W11); Major (Dom W4) | text: Section 5, second paragraph, "This is consistent with the conjecture of Section 3.2" | 4 (EIC); 4 (Meth); 4 (Dom) | EIC W1; Meth W11; Dom W4; DA m2 | must_fix | sentence: §5 second paragraph, §4.5, §1 findings list (braking ratio) | interpretive_ambiguity_remains; section: §5 Discussion |
| R3 | Report H1 against its specified comparator `Base-Rerun` (pending), and complete the Tables 2 to 4 rows, §4.3 and the 24-route comparison | SC-4 | Major (EIC W2); Minor (Meth W12) | text: §5 Limitation 7 "so H1 awaits the re-run" | 5 (EIC); 5 (Meth) | EIC W2; Meth W12 | must_fix | new_data: `Base-Rerun` closed-loop run; Tables 2 to 4, §4.3 | acceptance_criterion_unmet; claim: H1 |
| R4 | Report the decoupling model and the motion-history swap test (pending) and write the dependent Discussion text from their results, or remove their forward references | SC-5 | Major (EIC W2); Minor (Persp W7) | text: §3.3 "Comparisons between regimes therefore estimate the effect of the bundle." | 5 (EIC); 4 (Persp) | EIC W2; Persp W7 | must_fix | new_data: decoupling-model evaluation and swap test; §5 | evidence_gap_remains; claim: which factor of the bundle carries the effect, and the §5 mechanism sentence |
| R5 | Resolve the abstract and Conclusion placeholders; supply the CRediT, funding and competing-interest statements and the authors' AI-verification and responsibility statement | SC-6 | Major (EIC W2); Minor (EIC W10) | text: §6 AI assistance disclosure "Most commits of the revision were made with AI assistance." | 5 (EIC W2); 5 (EIC W10) | EIC W2; EIC W10 | must_fix | section: abstract, Conclusion, §6 statements | reporting_requirement_unmet; manuscript: front and back matter |
| R6 | Supply the archive DOI for logs and trainer artifacts and the code commit hash | SC-7 | Major (EIC W2); Minor (Meth W9); Minor (Persp W4) | absence: Section 6, Data availability and Code availability — expected a release statement for the six evaluated checkpoints and a fixed commit for both analysis scripts; checked Section 6 Data availability, Code availability, Section 3.4 and Table 2 | 5 (EIC); 4 (Meth); 4 (Persp) | EIC W2; Meth W9; Persp W4 | must_fix | other (availability_statements): §6 Data and Code availability | method_reproducibility_unresolved; section: §6 |
| R7 | Deposit ANALYSIS_ADDENDUM as citable supplementary material with the commit hash and time of each section, cite it formally, and give third-party evidence of timing | SC-8 | Major (EIC W3); Minor (Meth W6) | absence: reference list and Data and Code availability statements — expected a citable, persistent copy of ANALYSIS_ADDENDUM with per-section commit identifiers; checked references 1 to 47, Data availability, Code availability, §4.1 Record of pre-specification | 4 (EIC); 4 (Meth) | EIC W3; Meth W6 | must_fix | other (supplementary_material): ANALYSIS_ADDENDUM deposit; reference list; §4.1 | reader_traceability_reduced; claim: pre-specified status of H3, R2, R3 and the §10 criterion |
| R8 | Qualify "replicated" and "reproduced" as a second closed-loop pass of the same checkpoints, which addresses evaluation noise and not training-run variance | SC-9 | Minor (EIC W4); Major (Meth W1) | text: §5 opening paragraph "the change was reproduced in a second pass under rules fixed in advance" | 4 (EIC); 4 (Meth) | EIC W4; Meth W1; DA m1 | must_fix | sentence: abstract, §1 findings, §5, Conclusion | claim_scope_unsupported; claim: replication of the composition effect |
| R9 | Reword the §1 finding "Less hesitation has a cost" and contribution (iii) as an observation in this pair, matching the Discussion | SC-10 | Minor (EIC W5); Major (Persp W1) | text: §1 contribution (iii) "the observation that the resulting difference is a trade-off between hesitation and time blocked, not an improvement on the benchmark's score" | 4 (EIC); 4 (Persp) | EIC W5; Persp W1 | must_fix | sentence: §1 third finding, contribution (iii) | claim_scope_unsupported; claim: trade-off between hesitation and blocked time |
| R10 | Compare the two experts on identical low-speed inputs (offline, many noise draws, paired over inputs), or restate the plan-level results as closed-loop rates in self-generated states | SC-17 | Major (Meth W2); Major (Dom W1) | text: Section 4.6, Near-stationary plans, "The two models visit different states in closed loop, so this is not a same-input comparison." | 4 (Meth); 4 (Dom) | Meth W2; Dom W1; DA M2 | must_fix | re_analysis: offline expert queries on the 1,567-sample validation split and logged low-speed states; §4.6 | claim_scope_unsupported; claim: "what the policy planned once it was slow" |
| R11 | For every blocked run, report its onset relative to the route's collision timestamps and actor; classify it as before contact, after contact, or with no prior contact; report blocked time without post-contact runs, with a per-route listing; restate the cost accordingly | SC-18 | Major (Meth W3); Major (Persp W3) | text: Section 4.7, Blocked time, "Every route with blocked time has at least one collision event" | 3 (Meth); 3 (Persp) | Meth W3; Persp W3; DA M3 | must_fix | re_analysis: leaderboard collision records and command logs; §4.7 | evidence_gap_remains; claim: contribution (iii), cost of less hesitation |
| R12 | State in the abstract and Conclusion that the pass-1 H2 arms ran on different harness versions and that the only same-harness test gave case B | SC-19 | Major (Meth W4) | text: Section 4.1, Harness changes between the H2 arms, "We expect these changes to be behaviour-neutral on these routes, but this has not been shown." | 3 (Meth) | Meth W4 | must_fix | sentence: abstract, Conclusion | interpretive_ambiguity_remains; claim: H2 |
| R13 | Report at-rest and low-speed stay-put shares excluding blocked runs, and stratified by why the vehicle is at rest (gate-held, blocked, other) | SC-25 | Major (Dom W1) | text: §4.6 "The two models visit different states in closed loop, so this is not a same-input comparison." | 4 (Dom) | Dom W1 | must_fix | re_analysis: existing step logs; §4.6 | evidence_gap_remains; table: at-rest and low-speed stay-put shares |
| R14 | Describe H3 as a replication of a controller-coupled plan statistic, and argue the model-side origin from the gate-off, speed-conditioned shares | SC-26 | Major (Dom W2) | text: §1 H3 "produces near-stationary plans, with a predicted path shorter than 1.5 m, in a smaller share of steps than" | 4 (Dom) | Dom W2; DA m5 | must_fix | section: §1 H3, §4.3, abstract, Conclusion | claim_scope_unsupported; claim: H3 as support for a model-level statement |
| R15 | Restate §3.2 and §5 so that the sampling conjecture holds only in the exact-sampling limit, and name the deployed four-evaluation sampler as a rival mechanism | SC-27 | Major (Dom W3) | text: §3.2 "Each inference call therefore returns a sample from the conditional distribution, not its mean." | 4 (Dom) | Dom W3 | must_fix | section: §3.2, §5 | interpretive_ambiguity_remains; section: §3.2 stay-put sampling conjecture |
| R16 | Define "hesitation" operationally (a stay-put plan in a low-speed context, whether or not a stop was required), or replace it in the title and findings with a descriptive term | SC-35 | Major (Persp W2) | text: Title "Low-Speed Hesitation in a Vision-Language-Action Driving Policy" and §4.8 Strata "so we cannot tell when stopping was required" | 4 (Persp) | Persp W2; DA M4 | must_fix | sentence: title, abstract or §1 definition, §1 and §5 findings | interpretive_ambiguity_remains; claim: title term "hesitation" |

### Required Item Details

#### R1 — Composition attribution (SC-1)
- Minimum remedy: Journal-Fit W1, R1 W1 and R2 W4. The stronger option (further seeds) is S1.
- **Acceptance criteria**: The title, abstract, §1 findings and contributions, §5 and the Conclusion describe the result as a difference between two checkpoints whose dependence on composition across training runs is untested, and they state that `Golden-6400` is distinct from the other five checkpoints.

#### R2 — Conjecture cited with its counter-evidence (SC-3)
- Minimum remedy: R1 W11 ("put the disconfirming observations in the same sentence as each consistency claim").
- **Acceptance criteria**: Every sentence that calls a result consistent with the Section 3.2 conjecture also states, in that sentence, the 1,600-sample null and the gap between `Golden-6400`'s stay-put share and its training share, and the §1 braking ratio carries the §4.6 outlier and reversal caveat.

#### R3 — H1 against Base-Rerun (SC-4)
- Status: legitimately pending (`Base-Rerun`). It does not affect H2, H3, R2 or R3 (R1 W12).
- **Acceptance criteria**: H1 is reported against `Base-Rerun` with its pre-specified rule applied, the empty rows in Tables 2 to 4 and the §4.3 and 24-route comparisons are complete, and the abstract and Conclusion H1 sentences are written from that result.

#### R4 — Decoupling model and swap test (SC-5)
- Status: legitimately pending.
- **Acceptance criteria**: Both results are reported and the Discussion sentences that depend on them are written from them, or every forward reference to an unreported result is removed, so that no placeholder remains.

#### R5 — Placeholders and required statements (SC-6)
- **Acceptance criteria**: The abstract and Conclusion contain no placeholder, and the CRediT, funding, competing-interest and AI-verification statements are present, the last describing how the authors verified the scripts, the decision rules and the reported numbers.

#### R6 — DOI and code commit (SC-7)
- **Acceptance criteria**: §6 gives a resolvable archive DOI for the logs and trainer artifacts and a fixed code commit hash for both analysis scripts.

#### R7 — Citable pre-specification record (SC-8)
- **Acceptance criteria**: ANALYSIS_ADDENDUM is deposited as citable supplementary material and listed in the references, each cited section has its commit hash and commit time, and some form of third-party timing evidence is given (hosted-remote push times or a deposited snapshot).

#### R8 — "Replicated" wording (SC-9)
- **Acceptance criteria**: Every use of "replicated" or "reproduced" for the second pass says that it re-evaluated the same two checkpoints and addresses evaluation noise, not training-run variance.

#### R9 — Cost and trade-off headline (SC-10)
- Optional, at the author's discretion: R3 W1's descriptive six-model plot on both axes, labelled as confounded.
- **Acceptance criteria**: The §1 finding and contribution (iii) state the observation for this matched pair only (for example, "the balanced model had fewer stay-put plans and more blocked time") and are consistent with the outcome of R11.

#### R10 — Same-input comparison (SC-17)
- **Acceptance criteria**: Either a paired comparison of the two experts' stay-put rates on identical low-speed inputs is reported, or every plan-level claim is worded as a closed-loop rate in the states each model reached, with no propensity reading.

#### R11 — Blocked time and contact (SC-18)
- **Acceptance criteria**: For each blocked run, the onset relative to the route's collision events and actor is reported, blocked time is also given without post-contact runs together with a per-route listing, and the cost statement is restated to match.

#### R12 — H2 harness confound (SC-19)
- Optional (R1 W4): re-run a subset of `Golden-6400` routes on the old harness.
- **Acceptance criteria**: The abstract and Conclusion state that the pass-1 H2 arms ran on different harness versions and that the only same-harness comparison (pass 2) gave case B.

#### R13 — At-rest denominator (SC-25)
- **Acceptance criteria**: At-rest and low-speed stay-put shares are reported for both models excluding blocked runs and stratified by gate-held, blocked and other at-rest states.

#### R14 — H3 controller coupling (SC-26)
- Optional (R2 W2): a second gate-off pass with the at-rest stay-put share as its pre-specified endpoint.
- **Acceptance criteria**: H3 is described wherever it appears as a replication of a controller-coupled plan statistic, and the model-side argument is made from the gate-off, speed-conditioned shares.

#### R15 — Sampler as rival mechanism (SC-27)
- Optional (R2 W3): compare the deployed sampler with an exact many-step integration on logged low-speed contexts.
- **Acceptance criteria**: §3.2 and §5 state that the conjecture holds only in the exact-sampling limit, and they name the four-evaluation sampler's possible pull toward the mean as a rival mechanism.

#### R16 — "Hesitation" (SC-35)
- Optional (R3 W2): label required stops offline from CARLA ground truth.
- **Acceptance criteria**: "Hesitation" is either defined operationally at first use in the abstract or introduction, regardless of whether a stop was required, or replaced in the title and findings by a descriptive term.

### Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|--------|------------------|------------|---------------------|
| S1 | Train at least two further seeds or data-order permutations of each 6,400-sample arm and report plan-level measures with a between-seed component | SC-2 | Major (EIC W1); Major (Meth W1); Major (Dom W4) | text: §4.6 Plans at low speed, pooled paragraph "the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | 4 (EIC); 4 (Meth); 4 (Dom) | EIC W1; Meth W1; Dom W4 | should_fix | new_data: further training runs of both 6,400-sample arms | evidence_gap_remains; claim: composition effect across training runs |
| S2 | Write "not higher" for the two-pass Driving Score in the abstract and introduction, and report the pass-2 difference with its interval | SC-11 | Minor (EIC W5); Minor (Meth W5) | text: Abstract, "its two-pass Driving Score was 5.67 points lower (rank test p = 0.11)" | 4 (EIC); 4 (Meth) | EIC W5; Meth W5; DA m4 | should_fix | sentence: abstract, §1; §4.4 | claim_scope_unsupported; claim: Driving Score difference |
| S3 | Render Figures 1 to 5, with Fig. 5b marking the training-set share | SC-12 | Minor (EIC W6) | absence: §3.4, §4.2, §4.5 and §4.6 figure positions — expected rendered Figures 1 to 5; checked the five FIGURE caption markers and the Table 3 to 6 captions | 5 (EIC) | EIC W6 | should_fix | other (figures): Figures 1 to 5 | editorial_conformance_unmet; figure: Figures 1 to 5 |
| S4 | Move revision-history remnants from the body to the response letter | SC-13 | Minor (EIC W7) | text: §3.2 "The previous version of this manuscript argued the opposite; that argument treated the flow as a regressor and is withdrawn." | 5 (EIC) | EIC W7 | should_fix | section: body text throughout | reader_traceability_reduced; manuscript: body text |
| S5 | Limit the abstract to the headline numbers, split Table 4 into decomposition and strata tables, and move the secondary sensitivity prose of §§4.6 to 4.8 to the supplement | SC-14 | Minor (EIC W8) | table: Table 4, standstill decomposition and frozen strata (19 columns) | 4 (EIC) | EIC W8 | should_fix | section: abstract, Table 4, §§4.6 to 4.8 | reader_traceability_reduced; table: Table 4 |
| S6 | Move contribution (iv), single-GPU serving, to a reproducibility or availability paragraph | SC-15 | Minor (EIC W9) | text: §1 contributions paragraph "an open setup in which a 10B-parameter VLA policy, fine-tuned on an A100 machine" | 4 (EIC) | EIC W9 | consider | sentence: §1 contributions | claim_scope_unsupported; claim: contribution (iv) |
| S7 | Make the p-value notation consistent in §4.6; use one time convention in Table 2; say how the gate-off controller variant was produced | SC-16 | minor [SEVERITY-SOURCE: letter-fallback] | text: EIC Minor Issues list (§4.6 p-values, Table 2 dates, §3.4 controller thresholds) | not stated on the card | EIC Minor Issues | consider | sentence: §4.6, Table 2, §3.4 | editorial_conformance_unmet; section: §3.4, §4.6, Table 2 |
| S8 | Carry into §5 the qualifier that R2 and R3 were committed after 14 of the 44 second-pass `Golden-6400` routes had been seen | SC-20 | Minor (Meth W6) | text: Section 4.1, Record of pre-specification, "they were not time-stamped by a third party" | 4 (Meth) | Meth W6 | should_fix | sentence: §5 | interpretive_ambiguity_remains; claim: R2 and R3 "fixed in advance" |
| S9 | Name the estimand next to each inferential statement; keep decisions on the pre-specified interval; consider Hodges–Lehmann estimates | SC-21 | Minor (Meth W7) | table: Table 5, rows for the 37 routes without training overlap, standstill in seconds, and the second pass alone | 4 (Meth) | Meth W7 | should_fix | sentence: §4 inferential statements; Table 5 | interpretive_ambiguity_remains; table: Table 5 |
| S10 | For zero-inflated outcomes, print the number of non-zero routes next to each p, give per-route values, and use exact sign or permutation tests | SC-22 | Minor (Meth W8) | text: Section 4.7, Blocked time, "(2 runs on 1 route), a difference of +7.57 pp" | 4 (Meth) | Meth W8 | should_fix | re_analysis: blocked time, pedestrian contacts, per-stratum comparisons | evidence_gap_remains; section: §4.7, §4.8 |
| S11 | Release the six evaluated checkpoints or state why they cannot be released; add an option to seed or log the server noise | SC-23 | Minor (Meth W9); Minor (Persp W4) | text: §6 Data availability "The four Matrix fine-tuning datasets and the decoupling dataset are on the Hugging Face Hub" and §3.4 "The model server does not seed its noise draws" | 4 (Meth); 4 (Persp) | Meth W9; Persp W4 | should_fix | other (release_artifacts): checkpoints and server seeding option; §6 | method_reproducibility_unresolved; dataset: six evaluated checkpoints |
| S12 | Give intervals for the small strata, the 0.1 to 0.5 m/s at-rest band and the §4.8 Spearman correlations, or drop their p-values | SC-24 | Minor (Meth W10) | text: Section 4.8, Strata, "Overtaking (9 routes) gave −8.28 pp (p = 0.0039) and Merging (16) −12.18 pp (p = 0.034)" | 5 (Meth) | Meth W10 | should_fix | re_analysis: §4.6, §4.8 | reporting_requirement_unmet; section: §4.8 |
| S13 | Compare stop and restart per stop episode (entry rate and time to plan a start), not as per-step shares in different bands | SC-28 | Minor (Dom W5) | text: §1 "the difference is much larger once the vehicle is at rest" | 4 (Dom) | Dom W5 | should_fix | re_analysis: stop episodes in §4.7; §1 sentence | interpretive_ambiguity_remains; claim: difference lies mainly in restarting |
| S14 | Engage with the data-amount and data-bias results in [12] as the closest data-side antecedent | SC-29 | Minor (Dom W6) | text: §2 "proposed an auxiliary speed-prediction branch so that the network must estimate speed from images" | 3 (Dom) | Dom W6 | should_fix | section: §2 | reader_traceability_reduced; section: §2 related work |
| S15 | Cite controller-side anti-stall practice (for example the TransFuser agent) and discuss how it would interact with the blocked-time finding | SC-30 | Minor (Dom W7) | text: §2 "Closed-loop agents can also include controller-side anti-stall rules, such as creeping forward after a fixed time at rest; we do not survey them." | 4 (Dom) | Dom W7 | should_fix | section: §2, §5 | reader_traceability_reduced; section: §2 |
| S16 | State that the target speed, gate and L-based measures rely on the speed-from-waypoints representation questioned in [40] | SC-31 | Minor (Dom W8) | text: §3.4 "The target speed follows the trajectory: it is the planned speed to the lookahead waypoint" | 4 (Dom) | Dom W8 | should_fix | sentence: §3.4, §5 | interpretive_ambiguity_remains; section: §3.4 |
| S17 | State the rendering quality at which training data were recorded, and list the visual domain shift as a possible moderator | SC-32 | Minor (Dom W9) | text: §4.1 "all 44 routes lie in other towns, so every model ran at Low" | 3 (Dom) | Dom W9 | should_fix | sentence: §4.1, §5 Limitations | interpretive_ambiguity_remains; section: §5 Limitations |
| S18 | Describe π0, π0.5 and Alpamayo as VLM-plus-action-expert designs, or define "dual-system" | SC-33 | Minor (Dom W10) | text: §1 "In dual-system designs such as" | 3 (Dom) | Dom W10 | consider | sentence: §1 | interpretive_ambiguity_remains; section: §1 |
| S19 | Cite the original naming of the freezing robot problem (Trautman and Krause, IROS 2010), alone or alongside [42] | SC-34 | Minor (Dom W11) | text: §2 "the freezing robot problem [42] denotes a planner that judges every forward path through a dense crowd unsafe and stops" | 4 (Dom) | Dom W11 | should_fix | sentence: §2; reference list | reader_traceability_reduced; section: §2 |
| S20 | Add one table defining every construct and threshold (where it is defined; whether it is plan-, motion- or command-level), and carry the "issues no start" reading into the abstract | SC-36 | Minor (Persp W5) | text: §5 Discussion "In this action space a plan that stays put at rest is a plan without acceleration" | 4 (Persp) | Persp W5 | should_fix | other (definitions_table): new table; abstract | reader_traceability_reduced; table: construct definitions |
| S21 | Add a Limitations paragraph on the costs that waiting or blocking imposes on other road users, which scripted CARLA traffic does not represent | SC-37 | Minor (Persp W6) | absence: §2, §4 and §5 — expected a statement of how scripted CARLA traffic reacts to an ego vehicle that waits or is blocked, and what that means for interpreting both behaviours in mixed traffic; checked §2 Closed-loop evaluation, §4.1, §4.8 Gap-waiting, §5 Limitations 1 to 9 and Future work | 3 (Persp) | Persp W6 | consider | section: §5 Limitations | interpretive_ambiguity_remains; section: §5 Limitations |
| S22 | Add a clause to the introduction's safety-case framing stating that the study measures position on the waiting axis but cannot place it relative to safety | SC-38 | Minor (Persp W8) | text: §1 "Where a policy sits between the two is what a benchmark score and a safety case both depend on." | 3 (Persp) | Persp W8 | should_fix | sentence: §1 second paragraph | interpretive_ambiguity_remains; section: §1 |
| S23 | For the 1,600-sample pair, report the per-route paired comparison of low-speed stay-put plans with a BCa interval, as is done for the 6,400-sample pair | — | Minor (DA m3) | absence: §4.6 and Table 6 — expected a per-route paired comparison of low-speed stay-put plans for Golden-1600 vs Flooded-1600 with a BCa interval; checked §4.6, Table 6, Table 4, §4.8, Figure 5 caption | 4 (DA) | DA m3 (see also Dom Question 5) | consider | re_analysis: existing 1,600-sample logs; §4.6 | evidence_gap_remains; claim: generality beyond the 6,400-sample pair |

> Transported metadata reaches the emitted package ON EVERY ROW, never dies in the Step 1b working inventory (#574 A2/A3): each item carries the driving sub-claim's transported Severity (fallback tags like `[SEVERITY-SOURCE: letter-fallback]` travel with it), the finding's typed Evidence Anchor, and its per-finding Confidence — for every roadmap item, not only the ≤3 Top Blocking rows. Schema 7 `RoadmapItem` carries the same three optional fields for machine consumers.

Totals: 16 required revisions (must_fix, R1 to R16) and 23 suggested revisions (18 should_fix and 5 consider, S1 to S23).

### Source-Traceability Checklist

> Preserve source order and do not suggest a work order. Author triage is
> collected later as an explicit, complete sidecar.

- [ ] R1 — obligation `must_fix`: Restate the composition attribution as a two-checkpoint contrast and state the `Golden-6400` outlier pattern (SC-1)
- [ ] S1 — obligation `should_fix`: Further seeds of each 6,400-sample arm (SC-2)
- [ ] R2 — obligation `must_fix`: Disconfirming observations next to each conjecture-consistency claim (SC-3)
- [ ] R3 — obligation `must_fix`: H1 against `Base-Rerun` (SC-4)
- [ ] R4 — obligation `must_fix`: Decoupling model and swap test reported, or forward references removed (SC-5)
- [ ] R5 — obligation `must_fix`: Placeholders resolved; CRediT, funding, competing-interest and AI-verification statements (SC-6)
- [ ] R6 — obligation `must_fix`: Archive DOI and code commit (SC-7)
- [ ] R7 — obligation `must_fix`: Citable ANALYSIS_ADDENDUM with per-section commits (SC-8)
- [ ] R8 — obligation `must_fix`: Qualify "replicated" and "reproduced" (SC-9)
- [ ] R9 — obligation `must_fix`: Reword the cost and trade-off headline (SC-10)
- [ ] S2 — obligation `should_fix`: Driving Score "not higher", with the pass-2 interval (SC-11)
- [ ] S3 — obligation `should_fix`: Render the figures (SC-12)
- [ ] S4 — obligation `should_fix`: Remove revision-history remnants (SC-13)
- [ ] S5 — obligation `should_fix`: Reduce density; split Table 4 (SC-14)
- [ ] S6 — obligation `consider`: Relocate contribution (iv) (SC-15)
- [ ] S7 — obligation `consider`: EIC Minor Issues (SC-16)
- [ ] R10 — obligation `must_fix`: Same-input comparison, or closed-loop-rate wording (SC-17)
- [ ] R11 — obligation `must_fix`: Blocked-run onset relative to contact (SC-18)
- [ ] R12 — obligation `must_fix`: H2 harness qualifier in the abstract and Conclusion (SC-19)
- [ ] S8 — obligation `should_fix`: 14-route qualifier in §5 (SC-20)
- [ ] S9 — obligation `should_fix`: Estimand labelling (SC-21)
- [ ] S10 — obligation `should_fix`: Exact tests for zero-inflated outcomes (SC-22)
- [ ] S11 — obligation `should_fix`: Checkpoint release and noise seeding (SC-23)
- [ ] S12 — obligation `should_fix`: Missing intervals (SC-24)
- [ ] R13 — obligation `must_fix`: At-rest shares excluding blocked runs and stratified (SC-25)
- [ ] R14 — obligation `must_fix`: H3 described as controller-coupled (SC-26)
- [ ] R15 — obligation `must_fix`: Sampler named as a rival mechanism (SC-27)
- [ ] S13 — obligation `should_fix`: Per-stop-episode comparison (SC-28)
- [ ] S14 — obligation `should_fix`: Data-side part of [12] (SC-29)
- [ ] S15 — obligation `should_fix`: Anti-stall practice cited (SC-30)
- [ ] S16 — obligation `should_fix`: Waypoint-speed design and [40] (SC-31)
- [ ] S17 — obligation `should_fix`: Rendering-quality shift (SC-32)
- [ ] S18 — obligation `consider`: "Dual-system" terminology (SC-33)
- [ ] S19 — obligation `should_fix`: Original freezing-robot citation (SC-34)
- [ ] R16 — obligation `must_fix`: Define or replace "hesitation" (SC-35)
- [ ] S20 — obligation `should_fix`: Construct and threshold table (SC-36)
- [ ] S21 — obligation `consider`: Other road users in the Limitations (SC-37)
- [ ] S22 — obligation `should_fix`: Introduction safety-case clause (SC-38)
- [ ] S23 — obligation `consider`: 1,600-sample paired comparison (DA m3)

### Response Letter Template

Please answer every item above, R1 to R16 and S1 to S23, in the format of `templates/revision_response_template.md`. For each item, state the change made and its location, or give the reason for declining. A declined must_fix item remains visible and unresolved for the re-review. Please also answer the DA's MAJOR challenges M1 to M4 explicitly; they map to R1, R10, R11 and R16. The Questions for Authors in each card (Journal-Fit 1 to 4, R1 1 to 4, R2 1 to 6, R3 1 to 5) should be answered where they bear on these items.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Recommendation: Major Revision (preliminary signal) | Confidence: per finding 4 to 5; no report-level score
- Key Point: The plan-level difference is well supported as a difference between two checkpoints, but the headline attributes it to the mix on one checkpoint per arm, and pending results and an uncitable pre-specification record leave the paper not ready (D5 warn, D6 block, repairable).

### Reviewer 1 (Methodology) Summary
- Recommendation: not stated on the card (D1 warn, D3 warn) | Confidence: per finding 3 to 5
- Key Point: The inference is honest and pre-specified, but the design cannot separate composition from the training run, plans are not compared on identical inputs, blocked time is not separated from contact, and the H2 arms ran on different harnesses.

### Reviewer 2 (Domain) Summary
- Recommendation: not stated on the card (D2 warn) | Confidence: 4 (report level); per finding 3 to 4
- Key Point: The domain statements are correct in substance, but the plan comparison is not same-input, H3 is coupled to the gate, the sampling conjecture ignores the four-evaluation sampler, and `Golden-6400` is the outlier.

### Reviewer 3 (Perspective) Summary
- Recommendation: Major Revision | Confidence: 4 (report level); per finding 3 to 4
- Key Point: The model-versus-controller separation transfers well to validation practice, but "trade-off" rests on one contrast, "hesitation" presupposes unnecessary stops, and blocked time may be a post-contact state (D4 warn).

### Devil's Advocate Summary
- Recommendation: N/A — findings only
- Key Challenge: No unresolved Critical challenge. The strongest counter-argument (M1) is that the paper measured one unusual checkpoint (`Golden-6400`) rather than an effect of composition (D3 warn).

---

## Appendix: Synthesis Working Record

### Step 1a — Reviewer Summary Matrix

| Dimension | Journal-Fit Reviewer | R1 (Methodology) | R2 (Domain) | R3 (Cross-disciplinary) |
|-----------|----------------------|-------------------|-------------|------------------------|
| Overall Recommendation | Major Revision (preliminary signal) | Not stated; D1 warn, D3 warn | Not stated; D2 warn | Major Revision; D4 warn |
| Confidence / scope disclosure | Per finding 4–5; statistics outside remit | Per finding 3–5; driving-domain plausibility outside remit | 4; weaker on statistical inference; 2026 references unchecked | 4; weak on flow-matching theory |
| Key Strengths | Pre-specification record (S1); model-controller separation (S2); H3 replicated (S3); matched datasets released (S4); proportionate safety language (S5) | Honest H2 reporting (S1); dated record (S2); noise measured (S3); model and controller separated (S4); provenance (S5); artefact measures withdrawn (S6) | Speed dependence of L (S1); gate-off run (S2); positioning (S3); path geometry (S4); blocked-time split (S5); benchmark scope (S6); narrow novelty (S7) | Plan-level separation (S1); critique of standstill (S2); safety scope (S3); proxies labelled (S4); robotics links (S5) |
| Key Weaknesses | (→ Step 1b) | (→ Step 1b) | (→ Step 1b) | (→ Step 1b) |
| # of Questions | 4 | 4 | 6 | 5 |
| # of Minor Issues | 7 Minor findings (W4–W10) + 3 listed Minor Issues | 8 Minor findings (W5–W12) | 7 Minor findings (W5–W11) | 5 Minor findings (W4–W8) |

Major findings: Journal-Fit 3 (W1–W3), R1 4 (W1–W4), R2 4 (W1–W4), R3 3 (W1–W3). DA: 0 CRITICAL, 4 MAJOR (M1–M4), 6 minor (m1–m6).

### Step 1b — Weakness Sub-Claim Inventory

Only non-silent positions are listed. Every (sub-claim, seat) pair not shown is `not-mentioned`, which is silence, not opposition. DA positions are given in brackets for visibility only and are not counted. Severity and confidence are transported from the parent finding.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | EIC W1 attribution | EIC | raised | text: §4.6 Plans at low speed, pooled paragraph "the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | Major | 4 |
| SC-1 | R1 W1 one checkpoint per cell | R1 | corroborated | text: Section 4.6, paragraph on pooled stay-put shares across six models, "the balanced model at 6,400 samples plans to stay put far less often than its own training data do" | Major | 4 |
| SC-1 | R2 W4 Golden-6400 outlier | R2 | corroborated | text: §4.6 "is the low outlier among the six models, and at 1,600 samples the order of the two mixes is reversed" | Major | 4 |
| SC-2 | EIC W1 (stronger option) | EIC | raised | as SC-1 | Major | 4 |
| SC-2 | R1 W1 (stronger option) | R1 | corroborated | as SC-1 | Major | 4 |
| SC-2 | R2 W4 ("further seeds are what would decide it") | R2 | corroborated | as SC-1 | Major | 4 |
| SC-3 | EIC W1 (conjecture prediction opposite) | EIC | raised | as SC-1 | Major | 4 |
| SC-3 | R1 W11 selective consistency | R1 | corroborated | text: Section 5, second paragraph, "This is consistent with the conjecture of Section 3.2" | Minor | 4 |
| SC-3 | R2 W4 (§5 lacks the 1,600 qualification) | R2 | corroborated | text: §4.6 "is the low outlier among the six models, and at 1,600 samples the order of the two mixes is reversed" | Major | 4 |
| SC-3 | R3 Assumption Audit | R3 | disputed | Detailed Comments, Assumption Audit: "This is handled correctly." | — (not a finding) | 4 [CONFIDENCE-SOURCE: report-level] |
| SC-4 | EIC W2 pending (H1) | EIC | raised | text: §5 Limitation 7 "so H1 awaits the re-run" | Major | 5 |
| SC-4 | R1 W12 H1 no valid test | R1 | disputed (severity) | text: Section 4.1, Termination rule and censoring, "and H1 will use that run" | Minor | 5 |
| SC-5 | EIC W2 pending (decoupling, swap) | EIC | raised | text: §5 Limitation 7 "so H1 awaits the re-run" | Major | 5 |
| SC-5 | R3 W7 curation lesson pending | R3 | disputed (severity) | text: §3.3 "Comparisons between regimes therefore estimate the effect of the bundle." | Minor | 4 |
| SC-6 | EIC W2 placeholders, statements; EIC W10 AI verification | EIC | raised | text: §6 AI assistance disclosure "Most commits of the revision were made with AI assistance." | Major (W2); Minor (W10) | 5 |
| SC-7 | EIC W2 DOI and commit | EIC | raised | text: §5 Limitation 7 "so H1 awaits the re-run" | Major | 5 |
| SC-7 | R1 W9 materials incomplete | R1 | disputed (severity) | absence: Section 6, Data availability and Code availability (see R6 row) | Minor | 4 |
| SC-7 | R3 W4 reproduction path | R3 | disputed (severity) | text: §6 Data availability "The four Matrix fine-tuning datasets and the decoupling dataset are on the Hugging Face Hub" | Minor | 4 |
| SC-8 | EIC W3 addendum uncitable | EIC | raised | absence: reference list and Data and Code availability statements (see R7 row) | Major | 4 |
| SC-8 | R1 W6 record uncheckable | R1 | disputed (severity) | text: Section 4.1, Record of pre-specification, "they were not time-stamped by a third party" | Minor | 4 |
| SC-9 | EIC W4 "replicated" | EIC | raised | text: §5 opening paragraph "the change was reproduced in a second pass under rules fixed in advance" | Minor | 4 |
| SC-9 | R1 W1 (replication = evaluation noise only) | R1 | disputed (severity) | as SC-1 (R1) | Major | 4 |
| SC-10 | EIC W5 cost headline | EIC | raised | text: §1 third finding "Less hesitation has a cost." | Minor | 4 |
| SC-10 | R3 W1 trade-off single contrast | R3 | disputed (severity) | text: §1 contribution (iii) "the observation that the resulting difference is a trade-off between hesitation and time blocked, not an improvement on the benchmark's score" | Major | 4 |
| SC-11 | EIC W5 (DS p = 0.11) | EIC | raised | text: §1 third finding "Less hesitation has a cost." | Minor | 4 |
| SC-11 | R1 W5 DS "lower" | R1 | corroborated | text: Abstract, "its two-pass Driving Score was 5.67 points lower (rank test p = 0.11)" | Minor | 4 |
| SC-12 | EIC W6 figures | EIC | raised | absence: figure positions (see S3 row) | Minor | 5 |
| SC-13 | EIC W7 remnants | EIC | raised | text: §3.2 "The previous version of this manuscript argued the opposite; ..." | Minor | 5 |
| SC-14 | EIC W8 density | EIC | raised | table: Table 4, standstill decomposition and frozen strata (19 columns) | Minor | 4 |
| SC-15 | EIC W9 contribution (iv) | EIC | raised | text: §1 contributions paragraph | Minor | 4 |
| SC-16 | EIC Minor Issues | EIC | raised | EIC Minor Issues list | minor [SEVERITY-SOURCE: letter-fallback] | — |
| SC-17 | R1 W2 identical inputs | R1 | raised | text: Section 4.6, Near-stationary plans, "The two models visit different states in closed loop, so this is not a same-input comparison." | Major | 4 |
| SC-17 | R2 W1 different situations | R2 | corroborated | text: §4.6 "The two models visit different states in closed loop, so this is not a same-input comparison." | Major | 4 |
| SC-18 | R1 W3 blocked vs contact | R1 | raised | text: Section 4.7, Blocked time, "Every route with blocked time has at least one collision event" | Major | 3 |
| SC-18 | R3 W3 post-contact state | R3 | corroborated | text: §4.7 Blocked time "Every route with blocked time has at least one collision event" | Major | 3 |
| SC-19 | R1 W4 H2 harness | R1 | raised | text: Section 4.1, Harness changes between the H2 arms | Major | 3 |
| SC-20 | R1 W6 (14-route qualifier) | R1 | raised | text: Section 4.1, Record of pre-specification | Minor | 4 |
| SC-21 | R1 W7 estimands | R1 | raised | table: Table 5 | Minor | 4 |
| SC-22 | R1 W8 zero-inflated | R1 | raised | text: Section 4.7, Blocked time | Minor | 4 |
| SC-23 | R1 W9 checkpoints | R1 | raised | absence: Section 6 | Minor | 4 |
| SC-23 | R3 W4 checkpoints, unseeded noise | R3 | corroborated | text: §3.4 "The model server does not seed its noise draws" | Minor | 4 |
| SC-24 | R1 W10 intervals | R1 | raised | text: Section 4.8, Strata | Minor | 5 |
| SC-25 | R2 W1 at-rest denominator | R2 | raised | text: §4.6 (as SC-17) | Major | 4 |
| SC-26 | R2 W2 H3 controller-coupled | R2 | raised | text: §1 H3 | Major | 4 |
| SC-27 | R2 W3 sampler | R2 | raised | text: §3.2 | Major | 4 |
| SC-28 | R2 W5 stop and restart | R2 | raised | text: §1 | Minor | 4 |
| SC-29 | R2 W6 [12] | R2 | raised | text: §2 | Minor | 3 |
| SC-30 | R2 W7 anti-stall | R2 | raised | text: §2 | Minor | 4 |
| SC-31 | R2 W8 [40] | R2 | raised | text: §3.4 | Minor | 4 |
| SC-32 | R2 W9 visual shift | R2 | raised | text: §4.1 | Minor | 3 |
| SC-33 | R2 W10 dual-system | R2 | raised | text: §1 | Minor | 3 |
| SC-34 | R2 W11 freezing robot | R2 | raised | text: §2 | Minor | 4 |
| SC-35 | R3 W2 hesitation | R3 | raised | text: Title; §4.8 Strata | Major | 4 |
| SC-36 | R3 W5 thresholds | R3 | raised | text: §5 Discussion | Minor | 4 |
| SC-37 | R3 W6 other road users | R3 | raised | absence: §2, §4 and §5 | Minor | 3 |
| SC-38 | R3 W8 safety-case framing | R3 | raised | text: §1 | Minor | 3 |

DA corroboration, not counted: M1 → SC-1; M2 → SC-17; M3 → SC-18; M4 → SC-35; m1 → SC-9; m2 → SC-3; m4 → SC-11; m5 → SC-26. DA m3 is DA-only and enters the roadmap as S23 without a sub-claim id. DA m6 (headline chosen after seeing which measures held; disclosed, "a matter of emphasis") carries no remedy and is recorded here only.

### Disposition summary (over the 4 non-DA seats)

- CONSENSUS-4: none.
- CONSENSUS-3: SC-1, SC-2 (R3 silent).
- SPLIT (arbitrated above): SC-3 (existence and severity); SC-4, SC-5, SC-7, SC-8, SC-9, SC-10 (severity).
- Corroborated (2/4): SC-11, SC-17, SC-18, SC-23.
- Single-reviewer: SC-6, SC-12 to SC-16, SC-19 to SC-22, SC-24 to SC-38.

Surface-form parity check: no sub-claim was down-rated for informal wording or credited for technical phrasing. The R3 position on SC-3 was resolved by locating the passages in the manuscript, not by how either side was worded.

## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 13: VLA (the initials before its parentheses do not spell it)
- Body, line 13: VLM (the initials before its parentheses do not spell it)
- Body, line 127: W4A8 (the initials before its parentheses do not spell it)
- Body, line 427: ICLR (the initials before its parentheses do not spell it)
- Body, line 429: CoRL (the initials before its parentheses do not spell it)
- Body, line 451: SFT (the initials before its parentheses do not spell it)
- Body, line 465: RSS (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 6 | Not defined | CARLA | 16 |
| Body | 13 | Not defined | NVIDIA | 5 |
| Body | 35 | Not defined | GB | 3 |
| Body | 35 | Not defined | GPU | 3 |
| Body | 41 | Not defined | LiDAR | 1 |
| Body | 53 | Not defined | PID | 8 |
| Body | 55 | Not defined | LEAD | 6 |
| Body | 70 | Not defined | VL | 1 |
| Body | 99 | Not defined | AV | 1 |
| Body | 101 | Not defined | SHA | 2 |
| Body | 153 | Not defined | FIGURE | 5 |
| Body | 161 | Not defined | RTX | 1 |
| Body | 177 | Not defined | BCa | 4 |
| Body | 400 | Not defined | CRediT | 1 |
| Body | 408 | Not defined | AI | 3 |
| Body | 419 | Not defined | BC | 1 |
| Body | 419 | Not defined | CVF | 12 |
| Body | 419 | Not defined | IEEE | 13 |
| Body | 421 | Not defined | VAD | 1 |
| Body | 423 | Not defined | ECCV | 3 |
| Body | 425 | Defined again | CVPR | 8 |
| Body | 431 | Defined again | CVPR | 8 |
| Body | 433 | Defined again | CVPR | 8 |
| Body | 435 | Defined again | ICCV | 4 |
| Body | 439 | Not defined | LLM | 1 |
| Body | 443 | Not defined | PMLR | 2 |
| Body | 447 | Defined again | CVPR | 8 |
| Body | 453 | Defined again | CVPR | 8 |
| Body | 455 | Defined again | ICCV | 4 |
| Body | 457 | Not defined | MDP | 1 |
| Body | 459 | Defined again | CVPR | 8 |
| Body | 471 | Defined again | CVPR | 8 |
| Body | 479 | Not defined | CoT | 1 |
| Body | 487 | Not defined | KING | 1 |
| Body | 489 | Not defined | CAPS | 1 |
| Body | 491 | Defined again | ICCV | 4 |
| Body | 505 | Not defined | TITS | 1 |
