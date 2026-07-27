from app.database.connection import get_db

def list_asset_transactions(asset_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM asset_transaction
        WHERE asset_id = %s
        ORDER BY transaction_date DESC
    """, (asset_id,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def add_asset_transaction(asset_id: int, data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = """
        INSERT INTO asset_transaction (asset_id, transaction_type, quantity, price, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        asset_id,
        data["transaction_type"],
        data.get("quantity"),
        data.get("price"),
        data.get("notes")
    ))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asset transaction added"}
