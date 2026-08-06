from app.database.connection import get_db

def list_portfolios():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.portfolio_id, p.user_id, p.name, p.description, p.created_at,
               u.name AS user_name
        FROM portfolio p
        LEFT JOIN user u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def create_portfolio(data):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = "INSERT INTO portfolio (user_id, name, description) VALUES (%s, %s, %s)"
    cursor.execute(sql, (data.get("user_id"), data["name"], data.get("description")))
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
    user_id = data.get("user_id")
    updates = []
    params = []

    if name is not None:
        updates.append("name = %s")
        params.append(name)
    if description is not None:
        updates.append("description = %s")
        params.append(description)
    if user_id is not None:
        updates.append("user_id = %s")
        params.append(user_id)

    if not updates:
        cursor.close()
        db.close()
        return {"error": "Nothing to update"}

    sql = f"UPDATE portfolio SET {', '.join(updates)} WHERE portfolio_id = %s"
    params.append(portfolio_id)
    cursor.execute(sql, tuple(params))
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
