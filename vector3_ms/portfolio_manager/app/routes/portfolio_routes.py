from fastapi import APIRouter
from app.services.portfolio_service import (
    create_portfolio,
    list_portfolios
)

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/")
def get_portfolios():
    return list_portfolios()

@router.post("/")
def add_portfolio(data: dict):
    return create_portfolio(data)
