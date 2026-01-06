from pydantic import BaseModel

class stock_request(BaseModel):
    symbol: str