from fastapi import APIRouter, Query
from app.controller.report import get_major_investors
from app.schema.response.report import MajorInvestorsResponse
from app.schema.response.common import ErrorResponse

router = APIRouter()

@router.get("/major-investors", response_model=MajorInvestorsResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
async def fetch_major_investors(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    """
    API endpoint to fetch major investors data for a specific date.
    Args:
        date (str): The date in 'YYYY-MM-DD' format.
    Returns:
        JSON response with major investors data or an error message.
    """
    return await get_major_investors(date)