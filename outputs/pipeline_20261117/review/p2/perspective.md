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
trigger: "a stated limit on interpretation is not kept consistently in every part of the manuscript"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity

Peer Reviewer 3 (Perspective): AV safety-assurance and scenario-based validation engineer (SOTIF / ISO 21448), working on metric validity and simulation-to-deployment claims. I read this paper as an outsider to flow-matching theory and do not judge it. I judge whether a reader from validation and safety assurance would take away what the evidence supports. Calibration status: `NOT_CALIBRATED`. Overall confidence: 4 of 5 on measure validity and safety-related wording, 2 of 5 on anything that depends on the sampler.

Scope of what I saw: the main text and the supplement in full. Figures were present as captions only, so I did not assess them. The call is not bound to a venue and I make no venue-fit statement. I found no text in the manuscript addressed to reviewers or to an AI.

### Summary Assessment

For a paper about stopping behaviour, this manuscript is unusually disciplined about scope. The measures are defined operationally and sorted by level (plan, motion, command, controller, outcome), the model is separated from the controller by an actual gate-off run, repeat reliability is reported instead of hidden, a trade-off curve and the label "remedy" are both declined, and the limit "no safety claim" closes the abstract, the introduction and the conclusion. The title does not use the word caution. An adjacent-field reader who reads those three places receives the right main message, which is why D4 is not a block.

It is a warn because the stated limit is not kept everywhere. The reading that blocked time is not a cost, or not a harm, beyond the recorded collisions is a statement about harm, and it rests on merged collision counts that cannot register the behaviour in question (W1). The remaining points are smaller: a physical-state name for a command-state measure (W2), purposive verbs in the title and the discussion (W3), a one-axis framing in the introduction (W4), implications for evaluation practice given in one sentence (W5), release of the checkpoint weights not stated although every claim is checkpoint-specific (W6), and an abstract that mixes several near-synonymous state terms (W7). All are repairable by rewording, by a short added paragraph, or by a small rerun with contact logging.

### S1: The scope limit on safety is stated early and repeated

The abstract, the introduction and the conclusion each end on the limit, and the introduction adds that the study cannot place either checkpoint relative to safety. Limitation 11 extends it to effects on other road users. This is the correct default for a simulator study with about 4 km of driving per model.

**Evidence Anchor**: text: Section 1, third finding "We make no safety claim in either direction."

### S2: Measures are defined operationally and by level

Table 2 gives each measure a threshold, a unit and a level. A validation reader can tell that a near-stationary plan (plan level), standstill (motion level) and blocked time (command level) are three different observations. This is the single most useful aid for an outside reader in the paper.

**Evidence Anchor**: table: Table 2

### S3: The metric is separated from the integration it was measured in

The gate-off run shows that the pre-specified endpoint depends on a stateless controller rule, and the authors draw the right conclusion about their own endpoint instead of defending it. That lesson transfers directly to acceptance-metric design in scenario-based testing.

**Evidence Anchor**: text: Section 1, second finding "Total standstill time is a property of the model and the controller together, and a poor measure of either."

### S4: Repeat reliability of closed-loop runs is disclosed

Unseeded noise, a replicate route that diverged from the first step, intraclass correlations between 0.36 and 0.63, and a rank correlation of 0.01 between the per-route differences of two passes are all reported. Few closed-loop driving papers give a reader the numbers needed to judge how much one run per scenario is worth.

**Evidence Anchor**: text: Section 4.1 "a replicate of one route with the same checkpoint and controller differed from the stored run from the first step"

### S5: A trade-off curve and the label remedy are declined

With three checkpoints in two clusters and one seed each, the authors do not draw a relation between waiting and contact, and they apply their own advance rule against calling the decoupling mix a remedy. My Phase 1 concern about a trade-off claim on too few operating points is therefore largely met in the Discussion (the residue is W4).

**Evidence Anchor**: text: Section 5 "with three checkpoints we do not describe a trade-off curve"

### S6: The missing stakeholder is named

Scripted traffic does not react to a vehicle that holds or is stuck, and the authors say that the cost to other road users is not represented. This is the stakeholder a safety reader would ask about first.

**Evidence Anchor**: text: Supplementary Section S5, item 11 "neither behaviour can be judged for mixed traffic from these runs"

### W1: The harm-accounting reading of blocked time breaks the no-safety-claim limit

**Severity**: Major
**Evidence Anchor**: text: Section 1, third finding "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"
**Confidence**: 4 — safety-assurance practice on post-collision behaviour and on what collision counts can and cannot show

The third headline finding has a descriptive half and an accounting half. The descriptive half (time commanded to accelerate without moving lies at recorded collision positions) is supported. The accounting half says that this time is not a cost, or "not as an additional harm" (Section 4.10), beyond the collisions; Section 4.7 puts it as "it is not an additional, independent cost", and the Discussion repeats it. That is a statement about harm, placed next to a sentence that disclaims any safety claim in either direction.

The evidence offered is that collision event counts did not differ detectably. The manuscript itself gives three reasons why that cannot carry the statement. First, collision events are merged by actor (the leaderboard merge within 5 s or 5 m, then a second merge by actor identifier, Supplementary Section S4.1), so continued pushing against one actor is one event however long it lasts; the count is blind by construction to the behaviour that blocked time measures. Second, Section 4.7 says that whether a run began before or after the contact cannot be established. Third, Section 4.9 says the study is not powered to show equal rates. In post-collision terms, a vehicle that holds a throttle of 0.35 or more for 5 s or longer at a contact site is a different event from one that stops and holds. One of the six affected routes is a pedestrian-crossing scenario (Supplementary Section S4.7), and the contact objects are described only as mostly stationary vehicles.

I understand the motive: the authors do not want blocked time counted twice against the balanced checkpoint. The limit-respecting wording is that blocked time co-occurs with recorded collisions and that whether it adds harm beyond the recorded contact cannot be measured from these logs. If the authors want to say more, a rerun of the six or seven affected routes with the simulator's collision sensor logged per tick (time stamp, other-actor class, impulse) would give contact order, contact duration and object class.

### W2: Blocked time names a physical state that the measure does not observe

**Severity**: Minor
**Evidence Anchor**: text: Section 4.7 "This is inferred from the command log, not from a contact sensor."
**Confidence**: 4 — metric validity review in scenario-based testing

The measure is a run of at least 100 standstill steps with throttle at or above 0.35 and no brake. Table 2 correctly gives its level as Command, and the abstract describes it in command terms. The name, used in Tables 2 and 4, Figure 4 and throughout the text, asserts an obstruction. Three things an outside reader should be told in the main text: (a) 0.35 is the controller's own start-assist floor, which applies only to plans of 2.5 m or more, so the measure is tied to plan length and is partly the mirror image of a stay-put plan; (b) the second-pass interval includes zero at a throttle threshold of 0.2 (disclosed in Section 4.7, which is to the authors' credit); (c) the link to collisions is a 10 m match between distance travelled and collision position, with no time order, on routes with roughly 100 m of progress each (about 4 km over 44 routes in Table 3). The supplement's figure of 100.0 % within 5 m suggests the association is real, but a chance-match rate for that window is not given.

Suggestion: name the measure for what is observed (for example, commanded-acceleration standstill), or keep the name and validate it on the 22 to 25 runs with the contact-sensor rerun proposed under W1.

### W3: Wait, waited and pushed name a purpose that the logs cannot establish

**Severity**: Minor
**Evidence Anchor**: text: Section 5 "In scenarios the policy cannot solve, one checkpoint waited and the others pushed."
**Confidence**: 4 — reading of behavioural terms from a safety-assurance standpoint

To wait is to hold for a reason that will pass. The Discussion says that "whether a stop was required in a given situation is not known from our logs", because signal state, actor distances and conflict-zone occupancy are not logged. The plan-level term stay-put is neutral and well chosen. The title "Learning to Wait" and the quoted summary sentence are not, and "Learning" adds a causal reading of data composition that one seed per mix and the absent difference at 1,600 samples do not carry. The title avoids "caution", which I was asked to watch for; "wait" is milder but points the same way. A safety reader will take the waiting policy to be the conservative one, although an unintended standstill in a live lane is itself a hazardous behaviour under SOTIF.

Suggestion: let the title rest on the stay-put plans alone, and say that one checkpoint held and the others commanded a start. For a reference on required stops, the privileged LEAD expert could be run on the 44 evaluation routes to record where and for how long an infraction-free driver stops (a reference, not an oracle, since closed-loop states diverge), or conflict-zone occupancy could be logged as the future-work list already proposes.

### W4: The introduction frames waiting and contact as two ends of one axis

**Severity**: Minor
**Evidence Anchor**: text: Section 1, second paragraph "and one that never waits meets the obstacle"
**Confidence**: 3 — what a trade-off statement needs in validation practice

The motivating sentence presents waiting as the alternative to collision, and the next one says "This study measures where two policies sit on the waiting side". The results do not support a single axis: collision events did not differ detectably, and the checkpoint with more stay-put plans was not shown to collide less. Section 4.10 then calls more blocked time "a cost" of the decoupling mix two sentences before saying it is not an additional harm. The Discussion declines the curve (S5), so this is residue, but it sits where an outside reader starts.

Suggestion: present the two failure modes as two separately measured quantities with no assumed relation, and replace "at a cost" by the neutral statement that the second pre-specified condition was not met.

### W5: Implications for evaluation practice are given in one sentence

**Severity**: Minor
**Evidence Anchor**: text: Section 5 "For evaluation practice, the standstill fraction should be reported split by command and next to collisions"
**Confidence**: 4 — scenario-based validation practice

For readers in validation, three results matter more than the composition effect and are left for them to assemble. (i) Repeat reliability: with the reported intraclass correlations and a replicate route moving from a Driving Score of 60.0 to 4.1, a single run per concrete scenario does not support a per-scenario verdict; the paper has the data to say how many repetitions its own conclusions needed. (ii) Integration level: a stateless gate with thresholds of 1.5 m and 2.0 m decides which model appears to stand still more, so an acceptance metric has to be defined at the level at which it is measured. (iii) No reference for required stops, so standstill cannot be scored as good or bad. The practitioner whom the introduction addresses, who "decides what the fine-tuning set contains", is also never told what may be taken away about choosing a mix; at one seed per mix the honest answer is nothing prescriptive, and it should be said.

Suggestion: a short paragraph in the Discussion that states these three points and the non-recommendation on composition. The six scenario types on which the balanced checkpoint is stuck (supplement only) are candidate triggering conditions in SOTIF terms and could be named in the main text.

### W6: Checkpoint-specific claims without a stated release of the checkpoints

**Severity**: Minor
**Evidence Anchor**: absence: Section 6 availability statements — expected a statement that the fine-tuned checkpoint weights are released and where the repository holding the bridge controller, its gate-off variant and the evaluation harness can be obtained; checked Section 6 Data availability and Code availability, Section 3.4, Supplementary Sections S3.4 and S4.1, and Table S1
**Confidence**: 3 — reproducibility review from the text only, with the archive and commit identifiers still pending

Every result is, by the authors' own repeated statement, about specific checkpoints, and variation between training runs is untested. An outside group can therefore check the findings only with the same weights; retraining from the released datasets would test a different and open question. Section 6 releases five datasets and archives route-level records, step logs and trainer artifacts, which Supplementary Section S3.4 describes as state, argument and configuration files. The supplement says the repository is released with the paper, but Section 6 names only two analysis scripts and gives no location. Fine-tuning ran on an A100 machine, so the single-24-GB-GPU setup covers inference and evaluation only. Because the server does not seed its noise, even the same weights reproduce distributions and not runs.

Suggestion: state whether the five fine-tuned experts are released (or why not), where the repository is, that it holds the hashed bridge agent, the gate-off variant and the harness and server versions, and what one evaluation pass costs (44 routes at about 22 minutes each).

### W7: The abstract mixes near-synonymous state terms and two different plan measures

**Severity**: Minor
**Evidence Anchor**: text: Abstract "Once slow, the obstacle-heavy checkpoint planned to stay put in 14.00 % of steps"
**Confidence**: 3 — outside-reader accessibility

Within a few sentences the abstract uses stationary samples, once slow, planned to stay put, near-stationary plans, stood still and total standstill, with thresholds only in Table 2. The pair 14.00 % and 2.08 % (stay-put plans, plan length below 0.64 m, at 0.5 m/s or less) and the −7.11 points (near-stationary plans, below 1.5 m, all steps) are different measures, and the abstract does not signal the change. The same stay-put share of the obstacle-heavy checkpoint is 14.00 % as a mean of per-route shares and 24.9 % pooled over steps (Section 4.6, Figure 5b); both are labelled, but the reason for the gap is not given. The dataset term stationary (less than 0.5 m over 6.4 s) and the plan term stay put (below 0.64 m) differ in threshold, and Table 2 omits the dataset term. I could not find a statement of whether every logged 20 Hz step is a fresh inference call, which decides what a share of steps means behaviourally.

Suggestion: give the two thresholds in the abstract in parentheses, add the dataset term to Table 2, and state the inference rate.

### Detailed Comments

#### Assumption Audit

- **Explicit assumptions**: the sampling conjecture is declared post hoc, untested and at most partial, with a rival mechanism named. Nothing to add from my field.
- **Implicit assumptions**: (a) that a merged collision count is an adequate measure of harm at a contact site (W1); (b) that a per-step share of plans is behaviourally meaningful independent of the replanning rate (W7); (c) that the vehicle that holds is the reference case against which the vehicle that commands a start is described (W3).
- **Paradigmatic assumptions**: the paper stays within the benchmark-score paradigm and improves on it with plan-level measures. Scenario-based validation would add per-scenario acceptance criteria. The authors identify the lack of them as a limit; I agree and regard it as the most valuable follow-up.

#### Cross-Disciplinary Connections

- **Parallel research**: SOTIF treats unintended behaviour in both directions as hazardous and asks for the triggering condition. Both stuck behaviours here are functional insufficiencies on the same six scenario types.
- **Borrowing opportunities**: the vocabulary of functional insufficiency and triggering condition would let the Discussion describe the two behaviours without the verbs wait and push.
- **Methodological borrowing**: a reference run by the privileged expert on the evaluation routes; a stated number of repetitions per concrete scenario derived from the reported reliability; contact-sensor logging.

#### Practical Impact

- **Real-world application**: the transferable result is methodological (measure plans, commands and motion separately; do not accept total standstill as a metric), not a recommendation on data composition.
- **Implementation feasibility**: evaluation on one 24 GB GPU at about 16 hours per pass is within reach of a small group; fine-tuning is not, and checking the reported checkpoints needs their weights (W6).
- **Stakeholders**: other road users are acknowledged (S6). The struck actor at a contact site is the one not considered (W1).

#### Broader Implications

- **Ethical dimensions**: simulator only. The risk is one of citation: a sentence that blocked time is no additional harm, or that a balanced mix does not collide more, could be quoted without its limits. W1 addresses the first; the second is already guarded in Section 4.9.
- **Social impact**: none claimed, and none should be on this evidence.
- **Future directions**: per-scenario required-stop criteria; post-collision behaviour as its own measured outcome; the pending confirmation of rendering quality at data collection, which bears on any reading of these checkpoints outside this harness.

### Questions for Authors

1. For each blocked run, what is the class of the contact actor, and on the pedestrian-crossing route does the blocked time lie at a pedestrian contact?
2. Is every logged 20 Hz step a fresh inference call with fresh noise, or is a plan held across steps?
3. Will the weights of the five fine-tuned experts be released with the datasets?
4. Could the LEAD expert be run on the 44 evaluation routes to give a reference stop profile per route?
5. What is the chance rate of a 10 m match between a blocked-run start and a collision position on routes of this length?

### Minor Issues

- The related-work heading "Idling, freezing and over-caution" and the keyword class "caution" in the supplement are the remaining uses of the word. Both are labels, and the second is declared a heuristic; a half-sentence saying that the class is a text label and not a judgement of behaviour would close the point.
- Table 3 reports hard-brake share and steer jerk, which are never discussed. An outside reader may take them for comfort or safety indicators; either say what they are for or move them to the supplement.
- Limitation 10 depends on a pending confirmation of rendering quality at data collection. As it stands, the reader cannot tell whether a visual domain shift was present in every evaluation.

### Cross-Disciplinary Reading Recommendations

- ISO 21448:2022, Road vehicles — Safety of the intended functionality. Relevance: the terms functional insufficiency and triggering condition, and the treatment of unintended behaviour in either direction as hazardous (W3, W5).
- ISO 34502:2022, Road vehicles — Test scenarios for automated driving systems — Scenario based safety evaluation framework. Relevance: per-scenario acceptance criteria and the place of repetition in scenario-based evaluation (W5).
- [UNVERIFIED] Search lead, not a citation: type-approval provisions for automated lane keeping (UN Regulation No. 157) on vehicle behaviour after a detected collision, as background for treating post-collision behaviour as its own outcome (W1). I have not checked the clause.

~~~yaml suggested-references
- title: "Road vehicles — Safety of the intended functionality (ISO 21448:2022)"
  authors: ["International Organization for Standardization"]
  year: "2022"
  doi: null
  arxiv_id: null
- title: "Road vehicles — Test scenarios for automated driving systems — Scenario based safety evaluation framework (ISO 34502:2022)"
  authors: ["International Organization for Standardization"]
  year: "2022"
  doi: null
  arxiv_id: null
~~~
