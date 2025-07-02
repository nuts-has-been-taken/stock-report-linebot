from fastapi import APIRouter, Query
from app.controller.line import line_hao_report
from app.controller.line import get_daily_report as line_daily_report
from app.schema.request.report import LineReportRequest, ReportGenerationRequest
from app.schema.response.report import DailyReportResponse
from app.schema.response.common import ErrorResponse, SuccessResponse

router = APIRouter()

# Cron job
# 每日發送游庭皓的財經皓角報告
@router.get("/hao-report", response_model=SuccessResponse, responses={500: {"model": ErrorResponse}})
def get_line_hao_report(event_id: str = Query(..., description="Event ID for LINE callback"), 
                       cron_mode: bool = Query(True, description="Whether this is a cron job execution")):
    return line_hao_report(event_id, cron_mode)

# 每日發送法人、籌碼、期貨報告
@router.get("/daily-report", response_model=DailyReportResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def get_daily_report(event_id: str = Query(..., description="Event ID for LINE callback"),
                    report_type: str = Query(..., description="Type of report (major/futures/margin/hao)"),
                    data_number: int = Query(20, ge=1, le=100, description="Number of data points to include")):
    return line_daily_report(event_id, report_type, data_number)