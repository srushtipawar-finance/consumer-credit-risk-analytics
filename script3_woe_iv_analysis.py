# =============================================================
# SCRIPT 3 — Weight of Evidence & Information Value Analysis
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 3 — WEIGHT OF EVIDENCE & INFORMATION VALUE")
print("Industry Standard Scorecard Development Method")
print("=" * 60)
print()

def calculate_woe_iv(df, feature, target, bins=5):
    """Calculate WoE and IV for a given feature."""
    temp = df[[feature, target]].copy()

    if df[feature].dtype in ['float64', 'int64']:
        temp['bin'] = pd.qcut(temp[feature], q=bins, duplicates='drop')
    else:
        temp['bin'] = temp[feature]

    grouped = temp.groupby('bin')[target].agg(['sum','count'])
    grouped.columns = ['defaults', 'total']
    grouped['non_defaults'] = grouped['total'] - grouped['defaults']

    total_defaults = grouped['defaults'].sum()
    total_non_defaults = grouped['non_defaults'].sum()

    grouped['pct_defaults'] = grouped['defaults'] / total_defaults
    grouped['pct_non_defaults'] = grouped['non_defaults'] / total_non_defaults

    grouped['pct_defaults'] = grouped['pct_defaults'].replace(0, 0.0001)
    grouped['pct_non_defaults'] = grouped['pct_non_defaults'].replace(0, 0.0001)

    grouped['woe'] = np.log(grouped['pct_non_defaults'] / grouped['pct_defaults'])
    grouped['iv_component'] = (grouped['pct_non_defaults'] - grouped['pct_defaults']) * grouped['woe']

    iv = grouped['iv_component'].sum()
    return round(iv, 4), grouped

# ── Calculate IV for all features ────────────────────────────
features = ['credit_score','credit_utilization','dti_ratio',
            'annual_income','years_credit_hist','num_credit_lines',
            'accounts_delinquent']

iv_results = []
for feature in features:
    try:
        iv, _ = calculate_woe_iv(df, feature, 'default_label')
        strength = ('Very Strong' if iv >= 0.5 else
                    'Strong'      if iv >= 0.3 else
                    'Medium'      if iv >= 0.1 else
                    'Weak'        if iv >= 0.02 else 'Useless')
        iv_results.append({'Feature': feature, 'IV': iv, 'Predictive Power': strength})
        print("  %-25s IV = %.4f  (%s)" % (feature, iv, strength))
    except Exception as e:
        print("  %-25s Error: %s" % (feature, str(e)))

iv_df = pd.DataFrame(iv_results).sort_values('IV', ascending=False)
iv_df.to_csv("outputs/woe_iv_results.csv", index=False)
print()
print("IV results saved: outputs/woe_iv_results.csv")

# ── Chart: IV Rankings ────────────────────────────────────────
colors = ['#E24B4A' if iv >= 0.3 else '#EF9F27' if iv >= 0.1
          else '#63B179' for iv in iv_df['IV']]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(iv_df['Feature'], iv_df['IV'], color=colors, edgecolor='white')
ax.axvline(x=0.3, color='#E24B4A', linestyle='--', linewidth=1.5, label='Strong (0.3+)')
ax.axvline(x=0.1, color='#EF9F27', linestyle='--', linewidth=1.5, label='Medium (0.1+)')
ax.set_xlabel('Information Value (IV)', fontsize=11)
ax.set_title('Feature Predictive Power — Information Value Ranking\nWoE/IV Analysis | First National Retail Bank',
             fontsize=13, fontweight='bold')
ax.set_facecolor('#F9F9F9')
fig.patch.set_facecolor('white')
for bar, val in zip(bars, iv_df['IV']):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            '%.4f' % val, va='center', fontsize=9)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("outputs/chart_woe_iv.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_woe_iv.png")
print()
print("TOP PREDICTORS:")
for _, row in iv_df.head(3).iterrows():
    print("  %s: IV=%.4f (%s)" % (row['Feature'], row['IV'], row['Predictive Power']))
print()
print("Script 3 complete.")