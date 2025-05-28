from datetime import datetime

from aiogram.types import Message
from sqlmodel import select

from models import UserSession
from services.database import get_database_session


class UserSessionProcessor:
    @staticmethod
    def create_user_session(message: Message):
        session = next(get_database_session())

        query = select(UserSession).where(UserSession.chat_id == message.chat.id)
        previous_user_session = session.execute(query).scalar()
        if previous_user_session:
            previous_user_session.session_datetime = datetime.utcnow()

        else:
            user_session = UserSession(
                chat_id=message.chat.id,
                user_id=message.chat.id,
                session_datetime=datetime.utcnow(),
            )
            session.add(user_session)

        session.commit()
