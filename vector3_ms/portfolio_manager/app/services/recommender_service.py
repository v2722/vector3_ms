import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.database.connection import get_db

def content_based_recommendations(ticker: str, limit: int = 5, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT sector, industry, volatility FROM asset WHERE ticker = %s", (ticker,))
    asset = cursor.fetchone()

    if not asset:
        cursor.close()
        db.close()
        return {"error": "Asset not found"}

    sector = asset["sector"]
    industry = asset["industry"]
    volatility = asset["volatility"] or 0.15

    sql = """
    SELECT ticker, name, sector, volatility
    FROM asset
    WHERE ticker != %s AND sector = %s
    ORDER BY ABS(volatility - %s) ASC
    LIMIT %s
    """
    cursor.execute(sql, (ticker, sector, volatility, limit))
    recommendations = cursor.fetchall()
    cursor.close()
    db.close()

    return {
        "input_asset": ticker,
        "method": "content_based",
        "recommendations": [
            {
                "ticker": r["ticker"],
                "name": r["name"],
                "reason": f"Similar sector ({sector}) and volatility"
            }
            for r in recommendations
        ]
    }

def diversification_recommendations(portfolio_id: int, limit: int = 5, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT DISTINCT a.sector, COUNT(*) as count
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    GROUP BY a.sector
    ORDER BY count DESC
    """
    cursor.execute(sql, (portfolio_id,))
    sectors = cursor.fetchall()

    if not sectors:
        cursor.close()
        db.close()
        return {"error": "Portfolio has no holdings"}

    overrepresented_sector = sectors[0]["sector"] if sectors else None

    sql = """
    SELECT ticker, name, sector, volatility
    FROM asset
    WHERE sector != %s AND volatility < 0.25
    ORDER BY RAND()
    LIMIT %s
    """
    cursor.execute(sql, (overrepresented_sector, limit))
    recommendations = cursor.fetchall()
    cursor.close()
    db.close()

    return {
        "portfolio_id": portfolio_id,
        "method": "diversification",
        "overrepresented_sector": overrepresented_sector,
        "recommendations": [
            {
                "ticker": r["ticker"],
                "name": r["name"],
                "reason": f"Different sector to reduce concentration in {overrepresented_sector}"
            }
            for r in recommendations
        ]
    }

def collaborative_filtering(user_id: int, limit: int = 5, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT DISTINCT a.ticker, a.name
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id IN (
        SELECT id FROM portfolio WHERE user_id != %s LIMIT 10
    )
    AND a.ticker NOT IN (
        SELECT a2.ticker FROM transaction t2
        JOIN asset a2 ON t2.asset_id = a2.id
        WHERE t2.portfolio_id IN (SELECT id FROM portfolio WHERE user_id = %s)
    )
    ORDER BY RAND()
    LIMIT %s
    """
    cursor.execute(sql, (user_id, user_id, limit))
    recommendations = cursor.fetchall()
    cursor.close()
    db.close()

    return {
        "user_id": user_id,
        "method": "collaborative_filtering",
        "recommendations": [
            {
                "ticker": r["ticker"],
                "name": r["name"],
                "reason": "Popular among similar investors"
            }
            for r in recommendations
        ]
    }
