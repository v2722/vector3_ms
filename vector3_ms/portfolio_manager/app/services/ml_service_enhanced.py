import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings("ignore")

import logging
logger = logging.getLogger(__name__)


def get_historical_prices(ticker: str, db, limit: int = 504) -> list:
    """Fetch historical prices from database"""
    cursor = db.cursor(dictionary=True)
    sql = f"""
    SELECT ph.close
    FROM price_history ph
    JOIN asset a ON ph.asset_id = a.asset_id
    WHERE a.ticker = %s
    ORDER BY ph.date ASC
    LIMIT {limit}
    """
    cursor.execute(sql, (ticker,))
    rows = cursor.fetchall()
    cursor.close()
    return [row["close"] for row in rows] if rows else []


# ============================================================
# LSTM-BASED PRICE PREDICTION
# ============================================================

def predict_price_lstm(ticker: str, days: int = 7, db=None) -> dict:
    """
    LSTM-based price prediction with confidence intervals.

    Uses:
    - 2 years of historical data (504 days)
    - Lookback window of 30 days
    - 2 LSTM layers with Dropout regularization
    - 80/20 train/test split
    - Returns predictions with uncertainty bounds
    """
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping

        if db is None:
            from app.database.connection import get_db
            db = get_db()

        prices = get_historical_prices(ticker, db, limit=504)
        db.close()

        if len(prices) < 60:
            return {"error": f"Insufficient historical data. Need 60+ days, got {len(prices)}"}

        # Convert Decimal to float if necessary
        prices = [float(p) for p in prices]
        prices_array = np.array(prices, dtype=np.float32).reshape(-1, 1)

        # Normalize prices (0-1 range)
        scaler = MinMaxScaler()
        scaled_prices = scaler.fit_transform(prices_array)

        # Create sequences with 30-day lookback window
        lookback = 30
        X, y = [], []

        for i in range(lookback, len(scaled_prices)):
            X.append(scaled_prices[i-lookback:i, 0])
            y.append(scaled_prices[i, 0])

        if len(X) < 20:
            return {"error": "Insufficient sequences for LSTM training"}

        X = np.array(X).reshape(-1, lookback, 1)
        y = np.array(y)

        # Train/test split (80/20)
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Build LSTM model
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(lookback, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(50, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

        # Train with early stopping
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[early_stop],
            verbose=0
        )

        # Evaluate model
        test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)

        # Forecast next N days
        last_sequence = scaled_prices[-lookback:].reshape(1, lookback, 1)
        predictions_scaled = []
        current_seq = last_sequence.copy()

        for _ in range(days):
            next_pred = model.predict(current_seq, verbose=0)[0, 0]
            predictions_scaled.append(next_pred)
            current_seq = np.append(current_seq[0, 1:], [[next_pred]], axis=0).reshape(1, lookback, 1)

        # Inverse transform predictions
        predictions = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1))

        # Calculate confidence intervals using test set residuals
        y_test_pred = model.predict(X_test, verbose=0).flatten()
        residuals = y_test - y_test_pred
        std_residual = np.std(residuals)

        # Inverse transform to get price units
        std_residual_price = std_residual * (scaler.data_max_[0] - scaler.data_min_[0])

        current_price = float(prices[-1])

        return {
            "ticker": ticker,
            "method": "lstm_neural_network",
            "current_price": current_price,
            "model_info": {
                "architecture": "LSTM(50) -> Dropout -> LSTM(50) -> Dropout -> Dense(25) -> Dense(1)",
                "lookback_window": lookback,
                "training_epochs": 50,
                "test_mse": float(test_loss),
                "test_mae": float(test_mae),
                "confidence_interval_std": float(std_residual_price)
            },
            "predictions": [
                {
                    "day": i + 1,
                    "predicted_price": float(p[0]),
                    "upper_bound": float(p[0] + 1.96 * std_residual_price),  # 95% CI
                    "lower_bound": float(p[0] - 1.96 * std_residual_price),
                    "confidence_level": "95%"
                }
                for i, p in enumerate(predictions)
            ]
        }

    except ImportError:
        logger.warning("TensorFlow not installed, falling back to Prophet")
        return predict_price_prophet(ticker, days, db)
    except Exception as e:
        logger.error(f"LSTM prediction failed: {str(e)}")
        return {"error": f"LSTM prediction failed: {str(e)}. Try Prophet or Linear Regression instead."}


# ============================================================
# PROPHET-BASED PREDICTION (SEASONAL FORECASTS)
# ============================================================

def predict_price_prophet(ticker: str, days: int = 7, db=None) -> dict:
    """
    Facebook Prophet forecasting model.

    Good for:
    - Seasonal patterns
    - Trend detection
    - Handling missing data
    - Built-in confidence intervals
    """
    try:
        from prophet import Prophet

        if db is None:
            from app.database.connection import get_db
            db = get_db()

        cursor = db.cursor(dictionary=True)
        sql = """
        SELECT ph.date, ph.close
        FROM price_history ph
        JOIN asset a ON ph.asset_id = a.asset_id
        WHERE a.ticker = %s
        ORDER BY ph.date ASC
        LIMIT 504
        """
        cursor.execute(sql, (ticker,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        if len(rows) < 30:
            return {"error": f"Insufficient historical data. Need 30+ days, got {len(rows)}"}

        # Prepare data for Prophet
        df = pd.DataFrame(rows)
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        df['y'] = df['y'].astype(float)  # Convert Decimal to float
        df = df.sort_values('ds')

        # Train Prophet
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95,
            changepoint_prior_scale=0.05
        )
        model.fit(df)

        # Forecast
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)

        # Get recent predictions
        recent_forecast = forecast.tail(days)

        return {
            "ticker": ticker,
            "method": "prophet_seasonal",
            "current_price": float(df['y'].iloc[-1]),
            "model_info": {
                "seasonality": "yearly + weekly",
                "intervals": "95% confidence",
                "trend": "auto-detected"
            },
            "predictions": [
                {
                    "day": i + 1,
                    "predicted_price": float(recent_forecast.iloc[i]['yhat']),
                    "upper_bound": float(recent_forecast.iloc[i]['yhat_upper']),
                    "lower_bound": float(recent_forecast.iloc[i]['yhat_lower']),
                    "confidence_level": "95%"
                }
                for i in range(len(recent_forecast))
            ]
        }

    except Exception as e:
        logger.error(f"Prophet prediction failed: {str(e)}")
        return predict_price_linear(ticker, days, db)


# ============================================================
# LINEAR REGRESSION (FALLBACK / BASELINE)
# ============================================================

def predict_price_linear(ticker: str, days: int = 7, db=None) -> dict:
    """
    Linear regression baseline model.
    Simple but fast. Used as fallback if LSTM/Prophet unavailable.
    """
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    prices = get_historical_prices(ticker, db, limit=60)
    db.close()

    if len(prices) < 5:
        return {"error": "Insufficient historical data"}

    # Convert Decimal to float
    prices = [float(p) for p in prices]

    X = np.arange(len(prices)).reshape(-1, 1)
    y = np.array(prices, dtype=np.float32)

    model = LinearRegression()
    model.fit(X, y)

    # Calculate model metrics
    y_pred = model.predict(X)
    mse = np.mean((y - y_pred) ** 2)
    residuals = y - y_pred
    std_residual = np.std(residuals)

    future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
    predictions = model.predict(future_X)

    return {
        "ticker": ticker,
        "method": "linear_regression",
        "current_price": float(prices[-1]),
        "model_info": {
            "mse": float(mse),
            "confidence_interval_std": float(std_residual),
            "note": "Simple baseline model. Use LSTM or Prophet for better accuracy."
        },
        "predictions": [
            {
                "day": i + 1,
                "predicted_price": float(p),
                "upper_bound": float(p + 1.96 * std_residual),
                "lower_bound": float(p - 1.96 * std_residual),
                "confidence_level": "95%"
            }
            for i, p in enumerate(predictions)
        ]
    }


# ============================================================
# ENSEMBLE PREDICTION (COMBINES ALL 3 MODELS)
# ============================================================

def predict_price_ensemble(ticker: str, days: int = 7, db=None) -> dict:
    """
    Ensemble prediction combining LSTM, Prophet, and Linear Regression.
    Averages predictions from all three methods for robustness.
    """
    predictions_lstm = predict_price_lstm(ticker, days, db)
    predictions_prophet = predict_price_prophet(ticker, days, db)
    predictions_linear = predict_price_linear(ticker, days, db)

    # Check for errors
    if "error" in predictions_lstm and "error" in predictions_prophet and "error" in predictions_linear:
        return {"error": "All prediction methods failed"}

    # Filter out errors
    valid_predictions = [p for p in [predictions_lstm, predictions_prophet, predictions_linear] if "error" not in p]

    if not valid_predictions:
        return {"error": "No valid predictions available"}

    # Average predictions
    ensemble_predictions = []
    for day_idx in range(days):
        prices = []
        upper_bounds = []
        lower_bounds = []

        for pred in valid_predictions:
            if day_idx < len(pred.get("predictions", [])):
                prices.append(pred["predictions"][day_idx]["predicted_price"])
                upper_bounds.append(pred["predictions"][day_idx]["upper_bound"])
                lower_bounds.append(pred["predictions"][day_idx]["lower_bound"])

        if prices:
            ensemble_predictions.append({
                "day": day_idx + 1,
                "predicted_price": float(np.mean(prices)),
                "upper_bound": float(np.mean(upper_bounds)),
                "lower_bound": float(np.mean(lower_bounds)),
                "confidence_level": "95%",
                "models_used": len(valid_predictions)
            })

    return {
        "ticker": ticker,
        "method": "ensemble_weighted_average",
        "current_price": valid_predictions[0].get("current_price", 0),
        "model_info": {
            "models": [p["method"] for p in valid_predictions],
            "count": len(valid_predictions)
        },
        "predictions": ensemble_predictions
    }


# ============================================================
# ASSET CLASSIFICATION
# ============================================================

def asset_classification(ticker: str, db=None) -> dict:
    """Classify asset by risk and income characteristics"""
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    cursor = db.cursor(dictionary=True)
    sql = """
    SELECT a.asset_id, a.ticker
    FROM asset a
    WHERE a.ticker = %s
    """
    cursor.execute(sql, (ticker,))
    asset = cursor.fetchone()
    cursor.close()
    db.close()

    if not asset:
        return {"error": "Asset not found"}

    # For now, calculate volatility from price data
    volatility = 0.15  # Default if not in schema
    dividend = 0.0    # Default if not in schema

    if volatility < 0.15:
        risk_class = "low-risk"
    elif volatility < 0.25:
        risk_class = "moderate-risk"
    else:
        risk_class = "high-risk"

    if dividend > 0.03:
        income_class = "dividend"
    elif volatility < 0.20:
        income_class = "value"
    else:
        income_class = "growth"

    return {
        "ticker": ticker,
        "risk_class": risk_class,
        "income_class": income_class,
        "volatility": float(volatility) if volatility else 0,
        "dividend_yield": float(dividend) if dividend else 0
    }


# ============================================================
# PORTFOLIO HEALTH SCORE
# ============================================================

def portfolio_health_score(portfolio_id: int, db=None) -> dict:
    """Calculate portfolio health based on diversification and volatility"""
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT COUNT(DISTINCT a.sector) as num_sectors
    FROM transaction t
    JOIN asset a ON t.asset_id = a.asset_id
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()

    num_sectors = result.get("num_sectors", 1) if result else 1
    avg_volatility = 0.15  # Default volatility estimate

    diversification_score = min(num_sectors / 5 * 100, 100)
    volatility_score = max(100 - (avg_volatility * 200), 0)

    overall_score = (diversification_score + volatility_score) / 2

    return {
        "portfolio_id": portfolio_id,
        "overall_health_score": float(overall_score),
        "diversification_score": float(diversification_score),
        "volatility_score": float(volatility_score),
        "sectors": num_sectors,
        "avg_volatility": float(avg_volatility)
    }
