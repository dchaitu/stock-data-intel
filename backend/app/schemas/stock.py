from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class StockBase(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    daily_return: Optional[float] = None
    ma_7: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StockAnalytics(BaseModel):
    ticker: str
    latest_date: date
    latest_close: float
    daily_return: float
    ma_7: float
    high_52w: float
    low_52w: float

class StockSummary(BaseModel):
    ticker: str
    high_52w: float
    low_52w: float
    avg_close_52w: float

class CompanyList(BaseModel):
    companies: List[str]
