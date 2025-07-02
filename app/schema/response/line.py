from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from .common import BaseResponse


class LineEventInfo(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    room_id: Optional[str] = None
    message_text: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class LineMessageResponse(BaseResponse):
    message_id: Optional[str] = None
    sent_to: str  # user_id, group_id, or room_id
    message_type: str
    sent_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class LineBroadcastResponse(BaseResponse):
    broadcast_id: Optional[str] = None
    target_count: int
    sent_count: int
    failed_count: int
    sent_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class LineReplyResponse(BaseResponse):
    reply_token: str
    message_type: str
    replied_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class LineWebhookResponse(BaseResponse):
    events_processed: int
    events: List[LineEventInfo]
    processed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class LineUserProfileResponse(BaseModel):
    user_id: str
    display_name: str
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: Optional[str] = None


class LineGroupInfoResponse(BaseModel):
    group_id: str
    group_name: str
    picture_url: Optional[str] = None
    member_count: Optional[int] = None