from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from .common import DateRangeRequest


class HaoReportRequest(DateRangeRequest):
    pass


class YouTubeVideoRequest(BaseModel):
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    video_url: Optional[str] = Field(None, description="Full YouTube video URL")
    
    @field_validator('video_url')
    @classmethod
    def validate_youtube_url(cls, v):
        if v and not ('youtube.com' in v or 'youtu.be' in v):
            raise ValueError('Must be a valid YouTube URL')
        return v
    
    @field_validator('video_id')
    @classmethod
    def validate_video_id(cls, v):
        if v and len(v) != 11:
            raise ValueError('YouTube video ID must be 11 characters long')
        return v


class YouTubeSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for YouTube videos")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    channel_id: Optional[str] = Field(None, description="Specific channel ID to search in")
    published_after: Optional[str] = Field(None, description="Search for videos published after this date (RFC 3339)")
    published_before: Optional[str] = Field(None, description="Search for videos published before this date (RFC 3339)")
    
    @field_validator('published_after', 'published_before')
    @classmethod
    def validate_date_format(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
                return v
            except ValueError:
                raise ValueError('Date must be in RFC 3339 format')
        return v