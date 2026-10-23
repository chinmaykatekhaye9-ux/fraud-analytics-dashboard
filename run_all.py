"""Run the whole pipeline: python run_all.py"""
import subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parent
for step in ["01_generate_data", "02_clean_data", "03_sql_analysis",
             "04_fraud_rules", "05_evaluate", "06_export_for_tableau"]:
    print(f"\n{'=' * 8} {step} {'=' * 8}")
    subprocess.run([sys.executable, str(root / "src" / f"{step}.py")], check=True)
print("\nDone. Open the output/tableau_*.csv files in Tableau Public.")
