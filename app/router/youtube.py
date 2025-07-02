from fastapi import APIRouter
from app.controller.youtube import handle_hao_report_generation
from app.schema.request.youtube import HaoReportRequest
from app.schema.response.youtube import HaoReportResponse
from app.schema.response.common import ErrorResponse

router = APIRouter()

@router.post("/hao-report", response_model=HaoReportResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def create_hao_report(request: HaoReportRequest):
    return handle_hao_report_generation(start_date=request.start_date, end_date=request.end_date)