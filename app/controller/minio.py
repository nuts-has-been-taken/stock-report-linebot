from fastapi import HTTPException, Response
from datetime import datetime
from app.service.minio import retrieve_image_data, remove_image_from_storage
from app.schema.response.minio import ImageDeleteResponse

async def handle_image_fetch(bucket: str, object_name: str):
    """
    Handle request to fetch an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Image data in bytes or raises an HTTPException.
    """
    try:
        image_data = retrieve_image_data(bucket, object_name)
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

async def handle_image_deletion(bucket: str, object_name: str) -> ImageDeleteResponse:
    """
    Handle request to delete an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Success message or raises an HTTPException.
    """
    try:
        remove_image_from_storage(bucket, object_name)
        return ImageDeleteResponse(
            success=True,
            message=f"Image '{object_name}' deleted successfully from bucket '{bucket}'",
            bucket=bucket,
            object_name=object_name,
            deleted_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))