from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.routers.subscriptions.schemas import (
    CheckPurchaseStatusResponse,
    GetSubscriptionLinkRequest,
)
from processors.purchase_processor import PurchaseProcessor
from services.database import get_database_session

subscription_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


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
