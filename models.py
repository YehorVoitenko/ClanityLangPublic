from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship


class UserSubscriptionLevels(str, Enum):
    NON_SUBSCRIPTION = "NON_SUBSCRIPTION"
    FREE_TERM = "FREE_TERM"
    SIMPLE = "SIMPLE"
    START = "START"
    PRO = "PRO"


class UserFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("userdata.user_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    file_link: str = Field(nullable=False)

    user: Optional["UserData"] = Relationship(back_populates="files")


class PurchaseRegistry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        sa_column=Column(BigInteger, index=True, nullable=False)
    )
    purchase_datetime: datetime = Field(nullable=False)
    invoice_id: str = Field(nullable=False)


class UserData(SQLModel, table=True):
    user_id: int = Field(
        sa_column=Column(BigInteger, index=True, unique=True, primary_key=True),
    )
    username: str = Field(nullable=True)
    subscription_level: UserSubscriptionLevels = Field(
        default=UserSubscriptionLevels.FREE_TERM,
        nullable=True,
    )
    subscription_date: datetime = Field(default_factory=datetime.utcnow, nullable=True)

    files: List[UserFile] = Relationship(back_populates="user")


class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("userdata.user_id", ondelete="CASCADE"),
            index=True,
        )
    )
    chat_id: int = Field(
        sa_column=Column(BigInteger, index=True)
    )
    session_datetime: datetime = Field(nullable=False)
