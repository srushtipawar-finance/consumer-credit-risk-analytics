# Consumer Credit Risk & Retail Lending Analytics Platform

A four-part credit risk analytics build for a retail lending portfolio — covering scorecard modeling, SQL-based portfolio querying, statistical PD/EL modeling in Python, and an executive Power BI reporting layer. Built to mirror how a consumer credit risk team at a retail bank would actually structure this work: manual scorecards for underwriting, SQL for ad-hoc portfolio querying, Python for statistical modeling, and BI dashboards for the risk committee.

---

## Why this project

Retail lenders live or die by how well they price and monitor credit risk across personal loans, credit cards, and auto loans. This project rebuilds the core toolkit a credit risk analyst uses day to day:

- **Score and price** an individual loan application (Excel)
- **Query** the loan book for delinquency, exposure, and vintage performance (SQL)
- **Model** probability of default and expected loss statistically (Python)
- **Report** portfolio health to a risk committee (Power BI)

Each layer is self-contained and can be reviewed independently.

---

## Repository structure

```
├── Excel/
│   └── Consumer_Credit_Risk_Platform.xlsx
│
├── SQL/
│   ├── consumer_credit_portfolio.db
│   ├── 01_table_customers.png … 04_table_risk_scores.png
│   └── 05_query1_delinquency_rate.png … 09_query5_vintage_default.png
│
├── Python/
│   ├── script1_data_generation.py … script8_stress_testing.py
│   ├── data/
│   │   └── borrowers_data.csv
│   └── outputs/
│       ├── *.csv   (model outputs, WoE/IV, expected loss, vintage, stress test)
│       └── *.png   (EDA, model comparison, expected loss, vintage, stress charts)
│
└── PowerBI/
    ├── Consumer_Credit_Risk_Dashboards.pbix
    └── dashboard1_portfolio_overview.png … dashboard5_vintage_delinquency.png
```

---

## 1. Excel — Manual Scorecard & Stress Testing

A FICO-style scorecard model built from scratch, used the way an underwriter would use it at the point of origination.

- **Credit_Scorecard** — six-factor weighted scorecard (payment history, utilization, credit history length, DTI, employment stability, credit mix) producing a 300–850 score, risk tier, and approval decision
- **Application_Model** — live loan application calculator: enter an applicant's financials, get DTI, monthly payment, PD, LGD, and expected loss in real time
- **Delinquency_Tracker** — 24-month rolling delinquency trend across all three products with automated threshold alerts
- **Vintage_Analysis** — cumulative default curves by origination quarter
- **Stress_Test** — CCAR-style base/mild/severe recession scenarios with capital reserve sizing
- **Portfolio_Summary** — quarter-over-quarter executive KPI summary for a risk committee

**Key result:** severe recession stress increases portfolio expected loss by **119%** versus base case, driving a recommended capital reserve increase.

---

## 2. SQL — Portfolio Database & Query Layer

A normalized SQLite database (`customers`, `loan_applications`, `payment_history`, `risk_scores`) with five analytical queries an analyst would run to monitor the book:

| Query | Purpose |
|---|---|
| Delinquency rate | By product and risk tier |
| Approval rate | By credit tier, with average PD |
| Expected loss | By state and product, ranked by loss concentration |
| 90+ DPD | Borrowers in serious default, flagged for collections |
| Vintage default | Default rate by origination quarter and product |

**Key result:** the highest expected-loss concentration sits in **FL Auto Loans**, at 22.4% of exposure.

---

## 3. Python — Statistical Credit Risk Modeling

An eight-stage modeling pipeline, from raw data to stress-tested capital requirements.

1. **Data generation & summary** — portfolio-level exposure, approval, and default statistics
2. **Exploratory analysis** — score distribution, default rate by tier, DTI relationships, product mix
3. **WoE / Information Value** — feature-level predictive power ranking for scorecard development
4. **Logistic regression** — fully explainable PD model built for regulatory reporting
5. **Random forest** — higher-accuracy PD model for internal risk monitoring, benchmarked against logistic regression
6. **Expected loss (Basel II)** — EL = PD × LGD × EAD at the borrower level, with mild/severe stress multipliers
7. **Vintage analysis** — cumulative default curves by origination cohort
8. **Stress testing (CCAR-style)** — base/mild/severe scenario expected loss and capital reserve requirements

**Key result:** the **Q2-2023** origination cohort is the portfolio's weakest vintage, and severe-scenario stress testing raises expected loss from **$12.1K to $25.4K** — a **110% increase** — against a corresponding capital reserve requirement.

> **Note on model performance:** given the small, fully synthetic 25-borrower sample used for local development, default status is closely tied to credit score in the generated data, which produces near-perfect model separation (AUC ≈ 1.0). This is an expected artifact of a small synthetic dataset rather than a production result, and would not hold at real portfolio scale with thousands of borrowers and noisier outcomes.

---

## 4. Power BI — Executive Reporting Layer

Five interactive dashboards translating the SQL and Python outputs into a risk-committee-ready reporting layer.

| Dashboard | Focus |
|---|---|
| Portfolio Overview | Total exposure, borrower count, default rate, loan status mix |
| Approval Analysis | Approval/decline rates by credit tier, application funnel |
| Default Prediction | Logistic regression vs. random forest PD comparison, risk tier distribution |
| Expected Loss | Basel II EL by borrower and product, three-scenario stress test |
| Vintage & Delinquency | Cumulative default by origination quarter, early warning indicators |

---

## Tech stack

`Python` (pandas, scikit-learn, matplotlib) · `SQL` (SQLite) · `Power BI` (DAX, Power Query) · `Excel` (advanced formulas, conditional formatting, scenario modeling)

---

## Methodology notes

- Expected Loss follows the Basel II framework: **EL = PD × LGD × EAD**, with LGD assumptions set by product type (Credit Card 75%, Personal Loan 45%, Auto Loan 35%, reflecting collateral recovery differences)
- Stress scenarios apply CCAR-style macroeconomic shocks (unemployment, GDP, home prices, income growth) translated into PD multipliers by product
- The Excel scorecard and the Python/SQL/Power BI modeling pipeline are intentionally built at different scales — Excel models a hypothetical full-scale retail bank (5,000 borrowers, $340M exposure) for underwriting-level scorecard mechanics, while the SQL/Python/Power BI layer models a smaller generated loan sample end-to-end for statistical technique demonstration. Numbers are consistent *within* each layer, not merged across them.

---

## Author

Srushti Mahant Pawar
