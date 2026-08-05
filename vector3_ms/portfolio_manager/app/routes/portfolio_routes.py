from fastapi import APIRouter
from app.services.portfolio_service import (
    create_portfolio,
    list_portfolios,
    update_portfolio,
    delete_portfolio,
)

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("/")
def get_portfolios():
    return list_portfolios()

@router.post("/")
def add_portfolio(data: dict):
    return create_portfolio(data)

@router.put("/{portfolio_id}")
def edit_portfolio(portfolio_id: int, data: dict):
    return update_portfolio(portfolio_id, data)

@router.delete("/{portfolio_id}")
def remove_portfolio(portfolio_id: int):
    return delete_portfolio(portfolio_id)
