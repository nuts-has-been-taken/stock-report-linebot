from fastapi import HTTPException, Response
from datetime import datetime
from app.service.minio import get_image_service, delete_image_service
from app.schema.response.minio import ImageDeleteResponse

async def fetch_image(bucket: str, object_name: str):
    """
    Controller function to fetch an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Image data in bytes or raises an HTTPException.
    """
    try:
        image_data = get_image_service(bucket, object_name)
        if image_data:
            if object_name.endswith(".png"):
                content_type = "image/png"
            elif object_name.endswith(".jpg") or object_name.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif object_name.endswith(".gif"):
                content_type = "image/gif"
            else:
                content_type = "application/octet-stream"
            return Response(content=image_data, media_type=content_type)
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def remove_image(bucket: str, object_name: str) -> ImageDeleteResponse:
    """
    Controller function to delete an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Success message or raises an HTTPException.
    """
    try:
        delete_image_service(bucket, object_name)
        return ImageDeleteResponse(
            success=True,
            message=f"Image '{object_name}' deleted successfully from bucket '{bucket}'",
            bucket=bucket,
            object_name=object_name,
            deleted_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))