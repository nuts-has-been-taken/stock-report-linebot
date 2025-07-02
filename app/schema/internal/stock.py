from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MajorInvestorData(BaseModel):
    date: datetime
    foreign_investors: int
    investment_trust: int
    dealer: int
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }


class FutureData(BaseModel):
    date: datetime
    contract_type: str
    volume: int
    open_interest: int
    settlement_price: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }


class MarginData(BaseModel):
    date: datetime
    margin_purchase: int
    margin_sale: int
    short_sale: int
    short_cover: int
    margin_balance: int
    short_balance: int
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }