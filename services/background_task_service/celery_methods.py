import asyncio
from datetime import datetime, timedelta
from random import choice

from celery import Celery
from sqlmodel import select

from config.background_tasks_config import CELERY_BROKER_URL
from constants.constants import FREE_TERM_SUB_IN_DAYS, SUBSCRIPTION_PERIOD
from constants.phrases import USER_NOTIFICATIONS
from models import UserSession, UserData, UserSubscriptionLevels
from services.bot_services.bot_initializer import bot
from services.database import get_database_session

app = Celery('reports', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)
app.config_from_object('services.background_task_service.celery_config')
app.conf.timezone = 'UTC'
app.conf.enable_utc = True


@app.task(name='task.send_user_info_about_update')
def send_user_info_about_update():
    asyncio.run(send_user_info_about_update_processor())


async def send_user_info_about_update_processor():
    session = next(get_database_session())

    query = select(UserData.user_id)
    user_ids = session.execute(query).scalars().all()

    for user_id in user_ids:
        await bot.send_message(
            chat_id=user_id,
            text="привіт 🤝\n\n"
                 "у нашому боті з'явилися зміни: \n"
                 "↩️ тепер під час векторини ти можеш пропускати слово\n"
                 "💡 отримувати підказку\n"
                 "🔥 бот почав працювати швидше\n\n"
                 ""
                 "можеш спробувати оновлення за допомогою /start\n\n"
                 ""
                 "<i>*незабаром ми додамо 🇺🇦 інтерфейс, або зможеш залишити 🇺🇸</i>"
                 "<i>також додамо нові слова в різні рівні)</i>"
        )

@app.task(name='tasks.send_telegram_message')
def send_telegram_message():
    asyncio.run(_send_messages())


@app.task(name='tasks.update_free_term_sub_to_non')
def update_free_term_sub_to_non():
    session = next(get_database_session())
    three_days_ago = datetime.utcnow() - timedelta(days=FREE_TERM_SUB_IN_DAYS)

    query = select(UserData).where(UserData.subscription_level == UserSubscriptionLevels.FREE_TERM,
                                   UserData.subscription_date >= three_days_ago)
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()


@app.task(name='tasks.update_user_subscription_levels')
def update_user_subscription_levels():
    session = next(get_database_session())
    month_ago = datetime.utcnow() - timedelta(days=SUBSCRIPTION_PERIOD)

    query = select(UserData).where(
        UserData.subscription_level.in_(
            [
                UserSubscriptionLevels.START,
                UserSubscriptionLevels.SIMPLE,
                UserSubscriptionLevels.PRO,
            ]
        ),
        UserData.subscription_date >= month_ago
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()


async def _send_messages():
    session = next(get_database_session())
    two_days_ago = datetime.utcnow() - timedelta(days=2)

    query = select(UserSession).where(UserSession.session_datetime >= two_days_ago)
    user_sessions = session.execute(query).scalars().all()

    for user_session in user_sessions:
        user_session.session_datetime = datetime.utcnow()
        await bot.send_message(
            chat_id=user_session.chat_id,
            text=choice(USER_NOTIFICATIONS)
        )

    session.commit()
