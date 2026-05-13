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


def build_patch_history_event(task: dict, patch: dict) -> tuple[str, str, str]:
    changed_fields = {k: v for k, v in patch.items() if v is not None}
    changed_keys = sorted(changed_fields.keys())

    event_type = "task_updated"
    if "status" in changed_fields:
        event_type = f"status_changed_to_{changed_fields['status']}"

    summary = "Task updated: " + ", ".join(
        f"{key}={changed_fields[key]}" for key in changed_keys
    )

    result_state = (
        changed_fields.get("status") or changed_fields.get("output_state") or "updated"
    )
    return event_type, summary, result_state


def update_task_state(task_id: str, patch: dict) -> TaskDetails:
    changed_fields = {k: v for k, v in patch.items() if v is not None}
    if not changed_fields:
        task = mock_store.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")
        task["history_count"] = len(mock_store.list_history(task_id))
        return TaskDetails(**task)

    task = mock_store.update_task(task_id, changed_fields)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    event_type, summary, result_state = build_patch_history_event(task, changed_fields)
    mock_store.append_history(task_id, event_type, summary, result_state)

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
