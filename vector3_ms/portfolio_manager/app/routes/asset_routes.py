from fastapi import APIRouter
from app.services.asset_service import (
    upsert_asset,
    list_assets,
    get_asset,
    delete_asset
)

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/")
def get_assets():
    return list_assets()

@router.get("/{ticker}")
def get_asset_by_ticker(ticker: str):
    return get_asset(ticker)

@router.post("/{ticker}")
def update_asset_route(ticker: str, data: dict):
    return upsert_asset(ticker, data)

@router.delete("/{ticker}")
def remove_asset(ticker: str):
    return delete_asset(ticker)