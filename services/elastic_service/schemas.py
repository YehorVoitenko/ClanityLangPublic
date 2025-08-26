from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserActivity(BaseModel):
    activityId: str
    userId: int
    activityDate: datetime = Field(default_factory=lambda: datetime.now())
    tags: list[str] | None = None
    value: str | None = None
    additional_value: str | None = None
