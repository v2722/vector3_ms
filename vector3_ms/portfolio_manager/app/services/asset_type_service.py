from vector3_ms.portfolio_manager.app.database.connection import get_db

def list_asset_types():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM asset_type ORDER BY name")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def add_asset_type(data: dict):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO asset_type (name, description) VALUES (%s, %s)",
        (data["name"], data.get("description"))
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asset type added"}
