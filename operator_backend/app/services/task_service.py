from __future__ import annotations

from fastapi import HTTPException

from app.data import mock_store
from app.models import TaskDetails


def list_task_summaries() -> list[dict]:
    return mock_store.list_tasks()


def get_task_details(task_id: str) -> TaskDetails:
    task = mock_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task["history_count"] = len(mock_store.list_history(task_id))
    return TaskDetails(**task)


def create_task(title: str, task_type: str) -> TaskDetails:
    task = mock_store.create_task(title=title, task_type=task_type)
    task["history_count"] = len(mock_store.list_history(task["task_id"]))
    return TaskDetails(**task)


def update_task_state(task_id: str, patch: dict) -> TaskDetails:
    existing = mock_store.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found.")

    previous_status = existing.get("status")
    next_status = patch.get("status")
    task = mock_store.update_task(task_id, patch)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if next_status and next_status != previous_status:
        mock_store.append_history(
            task_id,
            event_type=f"status_changed_to_{next_status}",
            summary=f"Task status changed from {previous_status} to {next_status}.",
            result_state=next_status,
        )
    task["history_count"] = len(mock_store.list_history(task_id))
    return TaskDetails(**task)


def get_task_history(task_id: str) -> list[dict]:
    task = mock_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return mock_store.list_history(task_id)


def append_history(
    task_id: str, event_type: str, summary: str, result_state: str
) -> dict:
    event = mock_store.append_history(task_id, event_type, summary, result_state)
    if not event:
        raise HTTPException(status_code=404, detail="Task not found.")
    return event
