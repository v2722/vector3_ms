# 🚀 LSTM Price Prediction — Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd portfolio_manager
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import tensorflow; import prophet; print('✓ Ready to go!')"
```

### Step 2: Start the API
```bash
uvicorn app.main:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Test with Your First Prediction
Open a new terminal:
```bash
curl "http://localhost:8000/ml/predict/lstm/AAPL?days=7"
```

You should get a JSON response with predictions!

---

## 📊 Common Use Cases

### Use Case 1: Get 7-Day Price Forecast
```bash
curl "http://localhost:8000/ml/predict/lstm/AAPL"
```

**Response:**
```json
{
  "ticker": "AAPL",
  "method": "lstm_neural_network",
  "current_price": 150.25,
  "predictions": [
    {
      "day": 1,
      "predicted_price": 151.50,
      "upper_bound": 162.84,
      "lower_bound": 140.16,
      "confidence_level": "95%"
    }
  ]
}
```

---

### Use Case 2: Compare All 3 Methods
```bash
# LSTM (best accuracy)
curl "http://localhost:8000/ml/predict/lstm/TSLA"

# Prophet (seasonal patterns)
curl "http://localhost:8000/ml/predict/prophet/TSLA"

# Linear (baseline)
curl "http://localhost:8000/ml/predict/linear/TSLA"
```

**Quick Comparison:**
| Method | Speed | Accuracy | When to Use |
|--------|-------|----------|-------------|
| LSTM | 1-2s | ⭐⭐⭐⭐⭐ | Important decisions |
| Prophet | 0.5s | ⭐⭐⭐⭐ | Seasonal stocks |
| Linear | 0.1s | ⭐⭐ | Baseline only |

---

### Use Case 3: Ensemble Prediction (Most Reliable)
```bash
curl "http://localhost:8000/ml/predict/ensemble/MSFT?days=14"
```

**Ensemble = Average of all 3 methods**
- ✅ Most robust
- ✅ Combines strengths
- ✅ Best for critical decisions
- ❌ Slowest option

---

### Use Case 4: Forecast Multiple Days
```bash
# 14-day forecast
curl "http://localhost:8000/ml/predict/lstm/GOOGL?days=14"

# 30-day forecast (use ensemble for this)
curl "http://localhost:8000/ml/predict/ensemble/GOOGL?days=30"
```

⚠️ **Note:** Accuracy decreases beyond 14 days. Use longer forecasts for trends only.

---

### Use Case 5: Asset Risk Classification
```bash
curl "http://localhost:8000/ml/classify/AAPL"
```

**Response:**
```json
{
  "ticker": "AAPL",
  "risk_class": "moderate-risk",
  "income_class": "growth",
  "volatility": 0.185,
  "dividend_yield": 0.005
}
```

---

## 🐍 Python Examples

### Example 1: Simple LSTM Prediction
```python
import requests
import json

response = requests.get(
    "http://localhost:8000/ml/predict/lstm/AAPL",
    params={"days": 7}
)

data = response.json()
print(f"Current: ${data['current_price']:.2f}")

for pred in data['predictions']:
    print(f"Day {pred['day']}: ${pred['predicted_price']:.2f} "
          f"(${pred['lower_bound']:.2f} - ${pred['upper_bound']:.2f})")
```

**Output:**
```
Current: $150.25
Day 1: $151.50 ($140.16 - $162.84)
Day 2: $152.30 ($140.96 - $163.64)
...
```

---

### Example 2: Compare Methods & Pick Best
```python
import requests

ticker = "AAPL"
methods = ["lstm", "prophet", "linear"]

predictions = {}
for method in methods:
    response = requests.get(
        f"http://localhost:8000/ml/predict/{method}/{ticker}"
    )
    predictions[method] = response.json()

# Compare day 1 predictions
print(f"{'Method':<15} {'Prediction':<15} {'Confidence':<20}")
print("-" * 50)

for method, data in predictions.items():
    if "predictions" in data:
        day1 = data["predictions"][0]
        price = day1["predicted_price"]
        lower = day1["lower_bound"]
        upper = day1["upper_bound"]
        width = upper - lower
        print(f"{method:<15} ${price:<14.2f} Width: ${width:.2f}")

# Use ensemble for final decision
response = requests.get(
    f"http://localhost:8000/ml/predict/ensemble/{ticker}"
)
ensemble = response.json()
print(f"\n✓ Ensemble (use this): ${ensemble['predictions'][0]['predicted_price']:.2f}")
```

---

### Example 3: Get Confidence Intervals for Trading
```python
import requests

response = requests.get(
    "http://localhost:8000/ml/predict/lstm/AAPL?days=7"
)
data = response.json()

current_price = data['current_price']
prediction = data['predictions'][0]

print(f"Current Price: ${current_price:.2f}")
print(f"Predicted: ${prediction['predicted_price']:.2f}")
print(f"Worst Case (lower bound): ${prediction['lower_bound']:.2f}")
print(f"Best Case (upper bound): ${prediction['upper_bound']:.2f}")

# Trading decisions
print(f"\nTrading Strategy:")
print(f"- Stop Loss: ${prediction['lower_bound']:.2f}")
print(f"- Take Profit: ${prediction['upper_bound']:.2f}")
print(f"- Risk/Reward: 1:{(prediction['upper_bound'] - current_price) / (current_price - prediction['lower_bound']):.2f}")
```

---

### Example 4: Monitor Portfolio with Health Score
```python
import requests

portfolio_id = 1
response = requests.get(f"http://localhost:8000/ml/health/{portfolio_id}")
data = response.json()

score = data['overall_health_score']

if score >= 80:
    status = "✅ Excellent"
elif score >= 60:
    status = "🟡 Good"
else:
    status = "⚠️  Needs Work"

print(f"Portfolio Health: {score:.1f}/100 {status}")
print(f"  - Diversification: {data['diversification_score']:.1f}/100")
print(f"  - Volatility: {data['volatility_score']:.1f}/100")
print(f"  - Sectors: {data['sectors']}")
```

---

## 🔧 Understanding the Output

### Prediction Response Structure
```json
{
  "ticker": "AAPL",
  "method": "lstm_neural_network",
  "current_price": 150.25,
  "model_info": {
    "test_mse": 2.35,      ← Lower is better (avg squared error)
    "test_mae": 1.23,      ← Lower is better (avg absolute error ~$1.23)
    "confidence_interval_std": 5.67  ← Width of confidence bands
  },
  "predictions": [
    {
      "day": 1,
      "predicted_price": 151.50,   ← Most likely price
      "upper_bound": 162.84,       ← 95% won't go above this
      "lower_bound": 140.16,       ← 95% won't go below this
      "confidence_level": "95%"
    }
  ]
}
```

### How to Read Confidence Intervals

**Scenario:** LSTM predicts $151.50 ± $11.34
```
Lower Bound       Current     Prediction     Upper Bound
   $140.16  ←  $150.25  →  $151.50  →  $162.84

   ◄─────────────── 95% Confidence Zone ──────────────►
```

**Interpretation:**
- 95% probability price will be between $140.16 and $162.84
- 5% probability of price outside this range (tail risk)
- Wider bands = less certain
- Narrower bands = more certain

---

## ⚠️ Common Issues & Fixes

### Issue: "Insufficient historical data"
```
{
  "error": "Insufficient historical data. Need 60+ days, got 25"
}
```

**Fix:** This ticker needs more price history. Use Prophet or Linear instead:
```bash
curl "http://localhost:8000/ml/predict/prophet/NEW_TICKER"
```

---

### Issue: "TensorFlow not installed"
```bash
pip install tensorflow keras --upgrade
```

---

### Issue: Slow predictions (>5 seconds)
- **First call:** Takes 1-2 seconds (TensorFlow initialization)
- **Subsequent calls:** Fast (~1 second)
- **Solution:** Use Linear or Prophet if you need instant responses

---

### Issue: Very Wide Confidence Intervals
**Causes:**
- Stock is volatile
- Predicting too far ahead
- Not enough training data

**Solutions:**
```bash
# Try shorter forecast
curl "http://localhost:8000/ml/predict/lstm/VOLATILE_STOCK?days=3"

# Or use Prophet for stability
curl "http://localhost:8000/ml/predict/prophet/VOLATILE_STOCK?days=7"
```

---

## 📈 Best Practices

### ✅ Do This
1. **Use confidence intervals** — Never ignore the bounds
2. **Compare methods** — Run LSTM + Prophet + Ensemble
3. **Check model metrics** — MAE < 2.0 is good
4. **Use ensemble for decisions** — Average of 3 is more stable
5. **Forecast 7-14 days max** — Longer = less reliable
6. **Combine with other analysis** — Don't trade on ML alone

### ❌ Don't Do This
1. **Don't ignore uncertainty** — Confidence intervals exist for a reason
2. **Don't forecast >30 days** — Model accuracy degrades exponentially
3. **Don't skip validation** — Always compare models
4. **Don't trade high volatility** — Too much uncertainty
5. **Don't use point predictions** — Always consider bounds
6. **Don't trust 1 model** — Use ensemble approach

---

## 🎯 Next Steps

### Learn More
- Read: `ML_ENHANCEMENTS.md` (detailed documentation)
- Run: `python test_lstm_prediction.py` (full test suite)
- Check: `http://localhost:8000/docs` (interactive API docs)

### Try These Commands
```bash
# List all available tickers
python test_lstm_prediction.py --list

# Test specific ticker with custom days
python test_lstm_prediction.py --ticker TSLA --days 14

# Check portfolio health
python test_lstm_prediction.py --portfolio 1
```

### Integrate into Your Code
```python
# Add this to your application
from app.services.ml_service_enhanced import predict_price_lstm

# Direct function call (no HTTP)
result = predict_price_lstm("AAPL", days=7)
```

---

## 🆘 Quick Reference

| Task | Command |
|------|---------|
| LSTM Forecast | `curl http://localhost:8000/ml/predict/lstm/AAPL` |
| Compare All | `curl http://localhost:8000/ml/predict/ensemble/AAPL` |
| Asset Risk | `curl http://localhost:8000/ml/classify/AAPL` |
| Portfolio Health | `curl http://localhost:8000/ml/health/1` |
| List Tickers | `python test_lstm_prediction.py --list` |
| Full Test | `python test_lstm_prediction.py` |
| API Docs | Open browser to `http://localhost:8000/docs` |

---

## 📞 Still Need Help?

1. **Check the docs:** `ML_ENHANCEMENTS.md`
2. **Run tests:** `python test_lstm_prediction.py`
3. **Check logs:** Look at terminal output when running uvicorn
4. **Enable debugging:** Set `DEBUG=True` in `app/config.py`

---

**Ready to predict? Start with:**
```bash
curl "http://localhost:8000/ml/predict/lstm/AAPL"
```

🎉 **Happy forecasting!**
