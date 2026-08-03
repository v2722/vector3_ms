# 🤖 ML Enhancements: LSTM Price Prediction

## Overview

This document describes the new advanced machine learning features added to the Portfolio Manager, with a focus on **LSTM-based price prediction** as the primary enhancement.

---

## 📊 What's New

### Previous Implementation
- Linear Regression only
- 60 days of data
- No confidence intervals
- Limited forecasting accuracy

### Enhanced Implementation
- ✅ **LSTM Neural Networks** (primary model)
- ✅ **Prophet Seasonal Forecasting** (alternative)
- ✅ **Linear Regression** (fallback)
- ✅ **Ensemble Predictions** (combines all 3)
- ✅ 95% Confidence Intervals
- ✅ 2 years of historical data
- ✅ Dropout regularization to prevent overfitting
- ✅ Early stopping to avoid overtraining
- ✅ Test set evaluation metrics

---

## 🧠 LSTM Model Architecture

```
Input: 30-day price sequence (normalized)
    ↓
LSTM Layer 1: 50 units, return_sequences=True
    ↓
Dropout: 20% regularization
    ↓
LSTM Layer 2: 50 units, return_sequences=False
    ↓
Dropout: 20% regularization
    ↓
Dense Layer: 25 units, ReLU activation
    ↓
Output Layer: 1 unit (next day's price)
```

**Key Features:**
- **Lookback Window:** 30 days (learns 30-day patterns)
- **Training Data:** First 80% of 504 days (≈402 days)
- **Test Data:** Last 20% (≈102 days for validation)
- **Optimization:** Adam optimizer with learning rate 0.001
- **Loss Function:** Mean Squared Error (MSE)
- **Regularization:** Dropout 20% on both LSTM layers
- **Early Stopping:** Stops if validation loss doesn't improve for 5 epochs

---

## 📈 Prediction Methods

### 1. LSTM (Recommended)
**Endpoint:** `GET /ml/predict/lstm/{ticker}?days=7`

**Pros:**
- ✅ Best accuracy for complex patterns
- ✅ Captures non-linear relationships
- ✅ Uses 2 years of data
- ✅ Includes confidence intervals
- ✅ Provides model quality metrics (MSE, MAE)

**Cons:**
- ❌ Slower inference (1-2 seconds)
- ❌ Requires TensorFlow/Keras
- ❌ Needs sufficient training data (60+ days)

**Example Response:**
```json
{
  "ticker": "AAPL",
  "method": "lstm_neural_network",
  "current_price": 150.25,
  "model_info": {
    "architecture": "LSTM(50) -> Dropout -> LSTM(50) -> Dropout -> Dense(25) -> Dense(1)",
    "lookback_window": 30,
    "training_epochs": 50,
    "test_mse": 2.3456,
    "test_mae": 1.2345,
    "confidence_interval_std": 5.67
  },
  "predictions": [
    {
      "day": 1,
      "predicted_price": 151.50,
      "upper_bound": 162.84,
      "lower_bound": 140.16,
      "confidence_level": "95%"
    },
    {
      "day": 2,
      "predicted_price": 152.30,
      "upper_bound": 163.64,
      "lower_bound": 140.96,
      "confidence_level": "95%"
    }
  ]
}
```

---

### 2. Prophet (Seasonal Patterns)
**Endpoint:** `GET /ml/predict/prophet/{ticker}?days=7`

**Pros:**
- ✅ Great for seasonal patterns (annual, weekly)
- ✅ Robust to missing data
- ✅ Trend detection
- ✅ Fast inference
- ✅ Built-in uncertainty quantification

**Cons:**
- ❌ Less accurate for non-seasonal stocks
- ❌ Assumes additive seasonality

**When to Use:**
- Stocks with strong seasonal patterns (e.g., retail, energy)
- Fewer than 60 days of historical data
- When speed is critical

**Example:** `curl http://localhost:8000/ml/predict/prophet/AAPL?days=7`

---

### 3. Linear Regression (Fallback)
**Endpoint:** `GET /ml/predict/linear/{ticker}?days=7`

**Pros:**
- ✅ Simple and interpretable
- ✅ Very fast
- ✅ Works with minimal data

**Cons:**
- ❌ Poor accuracy for complex patterns
- ❌ Only captures linear trends
- ❌ Not recommended for real predictions

**When to Use:**
- Baseline comparison
- Stocks with perfect linear trends (rare)
- Quick proof-of-concept

---

### 4. Ensemble (Most Robust)
**Endpoint:** `GET /ml/predict/ensemble/{ticker}?days=7`

**How It Works:**
1. Run LSTM prediction
2. Run Prophet prediction
3. Run Linear Regression
4. Average all three predictions
5. Return ensemble result

**Pros:**
- ✅ Most robust (combines strengths of all models)
- ✅ Reduces overfitting risk
- ✅ Reports which models were used
- ✅ Best for critical decisions

**Cons:**
- ❌ Slowest (runs 3 models)
- ❌ Requires all data sources

**When to Use:**
- Portfolio rebalancing decisions
- Risk analysis
- When accuracy matters most

---

## 🔧 API Endpoints

### Generic Prediction Endpoint
```
GET /ml/predict/{ticker}?days=7&method=lstm
```

**Query Parameters:**
- `ticker` (required): Stock symbol (e.g., "AAPL")
- `days` (optional): Number of days to forecast (default: 7)
- `method` (optional): "lstm", "prophet", "linear", or "ensemble" (default: "lstm")

**Methods:**
```
GET /ml/predict/lstm/{ticker}          # LSTM prediction
GET /ml/predict/prophet/{ticker}       # Prophet prediction
GET /ml/predict/linear/{ticker}        # Linear regression
GET /ml/predict/ensemble/{ticker}      # Ensemble average
GET /ml/classify/{ticker}              # Asset classification
GET /ml/health/{portfolio_id}          # Portfolio health score
```

---

## 📊 Response Format

All prediction endpoints return:

```json
{
  "ticker": "AAPL",
  "method": "lstm_neural_network",
  "current_price": 150.25,
  "model_info": {
    "architecture": "...",
    "test_mse": 2.3456,
    "test_mae": 1.2345,
    "confidence_interval_std": 5.67
  },
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

**Fields:**
- `predicted_price`: Most likely future price
- `upper_bound`: 95% confidence upper bound (worse case scenario)
- `lower_bound`: 95% confidence lower bound (best case scenario)
- `confidence_level`: Confidence of the interval (always 95%)

---

## 🎯 Confidence Intervals Explained

The confidence intervals tell you how certain the prediction is:

**Example:** If LSTM predicts AAPL at $151.50 ± $11.34:
- **95% Confidence:** There's a 95% chance the real price will be between $140.16 and $162.84
- **Wider bounds** = Less certain prediction
- **Narrower bounds** = More certain prediction

**Use them to:**
- Assess prediction uncertainty
- Set stop-loss levels (use lower bound)
- Set profit-taking levels (use upper bound)
- Determine position sizing

---

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This includes:
- `tensorflow>=2.14.0` - Deep learning framework
- `keras>=3.0.0` - Neural network API
- `prophet>=1.1.5` - Time series forecasting
- Plus all existing dependencies

### 2. Verify Installation
```bash
python -c "import tensorflow; import prophet; print('✓ All ML dependencies installed')"
```

### 3. Run the API
```bash
uvicorn app.main:app --reload
```

### 4. Test the Endpoint
```bash
curl http://localhost:8000/ml/predict/lstm/AAPL?days=7
```

---

## 💡 Usage Examples

### Example 1: Get 7-Day LSTM Prediction
```bash
curl "http://localhost:8000/ml/predict/lstm/AAPL?days=7"
```

### Example 2: Compare All Methods
```bash
curl "http://localhost:8000/ml/predict/AAPL?method=lstm"
curl "http://localhost:8000/ml/predict/AAPL?method=prophet"
curl "http://localhost:8000/ml/predict/AAPL?method=linear"
curl "http://localhost:8000/ml/predict/AAPL?method=ensemble"
```

### Example 3: 14-Day Ensemble Forecast
```bash
curl "http://localhost:8000/ml/predict/ensemble/TSLA?days=14"
```

### Example 4: Python Client
```python
import requests

# Get LSTM prediction
response = requests.get(
    "http://localhost:8000/ml/predict/lstm/AAPL",
    params={"days": 7}
)
prediction = response.json()

print(f"Current: ${prediction['current_price']}")
print(f"Day 1 Forecast: ${prediction['predictions'][0]['predicted_price']}")
print(f"95% Range: ${prediction['predictions'][0]['lower_bound']:.2f} - ${prediction['predictions'][0]['upper_bound']:.2f}")
```

---

## 📈 Model Performance Metrics

### What They Mean

**MSE (Mean Squared Error):**
- Average of squared prediction errors
- Lower is better
- Penalizes large errors heavily
- Typical range: 1.0 - 10.0 for normalized stock prices

**MAE (Mean Absolute Error):**
- Average absolute prediction error
- More interpretable than MSE (in dollar units)
- Typical range: 0.5 - 3.0

**Example Interpretation:**
```json
"test_mae": 1.5  → Model predictions are off by ~$1.50 on average
"test_mse": 3.5  → Average squared error of 3.5
```

### Using Test Metrics to Assess Confidence

- **MAE < 1.0**: Very good predictions
- **1.0 < MAE < 2.0**: Good predictions
- **2.0 < MAE < 3.0**: Fair predictions (use ensemble)
- **MAE > 3.0**: Poor predictions (increase training data or try Prophet)

---

## 🔍 Troubleshooting

### Error: "Insufficient historical data"
**Solution:** Need at least 60 days of price history
```python
# Check available data
response = requests.get("http://localhost:8000/api/prices/YOUR_TICKER")
```

### Error: "TensorFlow not installed"
**Solution:**
```bash
pip install tensorflow keras
```

### Slow Predictions (>5 seconds)
**Solution:**
- First prediction is slow (TensorFlow initialization)
- Subsequent predictions are faster (~1-2 seconds)
- Use linear or Prophet for speed if needed

### Large Confidence Intervals
**Causes:**
- Volatile stock (high historical volatility)
- Short prediction window (further days = wider bounds)
- Insufficient training data

**Solutions:**
- Use more historical data if available
- Try shorter prediction windows (3-5 days)
- Use ensemble method for more stable estimates

---

## 🎓 Best Practices

### ✅ Do's
1. **Always use confidence intervals** — Never rely on point predictions alone
2. **Compare methods** — Run LSTM and Prophet, compare results
3. **Use ensemble for critical decisions** — Portfolio rebalancing, large trades
4. **Monitor model metrics** — Check MAE, confidence interval width
5. **Use 30-90 day forecasts** — Beyond that, uncertainty grows exponentially
6. **Combine with other analysis** — Never trade on ML predictions alone

### ❌ Don'ts
1. **Don't trade on point predictions alone** — Always consider confidence intervals
2. **Don't forecast >30 days ahead** — Model accuracy degrades quickly
3. **Don't ignore model quality metrics** — High MAE = low confidence
4. **Don't use linear regression for important decisions** — It's a baseline only
5. **Don't skip ensemble validation** — Run 3 methods before trusting one

---

## 🔮 Next Steps / Future Enhancements

1. **Hyperparameter Tuning:** Auto-optimize LSTM parameters per stock
2. **Multi-step Ahead Training:** Predict multiple days simultaneously
3. **Attention Mechanisms:** Better handling of important days
4. **Ensemble with XGBoost:** Add gradient boosting to ensemble
5. **Backtesting Framework:** Validate strategies with historical data
6. **Model Monitoring:** Track prediction accuracy over time
7. **Feature Engineering:** Add technical indicators (RSI, MACD, Bollinger Bands)
8. **Transfer Learning:** Pre-train on many stocks, fine-tune per ticker

---

## 📚 References

- **LSTM Basics:** https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- **Prophet Documentation:** https://facebook.github.io/prophet/
- **TensorFlow/Keras:** https://www.tensorflow.org/
- **Financial Time Series:** https://en.wikipedia.org/wiki/Time_series

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify TensorFlow/Prophet installation: `pip install --upgrade tensorflow prophet`
3. Check API logs: `curl http://localhost:8000/docs` (interactive docs)
4. Enable verbose logging in `app/utils/logger.py`

---

**Last Updated:** 2026-01-27
**Version:** 2.0 (LSTM Enhancement)
