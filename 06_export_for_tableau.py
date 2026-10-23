"""
STEP 6 - Export Tableau-ready CSV files (open them in Tableau Public).

Input : data/scored_transactions.csv
Output: output/tableau_*.csv
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
df = pd.read_csv(ROOT / "data" / "scored_transactions.csv", parse_dates=["timestamp"])
RULES = ["zscore_amount", "iqr_amount", "velocity", "location_jump", "new_device", "odd_hour"]

df["date"] = df["timestamp"].dt.date
df["amount_flagged"] = df["amount"] * df["flagged"]

# 1) full transaction-level table (main Tableau data source)
cols = ["txn_id", "customer_id", "timestamp", "date", "hour", "amount", "merchant_category",
        "channel", "city", "device_id", "risk_score", "risk_level", "flagged"] + RULES + \
       ["is_fraud", "fraud_type"]
df[cols].rename(columns={"is_fraud": "planted_fraud_label"}).to_csv(OUT / "tableau_transactions.csv", index=False)

# 2) daily trend
daily = df.groupby("date").agg(txns=("txn_id", "count"), flagged=("flagged", "sum"),
                               amount_flagged=("amount_flagged", "sum")).reset_index()
daily["flag_rate"] = (daily["flagged"] / daily["txns"]).round(4)
daily.to_csv(OUT / "tableau_daily.csv", index=False)

# 3) by city
city = df.groupby("city").agg(txns=("txn_id", "count"), flagged=("flagged", "sum"),
                              amount_flagged=("amount_flagged", "sum")).reset_index()
city["flag_rate"] = (city["flagged"] / city["txns"]).round(4)
city.to_csv(OUT / "tableau_city.csv", index=False)

# 4) by rule (how often each rule fires on flagged transactions)
fl = df[df["flagged"] == 1]
rules = pd.DataFrame({
    "rule": RULES,
    "total_hits": [int(df[r].sum()) for r in RULES],
    "hits_in_flagged_txns": [int(fl[r].sum()) for r in RULES],
    "amount_in_flagged_txns": [round(float(fl.loc[fl[r] == 1, "amount"].sum()), 2) for r in RULES],
})
rules.to_csv(OUT / "tableau_rules.csv", index=False)

# 5) headline KPIs
kpi = pd.DataFrame([{
    "total_txns": len(df),
    "flagged_txns": int(df["flagged"].sum()),
    "flag_rate_pct": round(df["flagged"].mean() * 100, 2),
    "high_risk_txns": int((df["risk_level"] == "High").sum()),
    "amount_at_risk": round(float(df["amount_flagged"].sum()), 2),
    "customers_with_flags": int(fl["customer_id"].nunique()),
}])
kpi.to_csv(OUT / "tableau_kpis.csv", index=False)
print(kpi.T.to_string(header=False))
