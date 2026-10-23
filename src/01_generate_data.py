"""
STEP 1 - Generate a SIMULATED retail-banking transaction dataset.

Why simulated? Real bank data is confidential. Simulating lets us control the
columns (city, device, channel) and plant KNOWN fraud patterns, so that later we
can measure how well our rules work (precision / recall).

Output: data/raw_transactions.csv
  - exactly 50,000 genuine transaction rows
  - plus a few hundred deliberately "dirty" rows (duplicates, messy city names,
    missing values) so the cleaning step has real work to do.
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
N_TOTAL = 50_000          # final clean row count
N_CUSTOMERS = 2_000
START = pd.Timestamp("2026-01-01")
DAYS = 90                 # Jan 1 - Mar 31, 2026
FRAUD_RATE = 0.015        # ~1.5% of transactions are fraud

rng = np.random.default_rng(SEED)

CITIES = ["Pune", "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
          "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Nagpur"]
CITY_W = np.array([14, 18, 16, 15, 10, 9, 6, 5, 4, 3], dtype=float)
CITY_W /= CITY_W.sum()
CATEGORIES = ["Groceries", "Fuel", "Dining", "Shopping", "Utilities",
              "Travel", "Entertainment", "Healthcare", "Electronics", "Transfer"]
CAT_W = np.array([22, 10, 14, 15, 10, 6, 6, 5, 4, 8], dtype=float)
CAT_W /= CAT_W.sum()
CHANNELS = ["UPI", "Card", "NetBanking", "ATM", "POS"]
CHAN_W = np.array([40, 25, 10, 8, 17], dtype=float)
CHAN_W /= CHAN_W.sum()

# ---------------------------------------------------------------- customers
customers = pd.DataFrame({
    "customer_id": [f"C{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)],
    "home_city": rng.choice(CITIES, N_CUSTOMERS, p=CITY_W),
    # typical spend level differs per customer (median amount between ~150 and ~3,000)
    "mu": rng.uniform(np.log(150), np.log(3000), N_CUSTOMERS),
    "device_main": [f"D{str(i).zfill(5)}A" for i in range(1, N_CUSTOMERS + 1)],
    "device_alt": [f"D{str(i).zfill(5)}B" for i in range(1, N_CUSTOMERS + 1)],
}).set_index("customer_id")

n_fraud = int(N_TOTAL * FRAUD_RATE)
n_normal = N_TOTAL - n_fraud

# ---------------------------------------------------------------- normal txns
def random_times(n):
    """Random timestamps in the 90-day window, mostly daytime/evening."""
    day = rng.integers(0, DAYS, n)
    hour = rng.choice(24, n, p=_hour_probs())
    minute = rng.integers(0, 60, n)
    second = rng.integers(0, 60, n)
    return (START + pd.to_timedelta(day, unit="D") + pd.to_timedelta(hour, unit="h")
            + pd.to_timedelta(minute, unit="m") + pd.to_timedelta(second, unit="s"))

def _hour_probs():
    w = np.array([1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 8, 8,
                  8, 8, 7, 7, 8, 9, 9, 8, 6, 4, 3, 2], dtype=float)
    return w / w.sum()

cust_ids = customers.index.to_numpy()
cid = rng.choice(cust_ids, n_normal)
c = customers.loc[cid]

normal = pd.DataFrame({
    "customer_id": cid,
    "timestamp": random_times(n_normal),
    "amount": np.round(np.exp(rng.normal(c["mu"].to_numpy(), 0.6)), 2),
    "merchant_category": rng.choice(CATEGORIES, n_normal, p=CAT_W),
    "channel": rng.choice(CHANNELS, n_normal, p=CHAN_W),
    "city": c["home_city"].to_numpy(),
    "device_id": c["device_main"].to_numpy(),
    "is_fraud": 0,
    "fraud_type": "none",
})
# genuine variation: ~3% of normal txns are made while travelling (another city)
trav = rng.random(n_normal) < 0.03
normal.loc[trav, "city"] = rng.choice(CITIES, trav.sum())
# genuine variation: ~4% use the customer's second device (e.g. a tablet)
alt = rng.random(n_normal) < 0.04
normal.loc[alt, "device_id"] = c["device_alt"].to_numpy()[alt]
# genuine "shopping sessions": ~1.5% of normal txns spawn 1-2 extra txns within 15 mins
sess = normal.sample(frac=0.015, random_state=SEED).copy()
extra = []
for _ in range(2):
    e = sess.copy()
    e["timestamp"] = e["timestamp"] + pd.to_timedelta(rng.integers(1, 15, len(e)), unit="m")
    e["amount"] = np.round(e["amount"] * rng.uniform(0.3, 1.2, len(e)), 2)
    extra.append(e.sample(frac=0.6, random_state=int(rng.integers(0, 10_000))))
normal = (pd.concat([normal] + extra, ignore_index=True)
          .sample(n_normal, random_state=SEED).reset_index(drop=True))  # keep exact count

# ---------------------------------------------------------------- fraud txns
# Four patterns, each planted deliberately.
n_a = int(n_fraud * 0.30)               # A: unusually high value
n_b = int(n_fraud * 0.30)               # B: velocity burst
n_c = int(n_fraud * 0.25)               # C: impossible location jump
n_d = n_fraud - n_a - n_b - n_c         # D: new device at night, big amount
fraud_parts = []

# A) unusually high-value
ca = rng.choice(cust_ids, n_a)
fa = pd.DataFrame({
    "customer_id": ca, "timestamp": random_times(n_a),
    "amount": np.round(np.exp(customers.loc[ca, "mu"].to_numpy()) * rng.uniform(8, 25, n_a), 2),
    "merchant_category": rng.choice(["Electronics", "Travel", "Transfer", "Shopping"], n_a),
    "channel": rng.choice(["Card", "NetBanking", "UPI"], n_a),
    "city": customers.loc[ca, "home_city"].to_numpy(),
    "device_id": customers.loc[ca, "device_main"].to_numpy(),
    "fraud_type": "high_value"})
fraud_parts.append(fa)

# B) velocity bursts: 5-7 txns inside ~8 minutes
rows, left = [], n_b
while left > 0:
    k = min(int(rng.integers(5, 8)), left)
    cu = rng.choice(cust_ids)
    t0 = random_times(1)[0]
    for j in range(k):
        rows.append({
            "customer_id": cu,
            "timestamp": t0 + pd.Timedelta(seconds=int(rng.integers(0, 480))),
            "amount": round(float(np.exp(customers.loc[cu, "mu"]) * rng.uniform(1.5, 4)), 2),
            "merchant_category": rng.choice(["Electronics", "Shopping", "Transfer"]),
            "channel": rng.choice(["Card", "UPI"]),
            "city": customers.loc[cu, "home_city"],
            "device_id": customers.loc[cu, "device_main"],
            "fraud_type": "velocity"})
    left -= k
fraud_parts.append(pd.DataFrame(rows))

# C) impossible location jump: far-away city within 20-90 mins of a normal txn
anchor = normal.sample(n_c, random_state=7).copy()
fc = anchor.copy()
fc["timestamp"] = anchor["timestamp"] + pd.to_timedelta(rng.integers(20, 90, n_c), unit="m")
fc["city"] = [rng.choice([x for x in CITIES if x != h]) for h in anchor["city"]]
fc["amount"] = np.round(anchor["amount"] * rng.uniform(1.5, 5, n_c), 2)
fc["merchant_category"] = rng.choice(["Electronics", "Shopping", "Travel"], n_c)
fc["fraud_type"] = "location_jump"
fraud_parts.append(fc[["customer_id", "timestamp", "amount", "merchant_category",
                       "channel", "city", "device_id", "fraud_type"]])

# D) brand-new device, 1-4 AM, large amount
cd = rng.choice(cust_ids, n_d)
day = rng.integers(0, DAYS, n_d)
fd = pd.DataFrame({
    "customer_id": cd,
    "timestamp": START + pd.to_timedelta(day, unit="D") + pd.to_timedelta(rng.integers(60, 290, n_d), unit="m"),
    "amount": np.round(np.exp(customers.loc[cd, "mu"].to_numpy()) * rng.uniform(3, 10, n_d), 2),
    "merchant_category": rng.choice(["Electronics", "Transfer", "Travel"], n_d),
    "channel": rng.choice(["NetBanking", "UPI"], n_d),
    "city": customers.loc[cd, "home_city"].to_numpy(),
    "device_id": [f"D{rng.integers(90000, 99999)}X" for _ in range(n_d)],
    "fraud_type": "new_device_night"})
fraud_parts.append(fd)

fraud = pd.concat(fraud_parts, ignore_index=True)
fraud["is_fraud"] = 1
fraud = fraud.iloc[:n_fraud]  # exact count

# ---------------------------------------------------------------- combine
df = pd.concat([normal, fraud], ignore_index=True)
df = df.sort_values("timestamp").reset_index(drop=True)
df.insert(0, "txn_id", [f"T{str(i).zfill(6)}" for i in range(1, len(df) + 1)])
assert len(df) == N_TOTAL, len(df)

# ---------------------------------------------------------------- make it dirty
dirty = df.copy()
dirty["timestamp"] = dirty["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
# 1) exact duplicate rows (same txn_id appearing twice) ~0.6%
dups = dirty.sample(frac=0.006, random_state=1)
# 2) messy city text (lower-case / trailing spaces / UPPER)
idx = dirty.sample(frac=0.04, random_state=2).index
dirty.loc[idx, "city"] = dirty.loc[idx, "city"].map(
    lambda s: rng.choice([s.lower(), s.upper(), s + " ", " " + s]))
# 3) missing values
dirty.loc[dirty.sample(frac=0.008, random_state=3).index, "merchant_category"] = np.nan
dirty.loc[dirty.sample(frac=0.004, random_state=4).index, "city"] = np.nan
raw = pd.concat([dirty, dups], ignore_index=True).sample(frac=1, random_state=5).reset_index(drop=True)

out = Path(__file__).resolve().parent.parent / "data"
out.mkdir(exist_ok=True)
raw.to_csv(out / "raw_transactions.csv", index=False)
print(f"raw rows written      : {len(raw):,}  (50,000 genuine + {len(dups)} duplicates)")
print(f"planted fraud rows    : {int(df['is_fraud'].sum()):,}  ({df['is_fraud'].mean():.2%})")
print(df.loc[df.is_fraud == 1, "fraud_type"].value_counts().to_string())
