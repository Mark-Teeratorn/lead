contract_role: domain
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: block
trigger: "a measured quantity is given a domain interpretation that it cannot support without additional evidence"
block_class: repairable

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

**Reviewer identity.** Peer Reviewer 2 (Domain): senior researcher in end-to-end driving and imitation learning (CARLA Leaderboard, Bench2Drive), familiar with the inertia, causal-confusion and copycat literature and with flow and diffusion planners. Reviewer confidence: 4 of 5 for the domain content, lower for statistical inference, which I leave to the methodology seat. Calibration status: `NOT_CALIBRATED`. The call is not bound to a venue, so I make no venue-fit statement. I had no web access in this session: the references that post-date what I can attest from memory ([15], [34], and the 2026 publication details of [10], [14], [19] and [20]) were not checked, and I report no finding on them.

**Summary assessment.** The manuscript reports that two 6,400-sample fine-tuned checkpoints of the Alpamayo 1.5 action expert differ in how often they output near-zero-acceleration plans at low speed, that the controller's standstill gate decides whether this becomes a difference in standstill time, and that the checkpoint with fewer such plans spends more time pressing against something at collision sites. As a description of these checkpoints this is supported, and it is useful to the field: it shows with logged plans that standstill in closed loop is a joint product of planner and controller. The descriptions of prior work that I could check are accurate, the flow-matching account in Section 3.1 is correct, and the manuscript is unusually open about what its design cannot show. My block on D2 concerns interpretation, not the measurements. Two statements at the level of title, abstract and positioning say more than the measured quantities support: (1) that the stay-put plans are not the inertia mechanism, which rests on a small test of one input channel whose prediction does not separate the accounts the paper itself groups together; and (2) that fine-tuning composition taught the policy to wait, when the manuscript's own table shows the unadapted policy already at the level of the obstacle-heavy checkpoint, so that the observed event is the loss of stay-put plans in two of three 6,400-sample fine-tunes. Both are repairable by rewording and by small analyses of data the authors already hold. The core finding stands.

**Scoring plan against the paper (D2).** Claims agree with the manuscript's own evidence except where W1, W2 and W8 say otherwise. Prior work is correctly described where I could check it, with the gaps listed in W9. Terms and benchmark names are used correctly and are defined in Table 2. The interpretation of measured quantities is where the block trigger is met (W1, W2, with W3 to W5 as lesser instances). None of my Major findings rests on a field norm: each compares a claim with the manuscript's own numbers or with the definitions the manuscript itself gives for [12], [13] and [25].

**Literature review.** Coverage is good for inertia and copycat work, generative action heads, data-mixture work and closed-loop evaluation, and the gap statement at the end of the composition paragraph is worded narrowly enough to be true as far as I know. The synthesis is organised by theme and is critical, not a list. Gaps are in W9.

**Theoretical framework.** The sampling conjecture of Section 3.2 is the right kind of framework for a generative head, and the manuscript states honestly that it was formulated after the result, that it does not predict the 1,600-sample null, and that the four-evaluation sampler is far from the limit in which it holds. On the question my configuration card puts first, whether the conjecture survives the 1,600-sample result: as an explanation it does not. The training shares differ almost as much at 1,600 samples (30.6 % against 11.4 %) and the plans do not (9.54 % against 8.86 %), and at 6,400 samples the model shares (24.9 % against 2.3 %, pooled) do not track the training shares (31.0 % against 10.9 %). What remains is the weaker statement that the ordering of one pair matches the ordering of its training sets. W4 gives the remaining wording problems and an alternative the manuscript should discuss.

**Argument accuracy, and whether a stay-put decision can be read from path length.** At rest it can be read in one sense only. Because the plan is integrated from the current speed, a path under 0.64 m from rest means that the summed planned acceleration is close to zero; the manuscript says this (Section 5: a plan that stays put at rest is a plan without acceleration). It cannot tell a decision to wait for something in the scene from the absence of a start command. The manuscript's own swap test bears on this: told it was moving at 4 m/s in the same scenes, neither model planned to brake (no plan ended at rest, and decelerating plans were 2.03 % and 0.46 %). A policy that was waiting for a reason visible in the cameras would be expected to brake when told it is approaching that scene at speed. Subject to the out-of-distribution caveat the authors give, this suggests the stay-put plan is a missing start, not a wait, which is one more reason to change the title (W2).

**Contribution.** Empirical and methodological: plan-level logging with a gate-off run as a way to separate planner from controller, and the observation that fewer stay-put plans did not bring a better benchmark result. The contribution is incremental and specific to one policy, one seed per mix and one controller, and the manuscript says so. The overclaiming risk is confined to the points in W1 and W2.

**Questions for authors.**
1. How many simulator steps is one sampled plan executed and logged for (W6)?
2. On the at-rest stay-put share of the obstacle-heavy checkpoint (16.02 % as a mean of per-route shares): how much comes from the 7 routes ended by the 60 s rule (7 of 44 routes is 15.9 %), and what are the median per-route share and the share measured per stop episode at its onset?
3. Were camera frames logged? If so, both experts can be run on identical logged low-speed inputs with many noise draws, which would answer W5 and test the conjecture directly without the simulator.
4. What is the stay-put share of `Base-Rerun` at rest, per route, on the same definition as Table 4?
5. In the swap test, what did the models plan when the camera window, not the history tokens, was the manipulated input (for example a repeated single frame while moving)? If this was not run, the non-attribution should be limited to the history tokens.
6. Does the unicycle integration clamp speed at zero, so that a braking plan from rest has zero length, or can planned speed become negative?
7. What are the realised composition of the decoupling set and its sample overlap with `Golden-6400` (W7)?

**Missing references.** None of these could be checked online in this session. The first three are given from memory with metadata I can attest; please verify before citing. (a) Chitta, Prakash, Jaeger, Yu, Renz and Geiger, the journal version of TransFuser (IEEE TPAMI, 2023): the primary source for a creeping rule added to the controller explicitly against the inertia problem. (b) Trautman and Krause, IROS 2010: the paper that named the freezing robot problem, which [42] builds on. (c) Prakash, Behl, Ohn-Bar, Chitta and Geiger, CVPR 2020: data aggregation and sampling of critical states for CARLA imitation policies, an earlier data-side intervention in the same setting. (d) `[UNVERIFIED]` search lead: work on temporal consistency when a sampled action chunk is re-drawn at every control step (the action-chunking discussion in [29] itself, and later work on closed-loop resampling of action chunks from the Stanford group), which is the literature for the second sentence of the conjecture.

~~~yaml suggested-references
- title: "TransFuser: Imitation with Transformer-Based Sensor Fusion for Autonomous Driving"
  authors: ["Chitta, K.", "Prakash, A.", "Jaeger, B.", "Yu, Z.", "Renz, K.", "Geiger, A."]
  year: "2023"
  doi: null
  arxiv_id: "2205.15997"
- title: "Unfreezing the Robot: Navigation in Dense, Interacting Crowds"
  authors: ["Trautman, P.", "Krause, A."]
  year: "2010"
  doi: null
  arxiv_id: null
- title: "Exploring Data Aggregation in Policy Learning for Vision-Based Urban Autonomous Driving"
  authors: ["Prakash, A.", "Behl, A.", "Ohn-Bar, E.", "Chitta, K.", "Geiger, A."]
  year: "2020"
  doi: null
  arxiv_id: null
~~~

### S1: Planner and controller are separated with logged plans and a gate-off run
The decomposition of standstill by plan length, the closed-loop run without the gate, and the split of standstill into commanded stops and blocked time show that the pre-specified endpoint mixes two effects of opposite sign. This is a real service to closed-loop evaluation practice in CARLA, where standstill and stuck counts are usually read as model properties.
**Evidence Anchor**: text: Section 1 "Total standstill time is a property of the model and the controller together, and a poor measure of either."

### S2: The speed dependence of the path-length measure is recognised and handled
The manuscript derives that the extent is integrated from the current speed, gives the worked values, and repeats the low-speed comparison among steps at rest and with blocked steps removed. This removes the most obvious artefact of an extent-based measure in an acceleration action space.
**Evidence Anchor**: equation: Section 3.1, unicycle integration and definition of the trajectory extent L, with the worked values 0.59 m from rest and 3.1 m from 0.4 m/s

### S3: Prior work is described accurately and the missing baselines are stated
The accounts of the inertia problem [12], causal confusion [13], copycat agents [25, 28], past-motion dropout [27], the longitudinal averaging bias of waypoints [40] and the data-mixture work [35, 36] match those papers as I know them, and the paper does not claim to compare against remedies it did not run.
**Evidence Anchor**: text: Section 2 "We did not run a history-dropout baseline or a creep-rule controller, so we cannot say how a data-side change compares with them"

### S4: Disconfirming results from the other checkpoints are reported
The 1,600-sample null, the six-checkpoint listing that shows `Golden-6400` as the outlier, and the failure of the model shares to reproduce the training shares are all in the main text. These are the facts a domain reader needs to weigh the composition claim.
**Evidence Anchor**: text: Section 1 "at 1,600 samples no difference between the mixes was detected"

### S5: No benchmark or safety benefit is claimed
The manuscript reports that the checkpoint with fewer stay-put plans did not score higher, applies its own pre-fixed remedy criterion against itself, and declines a safety reading in either direction.
**Evidence Anchor**: text: Section 4.10 "so we do not call the mix a remedy"

### W1: The history-swap test cannot carry the statement that the stay-put plans are not inertia
The abstract states a positive result of no dependence; the body reports a null on eight routes with intervals reaching +14 points, and then describes a stay-put plan as one the model issues whatever the history says. Three domain problems go beyond sample size. First, the test changes only the 48 ego-history tokens. The camera window was left unchanged, and four frames of a scene that does not move tell the network that the vehicle is at rest. Causal confusion [13] and copycat behaviour [25], which the Introduction names as the family the inertia problem belongs to, are defined for observation histories in general, images included, so the visual route to the same shortcut is untested. Second, the stated prediction (a lower hold-speed share under a moving history) follows from the low-speed form of the account in [12] but not from the copycat form: a constant 4.0 m/s history has zero past acceleration, so a policy that continues its past motion would also hold speed, and the positive point estimates (+5.32 and +4.79 points) are in that direction. Third, the inertia problem as the Introduction defines it (the policy learns that a vehicle at rest tends to stay at rest) and the sampling conjecture (more low-speed training samples that stay put give more stay-put plans at low speed) are the same statement about the training data, differing only in the head that reproduces it. They are presented as rival accounts, with the test deciding between them; it cannot, because which input carries the low-speed cue is not what distinguishes them. Needed: reword the abstract, the first finding, Section 4.11, the Discussion and the Conclusion to say that no dependence on the history tokens was detected in a small test and that the result does not separate inertia from the alternatives; present the conjecture as a data-side reading of the inertia problem for a sampling head. A stronger option is a camera-window manipulation or the same-input replay of question 3.
**Severity**: Major
**Evidence Anchor**: text: Abstract "A test that replaced the ego-motion history showed no dependence on it."
**Confidence**: 4 — published work on inertia and causal confusion in CARLA imitation policies

### W2: The direction of the effect relative to the pretrained policy contradicts the title and framing
The title and Introduction present fine-tuning composition as teaching the policy to wait, with the obstacle-heavy mix as the cause. The manuscript's own table shows otherwise. Standstill with a planned path under 0.64 m is 8.29 % of steps for the re-evaluated unadapted policy and 7.93 % for `Flooded-6400`; the gate is active in 15.37 % and 15.14 % of steps. The 1,600-sample models and the historical checkpoint lie a little lower (5.17 % to 5.85 %), and only `Golden-6400` and `Decoupling-6400` are far lower (0.75 %, 1.17 %). On these measures the obstacle-heavy checkpoint is where the pretrained policy already was, and the manuscript itself cites a report that this pretrained model gets stuck in CARLA [34]. What the data show is that two of three 6,400-sample fine-tunes lost the stay-put plans of the pretrained policy and one kept them. This changes the reading of the main finding: the open question is which data, and how many optimizer steps, remove a pretrained behaviour, and the 1,600-sample null then looks like partial adaptation, not an anomaly. The causal verb in contribution (i), that the compositions changed the low-speed behaviour, also conflicts with the Discussion's own statement that the mix cannot be separated from the training run. Needed: a title and Introduction that do not assert learning to wait; the unadapted policy (`Base-Rerun`) added as the reference row in Table 4 and Figure 5 with the per-route at-rest share; a paragraph discussing the pretrained prior. The pooled 33.3 % for `Base` comes from the run made mostly before the 60 s rule and should not be used for this.
**Severity**: Major
**Evidence Anchor**: table: Table S2, column Standstill with L under 0.64 m, rows Base-Rerun 8.29, Flooded-6400 7.93, Golden-6400 0.75, Decoupling-6400 1.17
**Confidence**: 4 — read directly from the manuscript's table; the comparison is descriptive and untested

### W3: The H3 statistic is nearly the same quantity as gate-held standstill
H3 is labelled the plan-level main finding. Its statistic is the share of all steps with a planned path under 1.5 m, the gate's first clause, with the gate in the loop. From Table S2, standstill steps with a path under 1.5 m are 12.64 % of all steps for `Flooded-6400` (7.93 + 4.71) against an H3 share of 13.03 % in the same pass, and 2.35 % against 2.47 % for `Golden-6400`. So 95 to 97 % of the steps H3 counts are standstill steps that the gate holds: H3 re-tests two bands of the H2 decomposition, not a separate property of the plans. The manuscript concedes the coupling in words; the label and the abstract's parenthesis still present it as the plan-level test. Needed: describe H3 as recurrence of gate-held standstill and move the weight of the plan-level claim to the at-rest and gate-off rows, stated as post hoc.
**Severity**: Minor
**Evidence Anchor**: text: Section 4.3 "H3 therefore shows that a controller-coupled plan statistic recurred when the same checkpoints were evaluated again"
**Confidence**: 4 — arithmetic on the manuscript's own tables

### W4: The sampling conjecture is asserted as fact in the Introduction and confuses a dataset share with per-context mixture weights
The Introduction states the conjecture's conclusion before any evidence, while Section 3.2 says it was formulated afterwards and is at most part of the explanation. There is also a conceptual gap: the 31.0 % and 10.9 % are shares over all low-speed samples, a marginal over contexts. Flow matching reproduces the conditional distribution in each context; changing the dataset changes which contexts are present, and it changes the mixture weights of a given context only where the frozen backbone's encoding makes stay and start contexts indistinguishable. The two 6,400-sample sets also share 67 % of their samples, for which the conditional targets are identical. Needed: remove the assertion from the Introduction, state the aliasing assumption, and discuss progressive overwriting of the pretrained prior (W2) as an alternative that does predict the 1,600-sample result.
**Severity**: Minor
**Evidence Anchor**: text: Section 1 "For a policy that samples from the futures it was shown, this share matters"
**Confidence**: 3 — flow and diffusion planners; the aliasing argument is conceptual and not tested here

### W5: Step shares are weighted by duration and confounded by the states reached
The manuscript says its plan-level shares are not propensities, but the Discussion still calls the result a model-level difference and the headline numbers are step shares. A stay-put plan keeps the vehicle where it is, so one long stall contributes hundreds of steps to numerator and denominator, and the two checkpoints are at rest in different places (one held short of an obstacle, the other in contact). Question 2 gives the arithmetic that makes this worth checking. The gate-off values suggest the difference is not only terminal stalls, which is reassuring. Needed: median and per-episode onset rates next to the step shares, and, if frames were logged, the same-input replay. This is the addition that would most strengthen the paper.
**Severity**: Minor
**Evidence Anchor**: text: Section 4.6 "none compares the two experts on identical inputs, so none is a measure of propensity"
**Confidence**: 4 — closed-loop evaluation of imitation policies

### W6: The replanning rate is not stated
Every plan-level measure is a share of logged 20 Hz steps, and the conjecture's second sentence is about repeated queries, but the text does not say whether the expert is queried at every step or a sampled plan is held for several. With fresh noise at every query the policy can switch between stay and start plans from step to step, and the meaning of a step share differs in the two cases.
**Severity**: Minor
**Evidence Anchor**: absence: Sections 3.1, 3.4 and S3.4 on inference and control — expected the replanning rate, that is how many 20 Hz simulator steps one sampled plan is executed and logged for; checked Sections 3.1, 3.4, 4.1, 4.6 and Supplementary S3.4, S4.1, S4.6
**Confidence**: 4 — system description of sampling-based planners

### W7: The decoupling dataset is described only in words
The abstract and Conclusion attribute the difference to the manoeuvre mix and stationary share on the strength of the third checkpoint, yet its dataset has no column in Table 1. A reader cannot check its low-speed stay-put share (the quantity the conjecture is about), nor how many samples it shares with `golden_6400`. If the overlap is large, and with the same seed, the statement that `Golden-6400` is not alone is weaker than it reads.
**Severity**: Minor
**Evidence Anchor**: absence: Table 1 and Sections 3.3, 4.10, S3.3, S4.10 — expected the realised composition of the decoupling dataset (group, manoeuvre and stationary shares, low-speed stay-put share, samples shared with the two Matrix 6,400 sets, samples touching evaluation routes); checked Table 1, Table S1, Sections 3.3 and 4.10, Supplementary S3.3 and S4.10
**Confidence**: 4 — dataset construction for CARLA imitation learning

### W8: Calling blocked time no additional cost is a judgement the logs cannot support
The manuscript makes no safety claim, yet states that blocked time is not a cost beyond the collisions already counted. A vehicle that keeps applying throttle against the object it has struck behaves differently after the collision from one that stops, and no count in the benchmark records that difference. The same passage admits that the order of contact and blocked run cannot be established. Needed: describe blocked time as post-contact (or at-contact) behaviour that the collision count does not distinguish, without ranking it.
**Severity**: Minor
**Evidence Anchor**: text: Section 1 "Blocked time is therefore a state at a collision site, not a cost in addition to the collisions"
**Confidence**: 4 — CARLA leaderboard infraction accounting

### W9: One related-work summary is too brief and two attributions should go to primary sources
(a) [37] is cited only for expert style. As I recall its abstract, it also reports that frames should not be weighted by simple class frequencies and that keeping frames whose labels change allows a much smaller dataset, evaluated on Bench2Drive: this is a data-composition result in the same benchmark and belongs in the positioning. (b) The creeping rule against the inertia problem comes from the journal version of TransFuser, which is not cited; [21] is the conference version. Please also check that [40] says what the sentence on controller heuristics attributes to it; I could not confirm this from memory. (c) The freezing robot problem was named in Trautman and Krause (2010), not in [42]. (d) The persistence part of the conjecture should be connected to the literature on re-sampling action chunks at every step. None of this changes a conclusion.
**Severity**: Minor
**Evidence Anchor**: text: Section 2 "find that the style of the expert significantly affects the trained policy"
**Confidence**: 3 — from memory of the cited papers, without online checking in this session

### W10: No comparison with the established remedies for the same symptom
History dropout, an auxiliary speed target and a creep rule are the standard answers to a policy that does not leave rest, and none was run, so the paper cannot say whether the plan-level difference it reports would survive any of them. The authors state this limit. Whether a study of this kind is expected to include such baselines is a field norm that I could not ground in a checkable source in this session, so this finding is held at the lowest band. `[FIELD-NORM UNVERIFIED]`
**Severity**: Minor
**Evidence Anchor**: text: Section 5, Limitation 6 "We did not compare against controller-side anti-stall rules or model-side remedies such as history dropout"
**Confidence**: 3 — field practice known from experience, not sourced here

### W11: The benchmark's own success measure is not reported
Bench2Drive [3], the manuscript's benchmark reference, defines a per-route Success Rate next to Driving Score. The paper's closing argument is that neither behaviour solves the obstacle scenarios; the share of routes each checkpoint completes without infraction is the direct measure of that and would let readers see whether waiting or pushing ever succeeds. It needs no new runs.
**Severity**: Minor
**Evidence Anchor**: absence: Table 3 and Sections 4.2, 4.3, S4.3 — expected the Bench2Drive Success Rate per checkpoint next to Driving Score and route completion; checked Tables 2, 3, 4, S2, S3 and Sections 4.2 to 4.10 with their supplementary counterparts
**Confidence**: 4 — Bench2Drive evaluation
