import numpy as np
import pandas as pd
from scipy.optimize import minimize
from app.database.connection import get_db

def efficient_frontier(portfolio_id: int, num_portfolios: int = 10000, db=None) -> dict:
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
        return {"error": "Need at least 2 assets"}

    prices_dict = {}
    for ticker in tickers:
        sql = """
        SELECT ph.close
        FROM price_history ph
        JOIN asset a ON ph.asset_id = a.asset_id
        WHERE a.ticker = %s
        ORDER BY ph.date DESC
        LIMIT 252
        """
        cursor.execute(sql, (ticker,))
        prices = [row["close"] for row in cursor.fetchall()]
        if prices:
            prices_dict[ticker] = list(reversed(prices))

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
    mean_returns = df.mean() * 252
    cov_matrix = df.cov() * 252

    n_assets = len(tickers)
    results = []

    for _ in range(num_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)

        portfolio_return = np.sum(mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0

        results.append({
            "weights": {tickers[i]: float(weights[i]) for i in range(n_assets)},
            "return": float(portfolio_return),
            "volatility": float(portfolio_vol),
            "sharpe": float(sharpe)
        })

    results_sorted = sorted(results, key=lambda x: x["sharpe"], reverse=True)

    return {
        "portfolio_id": portfolio_id,
        "efficient_frontier": results_sorted[:100],
        "optimal_portfolio": results_sorted[0] if results_sorted else None,
        "num_simulations": num_portfolios
    }

def optimal_allocation(portfolio_id: int, db=None) -> dict:
    if db is None:
        db = get_db()

    frontier = efficient_frontier(portfolio_id, num_portfolios=5000, db=db)

    if "error" in frontier:
        return frontier

    optimal = frontier["optimal_portfolio"]

    return {
        "portfolio_id": portfolio_id,
        "optimization_method": "maximum_sharpe_ratio",
        "optimal_weights": optimal["weights"],
        "expected_return": optimal["return"],
        "expected_volatility": optimal["volatility"],
        "expected_sharpe_ratio": optimal["sharpe"]
    }

def risk_parity(portfolio_id: int, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT DISTINCT a.ticker, a.volatility
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    assets = cursor.fetchall()
    cursor.close()
    db.close()

    if len(assets) < 2:
        return {"error": "Need at least 2 assets"}

    volatilities = [a["volatility"] or 0.15 for a in assets]
    inv_volatilities = 1 / np.array(volatilities)
    weights = inv_volatilities / np.sum(inv_volatilities)

    return {
        "portfolio_id": portfolio_id,
        "method": "risk_parity",
        "weights": {assets[i]["ticker"]: float(weights[i]) for i in range(len(assets))},
        "note": "Equal risk contribution from each asset"
    }

def monte_carlo_simulation(portfolio_id: int, days: int = 252, num_simulations: int = 1000, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT SUM(t.quantity * t.price) as portfolio_value
    FROM transaction t
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    result = cursor.fetchone()
    initial_value = result["portfolio_value"] if result["portfolio_value"] else 10000

    sql = """
    SELECT DISTINCT a.ticker, COALESCE(a.volatility, 0.15) as volatility
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    """
    cursor.execute(sql, (portfolio_id,))
    assets = cursor.fetchall()

    if not assets:
        cursor.close()
        db.close()
        return {"error": "Portfolio has no assets"}

    avg_volatility = np.mean([a["volatility"] for a in assets])
    cursor.close()
    db.close()

    simulations = []
    for _ in range(num_simulations):
        path = np.zeros(days)
        path[0] = initial_value
        for t in range(1, days):
            drift = 0.05
            random_return = np.random.normal(drift / 252, avg_volatility / np.sqrt(252))
            path[t] = path[t - 1] * (1 + random_return)
        simulations.append(path)

    simulations = np.array(simulations)
    final_values = simulations[:, -1]

    return {
        "portfolio_id": portfolio_id,
        "initial_value": float(initial_value),
        "days": days,
        "num_simulations": num_simulations,
        "expected_final_value": float(np.mean(final_values)),
        "std_final_value": float(np.std(final_values)),
        "min_final_value": float(np.min(final_values)),
        "max_final_value": float(np.max(final_values)),
        "percentile_5": float(np.percentile(final_values, 5)),
        "percentile_95": float(np.percentile(final_values, 95))
    }
