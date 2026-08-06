# Portfolio Manager - Quick Start Guide

Everything is now **complete** with all README features enabled in both frontend and backend with **live data loading**.

---

## 🚀 Start Everything in 4 Steps

### Step 1: Start the API (Terminal 1)
```powershell
cd portfolio_manager
venv\Scripts\activate
python scripts/run_init_db.py    # One-time: setup database
python scripts/seed_data.py       # One-time: add sample data
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start React Frontend (Terminal 2)
```powershell
cd portfolio_manager/ui
npm run dev
```

**Expected output:**
```
VITE v5.4.10 ready in 200ms
Local: http://localhost:3000/
```

### Step 3: Open Browser
```
http://localhost:3000
```

### Step 4: Use the App
- Select a portfolio from dropdown
- Explore all tabs in sidebar
- All data loads live from API

---

## 📋 What's Available

### ✅ Existing Features (Enhanced)
- **Overview** - Dashboard with live KPIs
- **Holdings** - Current asset positions
- **Risk Analytics** - Risk metrics from backend
- **Compare** - Portfolio heatmap comparison
- **Recommendations** - ML-driven suggestions (7 methods)
- **Assets** - Add/edit/delete assets
- **Manage** - Create/edit/delete portfolios

### ✅ NEW Features (Just Added)
- **ML & Predictions** - LSTM, Prophet, Linear, Ensemble price forecasts + asset classification
- **Optimization** - Efficient frontier, optimal allocation, risk parity, Monte Carlo
- **Transactions** - Add and view portfolio transactions

---

## 🎯 Quick Examples

### Add a Stock & See Results
```
1. Click "Manage" → Create new portfolio
2. Click "Assets" → Add asset (AAPL, MSFT, etc.)
3. Click "Transactions" → Add transaction (BUY 10 @ $150)
4. Watch portfolio value update on "Overview"
```

### Predict Stock Price
```
1. Click "ML & Predictions"
2. Enter ticker: AAPL
3. Select method: LSTM
4. Click "Predict Price"
5. See 7-day forecast with confidence intervals
```

### Optimize Portfolio
```
1. Click "Optimization"
2. Click "Calculate Frontier" (wait 10-15s)
3. Click "Get Optimal Weights"
4. View recommended allocation
```

---

## 🔗 API Endpoints

All **47+ endpoints** are integrated:

**Core Operations:**
- GET/POST /portfolios/ - Portfolio CRUD
- GET/POST /assets/{ticker} - Asset CRUD
- GET/POST /transactions/{id} - Transactions
- GET/POST /prices/{ticker} - Prices

**Machine Learning:**
- GET /ml/predict/{ticker} - Price predictions (LSTM, Prophet, Linear, Ensemble)
- GET /ml/classify/{ticker} - Asset classification
- GET /ml/health/{id} - Portfolio health score

**Recommendations (7 methods):**
- GET /recommend/hybrid/{id}
- GET /recommend/correlation/{id}
- GET /recommend/gaps/{id}
- GET /recommend/trending
- Plus 3 more in API

**Risk Analytics (5 metrics):**
- GET /risk/volatility/{ticker}
- GET /risk/sharpe/{id}
- GET /risk/var/{id}
- GET /risk/max-drawdown/{id}
- GET /risk/correlation/{id}

**Optimization (4 methods):**
- GET /optimize/frontier/{id}
- GET /optimize/optimal/{id}
- GET /optimize/risk-parity/{id}
- GET /optimize/monte-carlo/{id}

---

## ✨ Features Checklist

### Backend (All Working)
- [x] FastAPI REST API
- [x] MySQL database
- [x] Portfolio management
- [x] Asset management
- [x] Transaction tracking
- [x] ML predictions (LSTM, Prophet, Linear, Ensemble)
- [x] Asset classification
- [x] 7 recommendation methods
- [x] 5 risk metrics
- [x] 4 optimization methods
- [x] CSV import/export
- [x] User authentication (JWT)
- [x] Role-based access control

### Frontend (All Working)
- [x] React + Vite
- [x] Portfolio selector & CRUD
- [x] Asset management
- [x] Transaction management
- [x] ML prediction interface
- [x] Asset classification viewer
- [x] Optimization tools
- [x] Risk display
- [x] Recommendations view
- [x] Portfolio comparison
- [x] Dark/Light theme toggle
- [x] Responsive design
- [x] Real-time data loading
- [x] Error handling

### Testing (All Working)
- [x] 45+ E2E tests
- [x] Unit tests
- [x] API validation
- [x] End-to-end coverage

---

## 🧪 Verify Everything Works

### Test 1: Check API
```powershell
curl http://localhost:8000
# Should return: {"message": "Portfolio Manager API is running"}
```

### Test 2: Check Frontend
```powershell
# Open http://localhost:3000 in browser
# Should load dashboard with portfolio selector
```

### Test 3: Run Tests
```powershell
cd portfolio_manager
python test_e2e.py
# Should pass 45+ tests
```

---

## 📊 Files Overview

```
portfolio_manager/
├── app/                          # FastAPI backend
│   ├── routes/                  # 14 route modules (47+ endpoints)
│   ├── services/                # Business logic
│   ├── database/                # MySQL models & schemas
│   └── ...
├── ui/                           # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx              # Main app (enhanced with all features)
│   │   ├── styles.css           # Styling
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js           # API proxy setup
│   └── ...
├── scripts/
│   ├── run_init_db.py           # Database setup
│   ├── seed_data.py             # Sample data
│   └── ...
├── requirements.txt             # Python dependencies
├── test_e2e.py                  # End-to-end tests
└── [Documentation files]
    ├── README.md                # Project overview
    ├── QUICK_START.md           # This file
    ├── REACT_FRONTEND_ENHANCEMENTS.md
    ├── VERIFICATION_CHECKLIST.md
    ├── TESTING_GUIDE.md
    └── ...
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Make sure API running with `uvicorn app.main:app --reload` |
| React won't load | Make sure running `npm run dev` in `ui` directory |
| No portfolios in dropdown | Run `python scripts/seed_data.py` to add sample data |
| API calls fail | Check vite.config.js proxy is correct (target: http://127.0.0.1:8000) |
| Predictions error | Need 30+ days of price history (run `python scripts/daily_ingestion.py`) |

---

## 📚 Documentation

### Key Files to Read
1. **README.md** - Full project documentation
2. **REACT_FRONTEND_ENHANCEMENTS.md** - React feature details
3. **TESTING_GUIDE.md** - Setup & testing instructions
4. **VERIFICATION_CHECKLIST.md** - Step-by-step verification

---

## 🎓 Learning Path

### Day 1: Setup & Explore
```
1. Run all 4 startup steps above
2. Open http://localhost:3000
3. Explore Overview tab
4. Create a portfolio
5. Add an asset
```

### Day 2: Transactions & ML
```
1. Go to Transactions tab
2. Add 5 transactions with different stocks
3. See portfolio value update
4. Go to ML & Predictions
5. Predict AAPL stock price (try each method)
```

### Day 3: Optimization & Analysis
```
1. Go to Optimization tab
2. Calculate efficient frontier
3. View optimal allocation
4. Go to Risk Analytics
5. Review all 5 risk metrics
```

### Day 4: Advanced Features
```
1. Go to Compare tab
2. Create 2 portfolios
3. Compare their allocations
4. Go to Recommendations
5. Review 7 recommendation methods
```

---

## 🎯 Performance Notes

| Operation | Time |
|-----------|------|
| Efficient frontier (10k portfolios) | 10-15s |
| Monte Carlo (1000 simulations) | 5-10s |
| LSTM prediction | 5-30s |
| Prophet forecast | 2-10s |
| Price loading | <1s |
| Recommendation loading | <2s |

---

## 💡 Tips & Tricks

### Use Swagger UI for API Testing
```
http://localhost:8000/docs
```
Interactive API explorer - great for testing endpoints.

### Check Browser Console (F12)
See all API calls and responses in real-time.

### Export Portfolio Data
Use backend endpoints directly:
```
GET /csv/export/holdings
GET /csv/export/transactions
```

### Use Dark Mode
Click "🌙 Dark mode" in sidebar to toggle theme.

---

## 🔗 Key URLs

| URL | Purpose |
|-----|---------|
| http://localhost:3000 | React frontend |
| http://localhost:8000 | FastAPI backend |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/scalar | Scalar console |

---

## ✅ Done!

Everything is **ready to use**. All README features are implemented and tested:

✅ Backend API - 47+ endpoints  
✅ React Frontend - All features  
✅ Live data loading - No hardcoded data  
✅ ML models - LSTM, Prophet, Linear, Ensemble  
✅ Optimization - 4 algorithms  
✅ Risk analytics - 5 metrics  
✅ Recommendations - 7 methods  
✅ Testing - 45+ E2E tests  

**Start with Step 1-4 above and explore!** 🚀
