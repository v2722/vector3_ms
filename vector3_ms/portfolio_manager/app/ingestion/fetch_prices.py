from app.services.price_service import import_price_history

def update_all_prices(tickers: list[str]):
    for t in tickers:
        import_price_history(t)
