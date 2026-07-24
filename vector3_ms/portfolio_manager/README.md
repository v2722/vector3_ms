Here is your **complete, production‑ready `README.md` file** containing the **entire workflow of the project**, from ERD → DB → Backend → API → Market Data → Performance → Logging → Testing → UI → Future roadmap.

This is a **single Markdown file**.  
Copy/paste it directly into:

```
README.md
```

---

# 📘 Portfolio Manager — FastAPI + MySQL + Yahoo Finance  
A complete backend system for managing financial portfolios, tracking assets, recording transactions, storing historical market data, computing portfolio performance, and providing modern API documentation.

This project follows the **ERD visible in your repository** (Portfolio Management System ERD) and implements every major component using **FastAPI**, **MySQL**, and **Yahoo Finance (yfinance)**.

---

# 🧭 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [ERD](#erd)
- [Workflow](#workflow)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Core Features](#core-features)
- [Market Data Workflow](#market-data-workflow)
- [Performance Tracking Workflow](#performance-tracking-workflow)
- [Audit & Logging Workflow](#audit--logging-workflow)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

# 📘 Overview
The **Portfolio Manager** backend provides:

- Portfolio creation & management  
- Asset tracking  
- BUY/SELL/DIVIDEND transactions  
- Historical price ingestion  
- Market data caching  
- API request logging  
- Portfolio performance computation  
- Audit logging  
- Modern API UI (Scalar)

It is designed for training, prototyping, and extension into a full production system.

---

# 🏛 Architecture

### ✔ FastAPI  
REST API backend with modular routing and service layers.

### ✔ MySQL  
Relational database storing portfolios, assets, transactions, market data, performance metrics, and logs.

### ✔ Yahoo Finance (yfinance)  
External API used to fetch live and historical market data.

### ✔ Scalar API Console  
Modern interactive API documentation.

---

# 🧩 ERD  
The system follows the ERD visible in your GitHub tab, containing:

### Core Entities  
- Portfolio  
- Asset  
- Portfolio Item  
- Transaction  
- Price History  

### Extended Entities  
- Asset Type  
- Asset Transaction  
- Portfolio Performance  
- Market Data Cache  
- External API Request  
- Audit Log  

This ERD defines the full workflow of the system.

---

# 🔄 Workflow

## 1️⃣ Portfolio Creation  
User creates a portfolio → stored in `portfolio`.

## 2️⃣ Asset Registration  
Assets are added manually or fetched from Yahoo Finance → stored in `asset`.

## 3️⃣ Adding Items to Portfolio  
Portfolio items track quantity + average buy price → stored in `portfolio_item`.

## 4️⃣ Recording Transactions  
BUY / SELL / DIVIDEND → stored in `transaction` and `asset_transaction`.

## 5️⃣ Fetching Market Data  
Using yfinance:
- Live price  
- Historical OHLCV  
Stored in:
- `price_history`  
- `market_data_cache`  
- `external_api_request`

## 6️⃣ Performance Calculation  
Daily valuation computed → stored in `portfolio_performance`.

## 7️⃣ Audit Logging  
Every important action logged → stored in `audit_log`.

## 8️⃣ API Documentation  
User interacts with:
- Swagger (`/docs`)
- ReDoc (`/redoc`)
- Scalar (`/scalar`)

---

# 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Backend | FastAPI |
| Database | MySQL |
| Market Data | Yahoo Finance (yfinance) |
| API UI | Swagger, ReDoc, Scalar |
| Logging | Custom audit + API logs |
| Testing | pytest |

---

# 📁 Project Structure

```
portfolio_manager/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── portfolio_routes.py
│   │   ├── asset_routes.py
│   │   ├── price_routes.py
│   │   ├── transaction_routes.py
│   │   ├── asset_type_routes.py
│   │   ├── asset_transaction_routes.py
│   │   ├── performance_routes.py
│   │   ├── scalar_ui.py
│   │
│   ├── services/
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
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │
│   ├── utils/
│       ├── logger.py
│       ├── exceptions.py
│
├── scripts/
│   ├── init_db.sql
│   ├── seed_data.py
│
├── tests/
│   ├── test_portfolio.py
│   ├── test_assets.py
│   ├── test_prices.py
│
└── .env
```

---

# 🗄 Database Schema

All tables are defined in:

```
scripts/init_db.sql
```

Includes:

### Core Tables  
- portfolio  
- asset  
- portfolio_item  
- transaction  
- price_history  

### ERD Extensions  
- asset_type  
- asset_transaction  
- portfolio_performance  
- market_data_cache  
- external_api_request  
- audit_log  

---

# ⚙ Installation

### Install dependencies

```bash
pip install fastapi uvicorn mysql-connector-python yfinance python-dotenv
```

---

# 🔐 Environment Variables

Create `.env`:

```
DB_HOST=localhost
DB_USER=root
DB_PASS=yourpassword
DB_NAME=portfolio_manager
```

---

# ▶ Running the Application

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

---

# 📚 API Documentation

| UI | URL |
|----|-----|
| Swagger | `/docs` |
| ReDoc | `/redoc` |
| Scalar | `/scalar` |

Scalar provides the most modern UI.

---

# 🧩 Core Features

### ✔ Portfolio CRUD  
### ✔ Asset CRUD  
### ✔ Portfolio Item Management  
### ✔ BUY/SELL/DIVIDEND Transactions  
### ✔ Historical Price Ingestion  
### ✔ Market Data Caching  
### ✔ API Request Logging  
### ✔ Audit Logging  
### ✔ Portfolio Performance Tracking  

---

# 📡 Market Data Workflow

1. User requests price data  
2. yfinance fetches OHLCV  
3. Data stored in `price_history`  
4. Raw JSON cached in `market_data_cache`  
5. API request logged in `external_api_request`

---

# 📈 Performance Tracking Workflow

1. Compute total portfolio value  
2. Compare with previous day  
3. Store:
   - total_value  
   - daily_change  
   - daily_change_percent  
4. Saved in `portfolio_performance`

---

# 🛡 Audit & Logging Workflow

Every important action logs:

- entity_name  
- entity_id  
- action  
- timestamp  
- details  

Stored in `audit_log`.

---

# 🧪 Testing

Run tests:

```bash
pytest
```

---

# 🔮 Future Enhancements

- React/Vue frontend  
- Portfolio charts (Plotly/Chart.js)  
- Scheduled daily price ingestion  
- JWT authentication  
- Role-based access control  
- Docker deployment  
- CI/CD pipeline  
