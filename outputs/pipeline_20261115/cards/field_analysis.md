# Field Analysis Report

Phase 0 of the simulated peer review, Round 2 (pipeline_20261115). Written by the field analyst on 15 November 2026. No reviewer was dispatched and the paper was not reviewed here.

## Paper Basic Information
- **Title**: Fine-Tuning Data Composition Sets a Caution–Progress Trade-off in a Vision-Language-Action Driving Policy
- **File read**: `docs/manuscript_revision_draft.txt`, from the line after `%%% END NOTES` to the end (the authors' working notes above that line were not treated as manuscript text)
- **Abstract length**: 267 words
- **Full text length**: about 13,700 words of prose in Sections 1–6; about 15,900 words with tables, captions and statements (references excluded)
- **Number of references**: 47
- **Open placeholders**: 48 `[[PENDING …]]` marks. Three are results (H1 against the re-run baseline; the decoupling model; the motion-history swap test); the rest are table cells for the re-run baseline, author statements, the commit hash and the archive DOI. Five figures are present as captions only.

## Field Analysis

| Dimension | Analysis Result |
|-----------|----------------|
| Primary Discipline | End-to-end autonomous driving / robot learning: imitation fine-tuning of a pretrained vision-language-action driving policy, evaluated in closed loop (CARLA, Bench2Drive routes) |
| Secondary Disciplines | Generative action models (flow matching); evaluation methodology and statistics for machine-learning benchmarks; safety validation and metric validity for automated vehicles |
| Research Paradigm | Quantitative research |
| Methodology Type | Comparative experimental study in simulation, quasi-experimental in two respects (one training seed per condition; a bundled three-factor treatment). Paired route-level non-parametric tests with BCa bootstrap intervals, a controller ablation (gate-off run), plan-level analyses of logged trajectories, and pre-specified replication tests on a second evaluation pass. No new method. |
| Target Journal Tier | `criteria_binding_unavailable`. No author-confirmed venue. The authors aim at a Q2 journal in robotics / intelligent vehicles / applied machine learning; this is recorded as an aim, not as a bound target. Field-general observation only: the paper is written as a full-length journal article; its length should be checked against the word or page limit of whichever journal is chosen. No venue criteria are stated or assumed here. |
| Paper Maturity | Revised draft (second review round). Structure is complete, references are formatted and annotated, limitations are extensive. It is not at pre-submission level: three results are pending, one table row and several statements are empty, and figures are not embedded in the text file. |

## Recommended Target Journals (Top 3)
Not issued. With `criteria_binding_unavailable` the field analyst does not name a venue or produce venue criteria. If the authors confirm a journal, the Journal-Fit card should be rebound to it and this section filled from that journal's own author guidelines.

## Reviewer Configuration Cards

### Reviewer Configuration Card #1
**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Associate editor at a robotics / intelligent-vehicles journal who handles learning-based driving submissions and has run closed-loop CARLA evaluation tracks.
**Review Focus**:
  1. Whether a measurement study with no new method (one policy, one simulator, 44 routes, open single-GPU setup) is a sufficient contribution for a Q2 journal.
  2. Whether title, abstract and conclusion ("caution–progress trade-off") match the evidence; whether the Round-1 blocking issues are closed.
  3. Readiness with three results pending as placeholders; length (about 15,000 words) and structure.
**Will particularly care about**: whether the main message survives either outcome of the pending results.
**Possible blind spots**: statistical detail, controller internals.
**Target**: `criteria_binding_unavailable`; field-general, no venue-fit claim.

### Reviewer Configuration Card #2
**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1 (Methodology)
**Identity Description**: Biostatistics-trained ML evaluation methodologist specialising in paired non-parametric inference, multiplicity control, pre-registration and small-N benchmark design.
**Review Focus**:
  1. Pre-specification: was each rule (dated repository addendum) fixed before its data existed; what do the recorded partial looks allow; is "registered" the right word?
  2. Paired route-level tests under strong run-to-run noise (two passes; ICC about 0.6 for standstill, 0.4–0.5 for Driving Score); H2 met in one pass only; many unadjusted post hoc tests.
  3. One training seed, three bundled factors: what claim about "data composition" the design permits.
**Will particularly care about**: whether the Driving Score difference can carry the "progress" side of the trade-off.
**Possible blind spots**: driving-domain plausibility.
**Target**: `criteria_binding_unavailable`; field-general, no venue-fit claim.

### Reviewer Configuration Card #3
**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2 (Domain)
**Identity Description**: Senior researcher in end-to-end driving and imitation learning with CARLA Leaderboard and Bench2Drive publications, familiar with causal confusion, copycat and inertia work and with flow or diffusion planners.
**Review Focus**:
  1. Whether the plan-level finding (H3) is independent of the controller and the speed distribution: threshold equal to the gate's clause, path length dependent on current speed, different states visited, one gate-off pass.
  2. Positioning against inertia / causal-confusion work and data-mixture work for imitation policies; missing history-dropout and creep-rule baselines; reference accuracy.
  3. Whether the sampling hypothesis (Section 3.2) survives the 1,600-sample result.
**Will particularly care about**: whether "restarting, not stopping" can be read from path length at all.
**Possible blind spots**: statistical inference.
**Target**: `criteria_binding_unavailable`; field-general, no venue-fit claim.

### Reviewer Configuration Card #4
**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3 (Perspective)
**Identity Description**: AV safety-assurance and scenario-based validation engineer (SOTIF / ISO 21448) working on metric validity and simulation-to-deployment claims.
**Review Focus**:
  1. What a "trade-off" claim needs: a valid, reliable measure on each axis and more than two operating points. Is the obstacle-heavy model more cautious, or only more hesitant?
  2. Validity of "blocked time" (inferred from the command log) and of the censored standstill fraction; whether "no safety claim" holds throughout.
  3. Whether the open single-GPU setup is reproducible from the released data and code.
**Will particularly care about**: whether "caution" in the title brings back the safety reading removed after Round 1.
**Possible blind spots**: flow-matching theory.
**Target**: `criteria_binding_unavailable`; field-general, no venue-fit claim.

The fifth seat, the Devil's Advocate, is fixed by the skill and has no card.

## Continuity with Round 1
- All four identities are kept word for word, so the yardstick is the same as in Round 1.
- All review-focus items and "will particularly care about" lines are rewritten for the reframed paper (new title, H3 as the main finding, two passes, gate-off run, plan-level analyses).
- Every card now carries the literal token `criteria_binding_unavailable`. The Round-1 decision letter flagged that the peer-reviewer seats did not disclose the binding status.
- Round-1 blocking issues and where they are now tested: comparison against a checkpoint on a different schedule (Journal-Fit focus 2; Methodology focus 3); collision results worded as safety findings (Perspective focus 1 and 2); standstill not separated from the controller's gate (Domain focus 1).
- Dropped from the cards because the manuscript no longer contains them: the two titles in circulation, "at scale", the 4-test Holm family as the main issue, the Section 3.2 mixture-mean argument, crashes per km as a quality claim, the uncommitted analysis script.

## Review Strategy Recommendations
- **Pending results.** Seats should judge the text as it stands and say how each verdict depends on the three pending results. They should not assume an outcome.
- **Pre-specification can only be tested with the repository documents.** The manuscript cites `ANALYSIS_ADDENDUM` sections and commit hashes but does not reproduce them. If Reviewer 1 is to test the claims and not just the authors' description of them, the dispatcher should attach `docs/ANALYSIS_ADDENDUM.md`, `docs/CONFIRMATORY_PREREGISTRATION_FLOODED_6400.md` and `docs/CONFIRMATORY_DEVIATIONS.md`, and state whether the commit dates were checked. Without them the seat should mark the claims as author-reported.
- **One inconsistency between manuscript and addendum, seen while reading (not a review finding).** Addendum Section 17, written on 15 November at 15:49, withdraws the conclusion that neither model plans a stop from motion in more than 0.3 % of steps, because a plan shorter than 1.5 m is near zero by construction once the vehicle moves. The manuscript still states that conclusion in the abstract, Section 1, Section 4.6 and Section 5, and Section 1 adds that the difference "is one of restarting, not of stopping". The Domain card's "will particularly care about" line points at this. The dispatcher may want to tell the authors before the panel runs.
- **Wording to watch.** The abstract and Sections 1 and 4.3 call H1 and H2 "registered", while Section 4.1 says the pre-specification "is not a registration prior to all data". Reviewer 1 owns this point.
- **Tension to expect between seats.** Reviewer 2 may accept the plan-level finding as a model property on the strength of the gate-off run and the at-rest analysis; Reviewer 1 may hold that one seed and three bundled factors do not allow the title's causal verb ("sets"). Reviewer 3 may find that the title's word "caution" implies a safety benefit that the paper explicitly does not claim. The synthesizer should keep these three questions apart: is the plan-level difference real, what caused it, and what it may be called.
- **Complementarity.** Statistics sit with Reviewer 1 only; the other three cards list them as a blind spot. Controller internals and flow-matching theory sit with Reviewer 2 only. Length and structure sit with the Journal-Fit Reviewer only.
- **Instruction-like text.** None found in the manuscript that addresses the reviewers or the panel.
- **Length.** At about 13,700 words of prose with nine results subsections, every seat should say which parts it would move to a supplement, so that the synthesis can give the authors one consistent shortening plan.
