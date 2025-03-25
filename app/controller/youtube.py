from app.service.youtube import get_hao_report
from datetime import datetime

def download_hao_report(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    data = get_hao_report(start_date=start_date, end_date=end_date)
    return {"data": data}