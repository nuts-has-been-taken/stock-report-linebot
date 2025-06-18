from app.core.config import minio_client

BUCKET_LIST = ["reports"]

def ensure_buckets_exist():
    """
    Ensure that the specified buckets exist. If not, create them.
    """
    for bucket_name in BUCKET_LIST:
        if not minio_client.client.bucket_exists(bucket_name):
            minio_client.client.make_bucket(bucket_name)