class Portfolio:
    def __init__(self, portfolio_id, name, description, created_at):
        self.portfolio_id = portfolio_id
        self.name = name
        self.description = description
        self.created_at = created_at


class Asset:
    def __init__(self, asset_id, ticker, name, exchange, sector, industry):
        self.asset_id = asset_id
        self.ticker = ticker
        self.name = name
        self.exchange = exchange
        self.sector = sector
        self.industry = industry


class PriceHistory:
    def __init__(self, price_id, asset_id, date, open, high, low, close, volume):
        self.price_id = price_id
        self.asset_id = asset_id
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


class Transaction:
    def __init__(self, transaction_id, portfolio_id, asset_id, type, quantity, price, timestamp):
        self.transaction_id = transaction_id
        self.portfolio_id = portfolio_id
        self.asset_id = asset_id
        self.type = type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
