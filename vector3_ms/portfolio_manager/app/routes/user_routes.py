from fastapi import APIRouter
from app.services.user_service import (
    list_users,
    create_user,
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users():
    return list_users()

@router.post("/")
def add_user(data: dict):
    return create_user(data)
