from fastapi import APIRouter

from app.controller.line import line_hao_report
from app.controller.line import get_daily_report as line_daily_report

router = APIRouter()

# Cron job
# 每日發送游庭皓的財經皓角報告
@router.get("/hao-report")
def get_line_hao_report(event_id: str, cron_mode: bool = True):
    return line_hao_report(event_id, cron_mode)

# 每日發送法人、籌碼、期貨報告
@router.get("/daily-report")
def get_daily_report(event_id: str, report_type: str, data_number: int = 20):
    return line_daily_report(event_id, report_type, data_number)