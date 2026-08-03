import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.database.connection import get_db

def content_based_recommendations(ticker: str, limit: int = 5, db=None) -> dict:
    if db is None:
        db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT sector, industry FROM asset WHERE ticker = %s", (ticker,))
    asset = cursor.fetchone()

    if not asset:
        cursor.close()
        db.close()
        return {"error": "Asset not found"}

    sector = asset["sector"]
    industry = asset["industry"]

    sql = """
    SELECT ticker, name, sector, industry
    FROM asset
    WHERE ticker != %s AND sector = %s
    LIMIT %s
    """
    cursor.execute(sql, (ticker, sector, limit))
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
                "reason": f"Similar sector ({sector}) and industry ({r['industry']})"
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
    JOIN asset a ON t.asset_id = a.asset_id
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
    SELECT ticker, name, sector
    FROM asset
    WHERE sector != %s
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

    # Portfolio holdings of the user (or target portfolio)
    cursor.execute(
        "SELECT DISTINCT a.ticker FROM transaction t "
        "JOIN asset a ON t.asset_id = a.asset_id "
        "WHERE t.portfolio_id = %s",
        (user_id,)
    )
    held = {row["ticker"] for row in cursor.fetchall()}

    placeholders = ",".join(["%s"] * len(held)) if held else "'__none__'"
    args = [user_id]
    if held:
        args.extend(held)

    sql = f"""
    SELECT a.ticker, a.name, COUNT(*) as popularity
    FROM transaction t
    JOIN asset a ON t.asset_id = a.asset_id
    WHERE t.portfolio_id IN (
        SELECT portfolio_id FROM portfolio
    )
    AND a.ticker NOT IN ({placeholders})
    GROUP BY a.ticker, a.name
    ORDER BY popularity DESC
    LIMIT %s
    """
    cursor.execute(sql, args + [limit])
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
