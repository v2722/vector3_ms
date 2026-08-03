# 📋 LSTM Implementation — Quick Reference Card

## 🚀 Getting Started (5 minutes)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start API
uvicorn app.main:app --reload

# 3. Test (in another terminal)
curl "http://localhost:8000/ml/predict/lstm/AAPL"

# 4. View docs
# Open browser to: http://localhost:8000/docs
```

---

## 🔗 API Endpoints at a Glance

| Endpoint | Purpose | Speed | Accuracy |
|----------|---------|-------|----------|
| `/ml/predict/lstm/AAPL` | LSTM (best) | 1-2s | ⭐⭐⭐⭐⭐ |
| `/ml/predict/prophet/AAPL` | Prophet (seasonal) | 0.5s | ⭐⭐⭐⭐ |
| `/ml/predict/linear/AAPL` | Linear (baseline) | 0.1s | ⭐⭐ |
| `/ml/predict/ensemble/AAPL` | All 3 average | 3-4s | ⭐⭐⭐⭐⭐ |
| `/ml/classify/AAPL` | Risk/Income type | Fast | N/A |
| `/ml/health/1` | Portfolio score | Fast | N/A |

**Add parameters:** `?days=14` (forecast 14 days, default 7)

---

## 💬 Example: One-Liner Tests

```bash
# LSTM 7-day forecast
curl "http://localhost:8000/ml/predict/lstm/AAPL"

# Compare all methods
for method in lstm prophet linear ensemble; do
  echo "=== $method ===" 
  curl "http://localhost:8000/ml/predict/$method/AAPL"
done

# 14-day ensemble
curl "http://localhost:8000/ml/predict/ensemble/TSLA?days=14"

# Classify asset
curl "http://localhost:8000/ml/classify/AAPL"

# Portfolio health
curl "http://localhost:8000/ml/health/1"
```

---

## 🐍 Python: Copy & Paste

### Get LSTM Prediction
```python
import requests
r = requests.get("http://localhost:8000/ml/predict/lstm/AAPL")
data = r.json()
print(f"Predicted: ${data['predictions'][0]['predicted_price']:.2f}")
```

### Compare Methods
```python
for method in ["lstm", "prophet", "linear", "ensemble"]:
    r = requests.get(f"http://localhost:8000/ml/predict/{method}/AAPL")
    data = r.json()
    price = data['predictions'][0]['predicted_price']
    print(f"{method}: ${price:.2f}")
```

### Use Confidence Intervals
```python
pred = data['predictions'][0]
print(f"Best case: ${pred['upper_bound']:.2f}")
print(f"Worst case: ${pred['lower_bound']:.2f}")
print(f"Most likely: ${pred['predicted_price']:.2f}")
```

---

## 📊 Response Structure

```json
{
  "ticker": "AAPL",
  "method": "lstm_neural_network",
  "current_price": 150.25,
  "model_info": {
    "test_mae": 1.23,              ← Lower is better
    "test_mse": 2.35,              ← Model quality
    "confidence_interval_std": 5.67 ← Prediction uncertainty
  },
  "predictions": [
    {
      "day": 1,
      "predicted_price": 151.50,   ← Best estimate
      "upper_bound": 162.84,       ← 95% won't exceed
      "lower_bound": 140.16,       ← 95% won't go below
      "confidence_level": "95%"
    }
  ]
}
```

---

## ⚡ Performance Guide

| Model | Speed | Memory | Best For |
|-------|-------|--------|----------|
| **LSTM** | 1-2s | ~10MB | Accuracy |
| **Prophet** | 0.5s | ~5MB | Speed + seasonality |
| **Linear** | 0.1s | ~1MB | Baseline |
| **Ensemble** | 3-4s | ~30MB | Mission-critical |

**TIP:** First call slower (TensorFlow init), subsequent faster!

---

## 🧪 Test Suite

```bash
# Full test of all methods
python test_lstm_prediction.py

# Test specific ticker
python test_lstm_prediction.py --ticker TSLA --days 14

# List available tickers
python test_lstm_prediction.py --list

# Check portfolio health
python test_lstm_prediction.py --portfolio 1
```

---

## 🎛️ Quick Tuning

**Model too slow?**
```python
# In ml_service_enhanced.py, line ~50
lookback = 20  # Was 30
LSTM(25, ...)  # Was 50
batch_size = 64  # Was 32
```

**Predictions bad (MAE > 3)?**
```python
lookback = 60  # Was 30
LSTM(100, ...)  # Was 50
epochs = 100  # Was 50
```

**Overfitting (test >> train loss)?**
```python
Dropout(0.3)  # Was 0.2
learning_rate = 0.0001  # Was 0.001
```

See `LSTM_TUNING.md` for details.

---

## 📚 Documentation Map

```
QUICK_REFERENCE.md        ← You are here
├─ LSTM_QUICKSTART.md     ← 5-min setup guide
├─ ML_ENHANCEMENTS.md     ← Full technical docs
├─ LSTM_TUNING.md         ← Optimization guide
├─ IMPLEMENTATION_SUMMARY.md ← What was built
└─ README.md              ← Project overview
```

---

## ❓ Common Issues

| Issue | Solution |
|-------|----------|
| "Insufficient data" | Need 60+ days. Try Prophet instead. |
| "TensorFlow not found" | `pip install tensorflow keras` |
| Slow prediction | Normal (1-2s). Use Linear for speed. |
| Wide confidence intervals | Stock is volatile. Use ensemble. |
| Wrong predictions | Check test_mae in response. Retrain? |

---

## ✅ Checklist

- [ ] Run `pip install -r requirements.txt`
- [ ] Start API with `uvicorn app.main:app --reload`
- [ ] Test LSTM: `curl "http://localhost:8000/ml/predict/lstm/AAPL"`
- [ ] Run test suite: `python test_lstm_prediction.py`
- [ ] Read `LSTM_QUICKSTART.md`
- [ ] Compare methods: LSTM vs Prophet vs Linear
- [ ] Use ensemble for important decisions
- [ ] Check confidence intervals before trading

---

## 🎯 Which Method to Use?

```
Need speed?           → Use Prophet (0.5s)
Need accuracy?        → Use LSTM (1-2s)
Need simplicity?      → Use Linear (0.1s)
Need confidence?      → Use Ensemble (3-4s)
Mission critical?     → Use Ensemble
Seasonal stock?       → Use Prophet
Volatile stock?       → Use Ensemble
Just testing?         → Use Linear (fast)
Real trading?         → Use Ensemble (robust)
```

---

## 📈 Understanding Model Metrics

### Test MAE (Mean Absolute Error)
- **< 1.0:** Excellent predictions ✅
- **1-2:** Good predictions ✅
- **2-3:** Fair predictions 🟡 (consider Prophet)
- **> 3:** Poor predictions ⚠️ (increase data)

**What it means:** Average prediction error in dollars

### Test MSE (Mean Squared Error)
- Similar to MAE but penalizes large errors
- Use MAE for interpretation, MSE for optimization

### Confidence Interval Width
- **Narrow (±5%):** Very confident
- **Medium (±10%):** Reasonably confident
- **Wide (±20%+):** Low confidence (volatile stock)

---

## 🔐 Production Checklist

- [ ] Use LSTM for accuracy
- [ ] Use Ensemble for critical decisions
- [ ] Always check confidence intervals
- [ ] Monitor test_mae over time
- [ ] Combine with other analysis
- [ ] Don't trade on predictions alone
- [ ] Test on historical data first
- [ ] Set stop-losses (use lower_bound)
- [ ] Monitor model drift
- [ ] Retrain weekly/monthly

---

## 💾 File Summary

| File | Size | Purpose |
|------|------|---------|
| `app/services/ml_service_enhanced.py` | 650 lines | LSTM implementation |
| `app/routes/ml_routes.py` | 80 lines | API endpoints |
| `requirements.txt` | +2 lines | TensorFlow, Keras |
| `test_lstm_prediction.py` | 200 lines | Test suite |
| `ML_ENHANCEMENTS.md` | 400 lines | Full documentation |
| `LSTM_QUICKSTART.md` | 250 lines | Quick start guide |
| `LSTM_TUNING.md` | 350 lines | Tuning guide |
| `IMPLEMENTATION_SUMMARY.md` | 400 lines | What was built |

---

## 🚀 Next Steps

1. **Install:** `pip install -r requirements.txt`
2. **Run:** `uvicorn app.main:app --reload`
3. **Test:** `python test_lstm_prediction.py --ticker AAPL`
4. **Read:** `LSTM_QUICKSTART.md` (10 minutes)
5. **Tune:** `LSTM_TUNING.md` (if needed)
6. **Integrate:** Use predictions in your system

---

## 📞 Debugging

```bash
# Check TensorFlow
python -c "import tensorflow; print('✓ TensorFlow OK')"

# Test prediction locally
python -c "
from app.services.ml_service_enhanced import predict_price_lstm
from app.database.connection import get_db
print(predict_price_lstm('AAPL', 7, get_db()))
"

# View API docs
# Browser: http://localhost:8000/docs
# Swagger UI with interactive testing
```

---

## 🎓 Learning Resources

- **LSTM Explanation:** https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- **TensorFlow/Keras:** https://tensorflow.org/tutorials
- **Time Series:** https://www.tensorflow.org/tutorials/structured_data/time_series
- **Prophet:** https://facebook.github.io/prophet/

---

## 💡 Pro Tips

✅ **Always use ensemble** for critical trading decisions
✅ **Check confidence intervals** before position sizing
✅ **Monitor MAE** over time (model drift detection)
✅ **Combine with fundamentals** (never ML alone)
✅ **Backtest your strategy** before live trading
✅ **Use stop-losses** at the lower confidence bound
✅ **Retrain weekly** with new data
✅ **Compare methods** to understand each stock

❌ **Don't** trade on point predictions alone
❌ **Don't** forecast >30 days ahead
❌ **Don't** ignore confidence intervals
❌ **Don't** rely on ML as sole signal
❌ **Don't** use 1-year-old training data
❌ **Don't** overlook model quality metrics

---

**Version:** 2.0 LSTM Implementation
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-27

🎉 **Ready to predict stock prices? Start now!**
