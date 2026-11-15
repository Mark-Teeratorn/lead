contract_role: perspective
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: warn
trigger: "the wording in a prominent place invites a broader reading that the body then correctly narrows"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity

Peer Reviewer 3 (Perspective): AV safety-assurance and scenario-based validation engineer (SOTIF / ISO 21448), working on metric validity and simulation-to-deployment claims. I read this paper as someone who would have to decide whether its measures and conclusions can be carried into a validation argument. I am an outsider to flow-matching theory, so I do not judge Section 3.2 on its mathematics, and I leave statistics, domain accuracy and internal logic to the other seats.

### Overall Recommendation

Major Revision (seat recommendation only; the panel decision belongs to the synthesizer). Three Major findings below need rewriting and re-analysis of existing logs, not new simulation. Several results the paper relies on are still [[PENDING]] (H1 on Base-Rerun, the decoupling model, the motion-history swap test, code commit and archive DOI), and the paper cannot be judged complete until they are in.

### Confidence Score

4 (strong on validation-metric construct validity and closed-loop evaluation practice; weak on flow-matching theory). Confidence is an uncertainty and scope disclosure only.

### Calibration Status

`NOT_CALIBRATED`

### Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D4 cross_disciplinary_relevance: constructs defined operationally and tied to a measure | Contract D4 and Phase 1 scoring plan | PARTLY_MEETS | see S1, S4, W5 | Every measure has a numeric definition, but the definitions are spread over Sections 3.1, 3.3, 4.5 to 4.7, and "hesitation" itself is never defined | none identified | yes, contributes to warn |
| D4: adjacent-field meaning of central terms (title, abstract, conclusions) | Contract D4; Reviewer Card focus on "caution" and safety reading | PARTLY_MEETS | see W2, W8, S3 | "Caution" is gone from the title and "no safety claim" is held throughout, but "hesitation" implies an unnecessary stop that the data cannot identify | depends on how the venue's readers read "hesitation" | yes |
| D4: relation between two quantities ("trade-off") rests on measures and enough conditions | Phase 1 what_to_look_for; Reviewer Card focus 1 | PARTLY_MEETS | see W1, W3 | Both axes are measured, but the claim is stated for one matched contrast. Blocked time is a post hoc proxy whose link to collisions is not examined | the six-model ordering may support the claim descriptively (W1) | yes |
| D4: proxy measures identified with their limits | Reviewer Card focus 2 | MEETS | see S4, S2 | Blocked time, keyword classes and censoring are each named as proxies or censored with their limits | the blocked-time threshold dependence in pass 2 is disclosed | no |
| D4: deployment and simulation-to-real implications stay within evaluated conditions | Phase 1 what_to_look_for | MEETS | see S3, W6 | No deployment claim is made. Limitations 8 and 9 bound the harness | interaction with other road users is not discussed (W6, Minor) | no |
| D4: reproducibility for an outside group | Reviewer Card focus 3 | PARTLY_MEETS | see W4 | Datasets are released, but checkpoints are not listed, server noise is unseeded, and the code commit and archive are pending | pending items may resolve part of it | yes, contributes to warn |

### Summary Assessment

The paper has been reframed with care. The title now speaks of "low-speed hesitation" in a "matched-pair, single-seed study", not caution or safety. The abstract, Section 4.9, the Discussion and the Conclusion all repeat that no safety claim is made. The study's most transferable idea for validation engineers is that closed-loop standstill splits into what the model plans and what the controller does with it, checked by a run without the gate (S1, S2). That lesson reaches beyond this model and should interest anyone who uses standstill or Driving Score as a proxy for behaviour. My concerns are about how adjacent-field readers will read three constructs. First, "trade-off" is claimed from one matched contrast, although the paper's own six-model numbers look as if they could support a descriptive frontier (W1). Second, "hesitation" presupposes that the stop was unnecessary, which the authors say they cannot determine (W2). Third, blocked time occurs only on routes with a collision event. Whether it comes before or after the contact is not reported, so a reader cannot tell a cost of reduced hesitation apart from a post-contact state (W3). Each can be fixed by rewording and by re-analysing existing logs. The practical lesson for data curation, which factor of the bundled mix to change, depends on the pending decoupling model (W7).

### S1: Plan-level measures separate the model from the controller

The plan-level measures (stay-put plans by speed band, plans that end at rest, blocked time), the four-band decomposition of standstill, and the gate-off closed-loop run give a structure that a SOTIF analyst can use directly. A behaviour (standstill) is split into the decision layer's output and the execution layer's response, and each is checked under a changed execution layer. The paper also says where the decomposition stops working: "This is accounting, not a causal test" (Section 4.5).
**Evidence Anchor**: text: §1 contribution (ii) "separate what the model plans from what the controller makes of it"

### S2: Explicit critique of the standstill fraction as a measure

The authors state outright that their pre-specified endpoint measures the model and the controller together. They recommend reporting standstill split by command and next to collisions (Section 5). Benchmark designers in validation will find this more useful than the H2 result itself.
**Evidence Anchor**: text: §1 findings "Total standstill time is a property of the model and the controller together, and a poor measure of either."

### S3: Scope discipline on safety is kept throughout

The no-safety-claim wording appears in the abstract, the introduction, Section 4.9, the Discussion and the Conclusion, with no claim elsewhere that contradicts it. Earlier statements about crash rates are withdrawn explicitly (Section 4.9). The title no longer carries "caution".
**Evidence Anchor**: text: Abstract "Collision counts did not differ detectably; we make no safety claim."

### S4: Proxy and heuristic measures are labelled as such

Blocked time is labelled as inferred from the command log, the rationale keyword classes are labelled unvalidated, and the 60 s censoring is described with its effect on `Base`. A reader from validation can see which quantities are direct observations and which are inferred.
**Evidence Anchor**: text: §4.6 Proceed-cued standstill "which is not a validated classifier"

### S5: Related work reaches into robotics and motion planning

The paper connects driving-policy standstill to the freezing-robot problem, to policy idling in manipulation and to all-zero actions in VLA training data. This places the phenomenon in a shared vocabulary that adjacent communities will recognise.
**Evidence Anchor**: text: §2 Idling, freezing and over-caution "the freezing robot problem [42] denotes a planner that judges every forward path through a dense crowd unsafe and stops"

### W1: "Trade-off" is claimed from a single matched contrast

**Severity**: Major
**Evidence Anchor**: text: §1 contribution (iii) "the observation that the resulting difference is a trade-off between hesitation and time blocked, not an improvement on the benchmark's score"
**Confidence**: 4 (validation-metric practice; a trade-off claim is routinely read as a frontier between operating points)

In assurance and decision analysis, "trade-off" means a relation: moving the operating point to reduce one quantity raises another, along a curve that more than two points define. The paper shows one contrast, one checkpoint per regime with one seed, in which the model with fewer stay-put plans has more blocked time. Contribution (iii) presents this as an observation of a trade-off. The Discussion narrows it to "In this matched pair", which is why I score warn and not block, but the contributions list and the section headline "Less hesitation has a cost" invite the general reading. The paper may hold a stronger argument than it uses. As reported in §4.6 (pooled low-speed stay-put share) and §4.7 / ANALYSIS_ADDENDUM §8a (blocked time), the six models sort in exactly opposite orders on the two quantities: `Base` 33.3 % / 0.00 %, `Flooded-6400` 24.9 % / 0.18 %, `Flooded-1600` 19.8 % / 0.69 %, `Golden-1600` 16.4 % / 0.83 %, `Flooded-6400-Hist` 14.6 % / 2.11 %, `Golden-6400` 2.3 % / 7.75 %. These six are not a controlled series. Size, dataset, schedule and termination rule (`Base`) differ, and the two quantities may be aggregated differently. If the ordering holds up, it suggests that the cost is tied to how often the policy issues a start, whatever moved it there, and not to data composition in particular. In that reading the mix moves the operating point along a frontier and does not improve the frontier, which fits the authors' "not an improvement". Minimum remedy: reword contribution (iii) and the headline as an observation in this pair, for example "the balanced model had fewer stay-put plans and more blocked time". Stronger option: plot the six models on both axes with a common aggregation, clearly labelled as descriptive and confounded, and state whether a frontier reading is supported.

### W2: "Hesitation" presupposes an unnecessary stop that the data cannot identify

**Severity**: Major
**Evidence Anchor**: text: Title "Low-Speed Hesitation in a Vision-Language-Action Driving Policy" and §4.8 Strata "so we cannot tell when stopping was required"
**Confidence**: 4 (SOTIF practice separates unnecessary interventions from required ones as distinct hazard classes)

In SOTIF and scenario-based validation, a stop is a failure only relative to a reference for whether a stop was required. The paper says that this reference is not available: signal state, actor distances and conflict-zone occupancy are not logged, so stops cannot be classed as required. Even so, the title, contribution (iii) and the Discussion ("less hesitation came with more time blocked") use "hesitation", which in everyday and human-factors usage means a delay that was not needed. The measure behind the word is "stay-put plan in a low-speed context" (L below 0.64 m). The keyword analysis in §4.6 shows that both models produce such plans under "caution" rationales as well as "proceed" ones, so some of what is labelled hesitation may be correct waiting. The paper never defines "hesitation". A reader has to infer that it means the stay-put share, and has to find the caveat in §4.8. Minimum remedy: define "hesitation" in the abstract or the introduction as the operational measure, explicitly regardless of whether a stop was required, or replace it in the title with the measure itself (for example "stay-put planning at low speed"). Stronger option: derive required-stop labels offline from CARLA ground truth on replayed routes (scenario-runner trigger state, lead-actor distance, a rule such as RSS), and report stay-put plans separately for required and not-required contexts.

### W3: Blocked time may be a post-contact state, and the paper does not examine its link to collisions

**Severity**: Major
**Evidence Anchor**: text: §4.7 Blocked time "Every route with blocked time has at least one collision event" and "This is inferred from the command log, not from a contact sensor."
**Confidence**: 3 (closed-loop simulation experience; I cannot inspect the logs, so this is an alternative interpretation the paper leaves open, not a demonstrated error)

In CARLA, a vehicle that is commanded to accelerate with throttle at or above 0.35 and no brake, yet stays below 0.1 m/s for 5 s or more, is most plausibly held by a physical obstruction, often the actor it has just touched. The paper reports that every route with blocked time, for every model and under both controllers, has a collision event, against about half of the other routes. It does not report whether the blocked runs start after the collision, at its position, or against the same actor. If they do, blocked time is a consequence of contact and not a separate cost of fewer stay-put plans. The "trade-off" then becomes "the balanced model more often ends up pressed against an obstacle, while the obstacle-heavy model stops and holds before it". An assurance reader would treat that as safety-relevant even when aggregate collision counts do not differ. The authors' scope statement (no safety claim) is correct as far as it goes. The risk is that this pattern invites a safety reading that the paper neither tests nor rules out. Minimum remedy (existing logs): for each blocked run, report the time and position offset to the nearest collision event and whether the collided actor is the one ahead. State which came first. Stronger option: replay the six blocked routes with contact and actor-distance logging.

### W4: The reproduction path for an outside group is incomplete

**Severity**: Minor
**Evidence Anchor**: text: §6 Data availability "The four Matrix fine-tuning datasets and the decoupling dataset are on the Hugging Face Hub" and §3.4 "The model server does not seed its noise draws"
**Confidence**: 4 (reproducibility review practice)

Contribution (iv) claims an open setup. The datasets are released, but the Data availability statement does not list the fine-tuned checkpoints. Without them, an outside group has to retrain on an A100 at one seed and cannot check the plan-level results against the same weights. The server's noise is unseeded, so closed-loop runs cannot be repeated step by step. The code commit and the archive DOI are [[PENDING]]. Remedy: release the six evaluated checkpoints (or state why not), add an option to seed or log the noise per call, and fill in the commit and DOI before acceptance.

### W5: Thresholds behind the constructs are scattered, and "stay put" at rest effectively means "no start issued"

**Severity**: Minor
**Evidence Anchor**: text: §5 Discussion "In this action space a plan that stays put at rest is a plan without acceleration"
**Confidence**: 4 (construct-definition review)

An adjacent reader meets at least seven related thresholds: a stationary training sample (under 0.5 m over 6.4 s), a stay-put plan (L below 0.64 m), a near-stationary plan (L below 1.5 m), the gate's two clauses, standstill (below 0.1 m/s), crawling (0.1 to 1.0 m/s), a plan ending at rest (last second under 0.5 m) and blocked time (100 steps, throttle 0.35). §3.1 shows that a plan from rest with every control at its training mean has L = 0.59 m, just under the stay-put cut. At rest, therefore, "stays put" picks out plans with no more than mean acceleration, as the Discussion acknowledges. Remedy: add one table that defines every construct and its threshold, the section that defines it, and whether it is a plan-level, motion-level or command-level quantity. Carry the "issues no start" reading into the abstract wording.

### W6: Costs of waiting and blocking for other road users are outside the simulation and not discussed

**Severity**: Minor
**Evidence Anchor**: absence: §2, §4 and §5 — expected a statement of how scripted CARLA traffic reacts to an ego vehicle that waits or is blocked, and what that means for interpreting both behaviours in mixed traffic; checked §2 Closed-loop evaluation, §4.1, §4.8 Gap-waiting, §5 Limitations 1 to 9 and Future work
**Confidence**: 3 (human-factors and traffic-safety literature I know mostly secondhand)

In mixed traffic, a vehicle that waits without need or stays blocked imposes costs that Driving Score does not count and that scripted CARLA actors do not create: risky overtaking by followers, rear-end exposure, and blocked junctions. Both behaviours compared here (holding and blocked) would affect other road users differently on real roads. The paper makes no deployment claim, so this is not a scope violation. Still, one paragraph in the Limitations would tell adjacent readers that the cost side of the comparison is under-represented in this simulator.

### W7: The practical lesson for data curation depends on pending results

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "Comparisons between regimes therefore estimate the effect of the bundle."
**Confidence**: 4 (practical-impact assessment)

A practitioner wants to know which lever to pull: scenario-group mix, lateral balance, or stationary share. The authors correctly say that the design cannot separate them, and the decoupling model that would separate group mix from the rest is [[PENDING]]. The motion-history swap test that would support the inertia-like mechanism is also pending. As it stands, the actionable conclusion is limited to "this bundle, at 6,400 samples". At 1,600 samples no difference was found. Remedy: once the pending results are in, add one sentence stating which factor, if any, a practitioner should change, or that the evidence does not yet say.

### W8: The introduction's framing invokes a safety case before the paper sets its scope

**Severity**: Minor
**Evidence Anchor**: text: §1 "Where a policy sits between the two is what a benchmark score and a safety case both depend on."
**Confidence**: 3 (reading as an assurance practitioner)

The second paragraph of the introduction frames the study through a safety case and through a vehicle that "meets the obstacle". This primes a safety reading that the paper later disclaims. The framing is legitimate as motivation. A clause noting that this study measures the position on the waiting axis but cannot place it relative to safety would keep the opening consistent with S3.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions**: The stay-put sampling conjecture is labelled post hoc and untested, and the authors note that it does not predict the 1,600-sample result. This is handled correctly.
- **Implicit assumptions**: (a) Fewer stay-put plans is the direction of improvement unless costs appear (W2). (b) Blocked time and stay-put plans are independent outcomes, not causally linked through contact (W3). (c) Scripted traffic is an adequate reference for the cost of waiting (W6).
- **Paradigmatic assumptions**: The evaluation inherits the benchmark paradigm, in which route completion and infractions define success. The paper partly steps outside it by showing that Driving Score hides opposite movements in its components (§4.8). That is a valuable step.

#### Cross-Disciplinary Connections

- **Parallel research**: SOTIF treats unnecessary interventions and missed interventions as separate hazard classes, each with triggering conditions. The stay-put plans here are a candidate functional insufficiency, with low-speed contexts as the triggering condition.
- **Borrowing opportunities**: A formal reference for when the ego vehicle must yield, such as RSS, would let the authors label required stops offline. Criticality metrics (time to collision, post-encroachment time) would support the gap-acceptance analysis they say they cannot do.
- **Methodological borrowing**: Scenario-based safety evaluation reports outcomes per scenario class and per triggering condition, not as route means. The per-scenario results in §4.7 already lean this way.

#### Practical Impact

- **Real-world application**: The most usable result is methodological: report standstill split by command, with plan-level measures, and alongside collisions. The data-curation lesson awaits the decoupling model.
- **Implementation feasibility**: Single-GPU serving lowers the barrier to replication, provided the checkpoints are released (W4).
- **Stakeholders**: Other road users and following traffic are missing (W6).

#### Broader Implications

- **Ethical dimensions**: No human data are used. The authors disclose the extent of AI assistance, and their statement on their own verification and responsibility is still pending.
- **Social impact**: Practitioners may read the results as "obstacle-heavy fine-tuning makes the vehicle more cautious". The paper avoids that wording, and W2 and W8 aim to keep the framing consistent with this.
- **Future directions**: A frontier analysis across more operating points (W1), required-stop labelling (W2), contact-timed blocked-time analysis (W3), and per-context noise sampling, which the authors already propose.

### Cross-Disciplinary Reading Recommendations

- ISO 21448:2022, Road vehicles — Safety of the intended functionality. It gives the vocabulary of functional insufficiencies and triggering conditions, and the split between unnecessary and missing interventions that W2 relies on.
- ISO 34502:2022, Road vehicles — Test scenarios for automated driving systems — Scenario based safety evaluation framework. It offers a scenario-class reporting structure for the per-route and per-scenario results.
- Shalev-Shwartz, Shammah and Shashua (2017), "On a Formal Model of Safe and Scalable Self-driving Cars" (RSS). It is a rule-based reference for when the ego vehicle is required to yield, which could serve as offline required-stop labels.
- Westhofen et al. (2023), "Criticality Metrics for Automated Driving: A Review and Suitability Analysis of the State of the Art". It surveys metrics for quantifying gap acceptance and closeness to conflict.
- Koopman and Wagner (2016), "Challenges in Autonomous Vehicle Testing and Validation". It discusses the limits of simulation-based evidence and the role of proxy metrics.
- [UNVERIFIED] Search lead: analyses of real-world AV collision reports (for example the California DMV collision reports) on how often conservatively stopping AVs are rear-ended, relevant to W6.

~~~yaml suggested-references
- title: "Road vehicles — Safety of the intended functionality (ISO 21448:2022)"
  authors: ["ISO"]
  year: "2022"
  doi: null
  arxiv_id: null
- title: "Road vehicles — Test scenarios for automated driving systems — Scenario based safety evaluation framework (ISO 34502:2022)"
  authors: ["ISO"]
  year: "2022"
  doi: null
  arxiv_id: null
- title: "On a Formal Model of Safe and Scalable Self-driving Cars"
  authors: ["Shalev-Shwartz, S.", "Shammah, S.", "Shashua, A."]
  year: "2017"
  doi: null
  arxiv_id: "1708.06374"
- title: "Criticality Metrics for Automated Driving: A Review and Suitability Analysis of the State of the Art"
  authors: ["Westhofen, L."]
  year: "2023"
  doi: null
  arxiv_id: null
- title: "Challenges in Autonomous Vehicle Testing and Validation"
  authors: ["Koopman, P.", "Wagner, M."]
  year: "2016"
  doi: null
  arxiv_id: null
~~~

### Questions for Authors

1. For each blocked run, did a collision event come before it, and was the collided actor the one in the vehicle's path? (W3)
2. Using one aggregation for both, do the six models keep the opposite ordering of low-speed stay-put share and blocked time? Would you present that as a descriptive frontier? (W1)
3. Could required-stop labels be recovered offline from CARLA ground truth on replayed routes, so that "hesitation" can be restricted to stops that were not required? (W2)
4. Will the six evaluated checkpoints be released alongside the datasets? (W4)
5. Once the decoupling model is evaluated, which factor of the mix would you advise a practitioner to change? (W7)
