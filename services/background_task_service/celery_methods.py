import asyncio
from datetime import datetime, timedelta
from random import choice

from aiogram.exceptions import TelegramForbiddenError
from celery import Celery
from sqlmodel import select

from config.background_tasks_config import CELERY_BROKER_URL
from constants.constants import (
    FREE_TERM_SUB_IN_DAYS,
    SUBSCRIPTION_PERIOD,
    PROMOCODE_PERIOD,
    SUPERUSER_IDS,
)
from constants.phrases import USER_NOTIFICATIONS
from models import UserSession, UserData, UserSubscriptionLevels
from services.bot_services.bot_initializer import bot
from services.database import get_database_session

app = Celery("reports", broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)
app.config_from_object("services.background_task_service.celery_config")
app.conf.timezone = "UTC"
app.conf.enable_utc = True


@app.task(name="task.send_user_info_about_update")
def send_user_info_about_update():
    asyncio.run(send_user_info_about_update_processor())


async def send_user_info_about_update_processor():
    session = next(get_database_session())

    query = select(UserData.user_id)
    user_ids = session.execute(query).scalars().all()

    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="<b>NEW UPDATEEEEE 🇺🇦</b> \n\n"
                     "у нашому боті зміни: \n"
                     "😍<u><b>додали український інтерфейс боту</b></u>, для того, щоб інтерфейс став ще легше\n"
                     "🔥тепер можеш спробувати <u><b>всі базові рівні</b></u>: А1, А2, В1, В2 \n"
                     "\n\n"
                     "можеш спробувати оновлення за допомогою /start\n\n"
                     ""
                     "<i>*незабаром додамо ще рівні С1-С2, а також інші тематичні слова</i>",
            )
        except TelegramForbiddenError:
            print(f"Bot was blocked or forbidden to send message to user_id={user_id}")
            continue


@app.task(name="tasks.update_non_sub_to_free_term")
def update_non_sub_to_free_term():
    session = next(get_database_session())

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.NON_SUBSCRIPTION
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.FREE_TERM

    session.commit()


@app.task(name="tasks.update_promocodes_to_non_sub")
def update_promocodes_to_non_sub():
    session = next(get_database_session())
    promocode_period = datetime.utcnow() - timedelta(days=PROMOCODE_PERIOD)

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.PROMOCODE,
        UserData.subscription_date >= promocode_period,
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()


@app.task(name="tasks.send_telegram_message")
def send_telegram_message():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_send_messages())
    finally:
        loop.close()


async def _send_messages():
    session = next(get_database_session())
    two_days_ago = datetime.utcnow() - timedelta(days=2)

    query = select(UserSession).where(UserSession.session_datetime >= two_days_ago)
    user_sessions = session.execute(query).scalars().all()

    for user_session in user_sessions:
        user_session.session_datetime = datetime.utcnow()
        await bot.send_message(
            chat_id=user_session.chat_id,
            text=choice(USER_NOTIFICATIONS),
        )

    session.commit()


@app.task(name="tasks.update_free_term_sub_to_non")
def update_free_term_sub_to_non():
    session = next(get_database_session())
    three_days_ago = datetime.utcnow() - timedelta(days=FREE_TERM_SUB_IN_DAYS)

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.FREE_TERM,
        UserData.subscription_date >= three_days_ago,
        UserData.user_id.notin_(SUPERUSER_IDS),
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()


@app.task(name="tasks.update_user_subscription_levels")
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
        UserData.subscription_date >= month_ago,
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.utcnow()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()
