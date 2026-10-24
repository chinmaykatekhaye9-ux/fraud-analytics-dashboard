# Rule-Based Transaction Fraud Analytics and Monitoring

## Project Overview

An end-to-end fraud analytics project that analyzes **50,000 simulated retail banking transactions** to identify suspicious activity using Python, SQL, and six explainable fraud detection rules.

The project covers data generation, data cleaning, SQL analysis, risk scoring, performance evaluation, and dashboard-ready data preparation for Tableau.

> **Data Disclaimer:** This project uses simulated data, not real customer or banking records.

## Objectives

- Identify potentially fraudulent transactions.
- Detect unusual spending patterns and suspicious transaction behavior.
- Build a weighted risk-scoring system to prioritize transactions for review.
- Evaluate detection performance using precision, recall, and F1-score.
- Prepare transaction analytics for fraud monitoring dashboards.

## Tools and Technologies

- **Python:** Pandas, NumPy
- **SQL:** SQLite, CTEs, window functions, aggregations
- **Data Visualization:** Tableau
- **Analytics Techniques:** Z-score, IQR, transaction velocity, location and device anomaly detection

## Methodology

1. **Data Generation:** Generate 50,000 simulated transactions across 2,000 customers, including planted fraud patterns.
2. **Data Cleaning:** Remove duplicate records, standardize city names, handle missing values, and validate the dataset.
3. **SQL Analysis:** Analyze transaction trends, customer activity, and suspicious behavior using aggregations and window functions.
4. **Fraud Detection:** Apply six rules covering unusual amounts, transaction bursts, location changes, unfamiliar devices, and odd-hour activity.
5. **Risk Scoring:** Combine rule weights to classify transactions as Low, Medium, or High risk.
6. **Evaluation:** Compare flagged transactions against simulated fraud labels using classification metrics.
7. **Dashboard Preparation:** Export analysis results into dashboard-ready CSV files for visualization in Tableau.

## Fraud Detection Rules

- **Z-score analysis:** Identify unusually large or small transaction amounts.
- **Interquartile Range (IQR):** Detect statistical outliers.
- **Transaction velocity:** Flag unusually frequent transactions.
- **Location anomalies:** Identify suspicious location changes.
- **Device anomalies:** Detect transactions from unfamiliar devices.
- **Odd-hour monitoring:** Flag transactions occurring during unusual hours.

## Key Results

| Metric | Result |
|---|---:|
| Transactions analyzed | 50,000 |
| Simulated fraud cases | 750 |
| Transactions flagged | 796 |
| Precision | 81.3% |
| Recall | 86.3% |
| F1-score | 0.837 |

*These figures represent the project's reported evaluation results on simulated data. They are not indicative of real-world banking fraud detection performance.*

## Tableau Dashboard

The Tableau workbook is available in the repository:

**[View or download the Tableau packaged workbook (.twbx)](https://public.tableau.com/views/FraudAnalysisDashboard_17928646064980/FraudAnalysisDashboard)**

The workbook includes visualizations covering:

- KPI summary
- Precision and recall by rule
- Flag rate over time
- Transactions flagged by risk level
- Flagged amounts over time
- Transaction activity by hour
- Flag rate by city
- Rules triggered

The workbook's data-source availability and portability should be verified before sharing it as a fully reproducible dashboard.

## Key Insights

- Combining multiple weighted rules can help identify suspicious behavior across different transaction patterns.
- Transaction velocity and location inconsistencies provide useful risk indicators.
- High-value fraud remains an area for further investigation and threshold tuning.
- Fraud detection involves a trade-off between identifying more fraud cases and reducing false positives.

## Limitations and Future Improvements

- Fraud patterns are simulated, so results may not generalize to real-world transactions.
- Customer baselines use historical information from the full dataset rather than strictly time-ordered historical data.
- Future improvements include time-aware detection, threshold tuning, and comparisons with Logistic Regression or Random Forest models.
- Further validation is needed to confirm dashboard portability and reproducibility from a clean setup.

## Skills Demonstrated

- Data Cleaning and Validation
- Exploratory Data Analysis
- Python and Pandas
- SQL Querying and Window Functions
- Rule-Based Anomaly Detection
- Classification Metrics and Evaluation
- Tableau Dashboard Preparation

## How to Run

### Prerequisites

- Python 3 installed
- Git installed

### Setup

Clone the repository and open the project directory:

```bash
git clone https://github.com/chinmaykatekhaye9-ux/fraud-analytics-dashboard.git
cd fraud-analytics-dashboard
```

Create and activate a virtual environment.

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies and run the pipeline:

```bash
python -m pip install -r requirements.txt
python run_all.py
```

The pipeline is intended to generate simulated transaction data, clean records, perform SQL analysis, apply fraud detection rules, evaluate results, and export dashboard-ready datasets.

Actual outputs may vary depending on the implementation and configuration.
