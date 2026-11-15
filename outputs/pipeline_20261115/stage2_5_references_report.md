# Academic Integrity Verification Report — Stage 2.5, Phases A and B only

## Verification Mode
Initial Verification (Mode 1, pre-review). Scope of this report: Phase A (references: existence, bibliographic accuracy, ghost citations) and Phase B (citation context). Phases C, D and E are handled by another agent and are not covered here.

- Input: `/home/aimslab/lead/docs/manuscript_revision_draft.txt`, sha256 `8d2140a4a6d7c0b50ec68d25065e42a16ec962516ee6cda47b7d34d6bb0941f3` (manuscript text after the line `%%% END NOTES`).
- Executed: 15 Nov 2026, about 15:45–16:05 local time. Web pages and records can change after this time.
- The manuscript was not edited. Nothing in the project was run.

## Verdict (Phases A and B)
**FAIL, correctable.** No reference is fabricated: all 47 exist and were found on a primary page. There are 0 SERIOUS issues, 4 MEDIUM issues (one wrong page range, one wrong recipe identifier, two citation-context deviations) and several MINOR ones. By the protocol any MEDIUM issue blocks until corrected; the corrections are listed below and are all small.

## Verification Summary

| Category | Total | Passed | Issues |
|---|---|---|---|
| Reference existence (A1) | 47 | 47 | 0 NOT-FOUND, 0 MISMATCH |
| Bibliographic accuracy (A2) | 47 | 42 VERIFIED | 3 VERIFIED-WITH-CORRECTION ([5], [20], [35]); 2 NOT-CONFIRMED-DETAIL ([13] pages, [38] LNCS volume number) |
| Ghost citations (A3) | — | — | 0 orphan references, 0 dangling citations |
| Citation context (B1) | 70 statements (all found, not a sample) | 62 SUPPORTED | 7 PARTLY, 0 NOT-SUPPORTED, 1 COULD-NOT-CHECK (plus two unchecked sub-claims inside B65 and B66) |

A0 (Semantic Scholar batch): `API_UNAVAILABLE` (HTTP 429, no key). All references went through A1 on primary pages instead.

## Issue List (Sorted by Severity)

### SERIOUS (Must Fix)
None.

### MEDIUM (Must Fix)

| ID | # | Category | Location | Issue | Correct information | Source |
|---|---|---|---|---|---|---|
| IL-MEDIUM-1 | 1 | Reference | References [5] | Page range wrong: entry has pp. 8306–8316. | `[5] B. Jiang et al., "VAD: Vectorized Scene Representation for Efficient Autonomous Driving," in Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), 2023, pp. 8340–8350.` | https://openaccess.thecvf.com/content/ICCV2023/html/Jiang_VAD_Vectorized_Scene_Representation_for_Efficient_Autonomous_Driving_ICCV_2023_paper.html (BibTeX on the page: `pages = {8340-8350}`) |
| IL-MEDIUM-2 | 2 | Reference | References [20] | The entry names recipe `alpamayo1_sft` (the Alpamayo 1 recipe). The repository has a separate `alpamayo1_5_sft` recipe, and the project's own training provenance ran from it (`docs/provenance/a100_bundle/hydra_outputs/2026-10-17/10-24-58/.hydra/hydra.yaml`: `cwd: /workspace/alpamayo-recipes/recipes/alpamayo1_5_sft`, `config_name: sft_stage2_nav`). No project file mentions `alpamayo1_sft` except the reference entry. | `[20] NVIDIA Research (NVlabs), "Alpamayo Recipes: Supervised Fine-Tuning (SFT) and Reinforcement-Learning Post-Training Recipes for Alpamayo Models," GitHub repository (`NVlabs/alpamayo-recipes`, recipe `alpamayo1_5_sft`, configuration `sft_stage2_nav`), 2026.` Authors to confirm, and to add the commit hash or access date: the repository was created on 22 Apr 2026 and is still being changed (last push 11 Nov 2026), so "Apr.–May 2026" does not pin a version. | https://github.com/NVlabs/alpamayo-recipes (README recipe table); https://raw.githubusercontent.com/NVlabs/alpamayo-recipes/main/recipes/alpamayo1_5_sft/README.md |
| IL-MEDIUM-3 | 3 | Citation context | §1, paragraph 3 | "adding safety-critical or rare scenarios has been reported to improve collision avoidance and benchmark scores [38, 39]". [39] (CAPS) adds no scenarios: it re-balances an existing dataset by priority sampling over learned clusters. §2 describes it correctly ("reweight training samples by learned clusters"). | Suggested: "adding safety-critical scenarios has been reported to improve collision avoidance [38], and giving rare samples higher sampling priority to raise benchmark scores [39]". | https://arxiv.org/abs/2503.01650 ; https://arxiv.org/abs/2204.13683 |
| IL-MEDIUM-4 | 4 | Citation context | §3.4, "Parameter isolation" | "quantized with pairwise rotation quantization (ParoQuant, W4A8) [14]". ParoQuant [14] is evaluated as weight-only quantization (activations in FP16), with a W4A4 extension in its appendix; W4A8 does not occur in that paper. W4A8 is the FlashDrive [15] deployment: ParoQuant 4-bit weights executed with 8-bit activations through Marlin kernels. | Suggested: "the frozen VLM backbone is quantized to 4-bit weights with pairwise rotation quantization (ParoQuant) [14] and run with 8-bit activations (W4A8), as in the FlashDrive streaming server [15] that serves it". | https://arxiv.org/abs/2511.10645 (text: "keeping the activations in FP16"; appendix "4-bit weight-activation (W4A4)"); https://arxiv.org/abs/2608.12932 §3.4 |

### MINOR (Recommended Fix at Stage 2.5; Must Fix at Stage 4.5)

| ID | # | Category | Location | Issue | Suggestion |
|---|---|---|---|---|---|
| IL-MINOR-1 | 1 | Reference | [35] | The cited venue (PMLR 270) prints the title as "ReMix" and the second author as Chethan Anand Bhateja; "Re-Mix" is the arXiv spelling. | `[35] J. Hejna, C. A. Bhateja, Y. Jiang, K. Pertsch, and D. Sadigh, "ReMix: Optimizing Data Mixtures for Large Scale Imitation Learning," in Proceedings of The 8th Conference on Robot Learning (CoRL), Proceedings of Machine Learning Research, vol. 270, 2025, pp. 145–164.` |
| IL-MINOR-2 | 2 | Reference | [13] | Pages 11698–11709 could not be confirmed on a primary page: the official NeurIPS BibTeX has an empty `pages` field. A secondary index (mlanthology.org) gives 11698–11709. ACM DL and DBLP blocked automated access. | Keep, or drop the pages as was done for other entries. |
| IL-MINOR-3 | 3 | Reference | [38] | LNCS volume number 13698 not confirmed on a primary page (Springer redirects automated access to a login; Crossref carries no volume). Title, authors, book, year, pages 335–352 and DOI are confirmed by the DOI record. | Check the volume number on the Springer page by hand. |
| IL-MINOR-4 | 4 | Reference | [47] | Entry is correct but incomplete; the notes block says volume and pages were not confirmed. | Add `vol. 23, no. 11, pp. 20538–20552, Nov. 2022` (Crossref record of the DOI). |
| IL-MINOR-5 | 5 | Reference | [40], [41], [36], [22], [24], [28], [10] | Correct but pages missing; now confirmed. | [40] pp. 8240–8249; [41] Lecture Notes in Computer Science, pp. 392–409, doi: 10.1007/978-3-031-19842-7_23; [36] pp. 80375–80395; [22] pp. 15222–15232; [24] pp. 11993–12003; [28] pp. 11123–11133; [10] pp. 39775–39785. |
| IL-MINOR-6 | 6 | Reference | [26], [39], [45] | Cited as arXiv preprints; arXiv comments now give a venue. | [26] "Published in RSS 2025"; [39] "Accepted at ICRA 2026"; [45] "A similar version ... accepted at IROS 2025". Optional update. |
| IL-MINOR-7 | 7 | Reference | [14] | Author list differs by source: arXiv v2 and the authors' repository BibTeX (ICLR 2026) list five authors including Z. Zhang, as in the entry; the OpenReview ICLR 2026 record lists four (no Z. Zhang). | Entry kept as VERIFIED on the authors' BibTeX; check the camera-ready PDF once. |
| IL-MINOR-8 | 8 | Reference | [11], [12] | Page ranges are the CVF open-access ones (printed in the CVF PDFs). IEEE Xplore numbers the same papers 11618–11628 and 9328–9337. | No change needed if the CVF version is the one cited. |
| IL-MINOR-9 | 9 | Citation context | §2, "Generative action heads" | "straightness is obtained only with additional procedures such as minibatch optimal-transport coupling [31] or rectified-flow reflow [32]". The sources claim "straighter" flows [31] and "increasingly straight" / "nearly straight" paths [32], not straight ones, and neither states exclusivity ("only"). | "straighter paths are obtained with additional procedures such as ...". |
| IL-MINOR-10 | 10 | Citation context | §3.4, "Inference" | "S = 8 uniform forward Euler steps (..., with velocity caching on steps 3–6)" attributed to the FlashDrive server [15]. The paper states eight steps of which four intermediate ones reuse a cached velocity. It does not name the solver or the step indices. | If the indices and solver come from the server code or configuration, say so. |
| IL-MINOR-11 | 11 | Citation context | §3.4, "Parameter isolation" | "`PerWaypointActionInProjV2` (Fourier features, 20 frequencies up to 100)" [19]. In the released code `num_fourier_feats = 20` is the output dimension of `FourierEncoderV2`, which uses `dim // 2` = 10 log-spaced frequencies (sine and cosine each), maximum 100. | "20 Fourier features (10 log-spaced frequencies up to 100)". The 2,048-dimensional hidden size was not checked. |
| IL-MINOR-12 | 12 | Citation context | §1, paragraph 3 | "The remedies proposed so far act on the model input, the loss or the controller [12, 27, 28]". The three cited works act on the loss ([12] auxiliary speed prediction, [28] sample weights) and the input ([27] history dropout). None is a controller-side remedy. | Move the citation after "the loss", or cite a controller-side rule. |
| IL-MINOR-13 | 13 | Citation context | §2, "Closed-loop evaluation" | "Open-loop displacement metrics hide compounding errors [16, 17, 18]". [16] is about compounding errors of sequential prediction in imitation learning and says nothing about open-loop metrics; [17, 18] show that open-loop nuScenes metrics can be matched from ego status and do not discuss compounding errors. The sentence is a synthesis that no single source states. | Split: "Imitation policies compound their errors in closed loop [16], which open-loop displacement metrics do not measure [17, 18]." |
| IL-MINOR-14 | 14 | Citation context | §2, "Inertia ..." | "open-loop planning metrics on nuScenes [11] can be matched by models that use only ego status [17, 18]". True for L2 error in [17]; the same abstract says "the perception-based methods have an advantage in terms of collision rate". Counted as SUPPORTED. | Optional: "the L2 error on nuScenes". |

### Advisory notes (not issues)

1. **FlowDrive [33] and stationary samples.** The description of [33] is accurate. A reviewer who opens the paper will see that its cluster-based balancing acts first of all on stationary trajectories: "Without any weighting, the samples are heavily skewed toward cluster 0 (stationary trajectories)" (Appendix, Figure 4) and "∼350,000 for a simple stationary scenario" (§3.3). The manuscript's "they report benchmark scores, not standstill" is true, but [33] is closer to the manipulated factor (stationary share) than the text suggests.
2. **[34], scope of the "stuck" report.** Supported, and narrow: one empty route ("Empty Suburban"), four trials, out-of-distribution, in a wrapper (AlpaSim) that teleports the vehicle. The manuscript's wording ("on one of their routes") is adequate.
3. **Time sampling in the flow-matching loss (for the data/claims agent).** §3.1 writes the loss with s ~ U(0,1) and cites [8]. Alpamayo-R1 [2] states that training uses "a shifted beta distribution" for the flow time. Which one the fine-tuning recipe uses should be checked in the recipe code; it was outside my scope.
4. **CARLA version of LEAD.** LEAD [10] reports its evaluation in CARLA 0.9.15. The manuscript's "recorded in CARLA 0.9.16" (§3.3) is a statement about the authors' own collection, not an attribution to [10]; the notes block says it was confirmed from the collection repository.
5. **[2] calls its integration "Euler discretization".** Eq. (5) of [2] is nevertheless the trapezoid formula the manuscript writes, and the released code [19] implements it (`half_dt_term = 0.5 * dt`). "Trapezoidal quadrature [2, 19]" is supported.
6. **Software entries [19], [20]** have descriptive titles composed by the authors, not titles printed on the pages. Acceptable for software; a version or commit would make them checkable.

## Phase A: per-reference table

Class: V = VERIFIED, VC = VERIFIED-WITH-CORRECTION, NCD = NOT-CONFIRMED-DETAIL. "arXiv API" = `export.arxiv.org/api/query?id_list=<id>` (same record as `https://arxiv.org/abs/<id>`).

| # | Short name | Class | Primary source used | Confirmed / finding |
|---|---|---|---|---|
| 1 | π0.5 | V | https://arxiv.org/abs/2504.16054 | Title, first six authors (Physical Intelligence, Black, Brown, Darpinian, Dhabalia, Driess), 22 Apr 2025. |
| 2 | Alpamayo-R1 | V | https://arxiv.org/abs/2511.00088 | Title; authors NVIDIA, Yan Wang, Wenjie Luo, Junjie Bai, Yulong Cao, …; submitted 30 Oct 2025. |
| 3 | Bench2Drive | V | https://proceedings.neurips.cc/paper_files/paper/2024/hash/017761f94a1cd66d01c041aff85492c4-Abstract-Datasets_and_Benchmarks_Track.html | Five authors, vol. 37, pp. 819–844, 2024 (official BibTeX). |
| 4 | UniAD | V | https://openaccess.thecvf.com/content/CVPR2023/html/Hu_Planning-Oriented_Autonomous_Driving_CVPR_2023_paper.html | Y. Hu first author, CVPR 2023, pp. 17853–17862. Place of conference not on the page (not checked). |
| 5 | VAD | **VC** | https://openaccess.thecvf.com/content/ICCV2023/html/Jiang_VAD_Vectorized_Scene_Representation_for_Efficient_Autonomous_Driving_ICCV_2023_paper.html | Pages are **8340–8350**, not 8306–8316. Rest correct. |
| 6 | DriveLM | V | https://doi.org/10.1007/978-3-031-72943-0_15 (Crossref record) | Sima first author, Computer Vision – ECCV 2024, pp. 256–274, online 29 Nov 2024. |
| 7 | LMDrive | V | https://openaccess.thecvf.com/content/CVPR2024/html/Shao_LMDrive_Closed-Loop_End-to-End_Driving_with_Large_Language_Models_CVPR_2024_paper.html | Seven authors incl. G. Song (arXiv lists six), CVPR 2024, pp. 15120–15130. |
| 8 | Flow Matching | V | https://arxiv.org/abs/2210.02747 ; OpenReview search record `hv4gj2OUfY` (venue "ICLR 2023") | Five authors, title, ICLR 2023. The original forum page was behind a challenge. |
| 9 | CARLA | V | https://proceedings.mlr.press/v78/dosovitskiy17a.html | "Proceedings of the 1st Annual Conference on Robot Learning, PMLR 78:1-16, 2017". |
| 10 | LEAD | V | https://arxiv.org/abs/2512.20563 ; https://openaccess.thecvf.com/content/CVPR2026/html/Nguyen_LEAD_Minimizing_Learner-Expert_Asymmetry_in_End-to-End_Driving_CVPR_2026_paper.html | Seven authors, CVPR 2026; pages 39775–39785 available. |
| 11 | nuScenes | V | https://openaccess.thecvf.com/content_CVPR_2020/html/Caesar_nuScenes_A_Multimodal_Dataset_for_Autonomous_Driving_CVPR_2020_paper.html (+ PDF) | Ten authors, CVPR 2020; pages 11621–11631 printed in the CVF PDF (IEEE Xplore: 11618–11628). |
| 12 | Codevilla et al. | V | https://openaccess.thecvf.com/content_ICCV_2019/html/Codevilla_Exploring_the_Limitations_of_Behavior_Cloning_for_Autonomous_Driving_ICCV_2019_paper.html (+ PDF) | Four authors, ICCV 2019; pages 9329–9338 printed in the CVF PDF (IEEE Xplore: 9328–9337). |
| 13 | Causal Confusion | **NCD** (pages) | https://proceedings.neurips.cc/paper_files/paper/2019/hash/947018640bf36a2bb609d3557a285329-Abstract.html | Authors, title, vol. 32, 2019 confirmed. Official BibTeX has `pages = {}`. Secondary index agrees with 11698–11709. |
| 14 | ParoQuant | V (note) | https://arxiv.org/abs/2511.10645 ; https://github.com/z-lab/paroquant (BibTeX) ; OpenReview `1USeVjsKau` ("ICLR 2026 Poster") | Five authors and ICLR 2026 per arXiv and the authors' BibTeX. OpenReview record lists four authors. |
| 15 | FlashDrive | V | https://arxiv.org/abs/2608.12932 | Six authors (Zekai Li, Yihao Liang, Hongfei Zhang, Jian Chen, Yesheng Liang, Zhijian Liu), 13 Aug 2026. |
| 16 | DAgger | V | https://proceedings.mlr.press/v15/ross11a.html | AISTATS 2011, PMLR 15:627-635. |
| 17 | Zhai et al. | V | https://arxiv.org/abs/2305.10430 | Nine authors, title, 2023. |
| 18 | Ego status | V | https://openaccess.thecvf.com/content/CVPR2024/html/Li_Is_Ego_Status_All_You_Need_for_Open-Loop_End-to-End_Autonomous_CVPR_2024_paper.html | Seven authors, CVPR 2024, pp. 14864–14873. |
| 19 | Alpamayo 1.5 | V (software) | https://github.com/NVlabs/alpamayo1.5 ; https://huggingface.co/nvidia/Alpamayo-1.5-10B | Repository created 3 Mar 2026; model card: "Release Date: Hugging Face 03/19/2026". Entry title is descriptive. |
| 20 | Alpamayo recipes | **VC** | https://github.com/NVlabs/alpamayo-recipes | Repository exists (created 22 Apr 2026). Recipe used is `alpamayo1_5_sft`, not `alpamayo1_sft` (IL-MEDIUM-2). |
| 21 | TransFuser | V | https://openaccess.thecvf.com/content/CVPR2021/html/Prakash_Multi-Modal_Fusion_Transformer_for_End-to-End_Autonomous_Driving_CVPR_2021_paper.html | CVPR 2021, pp. 7077–7087. |
| 22 | Roach | V | https://openaccess.thecvf.com/content/ICCV2021/html/Zhang_End-to-End_Urban_Driving_by_Imitating_a_Reinforcement_Learning_Coach_ICCV_2021_paper.html | Five authors, ICCV 2021, arXiv:2108.08265; pages 15222–15232 available. |
| 23 | Hydra-MDP | V | https://arxiv.org/abs/2406.06978 | Zhenxin Li, Kailin Li, … (12 authors), 2024. |
| 24 | SimLingo | V | https://openaccess.thecvf.com/content/CVPR2025/html/Renz_SimLingo_Vision-Only_Closed-Loop_Autonomous_Driving_with_Language-Action_Alignment_CVPR_2025_paper.html | Four authors, CVPR 2025; pages 11993–12003 available. |
| 25 | Copycat agents | V | https://proceedings.neurips.cc/paper_files/paper/2020/hash/1b113258af3968aaf3969ca67e744ff8-Abstract.html | Five authors, vol. 33, pp. 2564–2575. |
| 26 | π0 | V | https://arxiv.org/abs/2410.24164 | K. Black first author, 2024; arXiv comment "Published in RSS 2025". |
| 27 | ChauffeurNet | V | https://www.roboticsproceedings.org/rss15/p31.html ; DOI 10.15607/RSS.2019.XV.031 | Three authors, RSS XV, 2019. |
| 28 | Keyframe | V | https://proceedings.mlr.press/v139/wen21d.html | Five authors, ICML 2021, PMLR 139; pages 11123–11133 available. |
| 29 | Diffusion Policy | V | https://www.roboticsproceedings.org/rss19/p026.html ; https://arxiv.org/abs/2303.04137 | Chi first author, RSS XIX, 2023. |
| 30 | DiffusionDrive | V | https://openaccess.thecvf.com/content/CVPR2025/html/Liao_DiffusionDrive_Truncated_Diffusion_Model_for_End-to-End_Autonomous_Driving_CVPR_2025_paper.html | CVPR 2025, pp. 12037–12047. |
| 31 | Minibatch OT CFM | V | https://arxiv.org/abs/2302.00482 ; OpenReview `CD9Snc73AW` ("Accepted by TMLR", March 2024) | Tong, Fatras, Malkin, … (eight authors), TMLR 2024. |
| 32 | Rectified flow | V | https://arxiv.org/abs/2209.03003 ; OpenReview search record `7RM5cguqAf` ("ICLR 2023") | Three authors, ICLR 2023. |
| 33 | FlowDrive | V | https://arxiv.org/abs/2509.21961 | Four authors, 2025 (arXiv title in lower case). |
| 34 | VLADriveBench | V | https://arxiv.org/abs/2606.12706 | Five authors (Thach Nguyen, Danhua Guo, Tom Lampo, Fei Wu, Burhan Yaman), 10 Jun 2026. |
| 35 | Re-Mix | **VC** (minor) | https://proceedings.mlr.press/v270/hejna25a.html | PMLR 270:145-164, 2025. PMLR title "ReMix"; author "Chethan Anand Bhateja". |
| 36 | Data Quality in IL | V | https://proceedings.neurips.cc/paper_files/paper/2023/hash/fe692980c5d9732cf153ce27947653a7-Abstract-Conference.html | vol. 36, 2023 confirmed; pages 80375–80395 available. |
| 37 | Hidden Biases (Datasets) | V | https://arxiv.org/abs/2412.09602 | Five authors, 2024. |
| 38 | KING | **NCD** (LNCS volume) | https://doi.org/10.1007/978-3-031-19839-7_20 (Crossref record) | Five authors, Computer Vision – ECCV 2022, pp. 335–352, DOI. Volume number 13698 not confirmed. |
| 39 | CAPS | V | https://arxiv.org/abs/2503.01650 | Nine authors, 2025; arXiv comment "Accepted at ... ICRA 2026". |
| 40 | Hidden Biases (Models) | V | https://openaccess.thecvf.com/content/ICCV2023/html/Jaeger_Hidden_Biases_of_End-to-End_Driving_Models_ICCV_2023_paper.html | ICCV 2023; pages 8240–8249 available. |
| 41 | Residual Action Prediction | V | https://arxiv.org/abs/2207.09705 ; Crossref DOI 10.1007/978-3-031-19842-7_23 | Four authors, ECCV 2022; pages 392–409 available. |
| 42 | Trautman et al. | V | https://doi.org/10.1177/0278364914557874 (Crossref record) | IJRR vol. 34, no. 3, pp. 335–356, 2015. |
| 43 | Sadigh et al. | V | https://www.roboticsproceedings.org/rss12/p29.html ; DOI 10.15607/RSS.2016.XII.029 | Four authors, RSS XII (2016). |
| 44 | OpenVLA | V | https://proceedings.mlr.press/v270/kim25c.html | 17 authors as listed (arXiv lists 18), PMLR 270:2679-2713, 2025. |
| 45 | Policy Idling | V | https://arxiv.org/abs/2508.15669 | Ten authors, 2025. |
| 46 | Shortcut Learning | V | https://proceedings.mlr.press/v305/xing25a.html | Six authors, PMLR 305:3239-3266, 2025. |
| 47 | Chance et al. | V | https://doi.org/10.1109/TITS.2022.3177887 (Crossref record) ; https://arxiv.org/abs/2104.06262 | Six authors, IEEE T-ITS; vol. 23, no. 11, pp. 20538–20552, Nov. 2022 available. |

Counts: VERIFIED 42, VERIFIED-WITH-CORRECTION 3, NOT-CONFIRMED-DETAIL 2, NOT-FOUND 0.

### A3. Ghost citations
- Every list entry [1]–[47] is cited at least once in the text. **0 orphan references.**
- Every bracketed citation number in the text has a list entry. **0 dangling citations.** (The pattern `[0,1]` in §3.1 is the interval of the flow time, not a citation.)
- Cited once only: [1], [4]–[7], [9], [11], [16], [21]–[24], [29], [30], [37], [40]–[43], [46], [47].

### Age of references
By year: 2026: 6; 2025: 10; 2024: 8; 2023: 8; 2022: 3; 2021: 3; 2020: 2; 2019: 3; 2017: 1; 2016: 1; 2015: 1; 2011: 1.
Older than ten years at 15 Nov 2026: [16] (2011), [42] (2015) and [43] (June 2016), **3 of 47 = 6.4 %** (2 of 47 = 4.3 % by calendar year 2015 or earlier). 24 of 47 (51 %) are from 2024–2026. 11 are preprints without a venue in the entry, and 2 are software or model pages.

### Self-citation
None detectable. The draft carries no author list (author statements are pending). No reference author matches the Hugging Face dataset namespace in §6 or the repository's git user name. This check has to be repeated when the author list exists.

## Phase B: per-statement table

All statements that attribute a finding, method or property to a cited work were checked (70 rows). Evidence is from the abstract unless "text" is given. arXiv full texts were read from the PDF of the listed id.

| ID | Where | Manuscript statement (short) | Class | Evidence (short) and URL |
|---|---|---|---|---|
| B01 | §1 | π0 [26], π0.5 [1], Alpamayo [2, 19]: action head is a flow-matching [8] expert, few solver steps | SUPPORTED | [26] "novel flow matching architecture built on top of a pre-trained vision-language model" https://arxiv.org/abs/2410.24164 ; [1] text: "action expert can specialize to flow matching-based action" https://arxiv.org/abs/2504.16054 ; [2] text: "an action-expert decoder using flow matching", Euler with δt = 0.1 https://arxiv.org/abs/2511.00088 ; [19] card: "diffusion-based action decoder" https://huggingface.co/nvidia/Alpamayo-1.5-10B |
| B02 | §1 | Codevilla et al. [12] named this the inertia problem | SUPPORTED | text: "we identify a typical failure mode due to a subtle dataset bias: the inertia problem. When the ego vehicle is stopped ... the probability it stays static is indeed overwhelming in the training data" (CVF PDF of [12]) |
| B03 | §1 | it is a form of causal confusion [13] | SUPPORTED | [12] text: "the inertia problem stemming from causal confusion"; [13] "causal misidentification" https://arxiv.org/abs/1905.11979 |
| B04 | §1 | ... and of the copycat behaviour described for policies trained on observation histories [25, 28] | SUPPORTED | [25] "the imitator learns to cheat by predicting the expert's previous action ... 'copycat problem'" https://arxiv.org/abs/2010.14876 ; [28] text: "Codevilla et al. (2019) report this special case of the copycat" https://arxiv.org/abs/2106.06452 |
| B05 | §1 | remedies act on the model input, the loss or the controller [12, 27, 28] | PARTLY | Input ([27]) and loss ([12], [28]) supported; none of the three is a controller-side remedy (IL-MINOR-12). |
| B06 | §1 | robot policies reported to freeze or idle because of what their training data contain [44, 45] | SUPPORTED | see B34, B35 |
| B07 | §1 | data mixtures and data quality: which demonstrations raise task success [35, 36] | SUPPORTED | see B40, B41 |
| B08 | §1 | adding safety-critical or rare scenarios improves collision avoidance and benchmark scores [38, 39] | PARTLY | [38] supported. [39] re-balances, adds nothing: "cluster IDs are then used to re-balance the dataset, ensuring that rare yet valuable samples receive higher priority" https://arxiv.org/abs/2503.01650 (IL-MEDIUM-3) |
| B09 | §1 | rebalancing raises the scores of a flow-matching planner without a language model [33] | SUPPORTED | text: "Applying the same strategy to FlowDrive− yields an average improvement of 4.94%"; inputs are "neighbor history, static objects, lanes/routes" https://arxiv.org/abs/2509.21961 |
| B10 | §1 | Alpamayo 1.5 reported to get stuck in CARLA [34] | SUPPORTED | text: "Alpamayo v1.5 has the tendency to get stuck on the Empty Suburban route ... It fails to complete the route in all 4 trials" https://arxiv.org/abs/2606.12706 |
| B11 | §1 | quantization method [14], streaming server [15], expert [10] are prior work | SUPPORTED | [14] "Pairwise Rotation Quantization (ParoQuant), a PTQ method"; [15] "streaming KV-cache reuse across frames"; [10] "privileged expert demonstrations" |
| B12 | §2 | camera–LiDAR fusion by transformer attention [21] | SUPPORTED | "integrate image and LiDAR representations using attention" https://arxiv.org/abs/2104.09224 |
| B13 | §2 | reinforcement-learning coaches for imitation agents [22] | SUPPORTED | "our expert is also a better coach that provides informative supervision signals for imitation learning agents" https://arxiv.org/abs/2108.08265 |
| B14 | §2 | planning-oriented multi-task networks [4] | SUPPORTED | "incorporates full-stack driving tasks in one network ... all these tasks contribute to planning" https://arxiv.org/abs/2212.10156 |
| B15 | §2 | vectorized scene representations [5] | SUPPORTED | "models the driving scene as a fully vectorized representation" https://arxiv.org/abs/2303.12077 |
| B16 | §2 | multi-teacher trajectory scoring [23] | SUPPORTED | "employing multiple teachers ... multi-head decoder to learn diverse trajectory candidates tailored to various evaluation metrics" https://arxiv.org/abs/2406.06978 |
| B17 | §2 | DriveLM [6]: graph-structured question answering | SUPPORTED | "Graph VQA, where we model graph-structured reasoning through perception, prediction and planning question-answer pairs" https://arxiv.org/abs/2312.14150 |
| B18 | §2 | LMDrive [7]: closed-loop control conditioned on language instructions | SUPPORTED | "language-guided, end-to-end, closed-loop autonomous driving framework" https://arxiv.org/abs/2312.07488 |
| B19 | §2 | SimLingo [24]: vision-only, language–action alignment, Bench2Drive | SUPPORTED | "using only camera ... language-action alignment ... state-of-the-art ... on the Bench2Drive benchmark" https://arxiv.org/abs/2503.09594 |
| B20 | §2 | Alpamayo-R1 [2] and 1.5 [19]: chain-of-causation reasoning with a flow-matching action expert | SUPPORTED | [2] "integrates Chain of Causation reasoning with trajectory planning"; text "diffusion-based action-expert trajectory decoder built on flow matching"; [19] card "chain-of-thought reasoning VLA ... diffusion-based action decoder" |
| B21 | §2 | Diffusion Policy [29]: conditional denoising diffusion over robot actions | SUPPORTED | "representing a robot's visuomotor policy as a conditional denoising diffusion process" https://www.roboticsproceedings.org/rss19/p026.html |
| B22 | §2 | DiffusionDrive [30]: truncated diffusion with anchor trajectories | SUPPORTED | "truncated diffusion policy that incorporates prior multi-mode anchors and truncates the diffusion schedule" https://arxiv.org/abs/2411.15139 |
| B23 | §2 | π0 [26]: flow-matching action expert on a pretrained VLM, continuous action chunks | SUPPORTED | text: "action expert that produces continuous actions via flow matching"; "an action chunking architecture [57] with flow matching" https://arxiv.org/abs/2410.24164 |
| B24 | §2 | Flow matching [8] regresses a velocity field along a probability path | SUPPORTED | "regressing vector fields of fixed conditional probability paths" https://arxiv.org/abs/2210.02747 |
| B25 | §2 | with linear path and independent coupling the marginal paths are not straight in general; straightness only with minibatch OT [31] or reflow [32] | PARTLY | [8] text: only the conditional OT paths "are guaranteed to stay straight". [31] text: "straighter flows"; [32]: "increasingly straight paths", "nearly straight flows". "Straight" and "only" overstate (IL-MINOR-9). https://arxiv.org/abs/2302.00482 ; https://arxiv.org/abs/2209.03003 |
| B26 | §2 | [12] documented the inertia problem and proposed an auxiliary speed-prediction branch so the network must estimate speed from images | SUPPORTED | text: "Speed Prediction Regularization. To cope with the inertia problem ... we jointly train a sensorimotor controller with a network that predicts the ego vehicle's speed ... enforces the perception module to have speed related features". Also in [12]: "It is, however, not a final solution to this problem" (CVF PDF) |
| B27 | §2 | de Haan et al. [13] framed the broader failure as causal confusion | SUPPORTED | title and "causal misidentification" https://arxiv.org/abs/1905.11979 |
| B28 | §2 | Wen et al. [25]: copycat agents; representations that suppress the previous action | SUPPORTED | "adversarial approach to learn a feature representation that removes excess information about the previous expert action nuisance correlate" https://arxiv.org/abs/2010.14876 |
| B29 | §2 | keyframe method [28] upweights frames at expert action changes; evaluated in CARLA | SUPPORTED | "upweighting demonstration keyframes corresponding to expert action changepoints ... on the CARLA photorealistic vision-based urban driving simulator" https://arxiv.org/abs/2106.06452 |
| B30 | §2 | ChauffeurNet [27]: dropout on the past-motion input | SUPPORTED | text §4.2 "Past Motion Dropout ... for 50% of the examples, we keep only the current position" https://arxiv.org/abs/1812.03079 |
| B31 | §2 | open-loop metrics on nuScenes [11] matched by ego-status-only models [17, 18] | SUPPORTED (note) | [17] "without using any perception ... achieves similar end-to-end planning performance ... reducing the average L2 error by about 20%. Meanwhile, the perception-based methods have an advantage in terms of collision rate" https://arxiv.org/abs/2305.10430 ; [18] "tend to rely predominantly on the ego vehicle's status" https://arxiv.org/abs/2312.03031 (IL-MINOR-14) |
| B32 | §2 | all of these remedies act on input, loss or controller | SUPPORTED | summary of B26–B30 plus the uncited controller rules |
| B33 | §2 | "A policy that stops and does not resume is also known outside driving" [44, 45] | SUPPORTED | see B34, B35 |
| B34 | §2 | Kim et al. [44]: all-zero actions in a robot dataset led a VLA policy to predict them and freeze; they removed those actions | SUPPORTED | text, Appendix C: "training a highly expressive VLA model on the original dataset without any data preprocessing led to a policy that frequently predicted all-zero actions and froze during evaluations. Therefore, we simply filtered out the first transition in every demonstration" https://arxiv.org/abs/2406.09246 |
| B35 | §2 | Chen et al. [45]: policy idling often a reflection of the training data | SUPPORTED | "This policy idling is often a reflection of the training data." https://arxiv.org/abs/2508.15669 |
| B36 | §2 | freezing robot problem [42]: planner judges every forward path unsafe and stops | SUPPORTED | "the planner decides that all forward paths are unsafe, and the robot freezes in place (or performs unnecessary maneuvers)" https://doi.org/10.1177/0278364914557874 |
| B37 | §2 | Sadigh et al. [43]: planners that stay out of the way of predicted trajectories tend toward defensive behaviour | SUPPORTED | "make predictions about other drivers' future trajectories, and plan to stay out of their way. This tends to result in defensive and opaque behaviors." https://www.roboticsproceedings.org/rss12/p29.html |
| B38 | §2 | Jaeger et al. [40]: shared bias, longitudinal averaging of multimodal waypoint predictions, slowing down | SUPPORTED | "two biases that recur in nearly all state-of-the-art methods ... (2) longitudinal averaging of multimodal waypoint predictions for slowing down" https://arxiv.org/abs/2306.07957 |
| B39 | §2 | Chuang et al. [41]: copycat problem, residual action target | SUPPORTED | title "... via Residual Action Prediction"; "it successfully alleviates the copycat problem" https://arxiv.org/abs/2207.09705 |
| B40 | §2 | Belkhale et al. [36]: action divergence and transition diversity | SUPPORTED | "two fundamental properties ... i) action divergence ... ii) transition diversity" https://arxiv.org/abs/2306.02437 |
| B41 | §2 | Hejna et al. [35]: mixture weights by distributionally robust optimisation; beat uniform and hand-chosen | SUPPORTED | "we use distributionally robust optimization (DRO) ... outperform uniform weights by 38% on average and outperform human-selected weights by 32%" https://arxiv.org/abs/2408.14037 |
| B42 | §2 | Xing et al. [46]: shortcut learning from limited diversity within sub-datasets and gaps between them | SUPPORTED | "(1) limited diversity within individual sub-datasets, and (2) significant distributional disparities across sub-datasets" https://arxiv.org/abs/2508.06426 |
| B43 | §2 | Hanselmann et al. [38]: generated safety-critical scenarios; training on them improves collision avoidance | SUPPORTED | "After fine-tuning on this new data, we show that the policy becomes better at avoiding collisions." https://arxiv.org/abs/2204.13683 |
| B44 | §2 | Mirkhani et al. [39]: reweight samples by learned clusters; closed-loop gains on Bench2Drive | SUPPORTED | "results on Bench2Drive scenarios ... substantial improvements in both driving score and success rate" https://arxiv.org/abs/2503.01650 |
| B45 | §2 | Zimmerlin et al. [37]: expert style matters; against weighting frames by class frequency | SUPPORTED | "(1) Expert style significantly affects downstream policy performance. (2) ... the frames should not be weighted on the basis of simplistic criteria such as class frequencies." https://arxiv.org/abs/2412.09602 |
| B46 | §2 | Wang et al. [33]: compare sampling strategies for a flow-matching planner on nuPlan and interPlan; reweighting by trajectory pattern effective | SUPPORTED | "we compare balancing strategies for sampling training data and find reweighting by trajectory pattern an effective approach ... On nuPlan and the interaction-focused interPlan benchmarks" https://arxiv.org/abs/2509.21961 |
| B47 | §2 | [33]: no vision-language model; benchmark scores, not standstill | SUPPORTED (advisory 1) | text: vectorised scene inputs; "Closed-loop scores on nuPlan"; no standstill measure. Stationary samples are the dominant cluster that the balancing reduces. |
| B48 | §2 | Nguyen et al. [34]: off-the-shelf VLA models incl. Alpamayo 1.5, CARLA 0.9.15, model-predictive wrapper instead of PID, stuck on one route | SUPPORTED | text: "We download the weights of these models from their public repositories"; "All experiments are conducted in CARLA 0.9.15. Alpamayo uses ... AlpaSim, a simulator wrapper that computes the next position and velocity via a Model Predictive Controller (MPC) and teleports the vehicle accordingly. The remaining models use the Bench2Drive PID controller" https://arxiv.org/abs/2606.12706 |
| B49 | §2 | open-loop displacement metrics hide compounding errors [16, 17, 18] | PARTLY | [16]: "future observations depend on previous predictions (actions) ... leads to poor performance" (compounding, no statement on metrics) https://proceedings.mlr.press/v15/ross11a.html ; [17, 18]: open-loop nuScenes evaluation questioned, no statement on compounding (IL-MINOR-13) |
| B50 | §2 | CARLA [9]; repeated executions not identical; Chance et al. [47] study the variance and when it becomes negligible | SUPPORTED | "game engines are seldom deterministic ... A case study using CARLA ... determine an operational domain where ... variance between repeated executions becomes negligible" https://arxiv.org/abs/2104.06262 |
| B51 | §2 | Bench2Drive [3]: 220 short routes, 44 scenario types, five abilities | SUPPORTED | "44 interactive scenarios ... which sums up to 220 routes"; text: "220 short routes"; "5 advanced skills for urban driving: Merging, Overtaking, Give Way, Traffic Sign, Emergency Brake" https://arxiv.org/abs/2406.03877 |
| B52 | §2 | LEAD [10] reduces learner–expert asymmetries in CARLA expert data | SUPPORTED | "misalignment between privileged expert demonstrations and sensor-based student observations ... careful modifications to narrow the gaps between expert and student" https://arxiv.org/abs/2512.20563 (the interventions concern both expert and student) |
| B53 | §3.1 | four cameras (cross-left, front-wide, cross-right 120°; front-tele 30°), 4-frame window [19] | SUPPORTED | card: "4 cameras by default: front-wide, front-tele, cross-left, cross-right ... 0.4 second history window at 10Hz (4 frames per camera)"; fields of view from the dataset card ("Front wide 120 fov", "Front tele 30 fov", "Cross left 120 fov", "Cross right 120 fov") https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles |
| B54 | §3.1 | ego history: 16 poses at 0.1 s [2, 19] | SUPPORTED | card: "egomotion history (16 waypoints at 10Hz)" |
| B55 | §3.1 | ... tokenized into 48 history tokens (three per pose) [2, 19] | COULD-NOT-CHECK | Not on the model card or README; token count per history trajectory not resolved from the source files read. |
| B56 | §3.1 | navigation instruction [19] | SUPPORTED | card: "introduces support for navigation guidance"; "Text inputs include user commands and navigation guidance" |
| B57 | §3.1 | 64 waypoints at 0.1 s, 6.4 s horizon [2, 19] | SUPPORTED | card: "6.4-second future trajectory (64 waypoints at 10Hz)"; [2] text: "64 waypoints" |
| B58 | §3.1 | about 10B; 8B VLM (Cosmos-Reason2-8B, Qwen3-VL architecture); 2.28B action expert; unicycle acceleration–curvature [2, 19] | SUPPORTED | card: "Backbone: 8.2B parameters; Action Expert: 2.3B parameters"; "acceleration and curvature following a unicycle model"; Cosmos-Reason2 card: "Network Architecture: Qwen3-VL-8B-Instruct" https://huggingface.co/nvidia/Cosmos-Reason2-8B |
| B59 | §3.1 | unicycle integration with trapezoidal quadrature, v0 estimated from history [2, 19] | SUPPORTED | [19] code `unicycle_accel_curvature.py`: `half_dt_term = 0.5 * dt`, `v0 = t0_states["v"]` from `estimate_t0_states(traj_history_xyz, ...)` https://github.com/NVlabs/alpamayo1.5 ; [2] Eq. (5), same formula, named "Euler discretization" |
| B60 | §3.1 | CFM with linear path and independent coupling [8] | SUPPORTED (advisory 3) | [2] text: "sample a_t = t a + (1 − t) ε with ε ∼ N(0, I) ... u(a_t|a) = a − ε"; [8]: OT displacement path |
| B61 | §3.2 | integrating the marginal field transports noise to the training conditional, in the limit of exact fit and integration [8] | SUPPORTED | [8] text, Theorem 1: "The marginal vector field (equation 8) generates the marginal probability path (equation 6)." |
| B62 | §3.3 | demonstrations from the LEAD [10] privileged expert | SUPPORTED (advisory 4) | "privileged expert demonstrations" |
| B63 | §3.4 | VLM frozen (`cotrain_vlm = false`, gradients stopped at the trajectory token) [2, 20] | SUPPORTED | [20] `configs/models/ar1_5_expert.yaml`: `cotrain_vlm: false`; README: "Stage 2: Freeze the Stage-1 VLM and train the action expert"; [2] text: "we apply a stop-gradient to the KV-cache produced by the VLM" |
| B64 | §3.4 | quantized with ParoQuant, W4A8 [14]; served by FlashDrive [15]; action expert in bfloat16 | PARTLY | [15] text: "We apply ParoQuant (Liang et al., 2026) to quantize the VLM backbone's weights to 4-bit and execute inference with 8-bit activations using the W4A8 variant of the Marlin kernels; the action expert ... remains in BF16." W4A8 is not from [14] (IL-MEDIUM-4). |
| B65 | §3.4 | `PerWaypointActionInProjV2` (Fourier features, 20 frequencies up to 100), 2,048-dimensional hidden space [19] | PARTLY | code `action_in_proj.py`: `max_freq: float = 100.0, num_fourier_feats: int = 20`; `half = dim // 2; freqs = torch.logspace(0, math.log10(max_freq), steps=half)`, i.e. 10 frequencies (IL-MINOR-11). Hidden size not checked. |
| B66 | §3.4 | Stage-2 recipe [20]: AdamW ..., gradient clipping 1.0, bfloat16, cosine schedule with minimum learning rate from 1e-4 to 1e-6, no EMA | SUPPORTED (core) | [20] `sft_base.yaml`: `learning_rate: 1e-4`, `lr_scheduler_type: cosine_warmup_with_min_lr`, `min_lr: 1e-6`, `bf16: True`, `warmup_steps: 100`. AdamW betas, epsilon, weight decay, clipping and absence of EMA are not set in the public configuration (trainer defaults) and were not checked. |
| B67 | §3.4 | FlashDrive server [15]: sliding-window key-value cache; 8 uniform forward Euler steps, velocity caching on steps 3–6 | PARTLY | [15]: "streaming KV-cache reuse across frames"; "reusing four of eight diffusion steps"; "we replace four intermediate evaluations with the cached velocity from the preceding step". Solver name and step indices are not in the paper (IL-MINOR-10). |
| B68 | §3.4 | with independent coupling the paths need not be straight [31, 32] | SUPPORTED | as B25 |
| B69 | §5 | the behaviour described as the inertia problem [12]; "the pattern the inertia account predicts" (restarting, not stopping) | SUPPORTED | [12] text: "a spurious correlation between low speed and no acceleration, inducing excessive stopping and difficult restarting" |
| B70 | §5 | model-side remedies such as history dropout [27] or speed prediction [12] | SUPPORTED | as B26, B30 |

Counts over the 70 rows: **62 SUPPORTED, 7 PARTLY (B05, B08, B25, B49, B64, B65, B67), 0 NOT-SUPPORTED, 1 COULD-NOT-CHECK (B55)**. Rows B06, B07 and B33 are summary sentences whose content is checked in later rows. Two sub-claims inside otherwise checked rows were not checked: the 2,048-dimensional hidden size (B65) and the optimizer details (B66).

### B2. Citation format
Numeric IEEE-style citations are used consistently. Small inconsistencies in the list: some conference entries carry an arXiv id and no pages ([22], [24], [28], [29], [10], [14]) while others carry pages and no arXiv id; author lists are sometimes complete and sometimes "et al." after one or two names ([4], [5], [6], [23], [26], [29], [30], [31]). Conference names are abbreviated in [8], [9], [14], [32] and written out elsewhere.

## What could not be checked, and why
- A0 Semantic Scholar batch: HTTP 429 without an API key.
- Page range of [13]: the official NeurIPS record has none; ACM Digital Library and DBLP refused automated access (403 / bot check).
- LNCS volume number of [38]: Springer Link redirects automated access to a login; Crossref has no volume for the chapter or the book.
- OpenReview forum pages of [8], [32], [31]: challenge page. Venue taken from OpenReview's search records and the arXiv record instead.
- "48 history tokens (three per pose)" and the 2,048-dimensional hidden size (§3.1, §3.4): code-level details not on the model card.
- AdamW betas, epsilon, weight decay, clipping, EMA (§3.4): not in the public recipe configuration.
- Conference location in [4] (Vancouver): not on the CVF page.
- Self-citation: no author list in the draft.

## Tool Limitation Disclaimer
This report covers reference and citation-context checks only. It uses publisher, proceedings, arXiv, Crossref, OpenReview, GitHub and Hugging Face pages as fetched on 15 Nov 2026 with automated requests. Citation contexts were checked against abstracts and, where named, the paper text; a statement classed SUPPORTED is supported by the passage quoted, which is not a review of the cited paper as a whole. Originality (Phase D) and data or claim verification (Phases C, E) are not part of this report.

## Verification Audit Trail (method)
1. arXiv API, two batch queries by id (42 ids): title, authors, date, comment and abstract for every entry except [16], [19], [20], [42] and [43], which have no arXiv record in the list or were checked elsewhere.
2. CVF open access pages, BibTeX block on each page: [4], [5], [7], [10], [11], [12], [18], [21], [22], [24], [30], [40]. Printed page numbers read from the CVF PDFs of [11] and [12].
3. PMLR pages, citation meta tags: [9], [16], [28], [35], [44], [46]; first page of the PMLR PDF of [35] for the title.
4. NeurIPS proceedings index pages for 2019, 2020, 2023, 2024, then the official BibTeX file of each paper: [3], [13], [25], [36].
5. Crossref REST API by DOI: [6], [27], [29], [38], [42], [43], [47]; by bibliographic query: [41], [12] (IEEE record), [11] (IEEE record).
6. Robotics: Science and Systems proceedings pages: [27], [29], [43].
7. OpenReview search API: [8], [14], [31], [32]. Authors' repository README for [14].
8. GitHub API and raw files: [19] (README, `src/alpamayo1_5/models/action_in_proj.py`, `src/alpamayo1_5/action_space/unicycle_accel_curvature.py`), [20] (README, `recipes/alpamayo1_sft/README.md`, `recipes/alpamayo1_5_sft/README.md`, `configs/sft_base.yaml`, `configs/sft_stage2_nav.yaml`, `configs/models/ar1_5_expert.yaml`). Hugging Face model card of [19]; Cosmos-Reason2-8B and PhysicalAI-Autonomous-Vehicles cards.
9. Full texts (arXiv PDFs converted to text) searched for the passages quoted in Phase B: [1], [2], [3], [8], [10], [12] (CVF PDF), [14], [15], [26], [27], [28], [31], [33], [34], [44].
10. One web search for the page range of [13] (query: title, authors, "NeurIPS 2019", page numbers); top results: papers.nips.cc record, mlanthology.org entry.
11. Ghost citations: bracketed numbers extracted from the manuscript body by script and compared with the 47 list numbers.
12. Read-only look-up in the project for IL-MEDIUM-2: `grep` for the two recipe names under `/home/aimslab/lead` (hits only in `docs/provenance/a100_bundle/hydra_outputs/...` and restored session notes for `alpamayo1_5_sft`; none for `alpamayo1_sft` outside the reference entry).

Only public bibliographic details (titles, cited authors, arXiv ids, DOIs, public repository names) were sent to outside services.
