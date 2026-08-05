from app.database.connection import get_db

def list_portfolios():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM portfolio ORDER BY created_at DESC")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def create_portfolio(data):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = "INSERT INTO portfolio (name, description) VALUES (%s, %s)"
    cursor.execute(sql, (data["name"], data.get("description")))
    db.commit()
    portfolio_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "Portfolio created", "portfolio_id": portfolio_id}

def update_portfolio(portfolio_id: int, data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    name = data.get("name")
    description = data.get("description")
    if name is not None and description is not None:
        sql = "UPDATE portfolio SET name = %s, description = %s WHERE portfolio_id = %s"
        cursor.execute(sql, (name, description, portfolio_id))
    elif name is not None:
        sql = "UPDATE portfolio SET name = %s WHERE portfolio_id = %s"
        cursor.execute(sql, (name, portfolio_id))
    elif description is not None:
        sql = "UPDATE portfolio SET description = %s WHERE portfolio_id = %s"
        cursor.execute(sql, (description, portfolio_id))
    else:
        cursor.close()
        db.close()
        return {"error": "Nothing to update"}
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Portfolio updated", "portfolio_id": portfolio_id}

def delete_portfolio(portfolio_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM portfolio WHERE portfolio_id = %s", (portfolio_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Portfolio deleted", "portfolio_id": portfolio_id}
