from fastapi import APIRouter
from app.services.transaction_service import list_transactions, add_transaction, delete_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/{portfolio_id}")
def get_transactions(portfolio_id: int):
    return list_transactions(portfolio_id)

@router.post("/{portfolio_id}")
def add_tx(portfolio_id: int, data: dict):
    return add_transaction(portfolio_id, data)

@router.delete("/{transaction_id}")
def remove_tx(transaction_id: int):
    return delete_transaction(transaction_id)
