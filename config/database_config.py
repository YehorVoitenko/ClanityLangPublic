from os import getenv

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = getenv(key="POSTGRES_DB")
POSTGRES_USER = getenv(key="POSTGRES_USER")
POSTGRES_PASSWORD = getenv(key="POSTGRES_PASSWORD")
POSTGRES_HOST = getenv(key="POSTGRES_HOST")
POSTGRES_PORT = getenv(key="POSTGRES_PORT")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
