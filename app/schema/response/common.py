from pydantic import BaseModel
from typing import Optional, Any, Dict


class BaseResponse(BaseModel):
    success: bool
    message: str


class SuccessResponse(BaseResponse):
    success: bool = True
    data: Optional[Any] = None
    
    
class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    message: str
    status: str = "healthy"
    timestamp: Optional[str] = None