from vector3_ms.portfolio_manager.app.database.connection import get_db

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
    cursor.close()
    db.close()
    return {"message": "Portfolio created"}
