from app.database.connection import get_db
from app.services.data_provider import fetch_asset_info
from app.utils.exceptions import not_found


def list_assets():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM asset ORDER BY ticker")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


def get_asset(ticker: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM asset WHERE ticker = %s", (ticker,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result


def upsert_asset(ticker: str, data=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if not data:
        info = fetch_asset_info(ticker)
        if info:
            data = {
                "name": info["name"],
                "exchange": info.get("exchange"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "asset_type_id": None,
            }

    if data:
        sql = """
            INSERT INTO asset (ticker, name, exchange, sector, industry, asset_type_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                exchange = VALUES(exchange),
                sector = VALUES(sector),
                industry = VALUES(industry),
                asset_type_id = VALUES(asset_type_id)
        """
        cursor.execute(sql, (
            ticker,
            data.get("name", ""),
            data.get("exchange"),
            data.get("sector"),
            data.get("industry"),
            data.get("asset_type_id"),
        ))
    else:
        cursor.execute("INSERT IGNORE INTO asset (ticker) VALUES (%s)", (ticker,))

    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asset updated"}


def delete_asset(ticker: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT asset_id FROM asset WHERE ticker = %s", (ticker,))
    if not cursor.fetchone():
        cursor.close()
        db.close()
        not_found(f"Asset {ticker} not found")

    cursor.execute("DELETE FROM asset WHERE ticker = %s", (ticker,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asset deleted"}
