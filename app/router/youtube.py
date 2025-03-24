from fastapi import APIRouter
from app.controller.youtube import download_hao_report

router = APIRouter()

@router.post("/hao-report")
def get_hao_report(start_date: str, end_date: str):
    """
    API endpoint to download Hao report.
    """
    data = download_hao_report(start_date=start_date, end_date=end_date)
    return {"data": data}