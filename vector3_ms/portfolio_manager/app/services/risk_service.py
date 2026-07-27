import numpy as np
import pandas as pd
from app.database.connection import get_db

def calculate_volatility(ticker: str, days: int = 252, db=None) -> float:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)
    sql = "SELECT close FROM price_history WHERE ticker = %s ORDER BY date DESC LIMIT %s"
    cursor.execute(sql, (ticker, days))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    if len(rows) < 2:
        return 0.15

    prices = [row["close"] for row in reversed(rows)]
    returns = np.diff(prices) / np.array(prices[:-1])
    volatility = np.std(returns) * np.sqrt(252)

    return float(volatility)

def calculate_sharpe_ratio(portfolio_id: int, risk_free_rate: float = 0.03, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT date, total_value FROM portfolio_performance
    WHERE portfolio_id = %s
    ORDER BY date ASC
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    if len(rows) < 2:
        return {"error": "Insufficient performance data"}

    values = [row["total_value"] for row in rows]
    returns = np.diff(values) / np.array(values[:-1])
    annual_return = np.mean(returns) * 252
    annual_volatility = np.std(returns) * np.sqrt(252)

    sharpe = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0

    return {
        "portfolio_id": portfolio_id,
        "sharpe_ratio": float(sharpe),
        "annual_return": float(annual_return),
        "annual_volatility": float(annual_volatility)
    }

def calculate_var(portfolio_id: int, confidence: float = 0.95, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT date, total_value FROM portfolio_performance
    WHERE portfolio_id = %s
    ORDER BY date ASC LIMIT 252
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    if len(rows) < 10:
        return {"error": "Insufficient data for VaR calculation"}

    values = [row["total_value"] for row in rows]
    returns = np.diff(values) / np.array(values[:-1])

    var = np.percentile(returns, (1 - confidence) * 100)
    current_value = values[-1]
    var_amount = abs(var * current_value)

    return {
        "portfolio_id": portfolio_id,
        "confidence_level": confidence,
        "var_percent": float(var),
        "var_amount": float(var_amount),
        "current_value": float(current_value),
        "interpretation": f"There is a {confidence*100:.0f}% chance the portfolio will not lose more than ${var_amount:.2f} in one day"
    }

def calculate_max_drawdown(portfolio_id: int, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT date, total_value FROM portfolio_performance
    WHERE portfolio_id = %s
    ORDER BY date ASC
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    if len(rows) < 2:
        return {"error": "Insufficient data"}

    values = np.array([row["total_value"] for row in rows])
    cummax = np.maximum.accumulate(values)
    drawdown = (values - cummax) / cummax
    max_drawdown = float(np.min(drawdown))

    return {
        "portfolio_id": portfolio_id,
        "max_drawdown": max_drawdown,
        "max_drawdown_percent": max_drawdown * 100,
        "interpretation": f"Maximum peak-to-trough decline was {abs(max_drawdown * 100):.2f}%"
    }

def correlation_matrix(portfolio_id: int, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT DISTINCT a.ticker
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    tickers = [row["ticker"] for row in cursor.fetchall()]

    if len(tickers) < 2:
        cursor.close()
        db.close()
        return {"error": "Need at least 2 assets for correlation"}

    prices_dict = {}
    for ticker in tickers:
        sql = "SELECT close FROM price_history WHERE ticker = %s ORDER BY date ASC LIMIT 252"
        cursor.execute(sql, (ticker,))
        prices = [row[0] for row in cursor.fetchall()]
        if prices:
            prices_dict[ticker] = prices

    cursor.close()
    db.close()

    common_length = min(len(p) for p in prices_dict.values()) if prices_dict else 0
    if common_length < 2:
        return {"error": "Insufficient price history"}

    aligned_prices = {t: np.array(p[-common_length:]) for t, p in prices_dict.items()}
    returns = {}
    for ticker, prices in aligned_prices.items():
        ret = np.diff(prices) / prices[:-1]
        returns[ticker] = ret

    df = pd.DataFrame(returns)
    corr_matrix = df.corr().to_dict()

    return {
        "portfolio_id": portfolio_id,
        "tickers": tickers,
        "correlation_matrix": corr_matrix
    }
