import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from config.database_config import DATABASE_URL

engine = create_engine(
    url=DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=20,
    pool_timeout=30,
)

SQLModel.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_database_session():
    session = SessionLocal()
    try:
        yield session

    finally:
        session.close()


def init_tables():
    os.system("alembic stamp head")
    os.system("alembic upgrade head")
    engine.dispose()
