from app.database.connection import get_db
import json
import datetime

def cache_market_data(ticker, payload):
    db = get_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO market_data_cache (ticker, last_updated, json_payload)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        last_updated = VALUES(last_updated),
        json_payload = VALUES(json_payload)
    """

    cursor.execute(sql, (ticker, datetime.datetime.now(), json.dumps(payload)))
    db.commit()

    cursor.close()
    db.close()

    return {"message": "Market data cached"}
