# 🧠 Clanity — Learn Languages with Smart Quizzes

Clanity is an intelligent, file-based language learning Telegram bot built with Python. It helps users expand their vocabulary through interactive quizzes generated from user-uploaded documents.

</br>

## 🔗 Links for project
```bash

https://linktr.ee/clanity

```
</br>

## 🚀 Features

- 📄 Upload `.xlsx` files with word translations
- 🧩 Auto-generates quizzes for memorization and testing
- 🔍 Notifications for inactive
- 🤖 Telegram bot interface for convenient interaction
- 💰 Subscriptions. Integrated MonobankAPI to create subscriptions

</br>

## 📸 Screenshots
<p align="center">
  <img src="https://github.com/user-attachments/assets/30e36d6e-4fc8-4d2b-9788-9b36288f137c" alt="screenshot 1" width="45%" />
  <img src="https://github.com/user-attachments/assets/7bd3fd47-5cd0-465a-bb20-61d36ebab4ae" alt="screenshot 2" width="45%" />
</p>



</br>

## 📦 Tech Stack

- **Python 3.11**
- **Celery | Redis** - distributed task queue 
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
git clone https://github.com/YehorVoitenko/ClanityLang.git
cd Clanity
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

```

