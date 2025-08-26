import asyncio
from datetime import datetime, timedelta
from random import choice

from aiogram.exceptions import TelegramForbiddenError
from celery import Celery
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlmodel import select

from config.background_tasks_config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
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

app = Celery("reports", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
app.config_from_object("services.background_task_service.celery_config")
app.conf.timezone = "UTC"
app.conf.enable_utc = True
app.task_ignore_result = False


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
                text="<b>NEW UPDATEEEEE 😍</b> \n\n"
                     "у нашому боті зміни: \n"
                     "🎁у нас для тебе <u><b>ПОДАРУНОК))</b></u> три дні безкоштовної підписки на всі види ігор\n"
                     "🏡<u><b>ми додали нову тематику 'ПОБУТ'</b></u>\nці слова для тематичного навчання\n"
                     "\n\n"
                     "можеш спробувати оновлення за допомогою /start\n\n"
                     ""
                     "<i>*незабаром додамо ще рівні С1-С2, а також інші тематичні слова</i>",
            )
        except TelegramForbiddenError:
            print(f"Bot was blocked or forbidden to send message to user_id={user_id}")
            continue


@app.task(name="task.send_message_to_bogdan")
def send_message_to_bogdan():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_message_to_bogdan_processor())


async def send_message_to_bogdan_processor():
    await bot.send_message(
        chat_id=346823500,
        text="Богданчик, бро, всьо відновив)) ти попав на неприємний баг, але всьо виправив🫂\n\nлюблю, обійняв-припідняв))🤍",
    )


@app.task(name="tasks.update_non_sub_to_free_term")
def update_non_sub_to_free_term():
    session = next(get_database_session())

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.NON_SUBSCRIPTION
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.now()
        user_instance.subscription_level = UserSubscriptionLevels.FREE_TERM

    session.commit()


@app.task(name="tasks.update_promocodes_to_non_sub")
def update_promocodes_to_non_sub():
    session = next(get_database_session())
    promocode_period = datetime.now() - timedelta(days=PROMOCODE_PERIOD)

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.PROMOCODE,
        UserData.subscription_date <= promocode_period,
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.now()
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
    two_days_ago = datetime.now() - timedelta(days=7)

    subquery = (
        select(
            UserSession.id,
            UserSession.user_id,
            UserSession.chat_id,
            UserSession.session_datetime,
            func.row_number()
            .over(
                partition_by=UserSession.user_id,
                order_by=UserSession.session_datetime.desc(),
            )
            .label("rnk"),
        )
        .where(UserSession.session_datetime <= two_days_ago)
        .subquery()
    )

    LatestUserSession = aliased(UserSession, subquery)

    query = select(LatestUserSession).where(subquery.c.rnk == 1)
    user_sessions = session.execute(query).scalars().all()

    for user_session in user_sessions:
        user_session.session_datetime = datetime.now()

        try:
            await bot.send_message(
                chat_id=user_session.chat_id,
                text=choice(USER_NOTIFICATIONS),
            )
        except TelegramForbiddenError as e:
            print(f"[WARN] Bot blocked by user {user_session.chat_id}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to send message to {user_session.chat_id}: {e}")

    session.commit()


@app.task(name="tasks.update_free_term_sub_to_non")
def update_free_term_sub_to_non():
    session = next(get_database_session())
    three_days_ago = datetime.now() - timedelta(days=FREE_TERM_SUB_IN_DAYS)

    query = select(UserData).where(
        UserData.subscription_level == UserSubscriptionLevels.FREE_TERM,
        UserData.subscription_date <= three_days_ago,
        UserData.user_id.notin_(SUPERUSER_IDS),
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.now()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()


@app.task(name="tasks.update_user_subscription_levels")
def update_user_subscription_levels():
    session = next(get_database_session())
    month_ago = datetime.now() - timedelta(days=SUBSCRIPTION_PERIOD)

    query = select(UserData).where(
        UserData.subscription_level.in_(
            [
                UserSubscriptionLevels.PRO,
            ]
        ),
        UserData.subscription_date <= month_ago,
    )
    user_instances = session.execute(query).scalars().all()

    for user_instance in user_instances:
        user_instance.subscription_date = datetime.now()
        user_instance.subscription_level = UserSubscriptionLevels.NON_SUBSCRIPTION

    session.commit()
