from os import getenv

from dotenv import load_dotenv

load_dotenv()

MINIO_ROOT_USER = getenv(key="MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = getenv(key="MINIO_ROOT_PASSWORD")
MINIO_HOST = getenv(key="MINIO_HOST")
MINIO_PORT = getenv(key="MINIO_PORT")
MINIO_BUCKET_NAME = getenv(key="MINIO_BUCKET_NAME")

MINIO_URL = f'{MINIO_HOST}:{MINIO_PORT}'
