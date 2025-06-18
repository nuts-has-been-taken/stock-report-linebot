from fastapi import APIRouter
from app.controller.minio import fetch_image, remove_image

router = APIRouter()

@router.get("/")
async def get_image(bucket: str, object_name: str):
    """
    API endpoint to fetch an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Image data in bytes or an error message.
    """
    return await fetch_image(bucket, object_name)

@router.delete("/")
async def delete_image(bucket: str, object_name: str):
    """
    API endpoint to delete an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Success message or an error message.
    """
    return await remove_image(bucket, object_name)