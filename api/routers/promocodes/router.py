from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.routers.promocodes.schemas import AddPromocodeRequest
from processors.promocode_processor import PromocodeProcessor
from services.database import get_database_session

promocodes_router = APIRouter(prefix="/promocodes", tags=["Promocodes"])


@promocodes_router.post(
    path="/process_user_promocode",
)
async def check_user_subscription_valid(
        request: AddPromocodeRequest, session: Session = Depends(get_database_session)
):
    return await PromocodeProcessor.process_user_promocode(
        session=session, request=request
    )
