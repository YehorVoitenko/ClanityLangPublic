from celery.result import AsyncResult
from fastapi import APIRouter

from api.routers.background.schemas import RevokeBackgroundTasks, GetBackgroundTasks
from services.background_task_service.celery_methods import app as celery_app

background_router = APIRouter(prefix="/background", tags=["Background"])


@background_router.post(
    path="/revoke_background_task",
)
async def check_user_subscription_valid(request: RevokeBackgroundTasks):
    celery_app.control.revoke(request.task_id, terminate=True, signal="SIGKILL")
    return {"status": "ok"}


@background_router.post("/get_background_task")
async def get_background_task(request: GetBackgroundTasks):
    task_id = str(request.task_id)
    result = AsyncResult(id=task_id, app=celery_app)

    info = {
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful(),
        "failed": result.failed(),
        "result": str(result.result),
    }

    return info
