from app.db.minio import get_image, delete_image
from logger import logger

def retrieve_image_data(bucket_name: str, object_name: str) -> bytes:
    """
    Service layer function to retrieve image data from MinIO storage.
    
    :param bucket_name: Name of the bucket containing the image.
    :param object_name: Name of the object in the bucket.
    :return: Image data in bytes.
    """
    try:
        image_data = get_image(bucket_name, object_name)
        return image_data
    except RuntimeError as e:
        logger.error(f"Error while retrieving image: {e}")
        return None

def remove_image_from_storage(bucket_name: str, object_name: str):
    """
    Service layer function to remove an image from MinIO storage.
    
    :param bucket_name: Name of the bucket containing the image.
    :return: None
    """
    try:
        delete_image(bucket_name, object_name)
        logger.info(f"Image '{object_name}' removed successfully from bucket '{bucket_name}'.")
    except RuntimeError as e:
        logger.error(f"Error while removing image: {e}")