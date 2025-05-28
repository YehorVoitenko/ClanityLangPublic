from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    user_id: int
    username: str | None = None


class AddUserSessionRequest(BaseModel):
    user_id: int
