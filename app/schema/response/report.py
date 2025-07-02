from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from .common import BaseResponse
from ..internal.stock import MajorInvestorData, FutureData, MarginData


class MajorInvestorsResponse(BaseModel):
    日期: datetime
    外資: int
    投信: int
    自營商: int
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }


class ReportDataResponse(BaseModel):
    report_type: str
    data_count: int
    generated_at: datetime
    chart_url: Optional[str] = None
    summary: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class DailyReportResponse(BaseResponse):
    report_data: Optional[ReportDataResponse] = None
    line_message_sent: bool = False


class ChartResponse(BaseModel):
    chart_url: str
    chart_type: str
    generated_at: datetime
    expiry_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }