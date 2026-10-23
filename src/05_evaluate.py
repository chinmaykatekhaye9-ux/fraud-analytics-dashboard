"""
STEP 5 - Evaluate the rules against the planted fraud labels.

Because we generated the data, we KNOW which rows are fraud (is_fraud). That lets us
measure how good the rules are:
  precision = of the txns we flagged, how many were really fraud?
  recall    = of all real fraud, how much did we catch?
  F1        = balance of the two

Input : data/scored_transactions.csv
Output: output/evaluation_report.txt, output/threshold_tradeoff.csv, output/rule_performance.csv
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "scored_transactions.csv")
RULES = ["zscore_amount", "iqr_amount", "velocity", "location_jump", "new_device", "odd_hour"]

def metrics(pred, actual):
    tp = int(((pred == 1) & (actual == 1)).sum())
    fp = int(((pred == 1) & (actual == 0)).sum())
    fn = int(((pred == 0) & (actual == 1)).sum())
    tn = int(((pred == 0) & (actual == 0)).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return dict(TP=tp, FP=fp, FN=fn, TN=tn, precision=round(p, 3), recall=round(r, 3), F1=round(f1, 3))

y = df["is_fraud"]
lines = []
def out(s=""):
    print(s)
    lines.append(s)

# 1) overall result at the chosen threshold (risk_score >= 3)
m = metrics(df["flagged"], y)
out("=== OVERALL (flag if risk_score >= 3) ===")
out(f"Transactions: {len(df):,} | planted fraud: {int(y.sum()):,}")
out(f"Confusion matrix: TP={m['TP']}  FP={m['FP']}  FN={m['FN']}  TN={m['TN']}")
out(f"Precision={m['precision']:.1%}  Recall={m['recall']:.1%}  F1={m['F1']:.3f}")

# 2) threshold trade-off
rows = []
for t in range(1, 8):
    rows.append({"threshold": t, **metrics((df["risk_score"] >= t).astype(int), y)})
trade = pd.DataFrame(rows)
trade.to_csv(ROOT / "output" / "threshold_tradeoff.csv", index=False)
out("\n=== THRESHOLD TRADE-OFF (lower threshold = catch more, more false alarms) ===")
out(trade.to_string(index=False))

# 3) each rule on its own
rr = pd.DataFrame([{"rule": r, "hits": int(df[r].sum()), **metrics(df[r], y)} for r in RULES])
rr.to_csv(ROOT / "output" / "rule_performance.csv", index=False)
out("\n=== EACH RULE ON ITS OWN ===")
out(rr[["rule", "hits", "TP", "FP", "precision", "recall"]].to_string(index=False))

# 4) recall by fraud pattern
out("\n=== RECALL BY FRAUD PATTERN (flagged at score >= 3) ===")
fr = df[df["is_fraud"] == 1]
by = fr.groupby("fraud_type")["flagged"].agg(total="count", caught="sum")
by["recall"] = (by["caught"] / by["total"]).round(3)
out(by.to_string())

(ROOT / "output" / "evaluation_report.txt").write_text("\n".join(lines) + "\n")
