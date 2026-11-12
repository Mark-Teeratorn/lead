---
license: mit
pretty_name: LEAD Alpamayo PAI matrix (Flooded groups, balanced lateral, N=6400)
tags:
- autonomous-driving
- carla
- alpamayo
- physical-ai-av
- trajectory-prediction
- navigation
- dataset-curation
size_categories:
- 1K<n<10K
---

# lead-alpamayo-pai_matrix_floodedgroups_balanced_6400

**Decoupling cell (optional)** — the Flooded group mix with the Golden manoeuvre mix and 2 % standing frames. **N = 6,400 training samples**, 1,567 validation samples.

> **Optional.** This cell exists to break a confound in the 2x2, not to complete it. The two regimes move the group mix and the lateral balance together, so the 2x2 alone cannot attribute an effect to hazard flooding specifically. Against `..._flooded_6400` this cell holds the group mix fixed and varies the lateral balance; against `..._golden_6400` it holds the lateral balance fixed and varies the group mix. Whether to train it is the data user's call, and the other four cells do not depend on it.

> **Honest limit:** it separates group mix from the *lateral + stationary* bundle, **not** lateral from stationary. Splitting those two needs a sixth cell.

## What this is

One cell of a 2x2 factorial design — dataset scale x curation regime — over the LEAD CARLA expert, in NVIDIA PhysicalAI-AV (PAI) layout, read unchanged by `alpamayo-recipes`' `PAIDatasetWithNav`.

It is a **draw**, not a conversion: every sample comes from `lead_multirig_pai_v4`'s verified training pool (34,132 samples at a 0.4 s stride).

**This dataset is self-contained.** It carries its own media for all **1,531 clips** it references — the camera videos and egomotion were repacked from the source's 29 chunk archives to hold *only* these clips, and `clip_index.parquet`, `metadata/*` and the clip id lists were filtered to match. Nothing outside this cell is shipped, so a model trained on it cannot silently see a superset. Nothing needs downloading alongside it.

Provenance: drawn from **`lead_multirig_pai_v4`** (`earth37815/lead-alpamayo-pai_large_v4`), whose media these clips are and which was verified against raw LEAD at 0.00 cm. The repack copies stored zip entries raw, so the videos are byte-identical to that dataset's.

## Composition, realised against target

| | target | realised |
|---|---|---|
| groups A–F (%) | 35 / 14 / 22 / 10 / 9 / 10 | 35.0 / 14.0 / 22.0 / 10.0 / 9.0 / 10.0 |
| Straight / Swerve Left / Swerve Right / Turn Left / Turn Right (%) | 50 / 13 / 13 / 12 / 12 | 50.0 / 13.0 / 13.0 / 12.0 / 12.0 |
| stationary (%) | 2 | 2.00 |
| brake (%) | *observed* | 35.1 |
| hazard (%) | *observed* | 24.2 |

`brake` and `hazard` are **observed outcomes of the draw, never targets** — forcing them would make them uninterpretable as behaviour.

### Allocation (group x manoeuvre)

| | Straight | Swerve Left | Swerve Right | Turn Left | Turn Right | total |
|---|---:|---:|---:|---:|---:|---:|
| A | 868 | 532 | 436 | 92 | 312 | **2240** |
| B | 360 | 4 | 0 | 324 | 208 | **896** |
| C | 828 | 252 | 196 | 0 | 132 | **1408** |
| D | 364 | 8 | 164 | 88 | 16 | **640** |
| E | 416 | 0 | 8 | 96 | 56 | **576** |
| F | 364 | 36 | 28 | 168 | 44 | **640** |
| **total** | **3200** | **832** | **832** | **768** | **768** | **6400** |

`B / Swerve Right` and `C / Turn Left` are **structural zeros**: a junction right turn is not a swerve and a hazard bypass is not a junction left turn. They are empty by construction, not by sampling.

The allocation is the **minimum-divergence** point — an IPF/RAS fit of the pool's own group x manoeuvre availability onto the required marginals, then integerised to the nearest feasible point. The marginals leave a large feasible set and most of it is scientifically wrong: a plain LP returns one regime with no straight driving in a group where the other regime has nothing else, which would let "regime" silently rewrite each group's internal composition. The stationary target is applied the same way, as a within-bucket preference, so it moves no marginal.

## Reproducing it

```bash
python scripts/build_curation_matrix.py --stage build \
    --pai-dir <v4> --out-root <root> --seed 0 \
    --gate <lead2hipad>/eval/gate_validation_lead.json
```

Deterministic: sha1 order of (seed, clip_id, t0_relative); no RNG. A rebuild is byte-identical; a different `--seed` gives a different draw.

## Validation split

All cells share **one** validation set of 1,567 samples, so a difference in val can never confound a comparison between cells. It is v4's curated val (1,720) minus the 153 samples whose route is flagged by the (c') union against the Bench2Drive eval routes. **Residual overlap: 0.**

## Eval-route overlap in training — read this before scoring on Bench2Drive

LEAD's PAI datasets are **exempt** from the eval-overlap filter that the HiP-AD pools apply, and that exemption is inherited here for the **training** split. Routes that overlap a Bench2Drive eval route stay eligible.

- **469 of 6,400 training samples (7.33 %)** sit on a route that overlaps one of the 220 Bench2Drive eval routes.
- **83 (1.3 %)** sit on a route overlapping the 44-route main-test subset.
- Counted against `lead2hipad/eval/gate_validation_lead.json`. These are **lower bounds**: 39 log names resolve to no route XML stem and are counted as clean.

A user scoring closed-loop on Bench2Drive should check their own eval list against that gate file, and report headline numbers both over all routes and over the non-overlapping subset.

## Caveats

- **"Flooded" does not mean uncurated.** All cells are curated draws from one pool. The source datasets differ in curation, not in collection — they are the same 1,840 clips over the same 646 routes — so nothing here was ever over-*collected*.
- The regimes differ on **three things at once** (group mix, lateral balance, stationary share). An effect cannot be attributed to any one of them from the 2x2 alone; that is what the optional decoupling cell is for.
- The two factors are **naturally coupled in this data**: groups A+C hold 88 % of all SWERVE_LEFT but only 58 % of SWERVE_RIGHT, an intrinsic 5.15:1 against 3.42:1 pool-wide, so raising the hazard share pushes lateral balance left unless deliberately countered.
- Trajectories and media are the source dataset's and were verified there against raw LEAD at 0.00 cm. This cell's own check covers the loader, shapes, camera indices, nav text, manoeuvre direction and the clip timeline contract.
