from app.database.connection import get_db

def list_transactions(portfolio_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM transaction
        WHERE portfolio_id = %s
        ORDER BY timestamp DESC
    """, (portfolio_id,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def add_transaction(portfolio_id: int, data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = """
        INSERT INTO transaction (portfolio_id, asset_id, type, quantity, price)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        portfolio_id,
        data["asset_id"],
        data["type"],
        data["quantity"],
        data["price"]
    ))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Transaction added"}


def delete_transaction(transaction_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM transaction WHERE transaction_id = %s", (transaction_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Transaction deleted", "transaction_id": transaction_id}
