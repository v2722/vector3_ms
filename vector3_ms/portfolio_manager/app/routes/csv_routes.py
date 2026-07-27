from fastapi import APIRouter, File, UploadFile
from app.services.csv_service import (
    import_assets_csv, import_transactions_csv,
    export_holdings_csv, export_transactions_csv, export_performance_csv
)

router = APIRouter(prefix="/csv", tags=["CSV"])

@router.post("/import/assets")
async def import_assets(file: UploadFile = File(...)):
    content = await file.read()
    return import_assets_csv(content.decode("utf-8"))

@router.post("/import/transactions/{portfolio_id}")
async def import_transactions(portfolio_id: int, file: UploadFile = File(...)):
    content = await file.read()
    return import_transactions_csv(content.decode("utf-8"), portfolio_id)

@router.get("/export/holdings/{portfolio_id}")
def export_holdings(portfolio_id: int):
    csv_data = export_holdings_csv(portfolio_id)
    return {"csv": csv_data, "format": "CSV"}

@router.get("/export/transactions/{portfolio_id}")
def export_transactions(portfolio_id: int):
    csv_data = export_transactions_csv(portfolio_id)
    return {"csv": csv_data, "format": "CSV"}

@router.get("/export/performance/{portfolio_id}")
def export_performance(portfolio_id: int):
    csv_data = export_performance_csv(portfolio_id)
    return {"csv": csv_data, "format": "CSV"}
