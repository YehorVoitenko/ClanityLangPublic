from aiogram.types import Message
from sqlalchemy.orm import Session
from sqlmodel import select

from models import UserData, UserFile
from services.database import get_database_session


class UserDBProcessor:
    def __init__(self, session: Session):
        self._session = session

    def get_user_by_id(self, user_id: int):
        query = select(UserData).where(UserData.user_id == user_id)
        user_instance = self._session.execute(query).scalar()

        if user_instance:
            return user_instance

        return None

    def create_user(self, user_id: int, username: str | None = None, commit: bool = True):
        new_user = UserData(user_id=user_id, username=username)
        self._session.add(new_user)
        self._session.flush()

        if commit:
            self._session.commit()
            return new_user

        return None

    def create_user_if_not_exists(self, message: Message):
        user_instance = self.get_user_by_id(user_id=message.chat.id)
        if user_instance:
            return

        self.create_user(user_id=message.chat.id, username=message.from_user.username)


class FileDBProcessor:
    def __init__(self, session: Session):
        self._session = session

    def get_file_link_by_user_id(self, user_id: int):
        query = select(UserFile).where(UserFile.user_id == user_id)
        file_link_instance = self._session.execute(query).scalar()

        if file_link_instance:
            return file_link_instance

        return None

    @staticmethod
    def create_file_link(user_id: int, file_link: str, commit: bool = True):
        session = next(get_database_session())
        new_file_link = UserFile(user_id=user_id, file_link=file_link)
        session.add(new_file_link)
        session.flush()

        if commit:
            session.commit()
            return new_file_link

        return None

    def create_file_link_if_not_exists(self, user_id: int, file_link: str):
        file_link_instance = self.get_file_link_by_user_id(user_id=user_id)
        if file_link_instance:
            return

        self.create_file_link(user_id=user_id, file_link=file_link)
