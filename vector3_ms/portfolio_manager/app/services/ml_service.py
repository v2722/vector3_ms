import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings("ignore")

def get_historical_prices(ticker: str, db) -> list:
    cursor = db.cursor(dictionary=True)
    sql = "SELECT close FROM price_history WHERE ticker = %s ORDER BY date ASC LIMIT 60"
    cursor.execute(sql, (ticker,))
    rows = cursor.fetchall()
    cursor.close()
    return [row["close"] for row in rows] if rows else []

def predict_price_linear(ticker: str, days: int = 7, db=None) -> dict:
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    prices = get_historical_prices(ticker, db)
    db.close()

    if len(prices) < 5:
        return {"error": "Insufficient historical data"}

    X = np.arange(len(prices)).reshape(-1, 1)
    y = np.array(prices)

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
    predictions = model.predict(future_X)

    return {
        "ticker": ticker,
        "method": "linear_regression",
        "current_price": float(prices[-1]),
        "predictions": [{"day": i + 1, "predicted_price": float(p)} for i, p in enumerate(predictions)]
    }

def asset_classification(ticker: str, db=None) -> dict:
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    cursor = db.cursor(dictionary=True)
    sql = "SELECT volatility, dividend_yield FROM asset WHERE ticker = %s"
    cursor.execute(sql, (ticker,))
    asset = cursor.fetchone()
    cursor.close()
    db.close()

    if not asset:
        return {"error": "Asset not found"}

    volatility = asset.get("volatility", 0)
    dividend = asset.get("dividend_yield", 0)

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

def portfolio_health_score(portfolio_id: int, db=None) -> dict:
    if db is None:
        from app.database.connection import get_db
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT COUNT(DISTINCT a.sector) as num_sectors, AVG(a.volatility) as avg_volatility
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()

    num_sectors = result.get("num_sectors", 1)
    avg_volatility = result.get("avg_volatility", 0.15)

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
