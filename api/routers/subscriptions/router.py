import logging
from datetime import datetime, timedelta, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlmodel import select

from api.routers.subscriptions.processor import SubscriptionProcessor
from api.routers.subscriptions.schemas import (
    CheckPurchaseStatusResponse,
    GetSubscriptionLinkRequest,
)
from config.banking_integration_config import MONO_API_URL, MONO_TOKEN
from constants.constants import SUBSCRIPTION_PERIOD
from models import PurchaseRegistry, UserSubscriptionLevels, UserData
from processors.purchase_processor import PurchaseProcessor
from services.cache_service.cache_service import (
    cache_user_sub_redis_client,
    USER_SUB_CACHE_STORES_IN_SEC,
)
from services.database import get_database_session

subscription_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

logging.basicConfig(level=logging.INFO)


@subscription_router.post("/monobank/webhook")
async def handle_monobank_webhook(request: Request):
    try:
        purchase_data = await request.json()

    except Exception as e:
        logging.warning(f"ERROR: {e}")

        raise HTTPException(status_code=400, detail="Invalid JSON body")

    return {
        "status": await SubscriptionProcessor.process_subscription_message_from_mono(
            session=next(get_database_session()), purchase_data=purchase_data
        )
    }


@subscription_router.get(
    path="/check_user_subscription_valid/{user_id}",
    response_model=CheckPurchaseStatusResponse,
)
async def check_user_subscription_valid(
        user_id: int, session: Session = Depends(get_database_session)
):
    return PurchaseProcessor.check_purchase_status(user_id=user_id, session=session)


@subscription_router.post(
    path="/get_subscription_link",
)
async def get_subscription_link(
        request: GetSubscriptionLinkRequest,
        session: Session = Depends(get_database_session),
):
    return PurchaseProcessor.send_purchase_request(request=request, session=session)


@subscription_router.post(
    path="/reload_user_subscription/{user_id}",
)
async def reload_user_subscription(
        user_id: int,
        session: Session = Depends(get_database_session),
):
    SUBSCRIPTION_LEVELS = [
        UserSubscriptionLevels.PRO,
    ]

    month_ago = datetime.now() - timedelta(days=SUBSCRIPTION_PERIOD)
    user_instance = session.get(UserData, user_id)

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


class InvoiceStatusWebhook(BaseModel):
    invoiceId: str
    status: str
    modifiedDate: datetime
    amount: int
    currency: str
    maskedCard: str | None = None
    cardTokenStatus: str | None = None
