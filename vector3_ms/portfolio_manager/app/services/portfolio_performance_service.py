from vector3_ms.portfolio_manager.app.database.connection import get_db

def record_portfolio_performance(portfolio_id, date, total_value, daily_change, daily_change_percent, notes=None):
    db = get_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO portfolio_performance
    (portfolio_id, date, total_value, daily_change, daily_change_percent, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (portfolio_id, date, total_value, daily_change, daily_change_percent, notes))
    db.commit()

    cursor.close()
    db.close()

    return {"message": "Portfolio performance recorded"}
