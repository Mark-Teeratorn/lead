# Reframe draft: title, abstract and introduction in two versions

Written 14 Nov 2026, before the second pass was complete. On 15 Nov rule R1 was met and Version A was applied to the manuscript (commit 7a419370), with the second-pass values filled in; this file is kept as the record of what was drafted in advance.
Which version is used is decided by the rules already committed in `ANALYSIS_ADDENDUM.md` (§9 R1–R3, §10, §12a), not by preference.

- **Version A** is used if the plan-level findings replicate on the second pass (R1 met; low-speed stay-put difference has the same sign and an interval that excludes 0).
- **Version B** is used if they do not. The paper then stays led by the registered comparison (H2), as the manuscript is now.

Markers to fill: `[[RUN-2: …]]` second-pass values, `[[BALANCED: …]]` the decoupling arm, `[[HISTORY-TEST: …]]` the motion-history swap test, `[[H1: …]]` H1 on the re-run Base. All other numbers are in the manifest today.

---

## Version A (findings replicate)

### Title

Recommended, pending the pooled collision result (addendum §12a):

> **Fine-Tuning Data Composition Sets a Caution–Progress Trade-off in a Vision-Language-Action Driving Policy**

Alternatives:

- *Stop, Creep or Go? Fine-Tuning Data Composition Sets a Caution–Progress Trade-off in Vision-Language-Action Driving* (uses the crawling result; that result is clear only without the gate).
- *Less Hesitation, More Time Blocked: Fine-Tuning Data Composition and Low-Speed Behaviour of a Vision-Language-Action Driving Policy* (names both sides of the trade-off without the word "contact").

Not supported by the data: any title with "safer" or "safety" as a finding.

### Abstract (about 265 words as drafted; to be trimmed to 250 when the markers are filled)

Vision-language-action driving policies with a flow-matching action expert are adapted by fine-tuning on demonstrations whose composition the practitioner chooses. We show that this choice sets how the policy behaves once it is slow, and that it trades caution against progress. We fine-tuned the action expert of Alpamayo 1.5 (backbone frozen) on a balanced mix and on an obstacle-heavy mix with more stationary samples, both drawn from one pool of CARLA expert data and trained on the same schedule (6,400 samples, one seed each). Both models were evaluated in closed loop on 44 Bench2Drive routes, in two passes, with and without the controller's standstill gate. At 0.5 m/s or less, the obstacle-heavy model planned to stay put in 14.00 % of steps and the balanced model in 2.08 % (10.25 % vs 1.78 % without the gate); the second pass gave [[RUN-2: stay-put shares and interval]]. Neither model planned a stop from motion in more than 0.3 % of steps. How this appears in motion depends on the controller. With the gate the obstacle-heavy model stood still longer (registered comparison: −8.06 percentage points, 95 % CI [−15.08, −1.25]); without it total standstill did not differ and the obstacle-heavy model crawled more (16.93 % vs 12.75 % of steps). The balanced model completed more of each route but spent more time commanded to accelerate without moving, always on routes with a collision (7.75 % vs 0.18 %; 14.05 % vs 2.89 % without the gate). Collision counts and Driving Score did not differ detectably, and we make no safety claim. The two mixes differ in three factors at once; [[BALANCED: one sentence]].

### Introduction

**1. What these policies are.** Vision-language-action (VLA) models for driving combine a pretrained vision-language model, which encodes camera images, ego-motion history and a navigation instruction, with an action head that outputs a future trajectory. In dual-system designs such as π0 [26], π0.5 [1] and NVIDIA's Alpamayo family [2, 19], the action head is a flow-matching [8] expert that turns a noise sample into a trajectory in a few solver steps. Unlike a regression head, it can represent several distinct futures for one scene and returns one of them at each call.

**2. The choice the practitioner makes, and why it matters.** Such a policy is commonly adapted to a new simulator or vehicle by fine-tuning the action expert with the backbone frozen. The practitioner then decides what the fine-tuning set contains. A natural instinct is to add more of what is hard: obstacles, hazards, emergency stops. Demonstrations of these scenarios contain more waiting, so the share of low-speed samples in which the expert stays put rises with them; in our data it is 31 % in the obstacle-heavy mix and 11 % in the balanced one. For a policy that samples from the futures it was shown, this share is not a detail. A vehicle that waits when the road is clear blocks the route and fails the task; one that never waits meets the obstacle. Where a policy sits between the two is what a benchmark score, a passenger and a safety case all depend on.

**3. What is known.** Imitation-learned driving policies that observe their own motion can learn that a vehicle at rest tends to stay at rest. Codevilla et al. [12] named this the inertia problem; it is a form of causal confusion [13] and of the copycat behaviour described for policies trained on observation histories [25, 28]. The remedies proposed so far act on the model input, the loss or the controller [12, 27, 28]. Rebalancing of training data has been shown to raise benchmark scores of a flow-matching planner without a language model [33], and Alpamayo 1.5 has been reported to get stuck in CARLA [34]. Outside driving, robot policies have been reported to freeze or idle because of what their training data contain [44, 45], and work on data mixtures and data quality for imitation learning asks which demonstrations raise task success [35, 36]. In driving, adding safety-critical or rare scenarios has been reported to improve collision avoidance and benchmark scores [38, 39].

**4. What is missing.** We have not found a study that changes only the composition of the fine-tuning set of such a policy, holds the model, the loss, the training schedule and the controller fixed, and measures the result in closed loop at the level of the plans the model produces. Without the last step the question cannot be answered, because standstill in closed loop is a joint product of the model and of the controller that executes its plans.

**5. What we did.** We fine-tuned the 2.28B-parameter action expert of Alpamayo 1.5 on two mixes drawn from one verified pool of CARLA expert samples: a balanced mix (`Golden`) and an obstacle-heavy mix (`Flooded`), at 1,600 and 6,400 samples, with identical training schedules at each size. We evaluated the models in closed loop on 44 Bench2Drive routes [3]. The comparison of the two 6,400-sample models on standstill time was specified, with its test and decision rule, before that pair was evaluated (Section 4.1). We then repeated both evaluations, ran both models with the controller's standstill gate removed, and analysed the logged plan of every step. Each of these later analyses was written down before its values were computed.

**6. What we found.**

- **Data composition shifts what the model plans once it is slow.** At 0.5 m/s or less the obstacle-heavy model planned to stay put in 14.00 % of steps and the balanced model in 2.08 %, on 43 of 44 routes, and the difference holds without the gate (10.25 % vs 1.78 %) and among steps at rest (16.02 % vs 2.62 %). [[RUN-2: replicated on the second pass, values.]] While moving, neither model planned a stop in more than 0.3 % of steps. [[HISTORY-TEST: one sentence, either "replacing the ego history with a moving one removed these plans, the mechanism described as the inertia problem" or "a test that replaced the ego history did not show this dependence".]]
- **How that appears in motion depends on the controller.** With the standstill gate, the obstacle-heavy model stood still longer: the registered comparison gave −8.06 pp (95 % CI [−15.08, −1.25]). Without the gate, total standstill did not differ (+2.85 pp, CI [−2.70, 10.32]) and the obstacle-heavy model crawled more (16.93 % vs 12.75 % of steps). Total standstill time is therefore a property of the model and the controller together, and a poor measure of either.
- **Less hesitation has a cost.** The balanced model completed more of each route (82.4 % vs 74.6 %) but spent more time commanded to accelerate without moving, always on routes with a collision event (7.75 % vs 0.18 % of steps; 14.05 % vs 2.89 % without the gate). Collision counts and Driving Score did not differ detectably [[RUN-2: pooled collision statement by the rule of addendum §12a]]. We make no safety claim in either direction.

**7. Contributions and limits.** The paper contributes (i) a controlled measurement of how fine-tuning data composition alone moves the low-speed behaviour of a flow-matching VLA driving policy; (ii) plan-level measures (stay-put plans by speed, crawling, blocked time) that separate what the model plans from what the controller makes of it, with a closed-loop run without the gate to check them; and (iii) the observation that the resulting difference is a trade-off between caution and progress, not an improvement on the benchmark's score. The limits are those of the design: one training seed per condition, two mixes that differ in three factors at once ([[BALANCED: what the third model adds]]), one policy, one simulator, 44 routes and a controller tuned on 20 of them. Only the standstill comparison was registered before its data; the plan-level findings are post hoc and rest on their replication in the second pass. [[H1: one sentence on adaptation, Section 4.3.]]

Notes for Version A:
- H1, H2 and H3 are no longer listed in the introduction. They are stated where they are tested (Sections 4.1 and 4.3), unchanged.
- "Obstacle-heavy" and "balanced" replace "flooded" and "curated" in running text; the dataset names `Flooded` and `Golden` stay as identifiers. "Curated" suggests one mix is better, which the results do not show.
- Section 5 needs the same change of order (plans, controller, cost), and Section 6 a new first paragraph.

---

## Version B (findings do not replicate)

The manuscript keeps its present title, abstract (the 250-word version now in the draft) and introduction, with these changes only:

1. **Abstract and introduction:** the second-pass sentence states plainly that the plan-level differences seen in the first pass were not reproduced, with both sets of values.
2. **Introduction, paragraph 2:** add the two "why it matters" sentences from Version A paragraph 2 (waiting blocks the route; never waiting meets the obstacle). They do not depend on the result.
3. **Introduction, paragraph 4:** move "specified after first results were known" from before the hypotheses to after them, so the reader meets the question before its caveat.
4. **Contributions:** set as a three-item list; drop item (iv), the list of protocol caveats, into Section 5 where it already is.
5. **Sections 4.6 and 4.7** are kept and labelled as first-pass observations that the second pass did not confirm. Figure 5 moves to the supplementary material.
6. **Title:** unchanged in substance; "Single-Seed Study at Two Dataset Sizes" stays.

In this case the paper's claim is the registered one alone: with the default controller the balanced mix reduced standstill time, the reduction is not robust to removing the gate, and the reasons remain open.
