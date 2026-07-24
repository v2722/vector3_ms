from vector3_ms.portfolio_manager.app.database.connection import get_db

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
            data["name"],
            data.get("exchange"),
            data.get("sector"),
            data.get("industry"),
            data.get("asset_type_id")
        ))
    else:
        cursor.execute("INSERT IGNORE INTO asset (ticker) VALUES (%s)", (ticker,))

    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asset updated"}
