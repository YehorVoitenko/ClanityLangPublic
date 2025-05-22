from minio import Minio

from config.storage_service_config import MINIO_URL, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD

storage_client = Minio(
    endpoint=MINIO_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)
