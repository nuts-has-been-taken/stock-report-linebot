from minio.error import S3Error
from io import BytesIO

from app.core.config import minio_client

def upload_image_to_minio(bucket_name: str, object_name: str, image_data: bytes, content_type: str = "image/jpeg"):
    """
    Upload an image to MinIO.
    
    :param bucket_name: Name of the bucket to upload the image to.
    :param object_name: Name of the object in the bucket.
    :param image_data: Image data in bytes.
    :param content_type: Content type of the image (default is 'image/jpeg').
    :return: None
    """
    try:
        # Ensure the bucket exists
        if not minio_client.client.bucket_exists(bucket_name):
            minio_client.client.make_bucket(bucket_name)
        
        # Upload the image
        minio_client.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=BytesIO(image_data),
            length=len(image_data),
            content_type=content_type
        )
        print(f"Image '{object_name}' uploaded successfully to bucket '{bucket_name}'.")
    except S3Error as e:
        print(f"Failed to upload image: {e}")

def get_image_from_minio(bucket_name: str, object_name: str) -> bytes:
    """
    Get an image from MinIO.
    
    :param bucket_name: Name of the bucket containing the image.
    :param object_name: Name of the object in the bucket.
    :return: Image data in bytes.
    """
    try:
        response = minio_client.client.get_object(bucket_name, object_name)
        image_data = response.read()
        response.close()
        response.release_conn()
        print(f"Image '{object_name}' retrieved successfully from bucket '{bucket_name}'.")
        return image_data
    except S3Error as e:
        print(f"Failed to retrieve image: {e}")
        return None

def delete_image_from_minio(bucket_name: str, object_name: str):
    """
    Delete an image from MinIO.
    
    :param bucket_name: Name of the bucket containing the image.
    :param object_name: Name of the object in the bucket.
    :return: None
    """
    try:
        minio_client.client.remove_object(bucket_name, object_name)
        print(f"Image '{object_name}' deleted successfully from bucket '{bucket_name}'.")
    except S3Error as e:
        print(f"Failed to delete image: {e}")