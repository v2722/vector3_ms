from app.services.asset_service import upsert_asset

def update_assets(tickers: list[str]):
    for t in tickers:
        upsert_asset(t)
