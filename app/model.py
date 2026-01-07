from pydantic import BaseModel

class StockRequest(BaseModel):
    symbol: str
    timeframe: str = "30d"
