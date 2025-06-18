from app.db.minio import get_image, delete_image

def get_image_service(bucket_name: str, object_name: str) -> bytes:
    """
    Service layer function to get an image from MinIO.
    
    :param bucket_name: Name of the bucket containing the image.
    :param object_name: Name of the object in the bucket.
    :return: Image data in bytes.
    """
    try:
        image_data = get_image(bucket_name, object_name)
        return image_data
    except RuntimeError as e:
        print(e)
        return None

def delete_image_service(bucket_name: str, object_name: str):
    """
    Service layer function to delete an image from MinIO.
    
    :param bucket_name: Name of the bucket containing the image.
    :return: None
    """
    try:
        delete_image(bucket_name, object_name)
        print(f"Image '{object_name}' deleted successfully from bucket '{bucket_name}'.")
    except RuntimeError as e:
        print(e)