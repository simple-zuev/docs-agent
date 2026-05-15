from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import mock_store  # noqa: E402
from app.main import app  # noqa: E402


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


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint_reports_mock_runtime(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "service": "operator-backend",
        "mode": "mock-runtime",
    }


def test_task_list_and_details_include_history_count(client: TestClient) -> None:
    list_response = client.get("/api/tasks")
    details_response = client.get("/api/tasks/task-001")

    assert list_response.status_code == 200
    tasks = list_response.json()
    task_ids = {item["task_id"] for item in tasks}
    assert {"task-001", "task-002"} <= task_ids
    listed_task = next(item for item in tasks if item["task_id"] == "task-001")
    assert listed_task["created_at"] == "2026-05-13T11:12:00Z"
    assert listed_task["updated_at"] == "2026-05-13T11:21:00Z"
    assert listed_task["created_by"] == "operator_backend"
    assert listed_task["authority_binding_id"] == "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ"
    assert listed_task["drive_context_id"] == "obj-001"
    assert listed_task["notes"] == "Canonical diagram source is retained for review."

    assert details_response.status_code == 200
    details = details_response.json()
    assert details["task_id"] == "task-001"
    assert details["history_count"] == 2
    assert details["safe_for_mutation"] is False


def test_missing_task_returns_404(client: TestClient) -> None:
    response = client.get("/api/tasks/missing-task")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}


def test_missing_task_subroutes_return_404(client: TestClient) -> None:
    patch_response = client.patch(
        "/api/tasks/missing-task",
        json={"status": "blocked"},
    )
    history_response = client.get("/api/tasks/missing-task/history")
    append_response = client.post(
        "/api/tasks/missing-task/history",
        json={
            "event_type": "task_blocked",
            "summary": "Missing task should not accept history.",
            "result_state": "blocked",
        },
    )

    for response in (patch_response, history_response, append_response):
        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found."}


def test_create_task_defaults_to_unbound_non_mutating_state(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/tasks",
        json={"title": "Prepare operator packet", "task_type": "prepare_packet"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Prepare operator packet"
    assert payload["task_type"] == "prepare_packet"
    assert payload["status"] == "created"
    assert payload["created_at"].endswith("Z")
    assert payload["updated_at"] == payload["created_at"]
    assert payload["created_by"] == "operator_backend"
    assert payload["authority_binding_id"] == "UNBOUND"
    assert payload["drive_context_id"] == "unbound"
    assert payload["approval_state"] == "not_required"
    assert payload["notes"] == ""
    assert payload["authority_source"] == "UNBOUND"
    assert payload["safe_for_mutation"] is False
    assert payload["history_count"] == 1

    history_response = client.get(f"/api/tasks/{payload['task_id']}/history")
    assert history_response.status_code == 200
    history_event = history_response.json()[0]
    assert history_event["event_type"] == "task_created"
    assert history_event["actor"] == "operator_backend"
    assert history_event["authority_reference"] == "UNBOUND"
    assert history_event["drive_context_reference"] == "unbound"
    assert history_event["approval_reference"] == "not_required"


def test_update_task_state_and_append_history(client: TestClient) -> None:
    patch_response = client.patch(
        "/api/tasks/task-001",
        json={"status": "awaiting_operator_review", "approval_state": "requested"},
    )

    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["status"] == "awaiting_operator_review"
    assert patched["approval_state"] == "requested"
    assert patched["updated_at"] >= "2026-05-13T11:21:00Z"
    assert patched["history_count"] == 3

    append_response = client.post(
        "/api/tasks/task-001/history",
        json={
            "event_type": "operator_review_requested",
            "summary": "Operator review requested for preview package.",
            "result_state": "awaiting_operator_review",
        },
    )

    assert append_response.status_code == 200
    event = append_response.json()
    assert event["task_id"] == "task-001"
    assert event["authority_source"] == "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ"
    assert event["authority_reference"] == "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ"
    assert event["drive_context_reference"] == "obj-001"
    assert event["approval_reference"] == "requested"
    assert event["actor"] == "operator_backend"
    assert event["result_state"] == "awaiting_operator_review"

    history_response = client.get("/api/tasks/task-001/history")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 4
    assert history[2]["event_type"] == "status_changed_to_awaiting_operator_review"
    assert history[2]["actor"] == "operator_backend"
    assert history[2]["authority_reference"] == "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ"
    assert history[2]["drive_context_reference"] == "obj-001"
    assert history[2]["approval_reference"] == "requested"
    assert history[2]["result_state"] == "awaiting_operator_review"
    assert history[3]["event_type"] == "operator_review_requested"


def test_update_without_status_change_does_not_append_history(
    client: TestClient,
) -> None:
    response = client.patch(
        "/api/tasks/task-001",
        json={"approval_state": "approved"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["approval_state"] == "approved"
    assert payload["history_count"] == 2


def test_create_task_validation_errors_are_explicit(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "No", "task_type": "x"})

    assert response.status_code == 422
    error_fields = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "title") in error_fields
    assert ("body", "task_type") in error_fields
