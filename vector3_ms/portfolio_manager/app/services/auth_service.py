from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.database.connection import get_db
from app.utils.exceptions import UnauthorizedException, UserAlreadyExistsException
from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")

def register_user(username: str, password: str, email: str = None) -> dict:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        db.close()
        raise UserAlreadyExistsException(f"Username {username} already exists")

    hashed_pwd = hash_password(password)
    sql = "INSERT INTO user (name, username, password, email, created_at) VALUES (%s, %s, %s, %s, NOW())"
    cursor.execute(sql, (username, username, hashed_pwd, email))
    db.commit()
    user_id = cursor.lastrowid

    cursor.close()
    db.close()

    return {"user_id": user_id, "username": username, "message": "User registered"}

def login_user(username: str, password: str) -> dict:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT user_id, username, password FROM user WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if not user or not verify_password(password, user["password"]):
        raise UnauthorizedException("Invalid username or password")

    token = create_access_token(user["user_id"], user["username"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["user_id"]}

def get_user(user_id: int) -> dict:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT user_id, username, email, name FROM user WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if not user:
        raise UnauthorizedException("User not found")

    return user
