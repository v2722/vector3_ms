import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from datetime import datetime, timedelta
from app.database.connection import get_db
from app.services.price_service import fetch_and_store_prices

def ingest_daily_prices():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT DISTINCT ticker FROM asset")
    tickers = [row["ticker"] for row in cursor.fetchall()]
    cursor.close()
    db.close()

    if not tickers:
        print("No assets found in database")
        return

    for ticker in tickers:
        try:
            print(f"Fetching prices for {ticker}...")
            fetch_and_store_prices(ticker)
            print(f"✓ {ticker} updated")
        except Exception as e:
            print(f"✗ Error fetching {ticker}: {e}")

    print("Daily ingestion complete")

def update_portfolio_valuations():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
    SELECT DISTINCT portfolio_id FROM transaction
    """)
    portfolios = [row["portfolio_id"] for row in cursor.fetchall()]
    cursor.close()
    db.close()

    for portfolio_id in portfolios:
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)

            sql = """
            SELECT
                SUM(CASE WHEN t.type = 'BUY' THEN t.quantity ELSE -t.quantity END * ph.close) as total_value
            FROM transaction t
            JOIN asset a ON t.asset_id = a.id
            JOIN (
                SELECT ticker, close FROM price_history
                WHERE date = CURDATE()
            ) ph ON a.ticker = ph.ticker
            WHERE t.portfolio_id = %s
            """
            cursor.execute(sql, (portfolio_id,))
            result = cursor.fetchone()
            total_value = result["total_value"] if result["total_value"] else 0

            sql = """
            SELECT total_value FROM portfolio_performance
            WHERE portfolio_id = %s AND date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
            ORDER BY date DESC LIMIT 1
            """
            cursor.execute(sql, (portfolio_id,))
            prev = cursor.fetchone()
            prev_value = prev["total_value"] if prev else total_value

            daily_change = total_value - prev_value
            daily_change_percent = (daily_change / prev_value * 100) if prev_value > 0 else 0

            sql = """
            INSERT INTO portfolio_performance (portfolio_id, date, total_value, daily_change, daily_change_percent, total_gain_loss)
            VALUES (%s, CURDATE(), %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE total_value=%s, daily_change=%s, daily_change_percent=%s
            """
            cursor.execute(sql, (portfolio_id, total_value, daily_change, daily_change_percent, total_value, daily_change, daily_change_percent))
            db.commit()

            cursor.close()
            db.close()

            print(f"✓ Portfolio {portfolio_id} valuation updated")
        except Exception as e:
            print(f"✗ Error updating portfolio {portfolio_id}: {e}")

    print("Portfolio valuations updated")

if __name__ == "__main__":
    print(f"Starting daily ingestion at {datetime.now()}")
    ingest_daily_prices()
    update_portfolio_valuations()
    print(f"Completed at {datetime.now()}")
