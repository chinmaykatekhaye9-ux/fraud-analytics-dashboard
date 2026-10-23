"""
STEP 4 - Rule-based fraud detection.

Six rules, each producing a 0/1 flag. Each rule has a weight; the weighted sum is
the RISK SCORE. The score is bucketed into Low / Medium / High.

  R1 zscore_amount   amount is a statistical outlier for THIS customer (Z-Score >= 3 on log-amount)
  R2 iqr_amount      amount above the customer's IQR "extreme" fence (Q3 + 3*IQR)
  R3 velocity        txn is part of a burst of >= 4 txns within 10 minutes
  R4 location_jump   city differs from the customer's previous txn city, within 2 hours
  R5 new_device      device never used before by this customer (after their first 3 txns)
  R6 odd_hour        txn between 00:00 and 04:59

Note: per-customer baselines use the customer's whole history (a simplification).
A production system would use only data seen BEFORE each transaction.

Input : data/clean_transactions.csv
Output: data/scored_transactions.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "clean_transactions.csv", parse_dates=["timestamp"])
df = df.sort_values(["customer_id", "timestamp"]).reset_index(drop=True)

# ---------------------------------------------------------------- settings
Z_THRESHOLD = 3.0
IQR_MULT = 3.0
VELOCITY_WINDOW_SEC = 600
VELOCITY_MIN_TXNS = 4
LOCATION_WINDOW_SEC = 7200
NEW_DEVICE_AFTER_N_TXNS = 3
NIGHT_HOURS = range(0, 5)

WEIGHTS = {"zscore_amount": 2, "iqr_amount": 1, "velocity": 3,
           "location_jump": 3, "new_device": 2, "odd_hour": 1}
HIGH_AT, MEDIUM_AT = 5, 3

g = df.groupby("customer_id")

# ---------------------------------------------------------------- R1: Z-Score
df["log_amount"] = np.log(df["amount"])
df["z_score"] = (df["log_amount"] - g["log_amount"].transform("mean")) / g["log_amount"].transform("std")
df["zscore_amount"] = (df["z_score"] >= Z_THRESHOLD).astype(int)

# ---------------------------------------------------------------- R2: IQR
q1 = g["amount"].transform(lambda s: s.quantile(0.25))
q3 = g["amount"].transform(lambda s: s.quantile(0.75))
df["iqr_upper_fence"] = q3 + IQR_MULT * (q3 - q1)
df["iqr_amount"] = (df["amount"] > df["iqr_upper_fence"]).astype(int)

# ---------------------------------------------------------------- R3: velocity
df["ts_sec"] = (df["timestamp"] - pd.Timestamp("1970-01-01")).dt.total_seconds()
df["velocity"] = 0
for cust, idx in g.indices.items():
    t = df["ts_sec"].to_numpy()[idx]                    # already sorted by time
    pos = np.arange(len(t))
    back = pos - np.searchsorted(t, t - VELOCITY_WINDOW_SEC, side="left") + 1
    fwd = np.searchsorted(t, t + VELOCITY_WINDOW_SEC, side="right") - pos
    df.loc[idx, "velocity"] = ((np.maximum(back, fwd)) >= VELOCITY_MIN_TXNS).astype(int)

# ---------------------------------------------------------------- R4: location jump
prev_city = g["city"].shift(1)
gap = df["ts_sec"] - g["ts_sec"].shift(1)
known = (df["city"] != "Unknown") & (prev_city.notna()) & (prev_city != "Unknown")
df["location_jump"] = (known & (df["city"] != prev_city) & (gap <= LOCATION_WINDOW_SEC)).astype(int)

# ---------------------------------------------------------------- R5: new device
df["txn_number"] = g.cumcount() + 1
first_use = ~df.duplicated(subset=["customer_id", "device_id"], keep="first")
df["new_device"] = (first_use & (df["txn_number"] > NEW_DEVICE_AFTER_N_TXNS)).astype(int)

# ---------------------------------------------------------------- R6: odd hour
df["hour"] = df["timestamp"].dt.hour
df["odd_hour"] = df["hour"].isin(NIGHT_HOURS).astype(int)

# ---------------------------------------------------------------- risk score
df["risk_score"] = sum(df[r] * w for r, w in WEIGHTS.items())
df["risk_level"] = np.select([df["risk_score"] >= HIGH_AT, df["risk_score"] >= MEDIUM_AT],
                             ["High", "Medium"], default="Low")
df["flagged"] = (df["risk_score"] >= MEDIUM_AT).astype(int)   # sent for manual review

df = df.drop(columns=["log_amount", "ts_sec"])
df.to_csv(ROOT / "data" / "scored_transactions.csv", index=False)

print("Rule hit counts:")
print(df[list(WEIGHTS)].sum().to_string())
print("\nRisk levels:")
print(df["risk_level"].value_counts().to_string())
print(f"\nFlagged for review: {df['flagged'].sum():,} of {len(df):,} ({df['flagged'].mean():.2%})")
