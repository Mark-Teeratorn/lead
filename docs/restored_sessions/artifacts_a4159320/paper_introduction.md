# Few Edge Cases Are All You Need: Adapting Pre-Trained Vision-Language Models for Safe Autonomous Driving

## 1. Introduction

End-to-end autonomous driving powered by Vision-Language Models (VLMs) has emerged as a compelling paradigm, where a single model maps raw sensory inputs directly to driving actions through learned visual reasoning [1, 2]. Pre-trained VLMs such as Alpamayo leverage billions of image-text pairs during pre-training, acquiring rich perceptual representations and commonsense reasoning about the physical world — including an implicit understanding of roads, vehicles, pedestrians, and traffic dynamics. This naturally raises a question central to their deployment in safety-critical settings: **does adapting these models to handle dangerous driving scenarios require large-scale, hazard-heavy fine-tuning datasets, or can a small number of well-chosen edge cases suffice?**

The prevailing approach in the autonomous driving community follows a *scale-first* philosophy: collect more data, particularly from hazardous scenarios, and expose the model to as many dangerous situations as possible during training [3, 4]. This hazard-flooding strategy is intuitive — if the model sees more crashes, near-misses, and obstructed intersections, it should learn to handle them better. However, this assumption overlooks a critical property of pre-trained VLMs: they already encode extensive world knowledge. Unlike models trained from scratch, a pre-trained VLM does not need to learn what a pedestrian looks like or how vehicles behave at intersections — it needs only to be *reminded* how to act safely in those contexts. Flooding such a model with hazard-heavy data risks distorting its well-calibrated representations rather than refining them.

We test this hypothesis through a controlled **2×2 factorial experiment** on the Bench2Drive benchmark [5], evaluating four fine-tuned variants of the Alpamayo VLM across all 44 canonical closed-loop driving routes in CARLA 0.9.15. The two experimental factors are: (i) **curation strategy** — *golden-ratio* curation, which preserves a balanced distribution across scenario categories, versus *hazard-flooded* curation, which maximizes the proportion of dangerous scenarios; and (ii) **data scale** — 1,600 versus 6,400 fine-tuning samples. All four models share the same pre-trained backbone, training pipeline, and evaluation controller, isolating the effect of data composition alone.

The results strongly support our hypothesis and can be summarized in three key findings:

**Finding 1: A few curated edge cases unlock significant safety gains.** Fine-tuning Alpamayo with only 1,600 golden-ratio curated samples improves the Driving Score from 38.45 to 49.88 — a 29.7% gain that is statistically significant under both parametric and non-parametric tests (paired t-test p = 0.017; Wilcoxon signed-rank p = 0.009). This improvement is accompanied by a 23.2% reduction in total collisions (56 → 44) and a 9.3 percentage-point increase in route completion.

**Finding 2: More data does not help.** Scaling golden-ratio curation from 1,600 to 6,400 samples yields virtually no improvement: Driving Scores of 49.88 versus 49.85 (paired t-test p = 0.995). The pre-trained model's capacity for safety adaptation saturates at approximately 1,600 well-curated examples, suggesting that the model's pre-existing knowledge requires only a small nudge — not a large push — to generalize to unseen hazard scenarios.

**Finding 3: Hazard flooding fails — and can backfire.** In contrast to golden-ratio curation, hazard-flooded fine-tuning fails to achieve statistically significant improvement over the base model at either data scale (p = 0.067 at 1,600; p = 0.137 at 6,400). More troublingly, the Flooded-6400 model produces 57 total collisions — exceeding even the un-fine-tuned base model's 56 — while Golden-6400 reduces collisions to 46 (a 19.3% reduction versus flooding at equal scale). Indiscriminate emphasis on dangerous scenarios appears to distort the model's driving distribution rather than improve it.

Together, these findings suggest that the conventional scale-first approach to safety data is misaligned with the properties of pre-trained VLMs. A large foundation model does not need to be taught about danger from scratch — it needs a carefully curated *reminder*. The golden-ratio strategy, by maintaining distributional balance, provides exactly this: sufficient exposure to edge cases without overwhelming the model's pre-trained priors.

Our contributions are:

1. **We demonstrate that pre-trained VLMs generalize to unseen safety-critical scenarios with minimal fine-tuning** — as few as 1,600 curated edge cases achieve statistically significant improvement (p < 0.01) across 44 diverse Bench2Drive routes, with no further gain from 4× more data.

2. **We present the first 2×2 factorial analysis of data curation and scale for VLM safety adaptation**, employing paired t-tests, Wilcoxon signed-rank tests, two-way ANOVA, and Cohen's d effect size reporting across all 44 matched routes.

3. **We expose the failure mode of hazard flooding for pre-trained VLMs**, providing statistical evidence that this widely-assumed strategy not only fails to reach significance but can actively increase collision rates.

The remainder of this paper is organized as follows. Section 2 reviews related work on VLMs for autonomous driving and data curation strategies. Section 3 describes the experimental setup, including the Alpamayo architecture, golden-ratio and hazard-flooded curation pipelines, and the Bench2Drive evaluation protocol. Section 4 presents the ablation results and statistical analysis. Section 5 discusses implications and limitations, and Section 6 concludes.
