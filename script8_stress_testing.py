# =============================================================
# SCRIPT 8 — Stress Testing (CCAR-Style Scenarios)
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 8 — STRESS TESTING")
print("CCAR-Style: Base / Mild / Severe Recession Scenarios")
print("=" * 60)
print()

# ── Scenario parameters ───────────────────────────────────────
scenarios = {
    'Base Case':        {'pd_mult': 1.00, 'lgd_mult': 1.00, 'color': '#63B179'},
    'Mild Recession':   {'pd_mult': 1.45, 'lgd_mult': 1.00, 'color': '#EF9F27'},
    'Severe Recession': {'pd_mult': 2.10, 'lgd_mult': 1.00, 'color': '#E24B4A'},
}

# ── LGD by product ────────────────────────────────────────────
def get_lgd(row):
    if row['product_type'] == 'Credit Card':  return 0.75
    if row['product_type'] == 'Auto Loan':    return 0.35
    return 0.45

df['lgd_base'] = df.apply(get_lgd, axis=1)

results = []
for scenario, params in scenarios.items():
    df_s = df.copy()
    df_s['stressed_pd']  = (df_s['final_pd'] * params['pd_mult']).clip(upper=0.99)
    df_s['stressed_lgd'] = (df_s['lgd_base'] * params['lgd_mult']).clip(upper=1.0)
    df_s['stressed_el']  = df_s['stressed_pd'] * df_s['stressed_lgd'] * df_s['ead']

    product_el = df_s.groupby('product_type')['stressed_el'].sum()

    results.append({
        'Scenario':              scenario,
        'Total EAD':             df_s['ead'].sum(),
        'Total EL':              df_s['stressed_el'].sum(),
        'EL as % of EAD':        df_s['stressed_el'].sum() / df_s['ead'].sum() * 100,
        'Personal Loan EL':      product_el.get('Personal Loan', 0),
        'Credit Card EL':        product_el.get('Credit Card', 0),
        'Auto Loan EL':          product_el.get('Auto Loan', 0),
        'Capital Reserve (8%)':  df_s['stressed_el'].sum() * 0.08,
        'PD Multiplier':         params['pd_mult'],
        'LGD Multiplier':        params['lgd_mult'],
    })

results_df = pd.DataFrame(results)
base_el = results_df.loc[results_df['Scenario']=='Base Case','Total EL'].values[0]

print("STRESS TEST RESULTS:")
print()
for _, row in results_df.iterrows():
    change = (row['Total EL'] - base_el) / base_el * 100
    change_str = "(baseline)" if row['Scenario'] == 'Base Case' else "(+%.1f%% vs base)" % change
    print("  %s:" % row['Scenario'])
    print("    Total EL:         $%s  %s" % (format(int(row['Total EL']),','), change_str))
    print("    EL as %% of EAD:  %.2f%%" % row['EL as % of EAD'])
    print("    Capital Reserve:  $%s" % format(int(row['Capital Reserve (8%)']),','))
    print()

results_df.to_csv("outputs/stress_test_results.csv", index=False)
print("Output saved: outputs/stress_test_results.csv")

# ── Charts ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.suptitle("CCAR-Style Stress Testing — Portfolio Expected Loss\nFirst National Retail Bank | FY 2024",
             fontsize=13, fontweight='bold')

scen_colors = [scenarios[s]['color'] for s in results_df['Scenario']]

# Total EL by scenario
bars = axes[0].bar(results_df['Scenario'], results_df['Total EL'],
                   color=scen_colors, edgecolor='white')
axes[0].set_ylabel('Total Expected Loss ($)')
axes[0].set_title('Total EL by Scenario', fontweight='bold')
axes[0].set_xticklabels(results_df['Scenario'], rotation=10)
axes[0].set_facecolor('#F9F9F9')
for bar, val in zip(bars, results_df['Total EL']):
    axes[0].text(bar.get_x() + bar.get_width()/2, val + 5,
                 '$%s' % format(int(val),','), ha='center', fontsize=8, fontweight='bold')

# EL by product across scenarios
x = np.arange(len(results_df))
w = 0.25
axes[1].bar(x - w, results_df['Personal Loan EL'], w,
            color='#1F3864', label='Personal Loan', edgecolor='white')
axes[1].bar(x,     results_df['Credit Card EL'],   w,
            color='#2E75B6', label='Credit Card', edgecolor='white')
axes[1].bar(x + w, results_df['Auto Loan EL'],     w,
            color='#5BA3C9', label='Auto Loan', edgecolor='white')
axes[1].set_xticks(x)
axes[1].set_xticklabels(results_df['Scenario'], rotation=10, fontsize=9)
axes[1].set_ylabel('Expected Loss ($)')
axes[1].set_title('EL by Product × Scenario', fontweight='bold')
axes[1].legend(fontsize=9)
axes[1].set_facecolor('#F9F9F9')

# Capital reserve
bars3 = axes[2].bar(results_df['Scenario'],
                    results_df['Capital Reserve (8%)'],
                    color=scen_colors, edgecolor='white')
axes[2].set_ylabel('Capital Reserve Required ($)')
axes[2].set_title('Capital Reserve Requirement (8%)\nby Scenario', fontweight='bold')
axes[2].set_xticklabels(results_df['Scenario'], rotation=10)
axes[2].set_facecolor('#F9F9F9')
for bar, val in zip(bars3, results_df['Capital Reserve (8%)']):
    axes[2].text(bar.get_x() + bar.get_width()/2, val + 0.5,
                 '$%s' % format(int(val),','), ha='center', fontsize=8, fontweight='bold')

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig("outputs/chart_stress_testing.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_stress_testing.png")
print()
print("Script 8 complete.")
print()
print("=" * 60)
print("ALL 8 SCRIPTS COMPLETE")
print("Check your outputs folder for all CSV files and charts")
print("=" * 60)