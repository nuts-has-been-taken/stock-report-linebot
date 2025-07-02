from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class ImageRequest(BaseModel):
    bucket: str = Field(..., description="Bucket name in MinIO")
    object_name: str = Field(..., description="Object name in the bucket")
    
    @field_validator('bucket')
    @classmethod
    def validate_bucket_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Bucket name must be at least 3 characters long')
        return v.lower()
    
    @field_validator('object_name')
    @classmethod
    def validate_object_name(cls, v):
        if not v:
            raise ValueError('Object name cannot be empty')
        return v


class ImageUploadRequest(BaseModel):
    bucket: str = Field(..., description="Bucket name in MinIO")
    object_name: str = Field(..., description="Object name in the bucket")
    content_type: Optional[str] = Field(None, description="MIME type of the image")
    metadata: Optional[dict] = Field(None, description="Additional metadata for the object")
    
    @field_validator('bucket')
    @classmethod
    def validate_bucket_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Bucket name must be at least 3 characters long')
        return v.lower()


class BucketRequest(BaseModel):
    bucket: str = Field(..., description="Bucket name in MinIO")
    
    @field_validator('bucket')
    @classmethod
    def validate_bucket_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Bucket name must be at least 3 characters long')
        return v.lower()