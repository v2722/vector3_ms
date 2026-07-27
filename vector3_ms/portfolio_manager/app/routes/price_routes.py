from fastapi import APIRouter
from app.services.price_service import get_price_history, import_price_history

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.get("/{ticker}")
def get_prices(ticker: str):
    return get_price_history(ticker)

@router.post("/{ticker}")
def import_prices(ticker: str):
    return import_price_history(ticker)
