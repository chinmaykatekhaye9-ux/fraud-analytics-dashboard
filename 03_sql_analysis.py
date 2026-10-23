"""
STEP 3 - Load clean data into SQLite and run the SQL analysis (sql/analysis.sql).

Input : data/clean_transactions.csv
Output: data/fraud.db (SQLite database) and output/sql_<name>.csv for each query
"""
import re
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "clean_transactions.csv", parse_dates=["timestamp"])
# seconds since 1970 - lets SQL do time-window maths easily
df["ts_epoch"] = (df["timestamp"] - pd.Timestamp("1970-01-01")).dt.total_seconds().astype("int64")
df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

db_path = ROOT / "data" / "fraud.db"
if db_path.exists():
    db_path.unlink()
con = sqlite3.connect(db_path)
df.to_sql("transactions", con, index=False)
con.execute("CREATE INDEX idx_cust_time ON transactions(customer_id, ts_epoch)")
print(f"Loaded {len(df):,} rows into {db_path.name}\n")

sql_text = (ROOT / "sql" / "analysis.sql").read_text()
blocks = re.split(r"^-- name:\s*(\w+)\s*$", sql_text, flags=re.M)[1:]
for name, body in zip(blocks[0::2], blocks[1::2]):
    result = pd.read_sql_query(body, con)
    result.to_csv(ROOT / "output" / f"sql_{name}.csv", index=False)
    print(f"[{name}] -> {len(result)} rows")
    print(result.head(3).to_string(index=False), "\n")
con.close()
