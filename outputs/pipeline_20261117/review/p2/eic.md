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
trigger: "presentation problems cost the reader real effort"

### D6: venue_fit_and_contribution
score: warn
trigger: "A real contribution is present but is framed more broadly than its evidence base"

## Review Body

**Reviewer identity and scope.** Journal-Fit Reviewer seat, configured as an associate editor at a robotics / intelligent-vehicles journal who handles learning-based driving submissions and has run closed-loop CARLA evaluation tracks. Confidence 4 of 5 on framing, contribution and presentation; statistical detail and controller internals are outside what this seat assesses. Calibration status: NOT_CALIBRATED. No venue criteria are bound to this call, so I make no venue-fit statement; D6 is judged on originality, significance and promise against delivery, at a field-general level for a Q2-level journal. I read the main text and the supplement in full. The five figures exist in the supplied file only as caption placeholders, so figure quality and legibility are not assessed and my D5 score does not rest on them. I was not given the earlier review and do not judge whether earlier requests were met.

**Summary assessment.** The manuscript fine-tunes the action expert of one flow-matching vision-language-action driving policy on two data mixes drawn from one pool, evaluates the checkpoints in closed loop on 44 Bench2Drive routes, and compares them at the level of the logged plans. It adds a repeat pass, a run with the controller's standstill gate removed, a third checkpoint that separates one of three bundled factors, and a history-swap test. It finds that two 6,400-sample checkpoints differ several-fold in how often they plan to stay put at low speed, that this becomes a difference in standstill time only through the controller gate, and that the checkpoint with fewer such plans scores no better. All experiments are reported, and the paper is unusually exact about what was fixed in advance and what was not. The abstract and the conclusion claim only what is shown. The weakness is the framing around them: the title, the motivation and the first listed contribution present an effect of data composition, in the direction "obstacle-heavy data teach waiting", that the paper's own six-checkpoint values and its one-run-per-mix design do not carry. What is firmly delivered is narrower and, in my view, still publishable: a reproducible plan-level characterisation of three checkpoints, a demonstration that standstill time is a joint quantity of model and controller, and evidence that Driving Score does not register a large behavioural difference. Presentation costs the reader effort throughout, which is the basis of the D5 score.

**Originality.** The source of originality is a controlled measurement combined with a new angle of view (plans separated from motion, with a closed-loop check without the gate). There is no new method, and the paper does not claim one. The gap is positioned against the inertia, copycat, robot-idling and data-composition literatures, and the novelty statement is worded as "we have not found", which is the right strength.

**Significance.** The reach is a sub-field: groups that adapt generative-head driving policies and execute their waypoints through a rule-bearing controller in CARLA. The evaluation-practice result reaches further, to anyone who reports standstill or stuck time from closed-loop runs. The paper gives no recommendation on which mix to use and declines to call either behaviour better. That restraint is justified by the evidence, but it leaves the reader without a stated take-away (W3).

**Is a measurement study without a new method a sufficient contribution?** In principle yes, when the measurement changes how readers should evaluate or build. Contributions (ii) and (iii) do that. Contribution (i), as worded, promises an effect of composition that the design cannot attribute (W2). The D6 score is "warn" and not "block" because rewording and tighter scoping resolve my concern without new experiments; the main message as stated in the abstract depends on no unreported result.

**Structural coherence, title, abstract, conclusion.** Abstract, introduction and conclusion tell one consistent story and each carries the limits. The title and the first paragraphs of the motivation do not match that story in direction (W1). Abstract and conclusion are lists of values and not summaries (W4). The section order is sound; the reporting order of the hypotheses and the place of the adaptation result need tidying (W8).

**Readiness and length.** By my count the main text up to the reference list is about 13,000 words including tables and the supplement about 14,000. The main text can be read alone. The supplement repeats much of it (W5). The remaining placeholders are author statements and identifiers, plus two confirmations that sit in content positions (W11).

**Questions for authors.**
1. What are the realised group, manoeuvre and stationary values of the decoupling set, and what share of its samples at 0.5 m/s or less stay put?
2. What is the pooled low-speed stay-put share for the re-run of the unadapted policy and for the decoupling checkpoint, on the same basis as the six values of Section 4.6?
3. Why is the obstacle-heavy checkpoint's low-speed stay-put share 24.9 % when pooled and 14.00 % as a mean of per-route shares, and which routes account for the gap?
4. Would the authors accept a title and a first contribution worded at the level of checkpoints, if no further training seeds are added?

**Preliminary signal from this seat (reference for the synthesizer, not a decision).** Revision is needed before acceptance. On the two dimensions I own, the changes are textual, with small additions to tables: this corresponds to a minor revision. If another seat requires further training seeds, that would change the picture and is not mine to judge.

### S1: Limits carried from the abstract to the conclusion

The single-seed design, the null result at 1,600 samples and the absence of a safety claim appear in the abstract, the introduction, the discussion and the conclusion in matching words. A reader who sees only the abstract is not misled about scope.

**Evidence Anchor**: text: Abstract "Variation between training runs is untested, and at 1,600 samples the mixes did not differ."

### S2: Model and controller separated, with a transferable lesson

The plan-level measures and the closed-loop run without the gate show that the pre-specified endpoint, standstill time, sums two parts that move in opposite directions. This is the part of the paper most likely to change what other groups report.

**Evidence Anchor**: text: §1 "Total standstill time is a property of the model and the controller together, and a poor measure of either."

### S3: Decision rules applied when they went against the authors

The paper reports that the pre-specified standstill comparison was not met on the second pass alone, and it declines to call the decoupling mix a remedy because one of three conditions fixed in advance failed. Post hoc analyses are labelled as such at the point of use.

**Evidence Anchor**: text: §4.10 "The first and third conditions hold and the second does not, so we do not call the mix a remedy."

### S4: Gap stated against a broad and relevant literature

Related work covers the inertia problem, copycat behaviour, idling in robot policies and data-mixture studies, and it states what those studies measured and what they did not. The novelty claim is hedged appropriately.

**Evidence Anchor**: text: §2 "We have not found a controlled change of the fine-tuning mix for such a model with low-speed behaviour in closed loop as the endpoint"

### S5: One table that defines every measure

Table 2 gives each measure with its definition, its level (plan, motion, command, controller, outcome) and the section that defines it. Given how many measures the paper uses, this table is what makes Section 4 followable.

**Evidence Anchor**: table: Table 2 (main text, §4.2)

### W1: Title and motivation point in a direction the six-checkpoint values do not support

The title and the opening motivation tell the reader that a policy learned to wait from its fine-tuning data, and that the obstacle-heavy mix is the source (the instinct "to add more of what is hard"). The paper's own descriptive values point the other way. Pooled over low-speed steps in the first pass, the stay-put share is highest for the unadapted policy (33.3 %), lies between 14.6 % and 24.9 % for four of the five fine-tuned checkpoints of the original design, and is 2.3 % for the balanced 6,400-sample checkpoint. On these values no checkpoint learned to wait. One checkpoint, and later the decoupling checkpoint, largely stopped producing the stay-put plans that the pretrained policy and the other checkpoints produce. The abstract gives 14.00 % against 2.08 % without the pretrained reference, so a reader cannot tell which checkpoint moved. This changes the practical message: the observation concerns a low-stationary, balanced-manoeuvre mix at 6,400 samples removing stay-put plans, with a consequence at collision sites, and not hazard-heavy data inducing over-caution. The pooled values are descriptive and the original unadapted run mostly used the earlier termination rule, so the reference value should be confirmed on the re-run (Question 2). Suggested direction: retitle to name what changed; rebuild the first two paragraphs of the motivation around the pretrained reference; put that reference beside the headline pair in the abstract.

**Severity**: Major
**Evidence Anchor**: text: §4.6 "and it is the low outlier among the six"
**Confidence**: 4 — editorial reading of the framing against values the paper itself reports

### W2: First contribution and title attribute the difference to composition; the design supports a checkpoint-level statement

Contribution (i) says that two data compositions changed the low-speed behaviour, and the title pairs composition with stay-put plans. The design has one training run per mix. At 1,600 samples, where the conditional stay-put shares of the two sets differ almost as much, the checkpoints do not differ; the balanced 6,400-sample checkpoint also differs from the 1,600-sample checkpoint trained on the same mix; and the body states in three places that dependence on composition across training runs is untested. The body is exact on this point; the contribution statement and the title are not. As it stands, contribution (i) is a three-checkpoint case study in which the decoupling checkpoint supplies one separately trained run in the same direction. Minimum remedy: word contribution (i) and the title at the level of checkpoints, and lead the contribution list with (ii) and (iii), which do not depend on attribution. Stronger and costlier option, at the authors' choice: further training seeds for the 6,400-sample pair, which the paper already lists as future work and which would let the composition wording stand if the result recurs. I do not prejudge what such runs would show.

**Severity**: Major
**Evidence Anchor**: text: §1 "a controlled measurement of how two fine-tuning data compositions, with the model, loss, schedule and controller held fixed, changed the low-speed behaviour"
**Confidence**: 4 — contribution scoping is the core of this seat; whether more seeds are required is for the methodology seat

### W3: The most transferable result is one sentence at the end of the discussion

What a reader outside this exact setup can use is the evaluation-practice result: standstill fraction counts a waiting vehicle and a vehicle commanded to move that does not move as the same thing, and Driving Score did not register a several-fold difference in plans. This appears as a closing sentence of Section 5 and is absent from the abstract and the conclusion. Suggested direction: state it as a named contribution, give it a short subsection or a boxed recommendation with the minimum logging needed (command class, plan extent, contact), and carry it into the abstract and conclusion.

**Severity**: Minor
**Evidence Anchor**: text: §5 "For evaluation practice, the standstill fraction should be reported split by command and next to collisions"
**Confidence**: 4 — judgement of reader interest from running closed-loop evaluation tracks

### W4: Abstract and conclusion are runs of values, not summaries

The abstract is one 253-word paragraph that carries six result values, two intervals and a p-value beside the design numbers, uses "once slow" and "the gate" without saying what they are, and never states in one sentence what the reader should conclude. The conclusion is a longer run of the same values. Suggested direction: question, design, the three findings in words with three or four numbers at most, then the limits; leave intervals to the body. If the adaptation result stays in the abstract, say there, as the body does, that its interval includes zero and that it was not established on routes the controller was not tuned on.

**Severity**: Minor
**Evidence Anchor**: text: Abstract "Once slow, the obstacle-heavy checkpoint planned to stay put in 14.00 % of steps and the balanced one in 2.08 %."
**Confidence**: 4 — standard editorial criterion for abstracts

### W5: The supplement repeats the main text instead of extending it

Large parts of S3.2, S3.3, S4.3, S4.5 to S4.7, S4.10 and S4.11 are the main-text paragraphs again, word for word, with further sentences inserted. A reader cannot see what the supplement adds without comparing the two files line by line, and every repeated number now has to be kept consistent in two places. Suggested direction: keep in the supplement only what the main text does not contain (the additional analyses, Tables S1 to S3, the controller constants, the record of pre-specification), each introduced by one sentence that points back to the main-text result it extends.

**Severity**: Minor
**Evidence Anchor**: text: Supplement preamble "Some statements of the main text are repeated here so that each section can be read on its own."
**Confidence**: 5 — direct comparison of the two parts of the supplied file

### W6: Repository file pointers are used as citations and cannot be followed from the submission

The main text cites sections of ANALYSIS_ADDENDUM eighteen times (forty-seven times across both parts) and also CONFIRMATORY_DEVIATIONS. These are repository files; the commit and the archive identifier are still placeholders, and the record is self-timed. The word "pre-specified" in the abstract rests on this record. The placeholders are administrative, but as submitted no reader can check a single one of these pointers, and the pointers interrupt the prose. Suggested direction: reproduce the rule texts (H2, H3, the two secondary rules, the decoupling and history-swap readings) with their commit times as a supplementary appendix, and refer to appendix items in the main text.

**Severity**: Minor
**Evidence Anchor**: text: §4.1 "they were not time-stamped by a third party"
**Confidence**: 4 — presentation and verifiability from the reader's side; the statistical weight of the record is for other seats

### W7: Too many near-synonymous names and thresholds

Datasets and checkpoints are called balanced and obstacle-heavy, Golden and Flooded, mixes, regimes and cells; "Matrix" is used for four of the datasets without ever being defined. "Not moving" has three definitions that sit close together: a stationary sample (less than 0.5 m over the future), a stay-put plan (extent below 0.64 m) and a near-stationary plan (extent below 1.5 m), beside "at rest", "low speed" and "once slow". Table 2 helps for the measures but covers neither the dataset terms nor the naming. Suggested direction: one name per object, defined once; add the dataset-side definition of stationary to Table 2 and state why it differs from the stay-put threshold.

**Severity**: Minor
**Evidence Anchor**: text: §3.3 "All four Matrix datasets are drawn from one verified training pool"
**Confidence**: 4 — terminology audit over the full text

### W8: Hypothesis numbering, reporting order and headline statistic do not line up

The hypotheses are numbered H1 to H3 and reported H3, H2, H1. H3, called the main finding, was specified last, and its statistic (plans below 1.5 m over all steps) is not the statistic that leads the abstract and the findings list (stay-put plans at 0.5 m/s or less), which is post hoc with a separate repeat criterion. H1, the adaptation gain over the unadapted policy, is peripheral to the question in the title yet closes both abstract and conclusion. A reader has to reconstruct which number is the tested one. Suggested direction: renumber by weight, name one primary plan-level statistic and say in the abstract which statistic the pre-specified test used, and present the adaptation result as context in one place.

**Severity**: Minor
**Evidence Anchor**: text: §4.3 "The three hypotheses are reported in order of their weight in this paper, not of their numbering."
**Confidence**: 3 — structural reading; the status of each test is for the methodology and coherence seats

### W9: The decoupling mix is not described in Table 1

The third checkpoint carries a statement in the abstract, yet its dataset is described only in one sentence of words. Table 1 has no column for it, and its stay-put share among low-speed samples, the quantity that the conjecture of Section 3.2 is about, is given nowhere. A reader cannot check that the set realises the manoeuvre and stationary targets of the balanced mix, nor relate its result to the conjecture. Suggested direction: add the column, with the same rows as for the other two mixes.

**Severity**: Minor
**Evidence Anchor**: absence: Table 1 and §3.3 — expected the realised composition of the decoupling mix and its stay-put share among low-speed samples; checked Table 1, §3.3, §4.10, Table S1, S3.3 and S4.10
**Confidence**: 5 — searched every occurrence of the dataset in both parts

### W10: The same quantity appears under two aggregations with very different values

The low-speed stay-put share of the obstacle-heavy 6,400-sample checkpoint is 14.00 % as a mean of per-route shares (abstract, Table 4, panel a of Figure 5) and 24.9 % pooled over steps (Section 4.6, panel b of Figure 5). The text marks which is which but does not explain the gap or say why the six-checkpoint comparison uses a different aggregation from the headline. Suggested direction: use one aggregation for both panels, or give both for the matched pair and say which routes drive the difference.

**Severity**: Minor
**Evidence Anchor**: figure: Figure 5 caption, panels (a) and (b)
**Confidence**: 4 — values compared across abstract, Table 4 and Section 4.6; the figure itself was not available

### W11: Two unconfirmed facts sit in content positions

Most placeholders are author statements and identifiers. Two are not: the rendering quality of data collection, on which limitation 10 depends, and the resume events and training end time of the decoupling checkpoint, while Sections 3.3 and 3.4 say that checkpoint used the recipe and schedule of the other 6,400-sample models. Both should be confirmed from logs and the sentences that depend on them made unconditional.

**Severity**: Minor
**Evidence Anchor**: table: Table S1, row Decoupling-6400, columns Resume events and Training (UTC)
**Confidence**: 5 — read directly from the table and limitation 10

### W12: Tables 3 and S2 are too wide to read

Table 3 has thirteen columns and Table S2 nineteen, several with two or three values per cell. In a journal layout neither will be legible without rotation or splitting. Suggested direction: split Table 3 into leaderboard outcomes and kinematics, move per-ability strata of Table S2 to their own table, and drop columns that no sentence in the text uses.

**Severity**: Minor
**Evidence Anchor**: table: Table 3 (main text, §4.2), thirteen columns
**Confidence**: 4 — layout judgement from the supplied tables
