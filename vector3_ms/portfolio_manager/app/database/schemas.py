from pydantic import BaseModel

class PortfolioCreate(BaseModel):
    name: str
    description: str | None = None


class PortfolioItemCreate(BaseModel):
    ticker: str
    quantity: float
    price: float


class AssetCreate(BaseModel):
    ticker: str


class TransactionCreate(BaseModel):
    ticker: str
    quantity: float
    price: float
    type: str  # BUY or SELL
