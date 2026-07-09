# =============================================================
# SCRIPT 1 — Data Generation & Database Population
# Consumer Credit Risk Platform — First National Retail Bank
# =============================================================

import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)
os.makedirs("outputs", exist_ok=True)

# ── Load the seed data ────────────────────────────────────────
df = pd.read_csv("data/borrowers_data.csv")

print("=" * 60)
print("CONSUMER CREDIT RISK PLATFORM — DATA GENERATION")
print("First National Retail Bank")
print("=" * 60)
print()
print("Data loaded successfully.")
print("Total borrowers: %d" % len(df))
print("Columns: %d" % len(df.columns))
print()

# ── Summary statistics ────────────────────────────────────────
print("PORTFOLIO SUMMARY:")
print("  Total loan exposure:  $%s" % format(int(df['ead'].sum()), ','))
print("  Avg credit score:     %d" % int(df['credit_score'].mean()))
print("  Approval rate:        %.1f%%" % (
    (df['approval_status'] == 'Approved').mean() * 100))
print("  Default rate:         %.1f%%" % (
    df['default_label'].mean() * 100))
print()

# ── Product breakdown ─────────────────────────────────────────
print("PRODUCT BREAKDOWN:")
product_summary = df.groupby('product_type').agg(
    count=('customer_id', 'count'),
    total_exposure=('ead', 'sum'),
    avg_pd=('final_pd', 'mean')
).round(3)
print(product_summary.to_string())
print()

# ── Credit tier breakdown ─────────────────────────────────────
print("CREDIT TIER BREAKDOWN:")
tier_summary = df.groupby('credit_tier').agg(
    count=('customer_id', 'count'),
    avg_score=('credit_score', 'mean'),
    avg_pd=('final_pd', 'mean')
).round(2)
print(tier_summary.to_string())
print()

# ── Populate SQLite database ──────────────────────────────────
print("Connecting to SQL database...")

db_path = "../SQL/consumer_credit_portfolio.db"
if not os.path.exists(db_path):
    db_path = "consumer_credit_portfolio.db"
    print("Note: Place database in SQL folder for best results")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables found:", tables)

    conn.close()
    print("Database connection successful.")
except Exception as e:
    print("Database note:", str(e))
    print("Continuing with CSV-based analysis...")

# ── Save cleaned data ─────────────────────────────────────────
df.to_csv("outputs/clean_borrowers_data.csv", index=False)
print()
print("Clean data saved to outputs/clean_borrowers_data.csv")
print()
print("Script 1 complete. Ready for Script 2.")