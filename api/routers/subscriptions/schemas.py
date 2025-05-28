from typing import Annotated, Optional, Union

from pydantic import BaseModel, AfterValidator

from models import UserSubscriptionLevels


class CheckPurchaseStatusResponse(BaseModel):
    valid: bool


CostType = Annotated[
    Optional[Union[int, float]], AfterValidator(lambda value: int(value * 10))
]


class GetSubscriptionLinkRequest(BaseModel):
    user_id: int
    cost_in_dollar: CostType = 1
    subscription_level: UserSubscriptionLevels


class GetSubscriptionLinkResponse(BaseModel):
    subscription_link: str
