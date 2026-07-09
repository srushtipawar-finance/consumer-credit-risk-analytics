# =============================================================
# SCRIPT 6 — Expected Loss Model (Basel II Framework)
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
print("SCRIPT 6 — EXPECTED LOSS MODEL")
print("Basel II Framework: EL = PD x LGD x EAD")
print("=" * 60)
print()

# ── LGD by product ────────────────────────────────────────────
def get_lgd(row):
    if row['product_type'] == 'Credit Card':  return 0.75
    if row['product_type'] == 'Auto Loan':    return 0.35
    return 0.45

df['lgd_calc'] = df.apply(get_lgd, axis=1)
df['el_calc']  = df['final_pd'] * df['lgd_calc'] * df['ead']

# ── Stress scenarios ──────────────────────────────────────────
df['el_mild']   = df['el_calc'] * 1.45
df['el_severe'] = df['el_calc'] * 2.10

# ── EL classification ─────────────────────────────────────────
df['el_class'] = df['el_calc'].apply(
    lambda x: 'High EL (>$500)' if x > 500 else
              'Moderate EL ($100-$500)' if x > 100 else 'Low EL (<$100)')

# ── Portfolio summary ─────────────────────────────────────────
total_ead    = df['ead'].sum()
total_el     = df['el_calc'].sum()
total_mild   = df['el_mild'].sum()
total_severe = df['el_severe'].sum()

print("PORTFOLIO EXPECTED LOSS SUMMARY:")
print("  Total EAD (Exposure):    $%s" % format(int(total_ead),','))
print("  Base Case EL:            $%s  (%.2f%% of EAD)" % (
    format(int(total_el),','), total_el/total_ead*100))
print("  Mild Recession EL:       $%s  (%.2f%% of EAD)" % (
    format(int(total_mild),','), total_mild/total_ead*100))
print("  Severe Recession EL:     $%s  (%.2f%% of EAD)" % (
    format(int(total_severe),','), total_severe/total_ead*100))
print("  Severe vs Base increase: +%.1f%%" % (
    (total_severe - total_el) / total_el * 100))
print()

# ── Anchor borrower ───────────────────────────────────────────
mpp = df[df['customer_id'] == 4].iloc[0]
print("HIGH RISK BORROWER (Customer 4 — FL Auto Loan):")
print("  PD:  %.1f%%" % (mpp['final_pd'] * 100))
print("  LGD: %.0f%%" % (mpp['lgd_calc'] * 100))
print("  EAD: $%s" % format(int(mpp['ead']),','))
print("  EL:  $%s" % format(int(mpp['el_calc']),','))
print()

# ── Save output ───────────────────────────────────────────────
out = df[['customer_id','product_type','final_pd','lgd_calc',
          'ead','el_calc','el_mild','el_severe','el_class',
          'risk_tier','loan_status']].copy()
out.columns = ['customer_id','product_type','pd','lgd','ead',
               'expected_loss','el_mild','el_severe','el_class',
               'risk_tier','loan_status']
out.to_csv("outputs/expected_loss_output.csv", index=False)
print("Output saved: outputs/expected_loss_output.csv")

# ── Charts ────────────────────────────────────────────────────
color_map = {'High EL (>$500)':'#E24B4A',
             'Moderate EL ($100-$500)':'#EF9F27',
             'Low EL (<$100)':'#63B179'}
colors = df['el_class'].map(color_map)

fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.suptitle("Expected Loss Analysis — Basel II Framework\nFirst National Retail Bank | FY 2024",
             fontsize=13, fontweight='bold')

# EL by borrower
bars = axes[0].barh(df.sort_values('el_calc')['customer_id'].astype(str),
                    df.sort_values('el_calc')['el_calc'],
                    color=df.sort_values('el_calc')['el_class'].map(color_map),
                    edgecolor='white')
axes[0].set_xlabel('Expected Loss ($)')
axes[0].set_ylabel('Customer ID')
axes[0].set_title('Expected Loss by Borrower\nEL = PD × LGD × EAD', fontweight='bold')
axes[0].set_facecolor('#F9F9F9')
handles = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
axes[0].legend(handles=handles, fontsize=8)

# EL by product
el_product = df.groupby('product_type')['el_calc'].sum()
prod_colors = ['#1F3864','#2E75B6','#5BA3C9']
axes[1].bar(el_product.index, el_product.values,
            color=prod_colors[:len(el_product)], edgecolor='white')
axes[1].set_xlabel('Product Type')
axes[1].set_ylabel('Total Expected Loss ($)')
axes[1].set_title('Expected Loss by Product\n($)', fontweight='bold')
axes[1].set_facecolor('#F9F9F9')
for i, val in enumerate(el_product.values):
    axes[1].text(i, val + 10, '$%d' % val, ha='center', fontsize=9, fontweight='bold')

# Stress scenarios
scenarios = ['Base Case', 'Mild Recession\n(×1.45)', 'Severe Recession\n(×2.10)']
values = [total_el, total_mild, total_severe]
scen_colors = ['#63B179', '#EF9F27', '#E24B4A']
bars2 = axes[2].bar(scenarios, values, color=scen_colors, edgecolor='white')
axes[2].set_ylabel('Total Expected Loss ($)')
axes[2].set_title('Stress Test Scenarios\nEL Under Different Conditions', fontweight='bold')
axes[2].set_facecolor('#F9F9F9')
for bar, val in zip(bars2, values):
    axes[2].text(bar.get_x() + bar.get_width()/2, val + 20,
                 '$%s' % format(int(val),','), ha='center', fontsize=9, fontweight='bold')

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig("outputs/chart_expected_loss.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_expected_loss.png")
print()
print("Script 6 complete.")