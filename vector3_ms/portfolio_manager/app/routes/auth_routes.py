from fastapi import APIRouter, Header
from pydantic import BaseModel
from app.services.auth_service import register_user, login_user, verify_token, get_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = None

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    return register_user(req.username, req.password, req.email)

@router.post("/login")
def login(req: LoginRequest):
    return login_user(req.username, req.password)

@router.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"error": "Missing or invalid authorization header"}

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    user = get_user(payload["user_id"])
    return user
