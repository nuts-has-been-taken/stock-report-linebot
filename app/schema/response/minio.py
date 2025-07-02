from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from .common import BaseResponse


class ImageResponse(BaseModel):
    bucket: str
    object_name: str
    content_type: str
    size: Optional[int] = None
    url: Optional[str] = None
    last_modified: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class ImageDeleteResponse(BaseResponse):
    bucket: str
    object_name: str
    deleted_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class ImageUploadResponse(BaseResponse):
    bucket: str  
    object_name: str
    url: str
    content_type: str
    size: int
    uploaded_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class BucketInfoResponse(BaseModel):
    bucket: str
    created_at: Optional[datetime] = None
    object_count: Optional[int] = None
    total_size: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }