from fastapi import APIRouter
from app.controller.youtube import download_hao_report
from app.schema.request.youtube import HaoReportRequest
from app.schema.response.youtube import HaoReportResponse
from app.schema.response.common import ErrorResponse

router = APIRouter()

@router.post("/hao-report", response_model=HaoReportResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def get_hao_report(request: HaoReportRequest):
    return download_hao_report(start_date=request.start_date, end_date=request.end_date)