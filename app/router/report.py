from fastapi import APIRouter
from app.controller.report import get_major_investors

router = APIRouter()

@router.get("/major-investors")
async def fetch_major_investors(date: str):
    """
    API endpoint to fetch major investors data for a specific date.
    Args:
        date (str): The date in 'YYYY-MM-DD' format.
    Returns:
        JSON response with major investors data or an error message.
    """
    return await get_major_investors(date)