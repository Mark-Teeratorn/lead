# Academic Integrity Verification Report — Stage 2.5, data / originality / claims / failure modes

Run: 15 Nov 2026, about 15:50–16:40 (UTC+7). Agent: `integrity_verification_agent`, phases C (reported data), D (originality, limited), E (claims) and the 7-mode checklist. Phases A and B (references, citation context) are handled by another agent and are not in this report.

Manuscript checked: `docs/manuscript_revision_draft.txt`, SHA-256 `8d2140a4a6d7c0b5…` (unchanged at the end of the run). Line numbers below are lines of that file.

**The repository changed during this review.** Commit `5ea85bca` (15:49:37) added `ANALYSIS_ADDENDUM.md` §17, and `scripts/evaluation/paper_reanalysis.py` has 29 uncommitted lines (`analysis_braking`). The manifest (15:33:46) has no `braking` key yet. §17 withdraws a conclusion that the manuscript under review still states (IL-SERIOUS-1).

## Verification mode

Initial verification (Mode 1, pre-review), restricted to the phases named above. Read-only; nothing in the project was changed.

## Verdict

**FAIL — corrections required before Stage 3.** One SERIOUS and eleven MEDIUM issues. All are statements, labels or omissions. No reported number was found to be fabricated, mis-transcribed or attributed to the wrong model, pass or controller: every headline number was traced to a manifest key, and the main ones were recomputed from the raw step logs with separate code.

The 7-mode checklist blocks independently: Modes 1, 5 and 6 are SUSPECTED.

## Verification summary

| Category | Checked | Passed | Issues |
|---|---|---|---|
| Number checker, Section 4 to references | 1,152 tokens (283 ignored) | 1,152 "supported", 0 unsupported | The check is weak, see C1 |
| Numbers in title, abstract, Section 1, Section 3, table headers and captions (by hand, key-directed) | all | all but 3 | 1 inconsistent (24 GB GPU), 2 without stored evidence (416 tensors, 10⁻⁵ m) |
| Independent recomputation from raw step logs | 7 quantities × 3 arms | all match | 0 |
| Internal consistency (same quantity everywhere) | abstract / intro / results / discussion / conclusion | values consistent | 2 statement contradictions (collisions; H1 timing) |
| Direction and labelling of comparisons | abstract and intro | directions correct | 3 labelling gaps (MINOR) |
| Decisions vs `second_pass_decisions` and addendum rules | R1, R2, R3, H2 pass 1, H2 pass 2, two-pass mean, collisions | all match | 1 wording violation of §12a |
| Pre-specification claims | 13 | 4 accurate as written, 1 not checkable | 6 stronger than the record, 2 omissions |
| Claims (E) | 24 registered (all HIGH-IMPACT, all checked) | 12 VERIFIED | 1 MAJOR_DISTORTION, 6 overstated (MEDIUM), 5 MINOR_DISTORTION |
| Originality (D) | internal duplication only | no duplicated paragraph | not checked against any external source |

Not run, and why: the claim-registry and evidence-row scripts (#737, #656), C3 figure trace and C4 passport check need a passport, a Figure Package and an evidence folder; none was in the dispatch. `[E4-SKIPPED: no scope context]`. `[E6-SKIPPED: no revision evidence]`. The orchestrator should run the C4 declaration check (D7) on the passport; this manuscript reports own experiments.

---

## Phase C — reported data

### C1. Number checker

`python3 scripts/paper/check_manuscript_numbers.py --manuscript docs/manuscript_revision_draft.txt` → `13338 numeric source values from 2 file(s)`; `supported: 1152 unsupported: 0 ignored: 283`.

What this result is worth: the script accepts a token if any of 13,338 source values (or its absolute value, or 100×) rounds to it. I measured how often an arbitrary number passes:

| Random token | Accepted |
|---|---|
| 0–100, two decimals | 31.8 % |
| 0–20, two decimals | 71.9 % |
| 0–1, two decimals | 100 % |
| 0–100, one decimal | 90.8 % |
| 100–1000, integer | 81.5 % |

So "0 unsupported" shows that no number is absent from the manifest. It cannot show that a number is attached to the right model, pass, controller or statistic. The statement "numbers in Sections 4–6 are machine-checked" should not be relied on beyond that. It also covers nothing before Section 4.

### C2. Independent recomputation (separate code, raw `predicted_trajectories.jsonl` and `checkpoint_endpoint.json`, 44 routes per arm)

No malformed line in any of the six arms; step logs of pass 1 and pass 2 are not byte-identical on any route.

| Quantity (balanced vs obstacle-heavy) | Pass 1 | Pass 2 | Gate-off | Manuscript |
|---|---|---|---|---|
| Standstill < 0.1 m/s | 25.71 / 33.78, −8.06, W = 213, p = 0.000709, lower on 36 | 28.01 / 33.10, −5.09, p = 0.00211, lower on 35 | 27.42 / 24.57, +2.85, p = 0.172 | match |
| Plans < 1.5 m, all steps (H3 / R1) | 2.47 / 13.03, −10.56, lower on 42 | 3.02 / 10.13, −7.11, p = 1.9e-9, lower on 41 | 2.72 / 8.94, −6.22, lower on 41 | match |
| Stay-put share at ≤ 0.5 m/s | 2.08 / 14.00, lower on 43 | 1.86 / 11.74, lower on 42 | 1.78 / 10.25, lower on 44 | match |
| Stay-put share at rest | 2.62 / 16.02 | 2.38 / 13.70 | 2.18 / 12.95 | match |
| Blocked time | 7.75 / 0.18 | 8.51 / 0.69 | 14.05 / 2.89 | match |
| Crawl 0.1–1.0 m/s | 11.74 / 12.39 | 12.79 / 12.63 | 12.75 / 16.93 | match |
| Driving Score | 49.85 / 53.09 | 42.45 / 50.57 | 45.69 / 47.95 | match |

BCa intervals from `scipy.stats.bootstrap` (different random stream) agree with the reported ones to within 0.1–0.3 pp, and no interval changes side of zero.

Primary result: `compute_paper_tables.py` is unchanged since `84b3eb3e` (`git diff 84b3eb3e HEAD` empty; `013a12bd → 84b3eb3e` adds one trailing blank line). `A.primary_reproduction_check.passed = true`. Confirmatory record: −8.0616 pp, CI [−15.076, −1.250], W = 213, p = 0.000709.

One coincidence was checked and cleared: the balanced model has exactly 7,262 blocked steps in pass 1 and in pass 2. The runs behind the two totals are different (22 runs on 6 routes; 25 runs on 8 routes).

### C3. Title, abstract, Section 1, Section 3, table headers and captions

Supported (source in brackets):

- Abstract and Section 1: 44 routes; 14.00 / 2.08; 11.74 / 1.86; 10.25 / 1.78; 16.02 / 2.62; "43 of 44 routes" [`V.golden_minus_flooded`, `Y`]. 3.02 / 10.13, −7.11, [−10.82, −4.68] [`second_pass_decisions.R1`, `T`]. −8.06 [−15.08, −1.25]; −5.09 [−11.79, 0.98]; −6.57 [−11.18, −1.73] [`A`, `O`, confirmatory record]. +2.85 [−2.70, 10.32] [`P(2)`]. 16.93 / 12.75 [`X`]. 7.75 / 0.18, 8.51 / 0.69, 14.05 / 2.89, 8.13 / 0.43 (0.4349) [`U`]. 46.15 / 51.83, [−12.10, −0.46] [`O(ii)`]. "always on routes with a collision event": 6/6, 1/1, 8/8, 1/1, 12/12, 2/2 [`U.routes_with_blocked_time`]. 31 % / 11 % [provenance L54–57].
- Section 3.1: K = 64, Δt = 0.1 s, 48 history tokens, normalisation constants (0.0290, 0.6810; 0.000269, 0.0261), 20 Fourier frequencies up to 100, hidden size 2,048 [`config.json` of the Golden-6400 export]. L = 0.59 m and 3.1 m [addendum 11-A; reproduced by arithmetic]. 1.6 % [6.4 / 6.3].
- Section 3.2: 31.0 / 10.9 / 30.6 / 11.4 %; −1.33 pp; 5.17 / 5.85 %.
- Section 3.3 and Table 1: every entry [dataset cards in `a100_bundle/datasets`, `A100_TRAINING_PROVENANCE.md`, `train_eval_overlap_canonical44.json`]; `large_v3` shares recomputed from `conversion_stats.json` (1,398 / 2,401 / 777 / 932 / 932 of 6,440). CARLA 0.9.16, 10 Hz capture-only cameras, 17.5 s, 5 m, the infraction list, stationary < 0.5 m over 6.4 s [`~/lead2alpa` README, `docs/COLLECTION_REPORT.md`, `src/lead2alpa/convert.py` L78–81]. Buckets divisible by four, SHA-1 order with seed 0 [`build_curation_matrix.py`].
- Section 3.4 and Table 2: every schedule entry [provenance table; `trainable_params: 2,280,592,386` in `train_golden_6400.log` L153]. Evaluation dates match the result-file dates of all six models (Base 38 + 5 + 1). Controller: all constants match `alpamayo_bridge_agent.py` L385–607; SHA-256 recomputed = `082c6ecc…10d3`. S = 8 and cache steps [3, 4, 5, 6] [`flashdrive_server.py` L59–60]. Tuning routes [`H.tuning_routes_union`].

Not supported or inconsistent:

| Line | Quote | Finding |
|---|---|---|
| 101 | "fine-tuned and evaluated in closed loop on a single 24 GB GPU" | INCONSISTENT. Training ran on an A100 (`A100_TRAINING_PROVENANCE.md` L1–3; addendum §6 "available A100 window"). Section 3.4 states 24 GB for deployment only, and no training hardware. See IL-MEDIUM-6. |
| 193 | "416 parameter tensors" | Found only in `HANDOFF.md` L52 and older notes, not in the trainer artifacts or the provenance file. |
| 139 | "the waypoints agree to within 10⁻⁵ m" | The script exists (`scripts/paper/check_action_space_equations.py`, 5 random control sets). No stored output was found, and I was not permitted to run it. |
| 169 | "one model was trained on it with the recipe and schedule of the other 6,400-sample models" | No trainer artifact for this model is in `docs/provenance` (the export on `/mnt/disk2` has weights and `config.json` only). The provenance file still says "No model has been trained on it". |

### C4. Same quantity, same value

Values agree everywhere they recur (H2 pass 1, pass 2, two-pass mean; H3; gate-off; blocked time; Driving Score; stay-put shares). Two statements contradict each other:

- L408 "the balanced model had **more** collision events" against L421 "we do not say that the balanced model collides more" and the abstract (IL-MEDIUM-5).
- L89 and L103 on when H1 was fixed, against L241 "H1's p-value was known before the family was declared" (IL-MEDIUM-2).

### C5. Direction and labelling in abstract and introduction

Directions are right throughout (balanced minus obstacle-heavy; obstacle-heavy value first where two values are listed in that order). Three labels are missing:

- L72, L97, L417: 14.00 % and 2.08 % are means of per-route shares of low-speed steps. Pooled over steps the shares are 24.9 % and 2.3 % (L358). The abstract says "% of steps".
- L72: "in two passes, with and without the controller's standstill gate". The gate-off run is one pass (L344).
- L72, L99: "its Driving Score was lower (46.15 vs 51.83)". The two-pass-mean BCa interval excludes zero, the Wilcoxon p is 0.11, no rule was attached, and neither pass alone has an interval excluding zero (−3.24 [−13.83, 6.41]; −8.11 [−17.15, 0.64]). The discussion (L423) says this; the abstract and introduction do not.

### C6. Decisions against `second_pass_decisions` and the addendum

| Statement | Line | Record | Result |
|---|---|---|---|
| H2 pass 1 "case A1, replicated" | 287 | CI upper −1.25 < 0, Δ = −8.06 ≤ −4.0 (§1; pre-registration §3) | matches |
| H2 pass 2 "case B" | 287, 320 | `H2 on run 2 alone: B` | matches |
| Two-pass mean, "no decision was attached" | 320 | key labelled "no decision attached" | matches |
| "H3 is met" / R1 "replicated" | 285, 354 | `R1: replicated`, −7.11, [−10.82, −4.68], p = 1.9e-9 | matches |
| R2, R3 "both replicated", adjusted p 1.4e-5 and 0.028 | 382 | `R2`, `R3: replicated`, Holm p 1.37e-5 and 0.0284 | matches |
| "collision counts did not differ detectably" | 72, 99, 320, 421 | §12a; two-pass mean +0.10, CI [−0.10, 0.28] | matches |
| "had **more** collision events" | 408 | §12a allows "more" only if that interval excludes 0 | violates the rule |
| Stop episodes "reads as mixed" | 378 | `T.prespecified_reading_run1.reading = mixed` | matches |
| Low-speed and at-rest differences in pass 2 | 356, 360 | §10 wording rule; same sign, intervals exclude 0 | matches |

---

## Pre-specification claims (task 2)

Record used: commit times of `ANALYSIS_ADDENDUM.md` and `CONFIRMATORY_DEVIATIONS.md`, `outputs/revision_suite2_audit.log`, result-file dates.

General limit on all of them: the branch `revision-round1` has no upstream, and the newest remote ref is `my-lead/main` at 3 Nov 2026. Every pre-specification commit (11–15 Nov) exists only in the local repository. Commit times are therefore self-asserted and were not time-stamped by a third party. Result-file dates are consistent with them.

| Claim | Line | Record | Assessment |
|---|---|---|---|
| H2 fixed before `Flooded-6400` was evaluated | 239 | `013a12bd` 11 Nov 17:05:00; run started 17:20:06; first result 18:00 | Accurate. The manuscript states the limits (routes already observed, endpoint chosen from earlier results). |
| Addendum committed after the run and before standstill was computed | 239 | `2e2bc0ef` 12 Nov 12:56:30; confirmatory record written 12:57:02 | Consistent (30 s margin). Whether nothing was computed earlier cannot be checked. |
| H1 "specified … before the comparison they concern was evaluated"; "Only H1 and H2 were fixed before their first data" | 89, 103 | Pre-registration §1 lists `Base` and `Golden-1600` results as known; addendum §1; manuscript L241 | **Not supported for H1.** Its result against the original `Base` run (+11.06, p = 0.0076) was known. Only the re-run comparator was specified before its data (§5b, 12 Nov 15:03). |
| H3 "before the second pass of the obstacle-heavy model existed" | 89, 285 | §9 `a1a2f96e` 14 Nov 12:35:56; obstacle-heavy pass 2 started 21:35:52 | Accurate. |
| "fixed before any second-pass value existed"; "on data that did not exist when it was written"; "fixed before that pass"; "fixed before the second pass"; "H3 was added before the second pass" | 354, 285, 72, 382, 441, 283 | Balanced pass 2 started 05:20 on 14 Nov. 14 of 44 routes were scored by 12:24, and their standstill was compared with pass 1 at 12:30 (run note 6, `fe9bc514` 12:29:38), six minutes before §9. | **Stronger than the record.** True only for the obstacle-heavy model and for plan-level values. |
| Collision wording rule "fixed before the second pass" | 320 | §12a `d7215b6c` 14 Nov 16:23; 25 balanced routes scored | **Stronger than the record.** True as "before any second-pass collision count was computed". |
| Partial looks | — | Run notes 6, 7 and 8 (14 Nov 12:30 and 21:45; 15 Nov 10:55, 31 of 44 routes, including the plan share 2.85 % vs 9.90 %) | The rules of §9, §10, §12a and §13 were committed before notes 7 and 8 and not changed. **The manuscript mentions none of the three looks.** §15 was written 45 minutes after look 8 (it says so). |
| "All other analyses were written into a dated addendum before their values were computed"; "each was written into the analysis addendum before its values were computed" | 94, 352 | §7a was looked at on 18–19 gate-off routes before it was written (addendum §7; manifest `T.label`). §16 was written after computing. Analyses E, F, G, I, J, K, L and M have no addendum entry; J is reported in Section 4.6. | **Not supported as written.** |
| Motion-history test fixed before any swap run | 417 | §11 16:13, 11-A 17:19, 11-B 18:25 on 14 Nov; no `*_histswap` output exists | Accurate; pending. The outcome was redefined twice before any data. When reported, both corrections should be stated. |
| Decoupling arm fixed before training | 169 | §6 `c56dbdee` 12 Nov 23:32:16 | The commit exists. The training start time cannot be checked here. The heading of §6 says 23:40, eight minutes after its own commit. |
| "registered" (ten places) | 72, 90, 91, 283, 287, 291, 352, 386, 390, 441 | `CONFIRMATORY_DEVIATIONS.md` A5: "not as a registration prior to all data"; manuscript L239 says the same; local commits only | **Stronger than the record.** |
| Section 3.2 hypothesis "predicts … which is what the offline decomposition in Section 4.5 shows" | 157 | Manifest with analysis D committed 12 Nov 13:14; low-speed training shares 14:02; first draft containing the hypothesis 15:15 | The hypothesis was written after the decomposition was computed. The text reads as a prediction confirmed. |
| §9 reporting commitment: R1–R3 on the 37 routes and with the §8 sensitivity settings, as sensitivity rows | 354, 382 | Not in the manuscript. The 37-route rows are not in the manifest. The sensitivity rows for pass 2 are in the manifest and are not all supportive. | **Commitment not met**, see IL-MEDIUM-11. |

Addendum headings that disagree with their commits: §6 (23:40 against 23:32:16) and §7 (22:30, and a clarification "22:50", against 21:19:48 and 21:20:44). In both cases the commit is earlier than the stated time, so no claim is weakened, but the heading times are not reliable.

---

## Phase E — claims (task 3)

Claim registry: built by reading, not by the registry script; extraction completeness is not machine-detectable. 24 claims, all HIGH-IMPACT (headline, numerical or causal), all checked against the manuscript's own evidence.

| Verdict | Count |
|---|---|
| VERIFIED | 12 |
| MINOR_DISTORTION | 5 |
| Overstated (MEDIUM) | 6 |
| MAJOR_DISTORTION | 1 |
| UNVERIFIABLE | 0 |

VERIFIED: stay-put difference at low speed, in both passes, both controllers and at rest; H3 met; H2 met in pass 1 and case B in pass 2; no detectable difference in total standstill without the gate; blocked time higher for the balanced model in three arms and always on routes with a collision event; R2 and R3 replicated; collision counts not detectably different; no safety claim made (stated at L72, L99, L441, and no sentence claims one model is safer); route completion not detectably different; 1,600-sample pair not detectably different; training-data shares, pool size and CARLA 0.9.16 for collection.

**MAJOR_DISTORTION (1)** — "Neither model planned a stop from motion in more than 0.3 % of steps" (L72); "so the difference is one of restarting, not of stopping" (L97); L356; L417. See IL-SERIOUS-1.

**Overstated (6)**

1. Causal and general wording: title "Sets"; L72 "We show that this choice sets how the policy behaves once it is slow, and that it trades hesitation against progress"; L101 "a controlled measurement of how fine-tuning data composition alone moves"; L423 "this class of policy". The evidence is one pair of checkpoints, one seed each, three bundled factors. At 1,600 samples, where the training shares differ as much (30.6 % against 11.4 %), no difference was detected (L400; pooled stay-put 19.8 % against 16.4 %). The historical obstacle-heavy checkpoint gives 14.6 % against 24.9 % for the matched one (L358). Section 3.2 itself says the hypothesis "is at most part of the explanation". The abstract omits the 1,600-sample null.
2. "Progress" in the title and L72: no progress measure differs detectably over both passes (route completion +3.12, CI [−2.32, 9.03]). The measured costs are blocked time and Driving Score.
3. Inertia: L417 "It is also the behaviour described as the inertia problem" and "That is the pattern the inertia account predicts"; keyword "inertia problem". Addendum 11-B allows the attribution only after outcome W-a. The same paragraph ends "we do not claim that mechanism", so the paragraph contradicts itself.
4. Collisions and contact: L408 "had **more** collision events"; L388 "drives into an obstruction and is held there"; L421 "held in place after contact". Blocked time is inferred from the command log (L380), and no ordering of collision and blocked run was analysed.
5. L441 "Fine-tuning itself raised Driving Score over the unadapted policy ([[PENDING: H1 on Base-Rerun]])" states the outcome of a pending test. On the 24 untuned routes the manuscript says the gain "is not established by these data" (L291).
6. L417 "at a rate that tracks their share in the training data". L358 says "the shares are not reproduced".

**MINOR_DISTORTION (5)**: the three labelling gaps of C5; L344 gate-off differences at 0.5 and 1.0 m/s given without their Wilcoxon p-values (0.045 and 0.025; balanced lower on 30 and 31 routes), although sign-based and mean-based readings diverge there; L334 "mean predicted extent was 5.75 m longer" without the caveat of Section 3.1 that L depends on speed.

Novelty-claim classification (advisory, not counted): ADV-E5-1 L85 "We have not found a study…", ADV-E5-2 L117 "We did not find in them a report…", ADV-E5-3 L119 "What we have not found…" — all UNRESOLVED: no documented search (databases, date range, date searched).

---

## Phase D — originality (task 4, limited)

Checked:

- Internal duplication, 10-word shingles over 119 paragraphs: no duplicated paragraph. The only repeats are result sentences shared by abstract, introduction and conclusion.
- Overlap with the authors' own dataset cards: L169 "groups A and C hold 88 % of all left swerves but 58 % of right swerves, so raising the hazard share pushes the lateral balance left" is a close paraphrase of the `matrix_flooded_6400` card (L86). Own material; cite the card.
- AI-assistance disclosure (L455): present. Accurate in kind for prose, equations, re-analysis scripts, table and bibliography checks and drafting. It under-describes the rest: 67 of the 72 commits since 11 Nov carry an AI co-author trailer, and they include the addendum sections and decision rules, the run notes, the gate-off and history-swap controller variants, the queue scripts, the related-work additions [35]–[47] and the training provenance report ("Report from the Claude session on the A100 training machine"). The closing attestation "All experimental designs, code, numerical results and conclusions were checked by the authors" cannot be verified here, and the notes block still lists items waiting for the authors.

Not checked: any comparison with cited or uncited external text (no plagiarism tool, no web); self-plagiarism against earlier publications; paraphrase closeness of Section 2. `docs/Few Edge Cases Are All You Need….pdf` (untracked, dated 10 Nov) is a slide deck whose second page states "the widely-used hazard-flooding strategy not only fails but can degrade safety". I read two pages only. If it was circulated, it contradicts the present manuscript.

> Tool limitation: no originality grade is given for any paragraph. Use iThenticate or an equivalent before submission.

---

## Issue list

### SERIOUS (must fix)

| ID | Location | Issue | Evidence | Fix |
|---|---|---|---|---|
| IL-SERIOUS-1 | L72, L97, L356, L417 | "Neither model planned a stop from motion in more than 0.3 % of steps", "the difference is one of restarting, not of stopping", "That is the pattern the inertia account predicts". The measure (plan < 1.5 m at more than 0.5 m/s) is close to zero by construction, because L is integrated from the current speed (L139). | Addendum §17 (`5ea85bca`, 15:49) withdraws the conclusion. My recomputation of the §17 quantity (plans ending at rest, v_end < 0.5 m/s, among moving steps), balanced vs obstacle-heavy: pass 1 0.73 % vs 1.62 % (−0.89, BCa [−1.27, −0.63]); pass 2 0.67 % vs 1.41 % (−0.74, [−1.02, −0.52]); gate-off 0.66 % vs 1.52 % (−0.85, [−1.14, −0.59]). By stratum: 0.5–2 m/s 0.35 / 0.78, 0.22 / 0.65, 0.22 / 0.74; above 2 m/s 0.99 / 2.17, 0.99 / 2.16, 1.02 / 2.26. Every interval excludes 0. | Remove the four statements. Run `analysis_braking`, report its values, and apply the §17 rule: the "restarting, not stopping" sentence is not kept, because the braking-plan shares differ in both strata and all arms. My values are a preview from separate code; the reported ones must come from the project script. |

### MEDIUM (must fix)

| ID | Location | Issue | Fix |
|---|---|---|---|
| IL-MEDIUM-1 | L72, L283, L285, L320, L354, L382, L441 | Timing of H3, R2, R3 and the collision rule stated as before the second pass or before any second-pass value. | Use the wording of L89 everywhere: "fixed on 14 Nov 2026, before the obstacle-heavy model's second pass started and before any second-pass plan-level value was computed; 14 of the balanced model's 44 second-pass routes had been run and their standstill looked at". Add the three partial looks (run notes 6–8) to Section 4.1. Correct the manifest label "committed before the second-pass values existed" in the script. |
| IL-MEDIUM-2 | L89, L103 | H1 described as fixed before its comparison or first data. | "H2 was specified before its comparison was evaluated. H1 is in the same document, but its result against the original `Base` run was already known; only the re-run comparator was specified before its data." |
| IL-MEDIUM-3 | L94, L352 | "All other analyses … before their values were computed." | "Analyses added from 13 Nov were written into a dated addendum that states what had been seen. Section 7a was looked at on a partial route set before it was written, §16 was written after computing, and the analyses of the first re-analysis (command classes, collision rates, threshold sweep, rationale keywords, RC–infraction correlation, harmonised truncation) have no addendum entry." |
| IL-MEDIUM-4 | L72, 90, 91, 283, 287, 291, 352, 386, 390, 441 | "registered". | "pre-specified (repository commit `013a12bd`)". State once that the commits are in the project repository and were not time-stamped by a third party. |
| IL-MEDIUM-5 | L408; L388, L421 | "had **more** collision events"; contact stated as fact. | "In the first pass the balanced model had 44 collision events and the obstacle-heavy model 36 (logged entries 46 and 37); over both passes the counts did not differ detectably (Section 4.4)." L388 and L421: "is commanded to accelerate without moving, on routes that have a collision event". |
| IL-MEDIUM-6 | L101; Section 3.4 | Fine-tuning on a 24 GB GPU. | "fine-tuned on one A100 and served and evaluated in closed loop on a single 24 GB GPU"; add the training hardware to Section 3.4. |
| IL-MEDIUM-7 | Title; L72; L101; L423; L417 | Causal and general wording; the abstract omits the 1,600-sample null; "progress"; "tracks". | Title without "Sets" and "Progress", with the single-seed scope. L72: "In one matched pair of 6,400-sample checkpoints (one seed each) the mix changed what the policy planned once it was slow … At 1,600 samples no difference was detected." L101: drop "alone". L423: "this policy". L417: "is ordered as". |
| IL-MEDIUM-8 | L417; keywords L74 | Inertia mechanism asserted before the test. | "This resembles the behaviour described as the inertia problem [12]"; delete "That is the pattern the inertia account predicts"; keep the keyword only if outcome W-a allows it. |
| IL-MEDIUM-9 | L441 | Outcome of pending H1 stated. | Replace the sentence by one placeholder: `[[PENDING: H1 result on Base-Rerun, sentence to be written from the result]]`. |
| IL-MEDIUM-10 | L157 | Post hoc hypothesis presented as a confirmed prediction. | Add: "This hypothesis was formulated on 12 Nov 2026, after the primary result and the band decomposition were known; their agreement with it is not a test of it." |
| IL-MEDIUM-11 | L354, L382 | Sensitivity rows promised in addendum §9 are missing. | Compute and report R1–R3 on the 37 routes and with the §8 settings for pass 2. Preview from my code, 37 routes: R1 −7.81 [−12.06, −5.24]; R2 −12.65 [−21.95, −6.36]; R3 +7.34 [1.98, 16.86], p = 0.050. From the manifest, pass 2: run ≥ 40 steps +7.66 [1.60, 15.59]; run ≥ 200 steps +6.54 [2.35, 14.11]; **throttle ≥ 0.2: +6.85 [−0.06, 14.81], which includes zero**. L382 "All of these intervals exclude zero" holds for pass 1 and gate-off only; say so. |

### MINOR (recommended now, required at Stage 4.5)

| ID | Location | Issue | Suggestion |
|---|---|---|---|
| IL-MINOR-1 | L72, L97, L417 | Per-route mean not labelled. | Add "(mean of per-route shares; pooled 24.9 % and 2.3 %)". |
| IL-MINOR-2 | L72 | Gate-off described as two passes. | "in two passes with the default controller and one pass without the standstill gate". |
| IL-MINOR-3 | L72, L99 | Driving Score "was lower" without the test. | Add "two-pass mean; BCa interval [−12.10, −0.46], Wilcoxon p = 0.11; no rule fixed in advance". |
| IL-MINOR-4 | L344 | p-values omitted at 0.5 and 1.0 m/s. | Add p = 0.045 and 0.025, balanced lower on 30 and 31 routes. |
| IL-MINOR-5 | Tables 3–4, L445 | `Base` standstill 40.45 against 40.32 in the confirmatory record (the registered script scores route 23687, which has no step log, as 0 %). Explained only in the notes block. | One sentence in Section 4.1 or the table note. |
| IL-MINOR-6 | L356 | "Both first-pass differences have the same sign…". | "Both differences have the same sign as in the first pass…". |
| IL-MINOR-7 | L209 | "velocity caching on steps 3–6". | Indices are zero-based; the expert is evaluated four times per call. |
| IL-MINOR-8 | L213–215 | The no-waypoint fallback (throttle 0.35, brake 0; controller L495–500) is not described. | One sentence. No logged step in the three arms I scanned has fewer than five waypoints. |
| IL-MINOR-9 | L334, L366 | L-based comparisons not conditioned on speed. | Add the caveat of Section 3.1. |
| IL-MINOR-10 | L193, L139, L169 | 416 tensors; 10⁻⁵ m; training of the fifth model. | Store the equation-check output; add trainer artifacts of the fifth model to `docs/provenance`; update the provenance file. |
| IL-MINOR-11 | L455 | AI disclosure narrower than the record. | Add analysis design and decision rules, experiment scripts and monitoring, controller variants, literature search; authors confirm the attestation. |
| IL-MINOR-12 | Addendum §6, §7 | Heading times later than commit times. | Add a dated correction note; do not rewrite the sections. |
| IL-MINOR-13 | Notes block L8, L12, L13 | Lists placeholders that were filled on 15 Nov. | Housekeeping; the block is stripped before submission. |

---

## Legitimately pending (not counted as issues)

| Item | Lines |
|---|---|
| H1 on `Base-Rerun`, its Table 3 and 4 rows, dates, 24-route comparison | 72, 103, 202, 231, 254, 268, 291, 441 |
| Decoupling model (Table 2 row, results, sentences) | 72, 103, 169, 427 |
| Motion-history swap test | 97, 417 |
| Archive DOI, commit hash | 443, 445 |
| Author contributions, funding, competing interests | 447, 449, 451 |

Status confirmed on disk: `base_run2` has one route directory (started 15:14 on 15 Nov); no `*_fgbalanced_*` or `*_histswap_*` output exists; manifest keys Q, S, S15, W and half of Z are `pending`.

---

## AI research failure mode checklist

| Mode | Outcome | Evidence | What would clear it | Blocks? |
|---|---|---|---|---|
| 1. Implementation bug passing self-review | **SUSPECTED** (two confirmed, bounded instances) | Headline numbers reproduced from raw logs with separate code; registered script unchanged; reproduction check passed. Instances: (a) the "stop from motion" measure, near zero by construction, reached the abstract; (b) the registered script silently scores a route without a step log as 0 % standstill (`Base` 40.32 against 40.45; the H2 arms are complete and not affected). Also: `except Exception: pass` in the registered loader; the number checker accepts 32–100 % of arbitrary numbers; the first correction of the history-swap outcome (11-A) was itself wrong and was caught by review (11-B). | Fix IL-SERIOUS-1; disclose IL-MINOR-5; make the number checker key-directed or stop citing it as verification; store the equation-check output. | Yes |
| 2. Hallucinated citation | INSUFFICIENT EVIDENCE (not my phase) | Handled by the reference agent. The notes block lists unconfirmed pages and volumes for [36], [40], [41], [47], and content statements for [12] and [27] taken "from the authors' knowledge". | Reference agent's report. | No |
| 3. Hallucinated experimental result | CLEAR | 44 result directories per arm with dates matching Table 2; per-job checkpoint and controller hashes in the audit log; both checkpoints served as `action_expert.safetensors` of identical size; logs of the two passes differ; all recomputed values match; pending items are marked pending and have no data. | — | No |
| 4. Shortcut reliance | **SUSPECTED** (flag only at this stage) | No same-input comparison: the models visit different states (the manuscript says so). The at-rest and rationale conditionings narrow this but do not remove it. The 1,600-sample pair and the historical checkpoint do not follow the training shares. Three factors bundled, one seed. | Sample many noise seeds at logged low-speed states for both experts; the decoupling arm; further seeds. | No (re-checked at 4.5) |
| 5. Bug reframed as insight | **SUSPECTED** (one confirmed instance) | "The difference is one of restarting, not of stopping" was built on the artefact of Mode 1(a). With a speed-robust measure the obstacle-heavy model plans to brake to rest about twice as often while moving. Second, weaker item: blocked time read as "held after contact" without a contact signal. No "surprisingly"-type wording in the text. | IL-SERIOUS-1 and IL-MEDIUM-5; for blocked time, show that a collision record precedes each blocked run, or keep the command-log wording. | Yes |
| 6. Methodology fabrication | **SUSPECTED** (one statement) | Verified against artifacts: Table 2, optimizer settings, dataset construction, collection details, controller constants and hash, the gate-off controller diff (two functional changes, six log fields). Not matching: L101 says fine-tuning ran on a 24 GB GPU; it ran on an A100. Gaps: fallback branch, cache-step convention, no trainer artifact for the fifth model, collection rendering quality open. | IL-MEDIUM-6; IL-MINOR-7, 8, 10. | Yes |
| 7. Frame-lock | INSUFFICIENT EVIDENCE | Against: the paper was reframed on 15 Nov by a rule written on 14 Nov, before the deciding data; withdrawn claims are listed. For: the causal title survives the 1,600-sample null and the single seed; the inertia keyword and the H1 conclusion are written ahead of their tests; the Section 3.2 hypothesis is kept as a prediction. | The authors' answer to: given one seed and no effect at 1,600 samples, is "composition sets a trade-off" still the question this design can answer, or is it "one matched pair differs at low speed, and the controller decides how that shows"? | No (warning; re-checked at 4.5) |

Blocking outcome: Modes 1, 5 and 6. The user may confirm and fix, override with reasoning, or revise the passages and ask for a re-check.

---

## What could not be verified

- That nothing was computed before the commit that says it was not computed (for any pre-specification claim). Commit times are local.
- Whether `Flooded-6400` standstill was unseen at 12:56 on 12 Nov (30-second margin).
- Training start time and trainer settings of the decoupling model.
- The equation check (not run); the 416-tensor count; that the server draws unseeded noise (no seeding call found by search, not traced).
- That the logged speed, throttle and brake are what the simulator applied; that blocked runs follow a contact.
- Tables 3–5 cell by cell: one full row (`Golden-6400`) and all termination counts were checked by key, the rest by the number checker only. Figures 1–5 were not inspected (placeholders in the text file).
- Originality against any external source.
- The authors' attestation in the AI disclosure.

## Audit trail

Read in full: the four role files; the manuscript; `ANALYSIS_ADDENDUM.md` (§1–17); `CONFIRMATORY_DEVIATIONS.md`; `CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md`; `A100_TRAINING_PROVENANCE.md`; `train_eval_overlap_canonical44.json`; `paper_tables_confirmatory_record.json`; `rerun_audit_matrix_flooded_6400.txt`; `revision_suite2_audit.log`; `check_manuscript_numbers.py`; `check_action_space_equations.py`. Read in part: the manifest (keys A, B, D, E, F, H, I, J, K, L, M, N, O, P, T, U, V, X, Y, Z, `second_pass_decisions`, `pass_agreement`, `data_checks`); `compute_paper_tables.py`; `paper_reanalysis.py` (structure, `main`, `analysis_braking`); the controller and its gate-off copy (diff); dataset cards; `build_curation_matrix.py`; `~/lead2alpa` README and `convert.py`; `flashdrive_server.py` (constants).

Commands: the number checker; read-only `git log`, `git diff`, `git status`, `git for-each-ref`; `ls`, `grep`, `sed -n`, `diff`; `nice python3` snippets that read JSON and step logs (several passes over the step logs of the six 6,400-sample arms, each well under a minute). No GPU use, no process signalled, no project file written. Snippets are in the session scratchpad, not in the repository.
