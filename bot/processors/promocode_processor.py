import httpx
from aiogram.types import Message

from api.routers.promocodes.schemas import AddPromocodeRequest
from config.api_config import API_URL
from constants.exceptions import NotValidPromocodeRequest


class PromocodeProcessor:
    @staticmethod
    async def process_user_promocode(promocode: str, message: Message) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"http://{API_URL}/promocodes/process_user_promocode",
                json=AddPromocodeRequest(
                    promocode=promocode,
                    user_id=message.chat.id,
                    username=message.from_user.username,
                ).dict(),
            )

            match response.status_code:
                case 200:
                    return response.json()["message"]

            raise NotValidPromocodeRequest()
