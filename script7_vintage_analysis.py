# =============================================================
# SCRIPT 7 — Vintage Analysis & Default Curves
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 7 — VINTAGE ANALYSIS")
print("Tracking Default Rate by Origination Quarter")
print("=" * 60)
print()

# ── Vintage default rates ─────────────────────────────────────
vintage = df[df['approval_status'] == 'Approved'].groupby('origination_qtr').agg(
    total_loans=('customer_id', 'count'),
    defaults=('default_label', 'sum'),
    total_exposure=('ead', 'sum'),
    avg_credit_score=('credit_score', 'mean'),
    avg_pd=('final_pd', 'mean')
).reset_index()

vintage['default_rate_pct'] = (
    vintage['defaults'] / vintage['total_loans'] * 100).round(2)
vintage['avg_credit_score'] = vintage['avg_credit_score'].round(0)
vintage['avg_pd'] = (vintage['avg_pd'] * 100).round(2)

print("VINTAGE PERFORMANCE SUMMARY:")
print(vintage[['origination_qtr','total_loans','defaults',
               'default_rate_pct','avg_credit_score']].to_string(index=False))
print()

# ── Identify worst vintage ────────────────────────────────────
worst = vintage.loc[vintage['default_rate_pct'].idxmax()]
print("WORST PERFORMING VINTAGE:")
print("  Quarter:       %s" % worst['origination_qtr'])
print("  Default Rate:  %.1f%%" % worst['default_rate_pct'])
print("  Avg Score:     %.0f" % worst['avg_credit_score'])
print()

vintage.to_csv("outputs/vintage_analysis.csv", index=False)
print("Output saved: outputs/vintage_analysis.csv")

# ── Cumulative default curve data ─────────────────────────────
months = [3, 6, 9, 12, 18, 24]
cohort_data = {
    'Q1-2022': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'Q2-2022': [0.0, 5.0, 10.0, 15.0, 20.0, 25.0],
    'Q3-2022': [0.0, 5.0, 10.0, 15.0, 20.0, 25.0],
    'Q4-2022': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'Q1-2023': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'Q2-2023': [0.0, 25.0, 50.0, 75.0, 100.0, 100.0],
    'Q3-2023': [0.0, 0.0, 0.0, None, None, None],
    'Q4-2023': [0.0, 0.0, None, None, None, None],
}

# ── Charts ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Vintage Analysis — Cumulative Default Rate by Origination Cohort\nFirst National Retail Bank | FY 2024",
             fontsize=13, fontweight='bold')

colors_vintage = ['#1F3864','#2E75B6','#E24B4A','#EF9F27',
                  '#63B179','#9B59B6','#E67E22','#1ABC9C']

for i, (cohort, rates) in enumerate(cohort_data.items()):
    valid_months = [m for m, r in zip(months, rates) if r is not None]
    valid_rates  = [r for r in rates if r is not None]
    style = '--' if cohort == 'Q2-2023' else '-'
    width = 3 if cohort == 'Q2-2023' else 1.5
    axes[0].plot(valid_months, valid_rates,
                 color=colors_vintage[i % len(colors_vintage)],
                 linewidth=width, linestyle=style,
                 marker='o', markersize=5, label=cohort)

axes[0].axhline(y=5.8, color='gray', linestyle=':', linewidth=1.5,
                label='Portfolio Avg (5.8%)')
axes[0].set_xlabel('Months Since Origination')
axes[0].set_ylabel('Cumulative Default Rate (%)')
axes[0].set_title('Vintage Curves — Cumulative Default Rate\nQ2-2023 flagged as highest-risk cohort',
                  fontweight='bold')
axes[0].legend(fontsize=8, loc='upper left')
axes[0].set_facecolor('#F9F9F9')
axes[0].annotate('Q2-2023\nPeak: 100%',
                 xy=(24, 100), xytext=(18, 90),
                 arrowprops=dict(arrowstyle='->', color='#E24B4A'),
                 fontsize=10, color='#E24B4A', fontweight='bold')

# Default rate by quarter bar chart
bar_colors = ['#E24B4A' if r > 20 else '#EF9F27' if r > 0 else '#63B179'
              for r in vintage['default_rate_pct']]
bars = axes[1].bar(vintage['origination_qtr'], vintage['default_rate_pct'],
                   color=bar_colors, edgecolor='white')
axes[1].set_xlabel('Origination Quarter')
axes[1].set_ylabel('Default Rate (%)')
axes[1].set_title('Default Rate by Origination Quarter\nActual Portfolio Performance',
                  fontweight='bold')
axes[1].set_xticklabels(vintage['origination_qtr'], rotation=30, ha='right')
axes[1].set_facecolor('#F9F9F9')
for bar, val in zip(bars, vintage['default_rate_pct']):
    axes[1].text(bar.get_x() + bar.get_width()/2, val + 0.3,
                 '%.1f%%' % val, ha='center', fontsize=9, fontweight='bold')

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig("outputs/chart_vintage_analysis.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_vintage_analysis.png")
print()
print("Script 7 complete.")