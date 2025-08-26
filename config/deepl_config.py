import os

from dotenv import load_dotenv

load_dotenv()

DEEPL_TOKEN = os.getenv(key="DEEPL_TOKEN")
