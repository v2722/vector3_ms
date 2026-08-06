from app.database.connection import get_db

def list_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user ORDER BY name")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def create_user(data):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    sql = "INSERT INTO user (name) VALUES (%s)"
    cursor.execute(sql, (data["name"],))
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "User created", "user_id": user_id}
