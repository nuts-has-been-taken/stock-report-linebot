from fastapi import HTTPException
from datetime import datetime
from app.service.report import get_today_major_investors

async def get_major_investors(date: str):
    """Fetch major investors data for a specific date."""
    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'")

    data = get_today_major_investors(parsed_date)
    if data:
        return data
    else:
        raise HTTPException(status_code=404, detail="No data available for the given date")