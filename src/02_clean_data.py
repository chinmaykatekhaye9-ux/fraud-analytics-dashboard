"""
STEP 2 - Clean and validate the raw data.

Input : data/raw_transactions.csv
Output: data/clean_transactions.csv  and  output/cleaning_report.txt
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
raw = pd.read_csv(ROOT / "data" / "raw_transactions.csv")
log = []

def note(msg):
    print(msg)
    log.append(msg)

note(f"Raw rows                         : {len(raw):,}")

df = raw.copy()

# 1) remove exact duplicate transactions (same txn_id)
before = len(df)
df = df.drop_duplicates(subset="txn_id", keep="first")
note(f"Duplicate rows removed           : {before - len(df):,}")

# 2) fix data types
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
bad_ts = int(df["timestamp"].isna().sum())
bad_amt = int(df["amount"].isna().sum())
note(f"Unparseable timestamps / amounts : {bad_ts} / {bad_amt}")
df = df.dropna(subset=["timestamp", "amount"])

# 3) standardise text (city names had mixed case and stray spaces)
messy = int((df["city"].dropna() != df["city"].dropna().str.strip().str.title()).sum())
df["city"] = df["city"].str.strip().str.title()
note(f"City values standardised         : {messy:,}")

# 4) missing values
miss_city = int(df["city"].isna().sum())
miss_cat = int(df["merchant_category"].isna().sum())
df["city"] = df["city"].fillna("Unknown")
df["merchant_category"] = df["merchant_category"].fillna("Unknown")
note(f"Missing city / category -> 'Unknown': {miss_city} / {miss_cat}")

# 5) validation checks (fail loudly if the data is wrong)
assert (df["amount"] > 0).all(), "non-positive amounts found"
assert df["txn_id"].is_unique, "txn_id not unique"
note(f"Date range                      : {df['timestamp'].min()}  ->  {df['timestamp'].max()}")
note(f"Customers                        : {df['customer_id'].nunique():,}")

df = df.sort_values(["customer_id", "timestamp"]).reset_index(drop=True)
note(f"CLEAN rows                       : {len(df):,}")

df.to_csv(ROOT / "data" / "clean_transactions.csv", index=False)
(ROOT / "output" / "cleaning_report.txt").write_text("\n".join(log) + "\n")
