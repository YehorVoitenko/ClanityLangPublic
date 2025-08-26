from uuid import UUID

from pydantic import BaseModel


class RevokeBackgroundTasks(BaseModel):
    task_id: UUID


class GetBackgroundTasks(BaseModel):
    task_id: UUID
