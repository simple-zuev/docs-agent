from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.models import TaskDetails
from app.repositories.task_repository import MockTaskRepository, TaskRepository


_TASK_REPOSITORY = MockTaskRepository()


def _get_repository(repository: TaskRepository | None = None) -> TaskRepository:
    return repository or _TASK_REPOSITORY


def list_task_summaries(
    repository: TaskRepository | None = None,
) -> list[dict[str, Any]]:
    task_repository = _get_repository(repository)
    return task_repository.list_tasks()


def get_task_details(
    task_id: str, repository: TaskRepository | None = None
) -> TaskDetails:
    task_repository = _get_repository(repository)
    task = task_repository.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task["history_count"] = len(task_repository.list_history(task_id))
    return TaskDetails(**task)


def create_task(
    title: str, task_type: str, repository: TaskRepository | None = None
) -> TaskDetails:
    task_repository = _get_repository(repository)
    task = task_repository.create_task(title=title, task_type=task_type)
    task["history_count"] = len(task_repository.list_history(task["task_id"]))
    return TaskDetails(**task)


def update_task_state(
    task_id: str,
    patch: dict[str, Any],
    repository: TaskRepository | None = None,
) -> TaskDetails:
    task_repository = _get_repository(repository)
    existing = task_repository.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found.")

    previous_status = existing.get("status")
    next_status = patch.get("status")
    task = task_repository.update_task(task_id, patch)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if next_status and next_status != previous_status:
        task_repository.append_history(
            task_id,
            event_type=f"status_changed_to_{next_status}",
            summary=f"Task status changed from {previous_status} to {next_status}.",
            result_state=next_status,
        )
    task["history_count"] = len(task_repository.list_history(task_id))
    return TaskDetails(**task)


def get_task_history(
    task_id: str, repository: TaskRepository | None = None
) -> list[dict[str, Any]]:
    task_repository = _get_repository(repository)
    task = task_repository.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task_repository.list_history(task_id)


def append_history(
    task_id: str,
    event_type: str,
    summary: str,
    result_state: str,
    repository: TaskRepository | None = None,
) -> dict[str, Any]:
    task_repository = _get_repository(repository)
    event = task_repository.append_history(task_id, event_type, summary, result_state)
    if not event:
        raise HTTPException(status_code=404, detail="Task not found.")
    return event
