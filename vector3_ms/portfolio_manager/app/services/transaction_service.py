from app.database.connection import get_db
from app.utils.exceptions import not_found

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


def delete_transaction(portfolio_id: int, transaction_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT transaction_id FROM transaction WHERE transaction_id = %s AND portfolio_id = %s",
        (transaction_id, portfolio_id)
    )
    if not cursor.fetchone():
        cursor.close()
        db.close()
        not_found(f"Transaction {transaction_id} not found in portfolio {portfolio_id}")

    cursor.execute("DELETE FROM transaction WHERE transaction_id = %s", (transaction_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Transaction deleted"}
