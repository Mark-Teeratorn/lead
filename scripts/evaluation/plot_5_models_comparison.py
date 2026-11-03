#!/usr/bin/env python3
"""
Publication-Quality Plot for 5-Model Benchmark Comparison:
Baseline vs. Flooded-1600 vs. Golden-1600 vs. Flooded-6400 vs. Golden-6400.
"""

import matplotlib.pyplot as plt
import numpy as np

# Set modern style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)

# Colors
color_base = '#4B5563'      # Slate Gray
color_f1600 = '#F87171'     # Light Coral
color_g1600 = '#10B981'     # Emerald Green (Star)
color_f6400 = '#DC2626'     # Dark Red
color_g6400 = '#047857'     # Dark Forest Green

models = ['Base\n(Pre-trained)', 'Flooded\n1,600', 'Golden\n1,600 (Best)', 'Flooded\n6,400', 'Golden\n6,400']
bar_colors = [color_base, color_f1600, color_g1600, color_f6400, color_g6400]

# Data
ds_means = [38.82, 45.77, 49.88, 49.04, 49.85]
ds_ci_lo = [30.97, 36.59, 41.51, 39.63, 41.89]
ds_ci_hi = [47.55, 54.71, 58.45, 58.26, 59.15]
yerr = [
    [m - lo for m, lo in zip(ds_means, ds_ci_lo)],
    [hi - m for m, hi in zip(ds_means, ds_ci_hi)]
]

rc_means = [69.07, 77.44, 78.16, 77.76, 82.38]
crashes = [57, 49, 44, 57, 46]

# ==========================================
# Panel 1: Driving Score with 95% Bootstrap CI
# ==========================================
bars1 = ax1.bar(models, ds_means, yerr=yerr, capsize=6, color=bar_colors, edgecolor='#1F2937', linewidth=1.2, alpha=0.9, width=0.6)
ax1.set_title('A. Driving Score (DS) & 95% Bootstrap CI', fontsize=13, fontweight='bold', pad=12)
ax1.set_ylabel('Mean Driving Score (0 - 100)', fontsize=11, fontweight='semibold')
ax1.set_ylim(0, 72)

# Add values cleanly: mean inside the bar and CI above the error bar
for bar, m, lo, hi in zip(bars1, ds_means, ds_ci_lo, ds_ci_hi):
    # Print mean value inside the bar
    ax1.text(bar.get_x() + bar.get_width()/2., m - 6.0, f'{m:.1f}', ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    # Print CI high value above error bar
    ax1.text(bar.get_x() + bar.get_width()/2., hi + 1.2, f'[{lo:.0f}, {hi:.0f}]', ha='center', va='bottom', fontsize=9, fontweight='semibold', color='#374151')

# Annotate baseline vs golden 1600
ax1.annotate(
    '+11.06\n(p = 0.0076**)',
    xy=(2, 58.5), xytext=(0.7, 63.5),
    arrowprops=dict(facecolor='#059669', shrink=0.08, width=1.5, headwidth=6),
    fontsize=9.5, fontweight='bold', color='#059669', ha='center',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECFDF5', edgecolor='#10B981', alpha=0.9)
)
ax1.grid(axis='y', linestyle='--', alpha=0.6)

# ==========================================
# Panel 2: Total Collisions (Safety Metric)
# ==========================================
bars2 = ax2.bar(models, crashes, color=bar_colors, edgecolor='#1F2937', linewidth=1.2, alpha=0.9, width=0.6)
ax2.set_title('B. Total Collisions Across 44 Routes (Lower = Safer)', fontsize=13, fontweight='bold', pad=12)
ax2.set_ylabel('Total Collisions (Crashes)', fontsize=11, fontweight='semibold')
ax2.set_ylim(0, 70)

for bar, c in zip(bars2, crashes):
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., y + 1.2, f'{c}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Highlight lowest crash count
ax2.text(2, 44 - 10, 'Lowest\nCrashes (44)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#047857',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#D1FAE5', edgecolor='#059669', alpha=0.9))

# Flooded 6400 note
ax2.text(3, 57 - 10, 'Same as Base\n(57 Crashes)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#991B1B',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEE2E2', edgecolor='#DC2626', alpha=0.9))
ax2.grid(axis='y', linestyle='--', alpha=0.6)

# ==========================================
# Panel 3: 2x2 Factorial Interaction (Scale x Curation)
# ==========================================
scales = [1600, 6400]
golden_scores = [49.88, 49.85]
flooded_scores = [45.77, 49.04]

ax3.plot(scales, golden_scores, marker='o', markersize=9, linewidth=2.5, color='#059669', label='Golden Curated')
ax3.plot(scales, flooded_scores, marker='s', markersize=9, linewidth=2.5, color='#DC2626', linestyle='--', label='Hazard Flooded')

# Base reference line
ax3.axhline(38.82, color='#4B5563', linestyle=':', linewidth=2, label='Baseline (38.82)')

ax3.set_title('C. Scale vs. Curation Interaction (ANOVA)', fontsize=13, fontweight='bold', pad=12)
ax3.set_xlabel('Dataset Sample Budget', fontsize=11, fontweight='semibold')
ax3.set_ylabel('Mean Driving Score', fontsize=11, fontweight='semibold')
ax3.set_xticks(scales)
ax3.set_xticklabels(['1,600 samples', '6,400 samples (4x)'], fontsize=10, fontweight='bold')
ax3.set_ylim(35, 55)

# ANOVA annotations
ax3.text(4000, 52.5, 'Scale Effect: p = 0.7265 (ns)\nGolden Scaling Δ = -0.03 DS', ha='center', fontsize=9.5, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#F3F4F6', edgecolor='#9CA3AF'))

ax3.legend(frameon=True, loc='lower right', fontsize=10)
ax3.grid(True, linestyle='--', alpha=0.6)

plt.suptitle('Few Edge Cases Are All You Need: 5-Model Closed-Loop Benchmark Evaluation',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()

# Save
output_path = '/home/aimslab/lead/docs/figures/benchmark_5_models_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved figure to: {output_path}")
