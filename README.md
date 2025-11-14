# Risk-Dashboard

This project builds a structured pipeline for collecting market data, cleaning it, storing it, and analysing it through a dashboard. It supports both intraday (hourly) and daily OHLCV data and applies downstream processing for returns, volatility, simulations and strategy evaluation.
It aims to provide users an understanding of the risk of their assets and the nature of potential future returns.

⸻

Project Structure

risk-dashboard/
│
├── data/                 # API clients (TwelveData, Treasury, etc)
├── db/                   # Database IO layer
├── jobs/                 # Scheduled tasks (hourly refresh, backfills)
├── notebooks/            # Exploratory work
├── app/                  # Dashboard application (e.g. Streamlit)
└── README.md


Data Pipeline Overview

1. Data Ingestion
	•	Hourly price data retrieved from TwelveData.
	•	Daily price data retrieved separately for backfill.
	•	Treasury yield data retrieved from FiscalData.
	•	All raw data written to bronze schema.

2. SQL Cleaning Layer
	•	Raw data validated with integrity checks.
	•	Cleaned data inserted into clean schema.
	•	Removes invalid OHLC values, null timestamps and duplicate entries.

3. Python Processing Layer

Data loaded from clean schema and enriched in Python:
	•	Convert timestamps to UTC.
	•	Split hourly and daily datasets.
	•	Fix timezone-related irregularities.
	•	Add computed columns such as:
	•	returns
	•	log returns
	•	rolling volatility
	•	moving averages
	•	drawdowns

No calculated fields are stored in SQL. All feature generation happens in Python.

⸻

4. Analysis Modules

4.1 Time Series Analysis
	•	Daily and intraday volatility
	•	Rolling Sharpe ratio
	•	Correlation matrices
	•	Drawdown curves

4.2 Monte Carlo Simulation
	•	GBM (Geometric Brownian Motion)
	•	Heavy-tailed distributions
	•	Volatility-adjusted paths
	•	Optional regime-switching simulation

4.3 Strategy Testing
	•	Apply trading rules to historical data
	•	Compare against buy-and-hold baseline
	•	Evaluate performance using:
	•	cumulative return
	•	volatility
	•	max drawdown
	•	Sharpe ratio

⸻

Scheduler Jobs

refresh.py

Runs hourly:
	1.	Pull latest hourly prices.
	2.	Pull latest Treasury yields.
	3.	Write to bronze.
	4.	Apply SQL cleaning into clean.

backfill_daily.py

Runs on demand:
	1.	Download 2-year daily history.
	2.	Load into bronze.
	3.	Clean into clean.

⸻

Technology Stack
	•	Python
pandas, numpy, plotly, SQLAlchemy
	•	Database
PostgreSQL with bronze and clean schemas
	•	Scheduler
APScheduler
	•	Dashboard
Streamlit (or similar)

⸻

Next Steps
	•	Build factor features (momentum, volatility regimes)
	•	Build Monte Carlo simulation engine
	•	Add scenario shocks and stress tests
	•	Implement simple trading strategies
	•	Deploy dashboard
