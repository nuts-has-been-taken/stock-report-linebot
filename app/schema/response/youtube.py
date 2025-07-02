from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from .common import BaseResponse


class YouTubeVideoInfo(BaseModel):
    video_id: str
    title: str
    description: Optional[str] = None
    channel_title: str
    published_at: datetime
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class HaoReportResponse(BaseResponse):
    data: List[YouTubeVideoInfo]
    total_count: int
    date_range: Dict[str, str]
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class YouTubeSearchResponse(BaseResponse):
    videos: List[YouTubeVideoInfo]
    total_results: int
    next_page_token: Optional[str] = None
    search_query: str
    
    
class YouTubeDownloadResponse(BaseResponse):
    video_id: str
    title: str
    download_url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    downloaded_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class YouTubeAnalyticsResponse(BaseModel):
    video_count: int
    total_views: int
    total_likes: int
    average_duration: Optional[str] = None
    most_popular_video: Optional[YouTubeVideoInfo] = None
    date_range: Dict[str, str]