from os import getenv

from dotenv import load_dotenv

load_dotenv()

MONO_API_URL = "https://api.monobank.ua"
MONO_TOKEN = getenv(key="MONO_TOKEN")
PURCHASE_UNIQUE_CODE = getenv(key="PURCHASE_UNIQUE_CODE")
