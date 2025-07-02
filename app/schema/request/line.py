from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, Any


class LineWebhookRequest(BaseModel):
    signature: str = Field(..., description="LINE webhook signature")
    body: str = Field(..., description="Webhook request body")


class LineMessageRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="LINE user ID")
    group_id: Optional[str] = Field(None, description="LINE group ID")
    room_id: Optional[str] = Field(None, description="LINE room ID")
    message_text: str = Field(..., description="Message text to send")
    message_type: Literal["text", "image", "flex", "template"] = Field("text", description="Type of LINE message")


class LineBroadcastRequest(BaseModel):
    message_text: str = Field(..., description="Message text to broadcast")
    message_type: Literal["text", "image", "flex", "template"] = Field("text", description="Type of LINE message")
    target_users: Optional[list] = Field(None, description="Specific user IDs to send to")


class LineReplyRequest(BaseModel):
    reply_token: str = Field(..., description="LINE reply token")
    message_text: str = Field(..., description="Message text to reply")
    message_type: Literal["text", "image", "flex", "template"] = Field("text", description="Type of LINE message")


class LineFlexMessageRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="LINE user ID")
    group_id: Optional[str] = Field(None, description="LINE group ID")
    alt_text: str = Field(..., description="Alternative text for flex message")
    flex_content: Dict[str, Any] = Field(..., description="Flex message JSON content")


class LineImageMessageRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="LINE user ID")
    group_id: Optional[str] = Field(None, description="LINE group ID")
    image_url: str = Field(..., description="Image URL to send")
    preview_url: Optional[str] = Field(None, description="Preview image URL")
    
    @field_validator('image_url', 'preview_url')
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith('http'):
            raise ValueError('URL must start with http or https')
        return v