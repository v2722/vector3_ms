from fastapi import APIRouter
from app.services.asset_type_service import list_asset_types, add_asset_type

router = APIRouter(prefix="/asset-types", tags=["Asset Types"])

@router.get("/")
def get_asset_types():
    return list_asset_types()

@router.post("/")
def add_type(data: dict):
    return add_asset_type(data)
