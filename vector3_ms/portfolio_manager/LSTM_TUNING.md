# 🔧 LSTM Model Tuning & Configuration Guide

## Overview

This guide explains how to tune the LSTM model for better predictions on your specific use case.

---

## 📋 Current Model Architecture

```python
# Input: 30-day normalized prices
model = Sequential([
    LSTM(50, activation='relu', input_shape=(30, 1), return_sequences=True),
    Dropout(0.2),
    LSTM(50, activation='relu', return_sequences=False),
    Dropout(0.2),
    Dense(25, activation='relu'),
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
```

---

## 🎛️ Key Hyperparameters

### 1. Lookback Window (Currently: 30 days)

**What it does:** Number of previous days used to predict the next day

**In the code:**
```python
lookback = 30
for i in range(lookback, len(scaled_prices)):
    X.append(scaled_prices[i-lookback:i, 0])
```

**Effect of Different Values:**
| Lookback | Use Case | Pros | Cons |
|----------|----------|------|------|
| 10 | Quick reactions | Fast, captures short-term | Ignores longer patterns |
| 20 | Balanced | Good for day traders | May miss weekly patterns |
| **30** | **Recommended** | Captures monthly patterns | Default, proven effective |
| 60 | Long-term | Captures 2-month trends | Slower, overfits on old data |
| 90+ | Trend trading | Long-term patterns | Very slow, requires tons of data |

**How to Change:**
```python
# In ml_service_enhanced.py, line 46
lookback = 30  # Change this value

# Then update the model input shape:
# input_shape=(lookback, 1)
```

**When to Change:**
- **Increase to 60** if stock has strong weekly/monthly patterns
- **Decrease to 20** if stock reacts quickly to news
- **Keep at 30** for most stocks (balanced approach)

---

### 2. LSTM Units (Currently: 50)

**What it does:** Number of "memory cells" in each LSTM layer. More = more capacity to learn patterns.

**In the code:**
```python
LSTM(50, activation='relu', ...)  # 50 units
```

**Effect of Different Values:**
| Units | Training Time | Memory | Accuracy | Risk |
|-------|---------------|--------|----------|------|
| 25 | 30 seconds | Low | ~80% | Underfitting |
| **50** | **1-2 min** | **Moderate** | **~85%** | **Balanced** |
| 100 | 3-4 min | High | ~87% | Overfitting |
| 200 | 5+ min | Very High | ~88% | Overfitting |

**How to Change:**
```python
# In ml_service_enhanced.py
LSTM(100, activation='relu', ...)  # Try 100 units
```

**When to Change:**
- **Increase to 100** if model underfits (test_mae > 3.0)
- **Decrease to 25** if training is too slow
- **Keep at 50** for quick training with good accuracy

---

### 3. Dropout Rate (Currently: 0.2)

**What it does:** Prevents overfitting by randomly disabling 20% of neurons during training

**In the code:**
```python
Dropout(0.2)  # Drop 20% of connections
```

**Effect of Different Values:**
| Dropout | Overfitting | Training | Generalization |
|---------|-----------|----------|-----------------|
| 0.0 | High ⚠️ | Fast | Poor |
| 0.1 | Moderate | Fast | Good |
| **0.2** | **Low** | **Balanced** | **Excellent** |
| 0.3 | Very Low | Slower | Excellent |
| 0.5 | Too Much | Slow | Underfitting |

**How to Change:**
```python
# In ml_service_enhanced.py
Dropout(0.25)  # Slightly more aggressive regularization
```

**When to Change:**
- **Increase to 0.3** if test_mae >> train_mae (overfitting)
- **Decrease to 0.1** if test_mae and train_mae are similar but high (underfitting)
- **Keep at 0.2** for most cases

---

### 4. Learning Rate (Currently: 0.001)

**What it does:** Controls how quickly the model updates weights. Affects convergence speed and stability.

**In the code:**
```python
optimizer=Adam(learning_rate=0.001)
```

**Effect of Different Values:**
| Learning Rate | Convergence | Stability | Final Loss |
|---------------|-------------|-----------|-----------|
| 0.0001 | Very Slow | Very Stable | Good |
| **0.001** | **Balanced** | **Stable** | **Good** |
| 0.01 | Fast | Unstable | Poor |
| 0.1 | Very Fast | Unstable | Poor |

**How to Change:**
```python
optimizer=Adam(learning_rate=0.0005)  # More conservative
optimizer=Adam(learning_rate=0.002)   # More aggressive
```

**When to Change:**
- **Decrease to 0.0001** if loss is fluctuating (unstable)
- **Increase to 0.002** if training is too slow
- **Keep at 0.001** for reliability

---

### 5. Batch Size (Currently: 32)

**What it does:** Number of samples processed before updating weights. Larger = more stable but slower.

**In the code:**
```python
model.fit(X_train, y_train, batch_size=32, ...)
```

**Effect of Different Values:**
| Batch Size | Memory | Speed | Stability |
|-----------|--------|-------|-----------|
| 8 | Low | Slow | Unstable |
| 16 | Low | Slow | Moderate |
| **32** | **Moderate** | **Balanced** | **Good** |
| 64 | High | Fast | Stable |
| 128 | Very High | Very Fast | Very Stable |

**How to Change:**
```python
model.fit(X_train, y_train, batch_size=16, ...)
```

**When to Change:**
- **Decrease to 16** if GPU memory is limited
- **Increase to 64** for more stable training
- **Keep at 32** for balance

---

### 6. Epochs (Currently: 50)

**What it does:** Number of times the model sees the entire training dataset

**In the code:**
```python
model.fit(X_train, y_train, epochs=50, ...)
```

**Effect of Different Values:**
| Epochs | Training Time | Underfitting | Overfitting |
|--------|---------------|-------------|-----------|
| 10 | 30 sec | Possible ⚠️ | No |
| 30 | 1 min | Unlikely | Low |
| **50** | **2 min** | **No** | **Minimal** |
| 100 | 4 min | No | Likely ⚠️ |
| 200 | 8 min | No | Very Likely ⚠️ |

**How to Change:**
```python
model.fit(X_train, y_train, epochs=100, ...)
```

**When to Change:**
- **Increase to 100** if val_loss still decreasing at epoch 50
- **Decrease to 30** if val_loss increases (overfitting)
- **Keep at 50** default
- **Note:** Early stopping prevents overfitting automatically!

---

## 🔍 Optimization Strategies

### Strategy 1: Improve Accuracy (Test MAE > 2.0)

```python
# Increase model capacity
LSTM(100, ...)  # More units
lookback = 60   # Longer context
Dropout(0.1)    # Less regularization
epochs = 100    # More training
```

**Expected Result:** MAE decreases from ~2.5 to ~1.5

---

### Strategy 2: Prevent Overfitting (Test MAE >> Train MAE)

```python
# Reduce model complexity
LSTM(25, ...)   # Fewer units
Dropout(0.3)    # More regularization
learning_rate=0.0005  # More conservative
batch_size=64   # Larger batches
```

**Expected Result:** Test loss becomes closer to training loss

---

### Strategy 3: Speed Up Training (Takes >5 seconds)

```python
lookback = 20   # Shorter sequences
LSTM(25, ...)   # Fewer units
epochs = 30     # Fewer epochs
batch_size = 64 # Larger batches
```

**Expected Result:** Training time drops from 2min to 30sec

---

### Strategy 4: Handle Volatile Stocks (Wide confidence intervals)

```python
# Increase look-back to capture volatility better
lookback = 60

# Increase dropout for more stable estimates
Dropout(0.3)

# More training to find patterns
epochs = 100
```

**Expected Result:** More stable predictions despite volatility

---

## 🧪 How to Tune for Your Case

### Step 1: Understand Current Performance
```bash
python test_lstm_prediction.py --ticker YOUR_TICKER
```

Look for:
- `test_mae`: Prediction error in dollars
- `confidence_interval_std`: Width of confidence bands

**Targets:**
- MAE < 1.0: Excellent
- MAE 1-2: Good
- MAE 2-3: Fair (consider Prophet)
- MAE > 3: Poor (increase training data)

---

### Step 2: Identify the Problem

**Problem: Underfitting (MAE too high on both train and test)**
```
Training MAE: 2.5
Test MAE: 2.6
→ Model not learning patterns
```

**Solution:**
```python
# Increase capacity
LSTM(100, ...)
lookback = 60
epochs = 100
Dropout(0.1)
```

---

**Problem: Overfitting (Test MAE >> Training MAE)**
```
Training MAE: 0.5
Test MAE: 3.2
→ Model memorizing training data
```

**Solution:**
```python
# Reduce complexity
LSTM(25, ...)
Dropout(0.3)
learning_rate = 0.0001
batch_size = 64
```

---

**Problem: Slow Training (>5 seconds)**

**Solution:**
```python
lookback = 20
LSTM(25, ...)
batch_size = 64
epochs = 30
```

---

### Step 3: Modify ml_service_enhanced.py

```python
# Find the predict_price_lstm function (around line 30)
# Change these parameters:

lookback = 30  # ← Adjust this
# ...
LSTM(50, ...)  # ← Adjust unit count
# ...
Dropout(0.2)   # ← Adjust dropout
# ...
Adam(learning_rate=0.001)  # ← Adjust learning rate
# ...
epochs=50      # ← Adjust epochs
batch_size=32  # ← Adjust batch size
```

---

### Step 4: Test & Validate

```bash
# Reinstall if you changed dependencies
pip install -r requirements.txt

# Test new configuration
python test_lstm_prediction.py --ticker YOUR_TICKER

# Compare with old results
# Is MAE better? Is it faster? Is test loss stable?
```

---

## 📊 Hyperparameter Tuning Checklist

| Parameter | Default | Tuning Range | Recommendation |
|-----------|---------|--------------|-----------------|
| Lookback | 30 | 10-90 | 20-60 for most stocks |
| LSTM Units | 50 | 25-200 | 50-100 for balance |
| Dropout | 0.2 | 0.1-0.5 | 0.2 for reliability |
| Learning Rate | 0.001 | 0.0001-0.01 | 0.001 for stability |
| Batch Size | 32 | 16-64 | 32-64 for balance |
| Epochs | 50 | 30-100 | 50-75 with early stopping |
| Dense Units | 25 | 10-50 | 25 for light networks |

---

## 🚀 Advanced Techniques

### Technique 1: Custom Callbacks for Monitoring
```python
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001)

model.fit(
    X_train, y_train,
    callbacks=[early_stop, reduce_lr],
    epochs=100,
    ...
)
```

---

### Technique 2: Ensemble with Different Lookback Windows
```python
def predict_price_lstm_ensemble(ticker, days=7):
    """Ensemble LSTM with multiple lookback windows"""
    predictions = []
    
    for lookback in [20, 30, 60]:
        pred = predict_with_lookback(ticker, days, lookback)
        predictions.append(pred)
    
    # Average them
    return ensemble_predictions(predictions)
```

---

### Technique 3: Stock-Specific Models
```python
def predict_with_stock_specific_params(ticker, days=7):
    """Use different params for different stocks"""
    
    if ticker in ["SPY", "QQQ"]:  # ETFs - stable
        lookback, units = 20, 25
    elif ticker in ["TSLA", "GME"]:  # Volatile
        lookback, units = 60, 100
    else:  # Default
        lookback, units = 30, 50
    
    return predict_price_lstm_with_params(ticker, days, lookback, units)
```

---

## 📈 Monitoring Training

### Watch These Metrics

**Good Training:**
```
Epoch 1/50: loss: 0.0245, val_loss: 0.0235
Epoch 10/50: loss: 0.0156, val_loss: 0.0168
Epoch 30/50: loss: 0.0098, val_loss: 0.0102
Epoch 50/50: loss: 0.0087, val_loss: 0.0095
→ Both decreasing smoothly ✓
```

**Overfitting:**
```
Epoch 1/50: loss: 0.0245, val_loss: 0.0235
Epoch 20/50: loss: 0.0050, val_loss: 0.0198
Epoch 40/50: loss: 0.0012, val_loss: 0.0289
Epoch 50/50: loss: 0.0001, val_loss: 0.0412
→ val_loss increasing = overfitting ⚠️
Solution: Increase dropout, add early stopping
```

**Underfitting:**
```
Epoch 10/50: loss: 0.0245, val_loss: 0.0243
Epoch 20/50: loss: 0.0244, val_loss: 0.0244
Epoch 50/50: loss: 0.0243, val_loss: 0.0243
→ No improvement = underfitting ⚠️
Solution: Increase units, increase epochs
```

---

## 🎯 Quick Recipes

### Recipe 1: Fast Training (For Development)
```python
lookback = 20
LSTM(25, ...)
Dropout(0.1)
epochs = 30
batch_size = 64
```
**Time:** 30 seconds | **Accuracy:** ~80%

---

### Recipe 2: Balanced (Recommended)
```python
lookback = 30
LSTM(50, ...)
Dropout(0.2)
epochs = 50
batch_size = 32
```
**Time:** 2 minutes | **Accuracy:** ~85%

---

### Recipe 3: High Accuracy (For Production)
```python
lookback = 60
LSTM(100, ...)
Dropout(0.15)
epochs = 100
batch_size = 16
```
**Time:** 5+ minutes | **Accuracy:** ~90%

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Tuning on Test Set
```python
# WRONG: Tune hyperparameters while watching test loss
for lookback in [20, 30, 60]:
    pred = model.predict(X_test)  # ← Don't do this!
```

**Why:** You'll overfit to the test set

**Fix:** Use cross-validation instead

---

### ❌ Mistake 2: Using Too Many Epochs
```python
# WRONG: Running for 1000 epochs
model.fit(..., epochs=1000)
```

**Why:** Massive overfitting, waste of time

**Fix:** Use early stopping (already in code)

---

### ❌ Mistake 3: Not Normalizing Data
```python
# WRONG: Feeding raw prices
model.fit(prices_raw, ...)
```

**Why:** Neural networks hate large numbers

**Fix:** Normalize to 0-1 range (already done in code)

---

## 📚 Further Reading

- **LSTM Fundamentals:** https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- **Keras Tuning:** https://keras.io/api/models/model_training_apis/
- **Time Series with TensorFlow:** https://www.tensorflow.org/tutorials/structured_data/time_series

---

**Last Updated:** 2026-01-27
**Version:** 1.0
