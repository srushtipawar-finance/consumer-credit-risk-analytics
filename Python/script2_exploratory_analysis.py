# =============================================================
# SCRIPT 2 — Exploratory Data Analysis
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 2 — EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# ── Chart 1: Credit Score Distribution ───────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Consumer Credit Portfolio — Exploratory Analysis\nFirst National Retail Bank | FY 2024",
             fontsize=14, fontweight='bold', y=1.01)

# Credit score histogram
axes[0,0].hist(df['credit_score'], bins=15, color='#2E75B6',
               edgecolor='white', linewidth=0.8)
axes[0,0].axvline(df['credit_score'].mean(), color='#E24B4A',
                  linestyle='--', linewidth=2, label='Mean: %.0f' % df['credit_score'].mean())
axes[0,0].set_title('Credit Score Distribution', fontweight='bold')
axes[0,0].set_xlabel('Credit Score')
axes[0,0].set_ylabel('Number of Borrowers')
axes[0,0].legend()
axes[0,0].set_facecolor('#F9F9F9')

# Default rate by credit tier
tier_order = ['Deep Subprime','Subprime','Near Prime','Prime','Super Prime']
tier_defaults = df[df['credit_tier'].isin(tier_order)].groupby('credit_tier')['default_label'].mean() * 100
tier_defaults = tier_defaults.reindex([t for t in tier_order if t in tier_defaults.index])
colors = ['#E24B4A','#E88040','#EF9F27','#63B179','#2E75B6'][:len(tier_defaults)]
bars = axes[0,1].bar(range(len(tier_defaults)), tier_defaults.values,
                      color=colors, edgecolor='white')
axes[0,1].set_xticks(range(len(tier_defaults)))
axes[0,1].set_xticklabels(tier_defaults.index, rotation=15, ha='right', fontsize=9)
axes[0,1].set_title('Default Rate by Credit Tier (%)', fontweight='bold')
axes[0,1].set_ylabel('Default Rate (%)')
axes[0,1].set_facecolor('#F9F9F9')
for bar, val in zip(bars, tier_defaults.values):
    axes[0,1].text(bar.get_x() + bar.get_width()/2, val + 0.5,
                   '%.1f%%' % val, ha='center', va='bottom', fontsize=9, fontweight='bold')

# DTI vs Credit Score scatter
colors_scatter = ['#E24B4A' if d == 1 else '#63B179' for d in df['default_label']]
axes[1,0].scatter(df['dti_ratio'], df['credit_score'],
                  c=colors_scatter, alpha=0.7, edgecolors='white', linewidth=0.5, s=80)
axes[1,0].set_xlabel('Debt-to-Income Ratio')
axes[1,0].set_ylabel('Credit Score')
axes[1,0].set_title('Credit Score vs DTI Ratio', fontweight='bold')
axes[1,0].set_facecolor('#F9F9F9')
handles = [mpatches.Patch(color='#E24B4A', label='Default'),
           mpatches.Patch(color='#63B179', label='Performing')]
axes[1,0].legend(handles=handles)

# Product mix donut chart
product_counts = df[df['approval_status']=='Approved']['product_type'].value_counts()
colors_donut = ['#1F3864','#2E75B6','#5BA3C9']
wedges, texts, autotexts = axes[1,1].pie(
    product_counts.values, labels=product_counts.index,
    autopct='%1.1f%%', colors=colors_donut,
    wedgeprops={'edgecolor':'white','linewidth':2})
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight('bold')
axes[1,1].set_title('Approved Portfolio by Product Type', fontweight='bold')

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig("outputs/chart_eda_analysis.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_eda_analysis.png")

# ── Summary stats ─────────────────────────────────────────────
print()
print("KEY STATISTICS:")
print("  Avg credit score:    %.0f" % df['credit_score'].mean())
print("  Avg DTI ratio:       %.2f" % df['dti_ratio'].mean())
print("  Avg credit util:     %.2f" % df['credit_utilization'].mean())
print("  Overall default rate: %.1f%%" % (df['default_label'].mean()*100))
print()
print("Script 2 complete.")