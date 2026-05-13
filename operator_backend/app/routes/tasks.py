from __future__ import annotations

from fastapi import APIRouter

from app.models import (
    AppendHistoryRequest,
    CreateTaskRequest,
    HistoryEvent,
    TaskDetails,
    TaskSummary,
    UpdateTaskStateRequest,
)
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskSummary])
def list_tasks():
    return task_service.list_task_summaries()


@router.post("", response_model=TaskDetails)
def create_task(payload: CreateTaskRequest):
    return task_service.create_task(title=payload.title, task_type=payload.task_type)


@router.get("/{task_id}", response_model=TaskDetails)
def get_task(task_id: str):
    return task_service.get_task_details(task_id)


@router.patch("/{task_id}", response_model=TaskDetails)
def update_task(task_id: str, payload: UpdateTaskStateRequest):
    return task_service.update_task_state(task_id, payload.model_dump())


@router.get("/{task_id}/history", response_model=list[HistoryEvent])
def get_task_history(task_id: str):
    return task_service.get_task_history(task_id)


@router.post("/{task_id}/history", response_model=HistoryEvent)
def append_task_history(task_id: str, payload: AppendHistoryRequest):
    return task_service.append_history(
        task_id=task_id,
        event_type=payload.event_type,
        summary=payload.summary,
        result_state=payload.result_state,
    )
