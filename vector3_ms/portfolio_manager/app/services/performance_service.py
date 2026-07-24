from app.database.connection import get_db

def list_performance(portfolio_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM portfolio_performance
        WHERE portfolio_id = %s
        ORDER BY date DESC
    """, (portfolio_id,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def add_performance(portfolio_id: int, data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = """
        INSERT INTO portfolio_performance
        (portfolio_id, date, total_value, daily_change, daily_change_percent, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        portfolio_id,
        data["date"],
        data["total_value"],
        data.get("daily_change"),
        data.get("daily_change_percent"),
        data.get("notes")
    ))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Performance added"}
