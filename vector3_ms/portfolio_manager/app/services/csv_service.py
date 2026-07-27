import pandas as pd
import io
from app.database.connection import get_db

def import_assets_csv(csv_content: str) -> dict:
    df = pd.read_csv(io.StringIO(csv_content))
    db = get_db()
    cursor = db.cursor()

    count = 0
    for _, row in df.iterrows():
        ticker = row.get("ticker")
        name = row.get("name")
        sector = row.get("sector")
        industry = row.get("industry")

        sql = "INSERT INTO asset (ticker, name, sector, industry) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE sector=VALUES(sector), industry=VALUES(industry)"
        cursor.execute(sql, (ticker, name, sector, industry))
        count += 1

    db.commit()
    cursor.close()
    db.close()

    return {"imported": count, "message": f"Imported {count} assets"}

def import_transactions_csv(csv_content: str, portfolio_id: int) -> dict:
    df = pd.read_csv(io.StringIO(csv_content))
    db = get_db()
    cursor = db.cursor()

    count = 0
    for _, row in df.iterrows():
        ticker = row.get("ticker")
        quantity = float(row.get("quantity"))
        price = float(row.get("price"))
        tx_type = row.get("type")  # BUY or SELL
        tx_date = row.get("date")

        cursor.execute("SELECT id FROM asset WHERE ticker = %s", (ticker,))
        asset = cursor.fetchone()
        if not asset:
            continue

        asset_id = asset[0]
        sql = "INSERT INTO transaction (portfolio_id, asset_id, quantity, price, type, transaction_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (portfolio_id, asset_id, quantity, price, tx_type, tx_date))
        count += 1

    db.commit()
    cursor.close()
    db.close()

    return {"imported": count, "message": f"Imported {count} transactions"}

def export_holdings_csv(portfolio_id: int) -> str:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT
        a.ticker, a.name,
        COALESCE(SUM(CASE WHEN t.type = 'BUY' THEN t.quantity ELSE -t.quantity END), 0) as quantity,
        MAX(t.price) as last_price
    FROM asset a
    LEFT JOIN transaction t ON a.id = t.asset_id
    WHERE t.portfolio_id = %s
    GROUP BY a.id, a.ticker, a.name
    ORDER BY a.ticker
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def export_transactions_csv(portfolio_id: int) -> str:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT a.ticker, t.quantity, t.price, t.type, t.transaction_date
    FROM transaction t
    JOIN asset a ON t.asset_id = a.id
    WHERE t.portfolio_id = %s
    ORDER BY t.transaction_date DESC
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def export_performance_csv(portfolio_id: int) -> str:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT date, total_value, daily_change, daily_change_percent, total_gain_loss
    FROM portfolio_performance
    WHERE portfolio_id = %s
    ORDER BY date DESC
    """
    cursor.execute(sql, (portfolio_id,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
