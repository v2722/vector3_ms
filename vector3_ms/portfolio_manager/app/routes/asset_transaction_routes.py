from fastapi import APIRouter
from app.services.asset_transaction_service import list_asset_transactions, add_asset_transaction

router = APIRouter(prefix="/asset-transactions", tags=["Asset Transactions"])

@router.get("/{asset_id}")
def get_asset_transactions(asset_id: int):
    return list_asset_transactions(asset_id)

@router.post("/{asset_id}")
def add_asset_tx(asset_id: int, data: dict):
    return add_asset_transaction(asset_id, data)
