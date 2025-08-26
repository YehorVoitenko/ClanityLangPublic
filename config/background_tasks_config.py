from os import getenv

from dotenv import load_dotenv

load_dotenv()

REDIS_URL = getenv(key="REDIS_URL")
REDIS_HOST = getenv(key="REDIS_HOST")
CELERY_BROKER_URL = getenv(key="CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = getenv(key="CELERY_RESULT_BACKEND")
