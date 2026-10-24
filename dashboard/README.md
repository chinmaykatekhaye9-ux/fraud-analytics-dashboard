# Tableau Dashboard

This folder contains the Tableau dashboard for the Fraud Analytics project.

**Live version:** [Tableau Public](https://public.tableau.com/views/FraudAnalysisDashboard_17928646064980/FraudAnalysisDashboard)

The dashboard shows transaction risk, flagged transaction trends, risk levels, city-wise flag rates, rule performance, and key fraud detection metrics.

## Files

- `Fraud Analysis Dashboard.twbx` - packaged Tableau workbook.
- `dashboard_overview.png` - screenshot of the dashboard.

## Opening the workbook locally

The dashboard reads the CSV files in `output/` (`tableau_*.csv`, `rule_performance.csv`). Run `python run_all.py` from the project root first, then open the workbook in Tableau and re-point any missing data source to the generated `output/` folder.
