from datetime import datetime

from sqlalchemy.orm import Session
from sqlmodel import select

from api.routers.promocodes.schemas import AddPromocodeRequest, AddPromocodeResponse
from models import PromocodeRegistry, UserData, UserSubscriptionLevels


class PromocodeProcessor:
    @staticmethod
    async def process_user_promocode(
            request: AddPromocodeRequest, session: Session
    ) -> AddPromocodeResponse:
        promocode = session.execute(
            select(PromocodeRegistry).where(
                PromocodeRegistry.promocode_name == request.promocode
            )
        ).scalar()

        if promocode:
            if promocode.activations == 0:
                return AddPromocodeResponse(
                    message="⚠️Промокод вже використав свій ліміт( \n В наступний раз поспішаааай",
                )

            user = session.execute(
                select(UserData).where(UserData.user_id == request.user_id)
            ).scalar()

            if user and user.subscription_level == UserSubscriptionLevels.PROMOCODE:
                return AddPromocodeResponse(
                    message="😏 Хмммм... він вже в тебе є))",
                )

            if not user:
                user = UserData(user_id=request.user_id, username=request.username)
                session.add(user)

            user.subscription_level = UserSubscriptionLevels.PROMOCODE
            user.subscription_date = datetime.utcnow()

            promocode.activations -= 1

            session.commit()

            return AddPromocodeResponse(
                message="✅ Промокод встановлено, вітаюююю) \n Твоя підписка активована)",
            )

        return AddPromocodeResponse(message="❌ На жаль, такого просокоду не існує(")
