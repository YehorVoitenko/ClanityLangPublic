import uuid
from datetime import datetime, timedelta
from typing import Union, List

import requests
from aiogram.types import Message
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import select

from config.banking_integration_config import MONO_API_URL, MONO_TOKEN, PURCHASE_UNIQUE_CODE
from constants.constants import MONTH_IN_SECOND, USD_CODE, TELEGRAM_BOT_LINK, SUBSCRIPTION_PERIOD
from constants.exceptions import PurchaseRequestExceptions
from constants.phrases import InteractivePhrases
from models import PurchaseRegistry, UserSubscriptionLevels, UserData
from services.bot_services.buttons import ButtonOrchestrator
from services.cache_service import cache_user_sub_redis_client, USER_SUB_CACHE_STORES_IN_SEC
from services.database import get_database_session


class InvoiceStatus(BaseModel):
    destination: str
    createdDate: str | None
    status: str | None


class PurchaseProcessor:
    @staticmethod
    def send_purchase_request(
            user_id: int,
            cost_in_dollar: Union[int, float],
            subscription_level: UserSubscriptionLevels
    ):
        session = next(get_database_session())
        cost = int(cost_in_dollar * 100)
        request_body = {
            "amount": cost,
            "ccy": USD_CODE,
            "merchantPaymInfo": {
                "reference": str(uuid.uuid4()),
                "destination": f"Покупка програмного забезпечення ({subscription_level.value})",
                "comment": "Know language - know world",
                "basketOrder": [
                    {
                        "name": "Підписка на сервіс Clanity",
                        "qty": 1,
                        "sum": cost,
                        "total": cost,
                        "code": PURCHASE_UNIQUE_CODE
                    }
                ]
            },
            "redirectUrl": TELEGRAM_BOT_LINK,
            "validity": MONTH_IN_SECOND,
            "saveCardData": {
                "saveCard": True
            }
        }
        response = requests.post(
            url=f'{MONO_API_URL}/api/merchant/invoice/create',
            headers={
                'X-Token': MONO_TOKEN
            },
            json=request_body
        )
        if response.status_code == 200:
            new_purchase = PurchaseRegistry(
                user_id=user_id,
                purchase_datetime=str(datetime.utcnow()),
                invoice_id=response.json()['invoiceId']
            )
            session.add(new_purchase)
            session.commit()

            return response.json()['pageUrl']

        raise PurchaseRequestExceptions()

    @staticmethod
    def check_purchase_status(message: Message) -> InvoiceStatus:
        session = next(get_database_session())
        month_ago = datetime.utcnow() - timedelta(days=SUBSCRIPTION_PERIOD)
        query = select(UserData).where(UserData.user_id == message.chat.id)
        user_instance = session.execute(query).scalar()

        check_user_sub_level = (
                user_instance.subscription_level != UserSubscriptionLevels.FREE_TERM or
                not cache_user_sub_redis_client.get(f'subscription_valid:{message.chat.id}')
        )

        if check_user_sub_level:
            query = (
                select(PurchaseRegistry.invoice_id).
                where(
                    PurchaseRegistry.user_id == message.chat.id,
                    PurchaseRegistry.purchase_datetime >= month_ago)
                .order_by(
                    desc(PurchaseRegistry.id)
                )
            )

            invoice_ids = session.execute(query).scalars().all()

            for invoice_id in invoice_ids:
                invoice_data = requests.get(
                    url=f'{MONO_API_URL}/api/merchant/invoice/status?invoiceId={invoice_id}',
                    headers={
                        'X-Token': MONO_TOKEN
                    },
                )
                invoice_data_json = invoice_data.json()
                if invoice_data.status_code == 200 and invoice_data_json['status'] == "success":
                    if UserSubscriptionLevels.SIMPLE.value in invoice_data_json['destination']:
                        user_instance.subscription_level = UserSubscriptionLevels.SIMPLE
                        cache_user_sub_redis_client.set(
                            name=f'subscription_valid:{message.chat.id}',
                            value=UserSubscriptionLevels.SIMPLE.value,
                            ex=USER_SUB_CACHE_STORES_IN_SEC
                        )

                    elif UserSubscriptionLevels.START.value in invoice_data_json['destination']:
                        user_instance.subscription_level = UserSubscriptionLevels.START
                        cache_user_sub_redis_client.set(
                            name=f'subscription_valid:{message.chat.id}',
                            value=UserSubscriptionLevels.START.value,
                            ex=USER_SUB_CACHE_STORES_IN_SEC
                        )

                    elif UserSubscriptionLevels.PRO.value in invoice_data_json['destination']:
                        user_instance.subscription_level = UserSubscriptionLevels.PRO
                        cache_user_sub_redis_client.set(
                            name=f'subscription_valid:{message.chat.id}',
                            value=UserSubscriptionLevels.PRO.value,
                            ex=USER_SUB_CACHE_STORES_IN_SEC
                        )

                    session.commit()

        return None

    @staticmethod
    async def check_user_subscription_for_start(message: Message):
        session = next(get_database_session())
        query = select(UserData.subscription_level).where(UserData.user_id == message.chat.id)

        user_subscription_level = session.execute(query).scalar()

        match user_subscription_level:
            case UserSubscriptionLevels.NON_SUBSCRIPTION:
                await message.answer(
                    text=InteractivePhrases.SUBSCRIPTION_LIST_MESSAGE.value,
                    reply_markup=ButtonOrchestrator.set_subscription_buttons()
                )

        return user_subscription_level

    @staticmethod
    async def compare_user_action_with_sub_level(message: Message, need_sub_levels: List[UserSubscriptionLevels]):
        session = next(get_database_session())
        query = select(UserData.subscription_level).where(UserData.user_id == message.chat.id)
        user_sub_level = session.execute(query).scalar()

        if user_sub_level in need_sub_levels:
            return True

        return False
