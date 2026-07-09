# =============================================================
# SCRIPT 4 — Logistic Regression PD Model
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 4 — LOGISTIC REGRESSION PD MODEL")
print("Regulatory Reporting Model | Fully Explainable")
print("=" * 60)
print()

# ── Features and target ───────────────────────────────────────
features = ['credit_score','credit_utilization','dti_ratio',
            'annual_income','years_credit_hist','num_credit_lines',
            'accounts_delinquent']

X = df[features].fillna(df[features].median())
y = df['default_label']

# ── Scale and train ───────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_scaled, y)

# ── Predict PD ────────────────────────────────────────────────
df['lr_pd'] = model.predict_proba(X_scaled)[:, 1]
df['lr_pd_pct'] = (df['lr_pd'] * 100).round(2)

# ── AUC and Gini ──────────────────────────────────────────────
auc = roc_auc_score(y, df['lr_pd'])
gini = 2 * auc - 1

print("MODEL PERFORMANCE:")
print("  AUC Score:  %.4f" % auc)
print("  Gini:       %.4f" % gini)
print("  (AUC > 0.7 = acceptable, > 0.8 = good, > 0.9 = excellent)")
print()

# ── Feature coefficients ──────────────────────────────────────
print("FEATURE IMPORTANCE (Coefficients):")
coef_df = pd.DataFrame({
    'Feature': features,
    'Coefficient': model.coef_[0]
}).sort_values('Coefficient', key=abs, ascending=False)
for _, row in coef_df.iterrows():
    direction = "increases" if row['Coefficient'] < 0 else "decreases"
    print("  %-25s %.4f  (higher value %s default risk)" % (
        row['Feature'], row['Coefficient'], direction))

# ── Save output ───────────────────────────────────────────────
output = df[['customer_id','credit_score','product_type','lr_pd_pct',
             'risk_tier','loan_status','ead']].copy()
output.columns = ['customer_id','credit_score','product_type',
                  'lr_pd_pct','risk_tier','loan_status','loan_amount']
output.to_csv("outputs/lr_model_output.csv", index=False)
print()
print("Output saved: outputs/lr_model_output.csv")

# ── ROC Curve Chart ───────────────────────────────────────────
fpr, tpr, _ = roc_curve(y, df['lr_pd'])
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].plot(fpr, tpr, color='#2E75B6', linewidth=2.5,
             label='LR Model (AUC=%.3f, Gini=%.3f)' % (auc, gini))
axes[0].plot([0,1],[0,1], 'k--', linewidth=1, label='Random (AUC=0.5)')
axes[0].fill_between(fpr, tpr, alpha=0.1, color='#2E75B6')
axes[0].set_xlabel('False Positive Rate', fontsize=11)
axes[0].set_ylabel('True Positive Rate', fontsize=11)
axes[0].set_title('ROC Curve — Logistic Regression\n(Used for Regulatory Reporting)',
                  fontsize=12, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].set_facecolor('#F9F9F9')

# PD distribution
colors = ['#E24B4A' if d == 1 else '#63B179' for d in df['default_label']]
axes[1].bar(range(len(df)), sorted(df['lr_pd_pct']),
            color=sorted(['#E24B4A' if d == 1 else '#63B179'
                          for d in df.sort_values('lr_pd')['default_label']]),
            edgecolor='white', linewidth=0.3)
axes[1].set_xlabel('Borrowers (sorted by PD)')
axes[1].set_ylabel('Probability of Default (%)')
axes[1].set_title('PD Distribution — All Borrowers\nLogistic Regression Model',
                  fontsize=12, fontweight='bold')
axes[1].set_facecolor('#F9F9F9')
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color='#E24B4A', label='Defaulted'),
           mpatches.Patch(color='#63B179', label='Performing')]
axes[1].legend(handles=handles)

fig.patch.set_facecolor('white')
plt.suptitle("Logistic Regression PD Model | First National Retail Bank",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig("outputs/chart_logistic_regression.png", dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved: outputs/chart_logistic_regression.png")
print()
print("Script 4 complete.")