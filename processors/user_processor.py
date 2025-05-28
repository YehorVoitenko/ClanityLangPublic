from sqlalchemy.orm import Session

from models import UserData


class UserProcessor:
    def __init__(self, session: Session):
        self._session: Session = session

    def get_user_by_id(self, user_id: int) -> UserData | None:
        return self._session.get(UserData, user_id)
