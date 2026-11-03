# Statistical Analysis: Few Edge Cases Are All You Need

**Paper Title:** *Few Edge Cases Are All You Need: Adapting Pre-Trained Vision-Language Models for Safe Autonomous Driving*

## 1. Two-Factor ANOVA (Scale × Curation)

| Source | Sum of Squares (SS) | df | Mean Square (MS) | F-statistic | p-value | Effect Size (η²) | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Factor A: Scale (1.6k vs 6.4k)** | 115.75 | 1 | 115.75 | 0.1227 | 0.7265 | 0.0007 | ns |
| **Factor B: Curation (Golden vs Flooded)** | 266.50 | 1 | 266.50 | 0.2826 | 0.5957 | 0.0016 | ns |
| **Interaction (Scale × Curation)** | 119.25 | 1 | 119.25 | 0.1265 | 0.7226 | 0.0007 | ns |
| **Within / Route Difficulty (Error)** | 162194.18 | 172 | 942.99 | — | — | 0.9969 | 99.7% variance |

> **Interpretation:** Scale has no statistically significant effect ($p = 0.7265$). Data volume beyond 1,600 edge cases does not provide additional score gains.

## 2. Wilcoxon Signed-Rank Test (Paired Route Matchups)

| Comparison | Wins / Losses / Ties | Median Δ | W statistic | p-value | Rank-Biserial r | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Golden-1600 vs Base** | 23/12/9 | +2.99 | 152.0 | 0.007590 | 0.7587 | ** |
| **Golden-6400 vs Base** | 29/9/6 | +9.30 | 163.0 | 0.002618 | 0.7800 | ** |
| **Flooded-1600 vs Base** | 25/13/6 | +2.50 | 243.0 | 0.064449 | 0.6721 | ns |
| **Flooded-6400 vs Base** | 25/13/6 | +2.36 | 253.0 | 0.088361 | 0.6586 | ns |
| **Golden-1600 vs Flooded-1600** | 25/13/6 | +1.02 | 282.0 | 0.199304 | 0.6194 | ns |
| **Golden-6400 vs Flooded-6400** | 18/20/6 | +0.00 | 364.5 | 0.930651 | 0.5081 | ns |
| **Golden-6400 vs Golden-1600** | 17/17/10 | +0.00 | 279.0 | 0.751764 | 0.5311 | ns |
| **Flooded-6400 vs Flooded-1600** | 22/17/5 | +0.17 | 346.5 | 0.543818 | 0.5558 | ns |

> **Interpretation:** Golden fine-tuning produces a statistically significant improvement over the base foundation model ($p < 0.01$). Comparing Golden-6400 vs Golden-1600 yields a dead tie (17 wins vs 17 losses, $p = 0.7518$).

## 3. 95% Bootstrap Confidence Intervals (1,000 Resamples)

### Per-Model Performance Bounds

| Model | Mean Driving Score | 95% Bootstrap CI | CI Width |
| :--- | :---: | :---: | :---: |
| **Base** | 38.82 | [30.97, 47.55] | 16.57 |
| **Flooded-1600** | 45.77 | [36.59, 54.71] | 18.12 |
| **Golden-1600** | 49.88 | [41.51, 58.45] | 16.94 |
| **Flooded-6400** | 49.04 | [39.63, 58.26] | 18.64 |
| **Golden-6400** | 49.85 | [41.89, 59.15] | 17.26 |

### Paired Difference Bounds (Δ = A − B)

| Comparison | Δ Mean | 95% CI Lower | 95% CI Upper | Excludes 0? | Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Golden-1600 − Base** | +11.06 | +3.00 | +18.94 | NO (excl 0) | ✅ Significant |
| **Golden-6400 − Base** | +11.03 | +4.19 | +17.47 | NO (excl 0) | ✅ Significant |
| **Flooded-1600 − Base** | +6.95 | -0.59 | +14.55 | YES (incl 0) | Not Significant |
| **Flooded-6400 − Base** | +10.22 | +1.22 | +19.83 | NO (excl 0) | ✅ Significant |
| **Golden-1600 − Flooded-1600** | +4.11 | -5.31 | +13.49 | YES (incl 0) | Not Significant |
| **Golden-6400 − Flooded-6400** | +0.81 | -8.03 | +9.52 | YES (incl 0) | Not Significant |
| **Golden-6400 − Golden-1600** | -0.02 | -8.64 | +7.60 | YES (incl 0) | Not Significant |

## 4. Multiplicative Metric Decomposition

$$\text{Driving Score} = \text{Route Completion} \times (0.60)^{\text{collisions}}$$

| Model | Overall DS | Route Completion | Total Crashes | Mean Penalty Factor | DS (Excl Outliers) | Clean Routes (Crash-Free) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Base** | 38.82 | 69.1% | 57 | 0.6517 | 42.40 | 17/44 (59.30 DS) |
| **Flooded-1600** | 45.77 | 77.4% | 49 | 0.6685 | 48.98 | 16/44 (68.11 DS) |
| **Golden-1600** | 49.88 | 78.2% | 44 | 0.6762 | 50.99 | 17/44 (73.28 DS) |
| **Flooded-6400** | 49.04 | 77.8% | 57 | 0.6840 | 54.96 | 23/44 (69.74 DS) |
| **Golden-6400** | 49.85 | 82.4% | 46 | 0.6836 | 52.07 | 18/44 (68.55 DS) |

---
*Generated automatically by `/home/aimslab/lead/scripts/evaluation/statistical_analysis.py`*
