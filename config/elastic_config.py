import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

ES_PROTOCOL = os.getenv("ELASTIC_PROTOCOL", "http")
ES_HOST = os.getenv("ELASTIC_HOST", "localhost")
ES_PORT = os.getenv("ELASTIC_PORT", "9200")
ES_PASS = os.getenv("ELASTIC_PASSWORD")
ES_URL = f"{ES_PROTOCOL}://{ES_HOST}:{ES_PORT}"


class ElasticAvailableIndexes(Enum):
    PURCHASES = "purchases"
    USER_ACTIVITY = "user_activity"


ELASTIC_INDEXES = {
    ElasticAvailableIndexes.PURCHASES.value,
    ElasticAvailableIndexes.USER_ACTIVITY.value,
}
