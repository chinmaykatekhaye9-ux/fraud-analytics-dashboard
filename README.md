# Rule-Based Transaction Fraud Analytics and Monitoring

## Project Overview

An end-to-end fraud analytics project that analyzes **50,000 simulated retail banking transactions** to identify suspicious activity using Python, SQL, and six explainable fraud detection rules.

The project covers data generation, data cleaning, SQL analysis, risk scoring, performance evaluation, and preparation of dashboard-ready datasets for Tableau.

> **Data Disclaimer:** This project uses simulated data, not real customer or banking records.

## Objectives

- Identify potentially fraudulent transactions.
- Detect unusual spending patterns and suspicious transaction behavior.
- Build a weighted risk-scoring system to prioritize transactions for review.
- Evaluate fraud detection performance using precision, recall, and F1-score.
- Prepare data for fraud monitoring dashboards.

## Tools and Technologies

- **Python:** Pandas, NumPy
- **SQL:** SQLite, CTEs, window functions, aggregations
- **Data Visualization:** Tableau Public (dashboard planned)
- **Analytics Techniques:** Z-Score, IQR, transaction velocity, location and device anomaly detection

## Methodology

1. **Data Generation:** Simulated 50,000 transactions across 2,000 customers, including planted fraud patterns.
2. **Data Cleaning:** Removed duplicate records, standardized city names, handled missing values, and validated the dataset.
3. **SQL Analysis:** Analyzed transaction trends, customer activity, and suspicious behavior using aggregations and window functions.
4. **Fraud Detection:** Implemented six rules covering unusual amounts, transaction bursts, location changes, unfamiliar devices, and odd-hour activity.
5. **Risk Scoring:** Combined rule weights to classify transactions as Low, Medium, or High risk.
6. **Evaluation:** Compared flagged transactions against simulated fraud labels using classification metrics.
7. **Dashboard Preparation:** Exported analysis results into Tableau-ready CSV files.

## Fraud Detection Rules

- Z-Score analysis of transaction amounts
- Interquartile Range (IQR) anomaly detection
- High transaction velocity
- Unusual location changes
- New device detection
- Odd-hour transaction monitoring

## Key Results

| Metric | Result |
|---|---:|
| Clean transactions analyzed | 50,000 |
| Simulated fraud cases | 750 |
| Transactions flagged | 796 |
| Precision | 81.3% |
| Recall | 86.3% |
| F1-score | 0.837 |

*Results are from the simulated dataset and the project's evaluation run. They should not be interpreted as real-world banking fraud detection performance.*

## Key Insights

- Combining multiple weighted rules performed better than relying on individual rules alone.
- Transaction velocity and location inconsistencies helped identify suspicious behavior.
- High-value fraud was a weaker detection area, providing an opportunity to improve rule weights and test alternative models.
- The evaluation demonstrates the trade-off between identifying more fraud cases and reducing false positives.

## Limitations and Future Improvements

- Fraud patterns were simulated, so results may be optimistic.
- Customer baselines use historical information from the full dataset rather than strictly time-ordered historical data.
- Future improvements include time-aware detection, threshold tuning, and comparison with Logistic Regression or Random Forest models.
- A Tableau Public dashboard will be added after development and publication.

## Skills Demonstrated

- Data Cleaning and Validation
- Exploratory Data Analysis
- Python and Pandas
- SQL Querying and Window Functions
- Rule-Based Anomaly Detection
- Classification Metrics and Model Evaluation
- Data Visualization and Dashboard Preparation

## How to Run

```bash
pip install -r requirements.txt
python run_all.py
```

The pipeline generates simulated transaction data, cleans the records, performs SQL analysis, applies fraud detection rules, evaluates results, and exports dashboard-ready datasets.
