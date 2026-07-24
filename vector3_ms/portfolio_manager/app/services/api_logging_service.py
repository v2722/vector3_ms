from vector3_ms.portfolio_manager.app.database.connection import get_db
import datetime
import json

def log_api_request(ticker, request_time, response_time, status, payload):
    db = get_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO external_api_request
    (ticker, request_time, response_time, status, payload)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        ticker,
        request_time,
        response_time,
        status,
        json.dumps(payload)
    ))

    db.commit()
    cursor.close()
    db.close()
