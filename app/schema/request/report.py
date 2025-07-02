from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from .common import DateRequest


class MajorInvestorsRequest(DateRequest):
    pass


class ReportGenerationRequest(BaseModel):
    event_id: str = Field(..., description="Event ID for LINE callback")
    report_type: Literal["major", "futures", "margin", "hao"] = Field(..., description="Type of report to generate")
    data_number: int = Field(20, ge=1, le=100, description="Number of data points to include")
    cron_mode: bool = Field(True, description="Whether this is a cron job execution")


class LineReportRequest(BaseModel):
    event_id: str = Field(..., description="Event ID for LINE callback")
    cron_mode: bool = Field(True, description="Whether this is a cron job execution")