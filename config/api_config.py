from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_URL = getenv(key="API_URL")
GLOBAL_SERVER_HOST = getenv(key="GLOBAL_SERVER_HOST")
