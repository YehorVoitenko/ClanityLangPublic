# 🧠 Clanity — Learn Languages with Smart Quizzes

Clanity is an intelligent, file-based language learning Telegram bot built with Python. It helps users expand their vocabulary through interactive quizzes generated from user-uploaded documents.

</br>

## 🔗 Links for project
```bash

https://linktr.ee/clanity

```
</br>

## 🚀 Features

- 🔍 User notifications by Scheduled Tasks Service 
- 🤖 Telegram bot interface for convenient interaction
- 💰 Subscriptions. Integrated MonobankAPI to create subscriptions
- 📄 Upload `.xlsx` files with word translations
- 🧩 Auto-generates quizzes for memorization and testing
</br>

## 📸 Screenshots
<p align="center">
  <img src="https://github.com/user-attachments/assets/f6879e88-47b0-401c-92d2-edfc06107e24" width="1000"/>
</p>



</br>

## 📦 Tech Stack

- **Python 3.11**
- **FastAPI** - API service for processing
- **Celery | Redis** - distributed task queue (user notification; scheduled tasks)
- **SQLAlchemy** – database ORM
- **PostgreSQL** – database service
- **Alembic** – database migrations tool
- **Pydantic** – data validation
- **MinIO** - storage service
- **Aiogram** – Telegram bot framework


</br>

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YehorVoitenko/ClanityLangPublic.git
cd ClanityLangPublic
```

### 2. Run project with docker-compose

``` bash
docker-compose up --build
```

### 3. Enviroments (.env)
```bash
BOT_TOKEN='token'

MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=bucket

POSTGRES_DB=clanity_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres 
POSTGRES_HOST=postgres 
POSTGRES_PORT=5432

PG_ADMIN_USERNAME=pgadmin
PG_ADMIN_PASSWORD=pgadmin

MONO_TOKEN=token

REDIS_HOST=redis 
REDIS_URL="${REDIS_HOST}://${REDIS_HOST}:6379/"
CELERY_BROKER_URL="${REDIS_URL}0"

API_URL=fastapi_app:8000

```

