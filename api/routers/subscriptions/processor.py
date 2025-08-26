import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlmodel import select

from config.elastic_config import ElasticAvailableIndexes
from models import UserSubscriptionLevels, UserData, PurchaseRegistry
from services.elastic_service.elastic_service import elastic_client


class SubscriptionProcessor:
    SUBSCRIPTION_LEVELS = [
        UserSubscriptionLevels.PRO,
    ]

    @staticmethod
    def _get_user_by_invoice_id(session: Session, invoice_id: str):
        query = select(PurchaseRegistry.user_id).where(
            PurchaseRegistry.invoice_id == invoice_id
        )
        user_id = session.execute(query).scalar()
        return session.get(UserData, user_id)

    @classmethod
    async def process_subscription_message_from_mono(
            cls, session: Session, purchase_data: json
    ) -> bool:
        elastic_client.index(
            index=ElasticAvailableIndexes.PURCHASES.value, doc_type=purchase_data
        )

        user_instance = cls._get_user_by_invoice_id(
            session=session, invoice_id=purchase_data["invoiceId"]
        )

        if purchase_data.get("status") == "success":
            modified_date = purchase_data.get("modifiedDate")
            destination = purchase_data.get("destination", "")

            for level in cls.SUBSCRIPTION_LEVELS:
                if level.value in destination:
                    user_instance.subscription_level = level

                    user_instance.subscription_date = datetime.strptime(
                        modified_date, "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)

                    session.commit()

                    return True

        return False
