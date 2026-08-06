# Portfolio Manager

Intelligent Local Investment Platform

A full-stack, local-only, ML-powered portfolio management system built with **FastAPI**, **MySQL**, **Yahoo Finance**, **Machine Learning**, **Recommender Systems**, **CSV Import/Export**, and a **Dashboard UI**.

This project runs entirely on localhost — no cloud, no external hosting.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start (Windows)](#quick-start-windows)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Tests](#tests)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Machine Learning Models](#machine-learning-models)
- [Recommender System](#recommender-system)
- [Automation](#automation)
- [Risk & Analytics](#risk--analytics)
- [Portfolio Optimization](#portfolio-optimization)
- [Logging & Monitoring](#logging--monitoring)
- [Recent Changes](#recent-changes)
- [Future Enhancements](#future-enhancements)

---

## Overview

The **Portfolio Manager** is a complete local backend + ML + analytics platform for managing financial portfolios, tracking assets, ingesting market data, computing performance, and generating intelligent insights.

---

## Quick Start (Windows)

Run these in order from the `portfolio_manager/` folder:

```powershell
# 1. Start MySQL Server (services.msc -> MySQL -> Start, or XAMPP/WAMP)

# 2. Create the database + tables (no mysql CLI needed)
python scripts/run_init_db.py

# 3. Verify DB connection
python -c "from app.database.connection import get_db; c = get_db(); print('Connected:', c.is_connected()); c.close()"

# 4. Seed sample portfolios + BUY transactions
python scripts/seed_data.py

# 5. (Optional) Ingest/refresh price history from Yahoo Finance
python scripts/daily_ingestion.py

# 6. Start the API
uvicorn app.main:app --reload
```

Then, in a **second terminal**, check the recommenders:

```powershell
# Asset-based
curl.exe "http://127.0.0.1:8000/recommend/content/AAPL?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/trending?limit=5"

# Portfolio-based (swap the portfolio id for one that has holdings)
curl.exe "http://127.0.0.1:8000/recommend/collaborative/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/hybrid/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/correlation/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/gaps/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/similar-portfolios/3?limit=5"
```

Interactive testing is also available at `http://localhost:8000/docs` → **Recommendations**.

---

## Architecture

### Backend

FastAPI modular service-based architecture with the following layers:

- **Routes** — HTTP endpoint definitions
- **Services** — Business logic
- **Database** — MySQL connection, models, and schemas
- **Ingestion** — Market data fetching (Yahoo Finance, Finnhub, Alpha Vantage)
- **Utils** — Logging, exceptions, and helpers

### Database

MySQL relational schema with tables for portfolios, assets, transactions, price history, performance metrics, market data cache, and audit logs.

### Market Data

Yahoo Finance (`yfinance`) for live + historical data, with support for Finnhub and Alpha Vantage APIs.

### ML Layer

Local Python ML models for price prediction and risk analytics.

### Recommender Engine

Local content-based + collaborative filtering for asset recommendations.

### Automation

Local scheduler (APScheduler or cron) for daily ingestion, valuation, and risk metric updates.

---

## Features

- Portfolio CRUD
- Asset CRUD
- Portfolio Item Management
- BUY/SELL/DIVIDEND Transactions
- Historical Price Ingestion (Yahoo Finance, Finnhub, Alpha Vantage)
- Market Data Caching
- External API Logging
- Audit Logging
- Portfolio Performance Tracking
- User Authentication (JWT)
- Role-Based Access Control
- CSV Import/Export
- ML Price Prediction (LSTM, GRU, Prophet, ARIMA)
- Asset Recommendation Engine
- Risk Modeling (VaR, volatility, drawdown)
- Efficient Frontier Optimization
- Dashboard Visualization
- Daily Automated Ingestion

---

## Tech Stack

| Component        | Technology                          |
| ---------------- | ----------------------------------- |
| Backend          | FastAPI                             |
| Database         | MySQL                               |
| Market Data      | Yahoo Finance (yfinance), Finnhub, Alpha Vantage |
| ML Models        | TensorFlow / Prophet / Scikit-Learn |
| Recommender      | Scikit-Learn                        |
| Dashboard        | React / Vue / Chart.js / Plotly     |
| Automation       | APScheduler / Cron                  |
| Logging          | Custom audit + API logs             |

---

## Project Structure

```
portfolio_manager/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── portfolio_routes.py
│   │   ├── asset_routes.py
│   │   ├── price_routes.py
│   │   ├── transaction_routes.py
│   │   ├── asset_type_routes.py
│   │   ├── asset_transaction_routes.py
│   │   ├── performance_routes.py
│   │   ├── csv_routes.py
│   │   ├── ml_routes.py
│   │   ├── recommender_routes.py
│   │   ├── risk_routes.py
│   │   ├── optimization_routes.py
│   │   └── scalar_ui.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── portfolio_service.py
│   │   ├── asset_service.py
│   │   ├── price_service.py
│   │   ├── transaction_service.py
│   │   ├── asset_type_service.py
│   │   ├── asset_transaction_service.py
│   │   ├── portfolio_performance_service.py
│   │   ├── market_cache_service.py
│   │   ├── api_logging_service.py
│   │   ├── audit_service.py
│   │   ├── csv_service.py
│   │   ├── ml_service.py
│   │   ├── ml_service_enhanced.py
│   │   ├── recommender_service.py
│   │   ├── risk_service.py
│   │   ├── optimization_service.py
│   │   ├── data_provider.py
│   │   └── portfolio_service.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   │
│   ├── ingestion/
│   │   ├── fetch_assets.py
│   │   ├── fetch_prices.py
│   │   └── __init__.py
│   │
│   ├── tests/
│   │   ├── test_assets.py
│   │   ├── test_portfolio.py
│   │   ├── test_prices.py
│   │   ├── test_recommender.py
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── exceptions.py
│       └── __init__.py
│
├── scripts/
│   ├── daily_ingestion.py
│   ├── export_csv.py
│   ├── import_csv.py
│   ├── init_db.sql
│   ├── run_init_db.py
│   └── seed_data.py
│
├── .env
├── .gitignore
├── requirements.txt
├── flowchart.PNG
├── IMPLEMENTATION_SUMMARY.md
├── LSTM_QUICKSTART.md
├── LSTM_TUNING.md
├── ML_ENHANCEMENTS.md
├── populate_prices.py
├── QUICK_REFERENCE.md
├── test_lstm_prediction.py
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip

### Setup

```bash
# Navigate to the project directory
cd portfolio_manager

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the `portfolio_manager/` directory:

```
DB_HOST=localhost
DB_USER=root
DB_PASS=yourpassword
DB_NAME=portfolio_manager

JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key
```

---

## Database Setup

> If the `mysql` command-line client is **not** installed or not on your `PATH`, use the bundled Python runner instead of `mysql < scripts/init_db.sql`.

### 1. Make sure MySQL Server is running

- **Windows service:** run `services.msc`, find the MySQL service, and **Start** it (or use the XAMPP/WAMP control panel).

### 2. Create the database and tables

```bash
python scripts/run_init_db.py
```

Expected output: `Executed N statements from init_db.sql`.

### 3. Verify the connection

```bash
python -c "from app.database.connection import get_db; c = get_db(); print('Connected:', c.is_connected()); c.close()"
```

Output: `Connected: True`.

### 4. Seed sample portfolios + transactions (for recommenders)

```bash
python scripts/seed_data.py
```

This creates two portfolios and adds BUY transactions for `AAPL`, `MSFT`, `GOOGL`, and `TSLA`. (Run all scripts from the `portfolio_manager/` root, **not** from inside `scripts/`.)

### 5. Ingest price history (for similarity / momentum / correlation)

```bash
python scripts/daily_ingestion.py
```

> Yahoo Finance may return `429 Too Many Requests` under rate limits — that is a provider limit, not a bug. The recommender reads the price data already stored in the database.

---

## Tests

The recommender tests use an in-memory fake database, so they run without MySQL:

```bash
python -m pytest app/tests -q
```

---

## Running the Application

Start the API **after** the database is set up and seeded:

```bash
uvicorn app.main:app --reload
```

API available at:

- `http://localhost:8000`
- `/docs` — Swagger UI
- `/redoc` — ReDoc
- `/scalar` — Scalar API Console

---

## API Endpoints

### Portfolios

- `GET /portfolios/`
- `POST /portfolios/`

### Assets

- `GET /assets/`
- `GET /assets/{ticker}`
- `POST /assets/{ticker}`

### Prices (Yahoo Finance + DB)

- `GET /prices/{ticker}`
- `POST /prices/{ticker}`

### Transactions

- `GET /transactions/{portfolio_id}`
- `POST /transactions/{portfolio_id}`

### Asset Types

- `GET /asset-types/`
- `POST /asset-types/`

### Asset Transactions

- `GET /asset-transactions/{asset_id}`
- `POST /asset-transactions/{asset_id}`

### Portfolio Performance

- `GET /performance/{portfolio_id}`
- `POST /performance/{portfolio_id}`

### CSV

- `POST /csv/import/{type}`
- `GET /csv/export/{type}`

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

---

## Machine Learning Models

All models run **locally**. Prediction endpoints live under `/ml` and share a common response shape: `current_price`, `predictions[]` with `day`, `predicted_price`, `upper_bound`, `lower_bound`, and `confidence_level` (95%).

### Price Prediction — `/ml/predict/{ticker}?method=...&days=7`

| Method | What it is | When to use | Data needed |
| ------ | ---------- | ----------- | ----------- |
| `lstm` | **LSTM neural network** | Best short-term accuracy | 60+ days (uses 504) |
| `prophet` | **Facebook Prophet** seasonal forecasting | Trends & seasonality, missing data | 30+ days |
| `linear` | **Linear regression** baseline | Fast sanity check | 5+ days |
| `ensemble` | **Average of LSTM + Prophet + Linear** | Most robust, never fails if one fails | any |

**LSTM (default)** — `predict_price_lstm`
- Uses **2 years** of history (504 days), normalized with `MinMaxScaler`.
- **30-day lookback window** — each prediction is based on the previous 30 closes.
- Architecture: `LSTM(50) → Dropout(0.2) → LSTM(50) → Dropout(0.2) → Dense(25) → Dense(1)`, trained with **Adam** (lr 0.001), MSE loss, 50 epochs, batch 32, and **early stopping** (patience 5) on an 80/20 train/test split.
- Produces **95% confidence intervals** from the test-set residuals.
- Falls back to Prophet if TensorFlow is unavailable, and to linear regression if Prophet fails.

**Prophet** — `predict_price_prophet`
- Facebook Prophet with yearly + weekly seasonality and 95% intervals (`changepoint_prior_scale=0.05`). Handles gaps and holidays well.

**Linear regression** — `predict_price_linear`
- Simple least-squares trend line over the last 60 days. Fast baseline; used as a fallback.

**Ensemble** — `predict_price_ensemble`
- Averages the day-by-day predictions (and confidence bounds) of all models that succeeded, so a single failing model can't break the forecast.

### Asset Classification — `/ml/classify/{ticker}`

Labels an asset into:

- **risk_class** — `low-risk` (< 15% vol), `moderate-risk` (< 25%), `high-risk` (>= 25%)
- **income_class** — `dividend` (yield > 3%), `value` (low vol), `growth` (otherwise)

> The `asset` table currently has no volatility/dividend columns, so the classifier uses the price-based volatility when available and sensible defaults otherwise.

### Portfolio Health Score — `/ml/health/{portfolio_id}`

Blends diversification and volatility into a 0–100 score:

- `diversification_score` = number of sectors held / 5 × 100 (capped at 100)
- `volatility_score` = `max(100 − volatility × 200, 0)`
- `overall_health_score` = average of both

### Risk Models — `/risk/*`

| Endpoint | Formula / logic |
| -------- | --------------- |
| `/risk/volatility/{ticker}` | Annualized volatility = std(returns) × √252 |
| `/risk/sharpe/{portfolio_id}` | (annual return − risk-free) / annual volatility |
| `/risk/var/{portfolio_id}` | Value-at-Risk = (1−confidence) percentile of returns × current value (default 95%) |
| `/risk/max-drawdown/{portfolio_id}` | Largest peak-to-trough decline of portfolio value |
| `/risk/correlation/{portfolio_id}` | Return correlation matrix of held assets |

### Optimization Models — `/optimize/*`

| Endpoint | Model |
| -------- | ----- |
| `/optimize/frontier/{portfolio_id}` | **Efficient frontier** via Monte Carlo — samples 10,000 random weight vectors, plots risk vs return, keeps the highest-Sharpe result |
| `/optimize/optimal/{portfolio_id}` | **Maximum-Sharpe allocation** (top point of the frontier) |
| `/optimize/risk-parity/{portfolio_id}` | **Inverse-volatility weighting** so each asset contributes equal risk |
| `/optimize/monte-carlo/{portfolio_id}` | Simulates 1,000 future value paths (drift 5%, volatility from holdings) and reports expected/min/max final value and 5th/95th percentiles |

---

## Recommender System

The recommender generates asset suggestions from two real signals:

- **Feature vectors** — each asset is described by one-hot sector/industry plus volatility, 20-day and 60-day momentum computed from `price_history`.
- **Interaction matrix** — `portfolio × asset` holdings built from `transaction` records.

### Endpoints (prefix `/recommend`)

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/recommend/content/{ticker}` | Assets similar to a ticker (cosine similarity over features) |
| GET | `/recommend/trending` | Rank assets by momentum + investor popularity |
| GET | `/recommend/collaborative/{portfolio_id}` | What similar portfolios hold |
| GET | `/recommend/hybrid/{portfolio_id}` | Weighted blend of content + collaborative |
| GET | `/recommend/correlation/{portfolio_id}` | Assets least correlated with current holdings |
| GET | `/recommend/diversify/{portfolio_id}` | Alias of the correlation method |
| GET | `/recommend/gaps/{portfolio_id}` | Best asset in each unrepresented sector |
| GET | `/recommend/similar-portfolios/{portfolio_id}` | Most similar portfolios by holding overlap |

### How each method works

- **Content-based** — cosine similarity between the target asset vector and every other asset; returns the top-`limit` by similarity score, sorted descending.
- **Collaborative filtering** — builds a `portfolio × asset` matrix, computes cosine similarity between portfolios, and recommends assets held by similar portfolios that the target does **not** hold.
- **Hybrid** — combines the content similarity to current holdings with the collaborative score using `content_weight` (default `0.5`).
- **Correlation / diversification** — computes each candidate's return correlation with the portfolio and suggests the least-correlated assets (true risk reduction).
- **Trending** — ranks assets by momentum and cross-portfolio popularity.
- **Gap completion** — recommends the strongest-momentum asset from each sector the portfolio does not cover.
- **Similar portfolios** — ranks other portfolios by holding overlap similarity.

### Example request & response

```
GET /recommend/content/AAPL?limit=5
```

```json
{
  "input_asset": "AAPL",
  "method": "content_based_cosine",
  "recommendations": [
    {
      "ticker": "MSFT",
      "name": "Microsoft Corp",
      "similarity_score": 0.8993,
      "reason": "Shared profile: Technology, Unknown (similar to AAPL, sector Technology)"
    },
    {
      "ticker": "TSLA",
      "name": "Tesla Inc",
      "similarity_score": 0.2887,
      "reason": "Shared profile: Technology, Unknown (similar to AAPL, sector Automobiles)"
    }
  ]
}
```

If a portfolio has no holdings, an error object is returned instead:

```json
{"error": "Portfolio has no holdings"}
```

### Checking the recommendations

With the API running, use `curl.exe` (Windows) in a second terminal:

```bash
# Asset-based
curl.exe "http://127.0.0.1:8000/recommend/content/AAPL?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/trending?limit=5"

# Portfolio-based (use a portfolio id that has holdings, e.g. 3)
curl.exe "http://127.0.0.1:8000/recommend/collaborative/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/hybrid/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/correlation/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/gaps/3?limit=5"
curl.exe "http://127.0.0.1:8000/recommend/similar-portfolios/3?limit=5"
```

You can also explore them interactively at `http://localhost:8000/docs` → **Recommendations**.

---

## Automation

### Daily Price Ingestion

Fetches OHLCV via Yahoo Finance.

### Daily Portfolio Valuation

Computes:

- total value
- daily change
- daily % change

### Daily Risk Metrics

Updates:

- volatility
- beta
- Sharpe ratio

---

## Risk & Analytics

Includes:

- Sharpe Ratio
- Beta
- Volatility
- VaR
- Correlation Matrix
- Covariance Matrix
- Drawdown Analysis

---

## Portfolio Optimization

- Efficient Frontier
- Modern Portfolio Theory (MPT)
- Monte Carlo Simulation
- Optimal Asset Allocation
- Risk Parity

---

## Logging & Monitoring

### Audit Log

Tracks:

- entity changes
- updates
- deletes

### External API Request Log

Tracks:

- request time
- response time
- status

### Market Data Cache

Stores raw JSON from Yahoo Finance.

---

## Recent Changes

### Enhanced Recommender System

Rebuilt `app/services/recommender_service.py` from 3 naive methods into a proper engine:

- **Content-based v2** — cosine-similarity over feature vectors (sector, industry, volatility, 20d/60d momentum) instead of exact-sector equality.
- **Real collaborative filtering** — `portfolio × asset` interaction matrix and cosine similarity between portfolios. Replaces the old query that was mislabeled as CF (it conflated `user_id`/`portfolio_id` and was really just popularity-based).
- **Hybrid** — weighted blend of content + collaborative scores.
- **Correlation-based diversification** — recommends low-correlation assets; the old `diversify` method was a slow `ORDER BY RAND()` over a different sector.
- **Trending / momentum** — ranks by momentum + popularity.
- **Portfolio-gap completion** — strongest asset per unrepresented sector.
- **Similar portfolios** — ranks by holding overlap.
- Fixed a database-connection leak (callers now only close connections they own) and removed the slow random ordering.

New/clarified routes are listed under **Recommender System** above. Added tests in `app/tests/test_recommender.py` (run with `pytest`; they use an in-memory fake DB).

### Setup & scripting fixes

- **`scripts/run_init_db.py`** (new) — runs `scripts/init_db.sql` via the Python MySQL connector, so the schema can be created without the `mysql` CLI client (`Executed N statements`).
- **`scripts/seed_data.py`** — added the `app` package path fix (could not run from the project root before) and now resolves `ticker → asset_id` automatically because the transaction API expects `asset_id`, not `ticker`.
- **`scripts/daily_ingestion.py`** — fixed the wrong import (`fetch_and_store_prices` → `import_price_history`) and fixed the portfolio-valuation query: the invalid `t.asset_id = a.id` join and the reference to the nonexistent `price_history.ticker` column were replaced with a correct join on `price_history.asset_id`, and the nonexistent `total_gain_loss` column was removed. Inserts are now idempotent per day.

---

## Future Enhancements

- Strategy backtesting
- PDF portfolio reports
- Local websocket price streaming
- Custom strategy plugins
- Multi-user collaboration
