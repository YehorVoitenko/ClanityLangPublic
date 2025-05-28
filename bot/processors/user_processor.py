import httpx
from aiogram.types import Message

from api.routers.user.schemas import CreateUserRequest, AddUserSessionRequest
from config.api_config import API_URL
from constants.exceptions import UserNotExists
from models import UserData


class UserProcessor:
    @staticmethod
    async def create_user_if_not_exists(message: Message):
        async with httpx.AsyncClient() as client:
            await client.post(
                url=f"http://{API_URL}/user/create_user_if_not_exists",
                json=CreateUserRequest(
                    user_id=message.chat.id,
                    username=message.from_user.username,
                ).dict(),
            )

    @staticmethod
    async def add_user_session(message: Message):
        async with httpx.AsyncClient() as client:
            await client.post(
                url=f"http://{API_URL}/user/add_user_session",
                json=AddUserSessionRequest(
                    user_id=message.chat.id,
                ).dict(),
            )

    @staticmethod
    async def get_user_by_id(message: Message) -> UserData:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"http://{API_URL}/user/get_user_by_id/{message.chat.id}",
            )

        match response.status_code:
            case 200:
                return UserData(**response.json())

        raise UserNotExists()
