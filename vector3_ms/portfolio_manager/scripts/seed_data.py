import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.portfolio_service import create_portfolio
from app.services.transaction_service import add_transaction


def seed():
    p1 = create_portfolio({"name": "Tech Portfolio", "description": "Contains major tech stocks"})
    p2 = create_portfolio({"name": "Dividend Portfolio", "description": "Long-term dividend stocks"})

    p1_id = p1.get("portfolio_id")
    p2_id = p2.get("portfolio_id")

    # If create_portfolio didn't return the id, fall back to fetching the latest
    if p1_id is None or p2_id is None:
        from app.database.connection import get_db
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT portfolio_id FROM portfolio ORDER BY portfolio_id")
        row = cursor.fetchall()
        cursor.close()
        db.close()
        if len(row) >= 2:
            p1_id, p2_id = row[-2]["portfolio_id"], row[-1]["portfolio_id"]

    buys = [
        (p1_id, "AAPL", 10, 180),
        (p1_id, "MSFT", 15, 330),
        (p1_id, "GOOGL", 8, 140),
        (p2_id, "TSLA", 20, 250),
        (p2_id, "MSFT", 12, 330),
    ]
    from app.database.connection import get_db
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT asset_id, ticker FROM asset")
    id_by_ticker = {r["ticker"]: r["asset_id"] for r in cursor.fetchall()}
    cursor.close()
    db.close()

    for pid, ticker, qty, price in buys:
        asset_id = id_by_ticker.get(ticker)
        if not asset_id:
            print(f"  ! {ticker} not in asset table - add it first (POST /assets/{ticker})")
            continue
        try:
            add_transaction(pid, {"asset_id": asset_id, "quantity": qty, "price": price, "type": "BUY"})
            print(f"  + BUY {ticker} x{qty} @ {price} -> portfolio {pid}")
        except Exception as e:
            print(f"  ! Skipped {ticker}: {e}")

    print("Seeding complete. Portfolios:", p1.get("message", "OK"), "/", p2.get("message", "OK"))


if __name__ == "__main__":
    seed()