from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from fastapi import HTTPException

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services import task_service  # noqa: E402


def make_task(task_id: str = "fake-task") -> dict[str, Any]:
    return {
        "task_id": task_id,
        "title": "Injected repository task",
        "task_type": "repository_boundary_check",
        "status": "in_progress",
        "created_at": "2026-05-15T00:00:00Z",
        "updated_at": "2026-05-15T00:00:00Z",
        "created_by": "fake_repository",
        "authority_binding_id": "AUTHORITY",
        "drive_context_id": "drive-context",
        "output_state": "none",
        "approval_state": "required",
        "notes": "",
        "authority_source": "Authority label",
        "authority_topic": "repository boundary",
        "relevant_section": "service injection",
        "operator_hint": "Use injected repository.",
        "drive_object_id": "drive-object",
        "drive_object_title": "Injected object",
        "object_role": "source_document",
        "placement_state": "verified",
        "safe_for_mutation": False,
    }


def make_history_event(
    task_id: str = "fake-task",
    event_id: str = "fake-event-001",
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "task_id": task_id,
        "event_type": "task_created",
        "actor": "fake_repository",
        "summary": "Task created in fake repository.",
        "authority_source": "Authority label",
        "authority_reference": "Authority label",
        "drive_context_reference": "drive-object",
        "approval_reference": "required",
        "timestamp": "2026-05-15T00:00:00Z",
        "result_state": "created",
    }


class FakeTaskRepository:
    def __init__(
        self,
        task: dict[str, Any] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> None:
        self.tasks = {task["task_id"]: deepcopy(task)} if task else {}
        self.history = (
            {task["task_id"]: deepcopy(history or [])} if task is not None else {}
        )
        self.appended_events: list[dict[str, Any]] = []
        self.calls: list[str] = []

    def list_tasks(self) -> list[dict[str, Any]]:
        self.calls.append("list_tasks")
        return deepcopy(list(self.tasks.values()))

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        self.calls.append("get_task")
        task = self.tasks.get(task_id)
        return deepcopy(task) if task else None

    def create_task(self, title: str, task_type: str) -> dict[str, Any]:
        self.calls.append("create_task")
        task = make_task(task_id="fake-created-task")
        task["title"] = title
        task["task_type"] = task_type
        task["status"] = "created"
        task["approval_state"] = "not_required"
        self.tasks[task["task_id"]] = deepcopy(task)
        self.history[task["task_id"]] = [make_history_event(task["task_id"])]
        return deepcopy(task)

    def update_task(self, task_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        self.calls.append("update_task")
        task = self.tasks.get(task_id)
        if task is None:
            return None
        changes = {key: value for key, value in patch.items() if value is not None}
        if changes:
            changes["updated_at"] = "2026-05-15T00:01:00Z"
        task.update(changes)
        return deepcopy(task)

    def list_history(self, task_id: str) -> list[dict[str, Any]]:
        self.calls.append("list_history")
        return deepcopy(self.history.get(task_id, []))

    def append_history(
        self, task_id: str, event_type: str, summary: str, result_state: str
    ) -> dict[str, Any] | None:
        self.calls.append("append_history")
        task = self.tasks.get(task_id)
        if task is None:
            return None
        event = make_history_event(
            task_id=task_id,
            event_id=f"fake-event-{len(self.history.get(task_id, [])) + 1}",
        )
        event.update(
            {
                "event_type": event_type,
                "summary": summary,
                "approval_reference": task["approval_state"],
                "result_state": result_state,
            }
        )
        self.history.setdefault(task_id, []).append(event)
        self.appended_events.append(deepcopy(event))
        return deepcopy(event)


def test_service_reads_task_details_from_injected_repository() -> None:
    repository = FakeTaskRepository(
        task=make_task(),
        history=[make_history_event(), make_history_event(event_id="fake-event-002")],
    )

    details = task_service.get_task_details("fake-task", repository=repository)

    assert details.task_id == "fake-task"
    assert details.history_count == 2
    assert repository.calls == ["get_task", "list_history"]


def test_service_uses_injected_repository_for_core_task_operations() -> None:
    repository = FakeTaskRepository(
        task=make_task(),
        history=[make_history_event()],
    )

    summaries = task_service.list_task_summaries(repository=repository)
    created = task_service.create_task(
        title="Created through injected repository",
        task_type="repository_boundary_check",
        repository=repository,
    )
    history = task_service.get_task_history("fake-task", repository=repository)
    event = task_service.append_history(
        task_id="fake-task",
        event_type="operator_note",
        summary="Service append used injected repository.",
        result_state="in_progress",
        repository=repository,
    )

    assert summaries[0]["task_id"] == "fake-task"
    assert created.task_id == "fake-created-task"
    assert created.history_count == 1
    assert history[0]["task_id"] == "fake-task"
    assert event["event_type"] == "operator_note"
    assert "list_tasks" in repository.calls
    assert "create_task" in repository.calls
    assert "append_history" in repository.calls


def test_status_update_through_injected_repository_appends_one_history_event() -> None:
    repository = FakeTaskRepository(
        task=make_task(),
        history=[make_history_event()],
    )

    details = task_service.update_task_state(
        "fake-task",
        {"status": "awaiting_operator_review", "approval_state": "requested"},
        repository=repository,
    )

    assert details.status == "awaiting_operator_review"
    assert details.approval_state == "requested"
    assert details.history_count == 2
    assert len(repository.appended_events) == 1
    assert repository.appended_events[0]["event_type"] == (
        "status_changed_to_awaiting_operator_review"
    )
    assert repository.appended_events[0]["result_state"] == ("awaiting_operator_review")


def test_non_status_update_with_fake_repository_does_not_append_history() -> None:
    repository = FakeTaskRepository(
        task=make_task(),
        history=[make_history_event()],
    )

    details = task_service.update_task_state(
        "fake-task",
        {"approval_state": "approved"},
        repository=repository,
    )

    assert details.approval_state == "approved"
    assert details.history_count == 1
    assert repository.appended_events == []


@pytest.mark.parametrize(
    ("service_call", "expected_status_code"),
    [
        (lambda repository: task_service.get_task_details("missing", repository), 404),
        (lambda repository: task_service.get_task_history("missing", repository), 404),
        (
            lambda repository: task_service.update_task_state(
                "missing", {"status": "blocked"}, repository
            ),
            404,
        ),
        (
            lambda repository: task_service.append_history(
                "missing",
                "operator_note",
                "Missing task should not accept history.",
                "blocked",
                repository,
            ),
            404,
        ),
    ],
)
def test_missing_task_through_injected_repository_raises_404(
    service_call, expected_status_code: int
) -> None:
    repository = FakeTaskRepository()

    with pytest.raises(HTTPException) as exc_info:
        service_call(repository)

    assert exc_info.value.status_code == expected_status_code
    assert exc_info.value.detail == "Task not found."
