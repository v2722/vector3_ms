from vector3_ms.portfolio_manager.app.database.connection import get_db
import datetime
import json

def audit(entity_name, entity_id, action, details=None):
    db = get_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO audit_log (entity_name, entity_id, action, timestamp, details)
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        entity_name,
        entity_id,
        action,
        datetime.datetime.now(),
        json.dumps(details) if details else None
    ))

    db.commit()
    cursor.close()
    db.close()

