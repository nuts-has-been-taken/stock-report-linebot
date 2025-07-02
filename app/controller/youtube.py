from app.service.youtube import get_hao_report
from datetime import datetime
from app.schema.response.youtube import HaoReportResponse

def download_hao_report(start_date: str, end_date: str) -> HaoReportResponse:
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    data = get_hao_report(start_date=start_date_obj, end_date=end_date_obj)
    return HaoReportResponse(
        success=True,
        message="Hao report generated successfully",
        data=data,
        total_count=len(data) if data else 0,
        date_range={"start_date": start_date, "end_date": end_date},
        generated_at=datetime.now()
    )