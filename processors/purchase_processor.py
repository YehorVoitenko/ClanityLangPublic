import uuid
from datetime import datetime, timedelta, timezone
from typing import List

import requests
from aiogram.types import Message
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlmodel import select

from api.routers.subscriptions.schemas import (
    CheckPurchaseStatusResponse,
    GetSubscriptionLinkRequest,
    GetSubscriptionLinkResponse,
)
from config.api_config import GLOBAL_SERVER_HOST
from config.banking_integration_config import (
    MONO_API_URL,
    MONO_TOKEN,
    PURCHASE_UNIQUE_CODE,
)
from constants.constants import (
    MONTH_IN_SECOND,
    USD_CODE,
    TELEGRAM_BOT_LINK,
    SUBSCRIPTION_PERIOD,
)
from constants.exceptions import PurchaseRequestExceptions
from models import PurchaseRegistry, UserSubscriptionLevels, UserData
from services.cache_service.cache_service import (
    cache_user_sub_redis_client,
    USER_SUB_CACHE_STORES_IN_SEC,
)
from services.database import get_database_session


class CheckUserActionByCurrentSub(BaseModel):
    user_id: int
    required_sub_levels: List[UserSubscriptionLevels]


class PurchaseProcessor:
    @staticmethod
    def send_purchase_request(
            request: GetSubscriptionLinkRequest, session: Session
    ) -> GetSubscriptionLinkResponse:
        request_body = {
            "amount": request.cost_in_dollar,
            "webHookUrl": f"http://{GLOBAL_SERVER_HOST}:8000/subscriptions/monobank/webhook",
            "ccy": USD_CODE,
            "merchantPaymInfo": {
                "reference": str(uuid.uuid4()),
                "destination": f"Покупка програмного забезпечення ({request.subscription_level.value})",
                "comment": "Know language - know world",
                "basketOrder": [
                    {
                        "name": "Підписка на сервіс Clanity",
                        "qty": 1,
                        "sum": request.cost_in_dollar,
                        "total": request.cost_in_dollar,
                        "code": PURCHASE_UNIQUE_CODE,
                    }
                ],
            },
            "redirectUrl": TELEGRAM_BOT_LINK,
            "validity": MONTH_IN_SECOND,
            "saveCardData": {"saveCard": True},
        }
        response = requests.post(
            url=f"{MONO_API_URL}/api/merchant/invoice/create",
            headers={"X-Token": MONO_TOKEN},
            json=request_body,
        )

        if response.status_code == 200:
            new_purchase = PurchaseRegistry(
                user_id=request.user_id,
                purchase_datetime=str(datetime.now()),
                invoice_id=response.json()["invoiceId"],
            )
            session.add(new_purchase)
            session.commit()

            return GetSubscriptionLinkResponse(
                subscription_link=response.json()["pageUrl"]
            )

        raise PurchaseRequestExceptions()

    @staticmethod
    def check_purchase_status(
            user_id: int, session: Session
    ) -> CheckPurchaseStatusResponse:
        SUBSCRIPTION_LEVELS = [
            UserSubscriptionLevels.PRO,
        ]

        month_ago = datetime.now() - timedelta(days=SUBSCRIPTION_PERIOD)
        user_instance = session.get(UserData, user_id)
        need_check_user_sub_level = (
                user_instance.subscription_level != UserSubscriptionLevels.FREE_TERM
                or not cache_user_sub_redis_client.get(f"subscription_valid:{user_id}")
        )

        if need_check_user_sub_level:
            query = (
                select(PurchaseRegistry.invoice_id)
                .where(
                    PurchaseRegistry.user_id == user_id,
                    PurchaseRegistry.purchase_datetime >= month_ago,
                )
                .order_by(desc(PurchaseRegistry.id))
            )

            invoice_ids = session.execute(query).scalars().all()

            if invoice_ids:
                for invoice_id in invoice_ids:
                    response = requests.get(
                        url=f"{MONO_API_URL}/api/merchant/invoice/status?invoiceId={invoice_id}",
                        headers={"X-Token": MONO_TOKEN},
                    )

                    if response.status_code != 200:
                        continue

                    data = response.json()
                    if data.get("status") != "success":
                        continue

                    destination = data.get("destination", "")
                    for level in SUBSCRIPTION_LEVELS:
                        if level.value in destination:
                            user_instance.subscription_level = level
                            user_instance.subscription_date = datetime.strptime(
                                data["modifiedDate"], "%Y-%m-%dT%H:%M:%SZ"
                            ).replace(tzinfo=timezone.utc)

                            cache_user_sub_redis_client.set(
                                name=f"subscription_valid:{user_id}",
                                value=level.value,
                                ex=USER_SUB_CACHE_STORES_IN_SEC,
                            )

                            session.commit()
                            return CheckPurchaseStatusResponse(valid=True)

            return CheckPurchaseStatusResponse(valid=False)

        return CheckPurchaseStatusResponse(valid=True)

    @staticmethod
    async def get_user_subscription_level(message: Message):
        session = next(get_database_session())
        query = select(UserData.subscription_level).where(
            UserData.user_id == message.chat.id
        )

        user_subscription_level = session.execute(query).scalar()

        return user_subscription_level

    @staticmethod
    async def compare_user_action_with_sub_level(request: CheckUserActionByCurrentSub):
        session = next(get_database_session())
        query = select(UserData.subscription_level).where(
            UserData.user_id == request.user_id
        )
        user_sub_level = session.execute(query).scalar()

        if user_sub_level in request.required_sub_levels:
            return True

        return False
