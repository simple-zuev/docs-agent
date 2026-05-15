from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import mock_store  # noqa: E402
from app.repositories.task_repository import MockTaskRepository  # noqa: E402


@pytest.fixture(autouse=True)
def reset_mock_store():
    tasks = deepcopy(mock_store.TASKS)
    history = deepcopy(mock_store.HISTORY)
    try:
        yield
    finally:
        mock_store.TASKS.clear()
        mock_store.TASKS.update(tasks)
        mock_store.HISTORY.clear()
        mock_store.HISTORY.update(history)


def test_mock_task_repository_delegates_read_behavior_to_mock_store() -> None:
    repository = MockTaskRepository()

    assert repository.list_tasks() == mock_store.list_tasks()
    assert repository.get_task("task-001") == mock_store.get_task("task-001")
    assert repository.list_history("task-001") == mock_store.list_history("task-001")
    assert repository.get_task("missing-task") is None
    assert repository.list_history("missing-task") == []


def test_mock_task_repository_delegates_write_behavior_to_mock_store() -> None:
    repository = MockTaskRepository()

    created = repository.create_task(
        title="Prepare repository boundary packet",
        task_type="prepare_packet",
    )
    task_id = created["task_id"]

    assert mock_store.get_task(task_id) == created
    assert len(repository.list_history(task_id)) == 1

    patched = repository.update_task(task_id, {"approval_state": "approved"})
    assert patched is not None
    assert patched["approval_state"] == "approved"
    assert mock_store.get_task(task_id) == patched

    event = repository.append_history(
        task_id=task_id,
        event_type="operator_note",
        summary="Repository boundary write path exercised.",
        result_state="approved",
    )

    assert event is not None
    assert event in mock_store.list_history(task_id)
    assert repository.update_task("missing-task", {"status": "blocked"}) is None
    assert (
        repository.append_history(
            task_id="missing-task",
            event_type="operator_note",
            summary="Missing task should not accept history.",
            result_state="blocked",
        )
        is None
    )


def test_mock_task_repository_returns_copies_for_tasks_and_history() -> None:
    repository = MockTaskRepository()

    task = repository.get_task("task-001")
    assert task is not None
    task["title"] = "mutated outside repository"
    assert mock_store.TASKS["task-001"]["title"] != task["title"]

    tasks = repository.list_tasks()
    listed_task = next(item for item in tasks if item["task_id"] == "task-001")
    listed_task["status"] = "blocked"
    assert mock_store.TASKS["task-001"]["status"] != "blocked"

    history = repository.list_history("task-001")
    history[0]["summary"] = "mutated outside repository"
    assert mock_store.HISTORY["task-001"][0]["summary"] != history[0]["summary"]

    event = repository.append_history(
        task_id="task-001",
        event_type="operator_note",
        summary="Repository returned event copy.",
        result_state="in_progress",
    )
    assert event is not None
    event["summary"] = "mutated returned event"
    stored_event = next(
        item
        for item in mock_store.HISTORY["task-001"]
        if item["event_id"] == event["event_id"]
    )
    assert stored_event["summary"] != event["summary"]
