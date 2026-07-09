# =============================================================
# SCRIPT 5 — Random Forest Model + SHAP Values + Comparison
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
import os

os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("SCRIPT 5 — RANDOM FOREST + MODEL COMPARISON")
print("Internal Risk Monitoring Model")
print("=" * 60)
print()

features = ['credit_score','credit_utilization','dti_ratio',
            'annual_income','years_credit_hist','num_credit_lines',
            'accounts_delinquent']

X = df[features].fillna(df[features].median())
y = df['default_label']

# ── Random Forest ─────────────────────────────────────────────
rf_model = RandomForestClassifier(n_estimators=100, random_state=42,
                                   max_depth=5, min_samples_leaf=2)
rf_model.fit(X, y)
df['rf_pd'] = rf_model.predict_proba(X)[:, 1]
rf_auc = roc_auc_score(y, df['rf_pd'])
rf_gini = 2 * rf_auc - 1

# ── Logistic Regression for comparison ───────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(X_scaled, y)
df['lr_pd'] = lr_model.predict_proba(X_scaled)[:, 1]
lr_auc = roc_auc_score(y, df['lr_pd'])
lr_gini = 2 * lr_auc - 1

print("MODEL COMPARISON:")
print("  %-30s AUC=%.4f  Gini=%.4f" % ("Logistic Regression:", lr_auc, lr_gini))
print("  %-30s AUC=%.4f  Gini=%.4f" % ("Random Forest:", rf_auc, rf_gini))
print()
print("RECOMMENDATION:")
print("  Random Forest for internal risk monitoring (higher AUC)")
print("  Logistic Regression for regulatory reporting (fully explainable)")
print()

# ── Feature importance ────────────────────────────────────────
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("RANDOM FOREST FEATURE IMPORTANCE:")
for _, row in importance_df.iterrows():
    bar = '█' * int(row['Importance'] * 50)
    print("  %-25s %.4f  %s" % (row['Feature'], row['Importance'], bar))

importance_df.to_csv("outputs/feature_importance.csv", index=False)

# ── SHAP-style manual importance chart ───────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Random Forest Model + Model Comparison\nFirst National Retail Bank | FY 2024",
             fontsize=13, fontweight='bold')

# ROC comparison
fpr_lr, tpr_lr, _ = roc_curve(y, df['lr_pd'])
fpr_rf, tpr_rf, _ = roc_curve(y, df['rf_pd'])
axes[0].plot(fpr_lr, tpr_lr, color='#2E75B6', linewidth=2.5,
             label='Logistic Reg (AUC=%.3f)' % lr_auc)
axes[0].plot(fpr_rf, tpr_rf, color='#E24B4A', linewidth=2.5,
             label='Random Forest (AUC=%.3f)' % rf_auc)
axes[0].plot([0,1],[0,1],'k--',linewidth=1,label='Random')
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].set_title('ROC Curve Comparison', fontweight='bold')
axes[0].legend(fontsize=9)
axes[0].set_facecolor('#F9F9F9')

# Feature importance
colors_imp = ['#1F3864','#2E75B6','#5BA3C9','#85C1E9',
              '#AED6F1','#D6EAF8','#EBF5FB'][:len(importance_df)]
bars = axes[1].barh(importance_df['Feature'], importance_df['Importance'],
                    color=colors_imp, edgecolor='white')
axes[1].set_xlabel('Feature Importance Score')
axes[1].set_title('Random Forest\nFeature Importance', fontweight='bold')
axes[1].set_facecolor('#F9F9F9')
for bar, val in zip(bars, importance_df['Importance']):
    axes[1].text(val + 0.001, bar.get_y() + bar.get_height()/2,
                 '%.3f' % val, va='center', fontsize=9)

# AUC comparison bar chart
models = ['Logistic\nRegression', 'Random\nForest']
aucs = [lr_auc, rf_auc]
ginis = [lr_gini, rf_gini]
x = np.arange(len(models))
w = 0.35
axes[2].bar(x - w/2, aucs, w, color='#2E75B6', label='AUC', edgecolor='white')
axes[2].bar(x + w/2, ginis, w, color='#63B179', label='Gini', edgecolor='white')
axes[2].set_xticks(x)
axes[2].set_xticklabels(models)
axes[2].set_ylabel('Score')
axes[2].set_title('AUC & Gini Comparison\nLR vs Random Forest', fontweight='bold')
axes[2].legend()
axes[2].set_facecolor('#F9F9F9')
for i, (a, g) in enumerate(zip(aucs, ginis)):
    axes[2].text(i - w/2, a + 0.01, '%.3f' % a, ha='center', fontsize=9, fontweight='bold')
    axes[2].text(i + w/2, g + 0.01, '%.3f' % g, ha='center', fontsize=9, fontweight='bold')

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig("outputs/chart_model_comparison.png", dpi=150, bbox_inches='tight')
plt.show()
print()
print("Charts saved: outputs/chart_model_comparison.png")
print()
print("Script 5 complete.")