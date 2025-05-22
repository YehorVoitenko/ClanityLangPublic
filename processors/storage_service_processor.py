from minio import Minio

from config.storage_service_config import MINIO_BUCKET_NAME
from services.storage_service import storage_client


class StorageServiceProcessor:
    @staticmethod
    def init_minio_bucket(minio_client: Minio = storage_client):
        minio_client.bucket_exists(MINIO_BUCKET_NAME)
        if minio_client.bucket_exists(MINIO_BUCKET_NAME):
            return
        minio_client.make_bucket(MINIO_BUCKET_NAME)
