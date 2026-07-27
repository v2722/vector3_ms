from app.database.connection import get_db
from app.services.asset_service import upsert_asset
from app.services.data_provider import fetch_price_history


def get_price_history(ticker: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = """
        SELECT ph.*
        FROM price_history ph
        JOIN asset a ON ph.asset_id = a.asset_id
        WHERE a.ticker = %s
        ORDER BY ph.date DESC
    """
    cursor.execute(sql, (ticker,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


def import_price_history(ticker: str, period="1y", interval="1d"):
    db = get_db()
    cursor = db.cursor()

    upsert_asset(ticker)

    cursor.execute("SELECT asset_id FROM asset WHERE ticker=%s", (ticker,))
    asset_id = cursor.fetchone()[0]

    rows = fetch_price_history(ticker, period=period, interval=interval)

    sql = """
    INSERT INTO price_history (asset_id, date, open, high, low, close, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        open = VALUES(open),
        high = VALUES(high),
        low = VALUES(low),
        close = VALUES(close),
        volume = VALUES(volume);
    """

    for row in rows:
        cursor.execute(sql, (
            asset_id,
            row["date"],
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["volume"],
        ))

    db.commit()
    cursor.close()
    db.close()

    return {"message": f"Imported price history for {ticker}"}
