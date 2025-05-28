import httpx
from aiogram.types import Message

from api.routers.subscriptions.schemas import (
    GetSubscriptionLinkRequest,
    GetSubscriptionLinkResponse,
)
from config.api_config import API_URL
from constants.exceptions import PurchaseRequestExceptions


class SubscriptionProcessor:
    @staticmethod
    async def check_purchase_status(message: Message) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"http://{API_URL}/subscriptions/check_user_subscription_valid/{message.chat.id}"
            )

            match response.status_code:
                case 200:
                    return response.json()["valid"]

            raise PurchaseRequestExceptions()

    @staticmethod
    async def get_subscription_link(request: GetSubscriptionLinkRequest) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"http://{API_URL}/subscriptions/get_subscription_link",
                json=request.dict(),
            )

            match response.status_code:
                case 200:
                    return GetSubscriptionLinkResponse(
                        **response.json()
                    ).subscription_link

            raise PurchaseRequestExceptions()
