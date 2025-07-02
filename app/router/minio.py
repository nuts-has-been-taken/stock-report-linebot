from fastapi import APIRouter, Query, Depends
from app.controller.minio import handle_image_fetch, handle_image_deletion
from app.schema.request.minio import ImageRequest
from app.schema.response.minio import ImageDeleteResponse
from app.schema.response.common import ErrorResponse

router = APIRouter()

def get_image_request(bucket: str = Query(..., description="Bucket name in MinIO"), 
                     object_name: str = Query(..., description="Object name in the bucket")) -> ImageRequest:
    return ImageRequest(bucket=bucket, object_name=object_name)

@router.get("/", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_image(request: ImageRequest = Depends(get_image_request)):
    """
    API endpoint to fetch an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Image data in bytes or an error message.
    """
    return await handle_image_fetch(request.bucket, request.object_name)

@router.delete("/", response_model=ImageDeleteResponse, responses={500: {"model": ErrorResponse}})
async def delete_image(request: ImageRequest = Depends(get_image_request)):
    """
    API endpoint to delete an image from MinIO.
    
    Args:
        bucket (str): Name of the bucket containing the image.
        object_name (str): Name of the object in the bucket.
    
    Returns:
        Success message or an error message.
    """
    return await handle_image_deletion(request.bucket, request.object_name)