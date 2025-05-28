from pydantic import BaseModel


class AddPromocodeRequest(BaseModel):
    promocode: str
    user_id: int
    username: str | None = None


class AddPromocodeResponse(BaseModel):
    message: str
