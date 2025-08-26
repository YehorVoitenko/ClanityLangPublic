from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from processors.instances_db_processors import UserDBProcessor
from processors.user_activity_processor import UserActivityProcessor
from processors.user_processor import UserProcessor
from services.database import get_database_session
from .schemas import CreateUserRequest, AddUserSessionRequest

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/create_user_if_not_exists")
async def create_user_if_not_exists(
        request: CreateUserRequest, session: Session = Depends(get_database_session)
):
    task = UserDBProcessor(session=session)
    return task.create_user_if_not_exists(user_data=request)


@user_router.post("/add_user_session")
async def add_user_session(request: AddUserSessionRequest):
    task = UserActivityProcessor()
    return task.user_tap_start_button(user_id=request.user_id)


@user_router.get("/get_user_by_id/{user_id}")
async def get_user_by_id(
        user_id: int, session: Session = Depends(get_database_session)
):
    task = UserProcessor(session=session)
    return task.get_user_by_id(user_id=user_id)
