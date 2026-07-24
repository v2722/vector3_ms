import yfinance as yf
from vector3_ms.portfolio_manager.app.database.connection import get_db
from vector3_ms.portfolio_manager.app.services.asset_service import upsert_asset

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

    hist = yf.Ticker(ticker).history(period=period, interval=interval)

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

    for idx, row in hist.iterrows():
        cursor.execute(sql, (
            asset_id,
            idx.date(),
            row["Open"],
            row["High"],
            row["Low"],
            row["Close"],
            int(row["Volume"])
        ))

    db.commit()
    cursor.close()
    db.close()

    return {"message": f"Imported price history for {ticker}"}
