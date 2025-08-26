import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_TOKEN = os.getenv(key="OPENAI_TOKEN")
