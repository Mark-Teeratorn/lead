contract_role: domain
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "Domain statements are correct in substance but imprecise or overstated in places"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity
Peer Reviewer 2 (Domain): senior researcher in end-to-end driving and imitation learning (CARLA Leaderboard, Bench2Drive), familiar with causal confusion, copycat and inertia work and with flow and diffusion planners. Field-general review; no venue-fit claim (`criteria_binding_unavailable`).

### Confidence Score
4 (competence basis: end-to-end driving in CARLA, imitation-learning failure modes, flow-matching samplers; weaker on statistical inference, which I leave to the methodology seat).

### Calibration Status
`NOT_CALIBRATED`

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D2 domain_accuracy | contract `reviewer/reviewer_full/v2`, Phase 1 scoring plan | PARTLY_MEETS | see W1 to W11 and S1 to S7 below | Prior work is mostly represented correctly and the paper is positioned honestly; the flow-matching framework is overstated for the sampler actually run, and the plan-level headline is read more strongly than a closed-loop, single-checkpoint measure carries | Several 2026 references could not be checked (no web access); pending results (swap test, decoupling model, Base-Rerun) not assessable | yes: supports `warn`, not `block`, because the claims are scoped to the matched pair and the repairs are mainly rewording plus analyses of existing logs |

### Summary Assessment
The revised manuscript asks a well-posed domain question: when the composition of the fine-tuning set of a flow-matching VLA driving policy changes, what happens to its low-speed behaviour, and how much of what is seen on the road is the controller's doing. The answer it gives is careful in most places. It treats the dependence of the plan length L on the current speed correctly, withdraws a measure that was near zero by construction, separates the model from the controller with a gate-off run, and shows that total standstill mixes waiting with being stuck, which is a useful lesson for the field. The related work now covers inertia, causal confusion, copycat agents, history dropout, data mixtures and earlier reports on this model, and it positions the study honestly.

My domain concerns are about how far the plan-level evidence goes. The plan comparison is not a same-input comparison, and the reason each model is at rest differs systematically between them. The confirmatory H3 statistic uses the gate's own threshold over all steps. The sampling conjecture assumes exact sampling, but the server makes four network evaluations per call. Across the six models, the checkpoint that stands out is Golden-6400, which makes it hard to tell an effect of the mix from a quirk of one checkpoint. None of these defeats the scoped descriptive claim. Each of them makes the mechanistic and causal reading weaker than the text suggests. I score D2 `warn`.

### Strengths

### S1: Correct handling of the speed dependence of the plan length
The paper shows that L is integrated from the current speed v0 (a plan from rest with mean controls is 0.59 m; one from 0.4 m/s is 3.1 m), conditions the low-speed analyses on speed, adds an at-rest stratum, and withdraws the earlier from-motion count as near zero by construction. Many papers on waypoint-based driving policies miss this kinematic dependence.
**Evidence Anchor**: text: §4.6 "that count is close to zero by construction, because the plan is integrated from the current speed, and is withdrawn"

### S2: A closed-loop gate-off run separates model from controller
Running both 6,400-sample models without the standstill gate, with the reading fixed in advance, is the right domain test of whether standstill is a model or a controller property. The result (near-stationary plans persist, total standstill difference disappears) is informative either way.
**Evidence Anchor**: text: §4.5 "The interpretation was fixed in advance."

### S3: Honest positioning against model-side and controller-side remedies
Inertia [12], causal confusion [13], copycat agents [25, 28], ChauffeurNet past-motion dropout [27] and the ego-status shortcut [17, 18] are described correctly, and the paper states plainly that it did not compare against them.
**Evidence Anchor**: text: §2 "We did not run a history-dropout baseline or a creep-rule controller"

### S4: Accurate statement of flow-matching path geometry
The paper states correctly that with a linear path and independent coupling the marginal paths are not straight, and cites minibatch OT [31] and reflow [32] as the procedures that straighten them.
**Evidence Anchor**: text: §2 "the learned marginal paths are not straight in general"

### S5: Splitting standstill into blocked time and commanded stops
Separating time commanded to accelerate without moving from other standstill shows that a single standstill fraction counts a stuck vehicle the same as a waiting one. This is a measurement lesson that transfers to other closed-loop CARLA studies.
**Evidence Anchor**: text: §5 "the standstill fraction should be reported split by command and next to collisions"

### S6: Benchmark scope stated correctly
The 44-route subset, the custom controller, the train/evaluation route overlap and the version and rendering deviations are disclosed, and Driving Scores are explicitly not compared with published Bench2Drive numbers.
**Evidence Anchor**: text: §4.1 "the Driving Scores reported here are not comparable with published 220-route Bench2Drive results"

### S7: Novelty claimed narrowly and against the closest prior reports
The paper acknowledges FlowDrive's data balancing for a flow-matching planner [33] and the earlier report of this model getting stuck in CARLA [34], and claims only the controlled-mix, controller-separated design as new.
**Evidence Anchor**: text: §2 "Rebalancing of training data for a flow-matching planner and standstill of this model in CARLA are therefore both on record."

### List of Weaknesses

### W1: The plan-level contrast compares plans in different situations, and the at-rest denominator differs by construction
The headline reading is that the mix changed what the policy plans once it is slow. The paper concedes that the two models reach different states, but conditioning on speed does not make the states comparable. The reason a vehicle is at rest differs systematically between the two models. Blocked time is 7.75 % of Golden-6400's steps against 25.71 % total standstill, so roughly three in ten of its at-rest steps are blocked steps. In those steps the gate is not firing, so the plan is at least 2.0 m long and cannot count as stay-put. For Flooded-6400 blocked time is 0.18 %. The balanced model's at-rest stay-put share (2.62 %) is therefore diluted by stuck states in which it plans to move. The obstacle-heavy model's at-rest steps are dominated by held stops. A held stop sets up the next query at rest, and the plan that follows it is the measured quantity. The gap probably survives; a crude pooled correction gives roughly 3.7 % against 16 %. But the at-rest share compares one model waiting with the other model stuck, not the two models in the same situation. The inertia reading in §5 also needs a same-input comparison. Minimum remedy: report the at-rest and low-speed stay-put shares excluding blocked runs, and stratified by why the vehicle is at rest (gate-held, blocked, other). Stronger option: query both experts, with many noise seeds, on one common set of logged low-speed contexts, for example the union of both models' at-rest states, if the inputs or cached VLM states are logged. The authors already name this test as future work, and the pending motion-history swap test may partly provide it.
**Severity**: Major
**Evidence Anchor**: text: §4.6 "The two models visit different states in closed loop, so this is not a same-input comparison."
**Confidence**: 4 (follows from the gate and blocked-time definitions given in §3.4 and §4.7)

### W2: The confirmatory H3 statistic is coupled to the controller
H3, called the main finding, counts steps with L < 1.5 m over all steps, in a pass with the gate in the loop. That threshold is the gate's first clause. When it fires, the holding brake keeps v0 near zero, and from rest a plan with mean controls is 0.59 m long. So the measured share contains a feedback loop: a short plan leads to a held stop, which leads to another short plan. The all-step denominator also carries each model's speed distribution, which the paper itself notes. The obstacle-heavy model's own rate falls from 13.03 % to 8.94 % without the gate, so a substantial part of the gated rate is gate feedback. The only replication fixed before its data was therefore run on the plan-level quantity most entangled with the controller. The cleaner forms are post hoc: speed-conditioned, at rest, and gate-off. The gate-off form is also a single pass. The abstract and conclusion use H3 as confirmatory support for a model-level statement. Minimum remedy: describe H3 as a replication of a controller-coupled plan statistic. Make the case for model-side origin from the gate-off, speed-conditioned shares. The authors could add that without the gate the time below 1 m/s was nearly matched (27.42 + 12.75 = 40.17 % against 24.57 + 16.93 = 41.50 % of steps), while near-stationary plans were 2.72 % against 8.94 %. Stronger option: a second gate-off pass, with the at-rest stay-put share as its pre-specified endpoint.
**Severity**: Major
**Evidence Anchor**: text: §1 H3 "produces near-stationary plans, with a predicted path shorter than 1.5 m, in a smaller share of steps than"
**Confidence**: 4 (follows from the gate rule and the kinematics stated in §3.1 and §3.4)

### W3: The sampling conjecture assumes exact sampling, but the deployed sampler makes four evaluations per call
Section 3.2 replaces the withdrawn averaging argument with the claim that each call returns a sample from the conditional distribution, not its mean, and that composition does not shift samples toward an average. That holds only in the limit the paragraph itself names. The server takes eight forward-Euler steps and reuses the velocity on steps 3 to 6, so the expert is evaluated four times and the field is frozen from s = 0.375 to s = 0.875. Under independent coupling the field at s = 0 equals the conditional mean of A1 given c minus A0, so one full Euler step returns exactly the conditional mean. Coarse integration of non-straight paths therefore leaves samples partly pulled toward the mean, which is the averaging that rectified flow's reflow [32] is designed to remove. For this sampler the degree of pull is unmeasured. It matters for interpretation in three ways. First, mean-pull toward a start-moving majority predicts what the conjecture cannot: Golden-6400 plans to stay put far less often (2.3 % pooled) than its training data (10.9 %). Second, the obstacle-heavy model's in-between class is about 15 % of its low-speed steps against 6.4 % of its low-speed training samples, which is consistent with between-mode outputs (consistent with, not evidence for). Third, it offers a rival account of the 1,600-sample result. Minimum remedy: restate §3.2 and the §5 discussion as holding only in the limit, and name the sampler as a rival mechanism. Stronger option: on logged low-speed contexts, compare the deployed sampler with an exact many-step integration (for example 32 or 64 Euler or Heun steps without reuse) over many seeds. This is cheap, needs no closed-loop runs, and would also be the direct test the paper lists as future work.
**Severity**: Major
**Evidence Anchor**: text: §3.2 "Each inference call therefore returns a sample from the conditional distribution, not its mean."
**Confidence**: 4 (standard property of conditional flow matching with independent coupling; sampler details as stated in §3.4)

### W4: Across the six models, the outlier is Golden-6400, so the plan difference cannot be attributed to the mix rather than to one checkpoint
The paper attributes the plan difference to data composition, and §5 calls it consistent with the conjecture because the training shares differ nearly threefold. The reported cross-model pattern points elsewhere. On pooled low-speed stay-put share, the order is Base 33.3 %, Flooded-6400 24.9 %, Flooded-1600 19.8 %, Golden-1600 16.4 %, Flooded-6400-Hist 14.6 %, and Golden-6400 2.3 %. Golden-6400 is also the extreme on braking from motion (0.82 %), on blocked time (7.75 %, the others 0 to 2.11 %) and on standstill outside blocked time (17.97 %, the others 31.54 to 40.45 %). The 1,600-sample pair has almost the same conditional training shares (30.6 % against 11.4 %), yet its plans barely differ. So the matched-pair contrast is mostly Golden-6400 against a cluster of other fine-tuned checkpoints. That fits "the mix changed the plans" no better than "this balanced checkpoint is atypical". The paper notes the 1,600 inconsistency in §3.2 and the outlier status for braking in §4.6, but the abstract and §5 do not carry the qualification over to the stay-put result. Training-seed variation of imitation driving policies in CARLA is large enough that the field reports results over several training seeds (for example the TransFuser journal version, Chitta et al., listed below). With one seed this cannot be resolved inside the paper. The repair is wording: state in the abstract and §5 that the plan difference is specific to the 6,400-sample pair, that Golden-6400 is the outlier among the six models, and that the 1,600-sample pair does not show it. The pending decoupling model and further seeds are what would decide it.
**Severity**: Major
**Evidence Anchor**: text: §4.6 "is the low outlier among the six models, and at 1,600 samples the order of the two mixes is reversed"
**Confidence**: 4 (read directly from the six-model values the paper reports in §4.6 and §4.7)

### W5: Stop and restart are compared on measures with different units
The text says the difference is small from motion and much larger at rest, which implies the models differ mainly in restarting. That comparison sets a per-step share of moving steps whose plan ends at rest (about 1 pp) against a per-step share of at-rest steps (more than 10 pp). One stop needs only a few seconds of braking plans but can produce many seconds at rest, so per-step magnitudes in the two bands do not say where the difference lies. The obstacle-heavy model also had more than twice as many stop episodes per route (5.23 against 2.27; 5.36 against 1.89 in the second pass), so it comes to rest more often, not only stays longer. The §5 sentence that at rest a stay-put plan is a plan without acceleration is correct. Compare per stop episode instead: how often each model enters a stop, and how long it takes to plan a start.
**Severity**: Minor
**Evidence Anchor**: text: §1 "the difference is much larger once the vehicle is at rest"
**Confidence**: 4 (follows from the episode counts in §4.7)

### W6: The closest data-side antecedent in [12] is not represented
Codevilla et al. [12] are cited only for the inertia problem and the speed-prediction branch. The same paper also examines how the amount and bias of the training data affect behaviour-cloned driving in CARLA, including how dominant driving modes shape what the policy learns. That is the closest existing data-side result to this paper's question. Engaging with it would sharpen the novelty statement, which is narrow enough to survive.
**Severity**: Minor
**Evidence Anchor**: text: §2 "proposed an auxiliary speed-prediction branch so that the network must estimate speed from images"
**Confidence**: 3 (from my reading of [12]; worth the authors re-checking)

### W7: Controller-side anti-stall practice is mentioned without a source
Creep and anti-stall rules are standard in CARLA agents. TransFuser's released agent, for example, forces forward motion after a long time stationary (Chitta et al., listed below). This bears directly on the blocked-time finding: a creep rule would turn the obstacle-heavy model's held stops into forced motion in exactly the scenarios where the balanced model is blocked. The missing baseline is acknowledged and is not required for a measurement study, but the practice should be cited and its likely interaction with the findings discussed.
**Severity**: Minor
**Evidence Anchor**: text: §2 "Closed-loop agents can also include controller-side anti-stall rules, such as creeping forward after a fixed time at rest; we do not survey them."
**Confidence**: 4 (documented in the TransFuser agent and controller)

### W8: The controller's speed-from-waypoints design is the one [40] questions
The bridge controller takes the target speed and the gate from the waypoint path length. Jaeger et al. [40], cited in §2, show that taking longitudinal control from waypoints is a source of unwanted slowing, and move speed to a separate output. With a sampling head the mechanism differs (no averaging in the limit), but the paper should say that its target speed, standstill gate and L-based measures all rely on the representation [40] criticises, and that this design choice is part of why standstill depends on the controller here.
**Severity**: Minor
**Evidence Anchor**: text: §3.4 "The target speed follows the trajectory: it is the planned speed to the lookahead waypoint"
**Confidence**: 4

### W9: The visual domain shift between training and evaluation is not characterised
The data were recorded in CARLA 0.9.16 and evaluation ran in 0.9.15 at Low rendering quality; the recording quality is not stated. For a camera-only policy, Low quality changes lighting, shadows and texture detail. The shift applies to both arms, but a less certain scene reading could raise the rate of stay-put samples, and it may interact with an obstacle-heavy mix. State the recording quality and list this as a possible moderator of the plan-level effect.
**Severity**: Minor
**Evidence Anchor**: text: §4.1 "all 44 routes lie in other towns, so every model ran at Low"
**Confidence**: 3 (general CARLA rendering knowledge; size of the effect unknown)

### W10: "Dual-system" is used loosely
In the VLA literature "dual-system" usually means a slow reasoning model paired with a fast control policy at a separate rate. π0 is usually described as a single model with a flow-matching action expert. Describe π0, π0.5 and Alpamayo as VLM-plus-action-expert designs, or define the term.
**Severity**: Minor
**Evidence Anchor**: text: §1 "In dual-system designs such as"
**Confidence**: 3 (terminology convention)

### W11: The freezing robot problem is attributed to a later paper
The freezing robot problem was named by Trautman and Krause (IROS 2010). The paper cites the 2015 IJRR study [42]. Cite the original, or both.
**Severity**: Minor
**Evidence Anchor**: text: §2 "the freezing robot problem [42] denotes a planner that judges every forward path through a dense crowd unsafe and stops"
**Confidence**: 4

### Detailed Comments

**Literature review.** Coverage of inertia, causal confusion and copycat work is now adequate and correctly attributed ([12], [13], [25], [27], [28], [41]). The data-mixture and data-quality line ([35], [36], [37], [38], [39], [46]) and the reports closest to this study ([33], [34]) are present. The synthesis is critical rather than a list, and the gap statement (a controlled change of mix with the controller's part separated) holds. Gaps: the data-bias part of [12] (W6), any source for creep and anti-stall practice (W7), and the original freezing-robot paper (W11). I could not check the 2026 items ([10], [14], [15], [34]) without web access; their descriptions are plausible and internally consistent, but I make no claim about their existence or content.

**Theoretical framework.** The flow-matching account (marginal velocity field, transport to the training conditional, sample frequency following mixture weight) is correct in the limit and correctly labelled a post hoc conjecture, not a tested hypothesis. It is applied a step too far for the sampler actually run (W3). It fails one of its own predictions, the 1,600-sample pair, and that failure is acknowledged in §3.2 but not in §5 (W4). The rival explanations named (lateral asymmetry, optimizer steps) are appropriate. The sampler's mean-pull should be added to them.

**Factual accuracy and terminology.** The kinematic equations, the dependence of L on speed, the gate logic, and the Bench2Drive description (220 routes, 44 scenarios, five abilities) are stated correctly. I found no factual error about the cited driving works. The terminology issues are W10, and the use of "stay put" for a 6.4 s horizon. A plan that waits about five seconds and then starts can still fall below 0.64 m, so "stay put" also covers plans with a late start. Saying so would avoid over-reading.

**Contribution to the field.** The contribution is empirical and methodological. It is a controlled measurement on one matched pair. It shows that a standstill fraction is a joint property of model and controller, and that it hides a trade-off between hesitation and time spent stuck. Splitting standstill by command and running a gate-off check is the most transferable part. The scale is incremental. The overclaiming risk is now mainly in the mechanistic reading (W1 to W4), not in the headline wording, which is scoped to the matched pair throughout.

**What depends on pending results.** The motion-history swap test decides whether the inertia resemblance in §5 can be claimed, and may provide the same-input comparison W1 asks for. The decoupling model decides whether the plan difference follows the scenario-group mix or the lateral-plus-stationary bundle, and gives a second balanced-versus-obstacle-heavy contrast at 6,400 samples that bears on W4. Base-Rerun affects H1 only and not my domain assessment.

### Missing Key References
- Trautman, P. and Krause, A., "Unfreezing the robot: Navigation in dense, interacting crowds," IROS 2010: the original naming of the freezing robot problem (W11).
- Chitta, K., Prakash, A., Jaeger, B., Yu, Z., Renz, K. and Geiger, A., "TransFuser: Imitation with Transformer-Based Sensor Fusion for Autonomous Driving," IEEE TPAMI 2023: a documented CARLA agent with a creep (forced-forward) heuristic and with results reported over several training seeds (W4, W7).

~~~yaml suggested-references
- title: "Unfreezing the robot: Navigation in dense, interacting crowds"
  authors: ["Trautman, P.", "Krause, A."]
  year: "2010"
  doi: null
  arxiv_id: null
- title: "TransFuser: Imitation with Transformer-Based Sensor Fusion for Autonomous Driving"
  authors: ["Chitta, K.", "Prakash, A.", "Jaeger, B.", "Yu, Z.", "Renz, K.", "Geiger, A."]
  year: "2023"
  doi: null
  arxiv_id: "2205.15997"
~~~

### Questions for Authors
1. Does the unicycle integration clamp speed at zero? If not, a plan from rest with negative accelerations produces reverse motion, and L, a path length, counts it. How often does that happen in the at-rest stratum?
2. Are the per-step inputs (images and history, or the cached VLM state) logged, so that both experts could be queried on one common set of low-speed contexts? Is the pending swap test such a same-input test?
3. At what rendering quality were the training data recorded in CARLA 0.9.16?
4. Can you report the at-rest stay-put share excluding blocked runs, and stratified by the reason the vehicle is at rest (gate-held, blocked, other)?
5. For the 1,600-sample pair, can you give the low-speed and at-rest stay-put shares as means of per-route shares with intervals, as for the 6,400-sample pair, rather than pooled values only?
6. Please confirm that the expert is evaluated four times per call. Have you compared its outputs with an exact many-step integration on any logged contexts?
