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

TASK_SUMMARY_FIELDS = {
    "task_id",
    "title",
    "task_type",
    "status",
    "created_at",
    "updated_at",
    "created_by",
    "authority_binding_id",
    "drive_context_id",
    "output_state",
    "approval_state",
    "notes",
}

TASK_DETAIL_FIELDS = TASK_SUMMARY_FIELDS | {
    "authority_source",
    "authority_topic",
    "relevant_section",
    "operator_hint",
    "drive_object_id",
    "drive_object_title",
    "object_role",
    "placement_state",
    "safe_for_mutation",
    "history_count",
}

HISTORY_EVENT_FIELDS = {
    "event_id",
    "task_id",
    "event_type",
    "actor",
    "summary",
    "authority_source",
    "authority_reference",
    "drive_context_reference",
    "approval_reference",
    "timestamp",
    "result_state",
}

TASK_STATUSES = {
    "created",
    "authority_bound",
    "context_loaded",
    "in_progress",
    "awaiting_approval",
    "awaiting_operator_review",
    "completed",
    "blocked",
    "cancelled",
}

OUTPUT_STATES = {
    "none",
    "preview_ready",
    "body_prepared",
    "export_package_ready",
    "publication_ready",
    "published",
    "review_note_required",
}

APPROVAL_STATES = {"not_required", "required", "requested", "approved", "rejected"}


def assert_timestamp(value: str) -> None:
    assert isinstance(value, str)
    assert value.endswith("Z")


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


def test_task_list_and_details_expose_semantic_contract(
    client: TestClient,
) -> None:
    list_response = client.get("/api/tasks")
    details_response = client.get("/api/tasks/task-001")
    history_response = client.get("/api/tasks/task-001/history")

    assert list_response.status_code == 200
    tasks = list_response.json()
    task_ids = {item["task_id"] for item in tasks}
    assert {"task-001", "task-002"} <= task_ids
    listed_task = next(item for item in tasks if item["task_id"] == "task-001")
    assert TASK_SUMMARY_FIELDS <= listed_task.keys()
    assert listed_task["status"] in TASK_STATUSES
    assert listed_task["output_state"] in OUTPUT_STATES
    assert listed_task["approval_state"] in APPROVAL_STATES
    assert_timestamp(listed_task["created_at"])
    assert_timestamp(listed_task["updated_at"])
    assert listed_task["updated_at"] >= listed_task["created_at"]
    assert listed_task["created_by"]
    assert listed_task["authority_binding_id"]
    assert listed_task["drive_context_id"]
    assert isinstance(listed_task["notes"], str)

    assert details_response.status_code == 200
    assert history_response.status_code == 200
    details = details_response.json()
    history = history_response.json()
    assert TASK_DETAIL_FIELDS <= details.keys()
    assert details["task_id"] == "task-001"
    assert details["history_count"] == len(history)
    assert isinstance(details["safe_for_mutation"], bool)
    assert details["authority_binding_id"] == listed_task["authority_binding_id"]
    assert details["drive_context_id"] == listed_task["drive_context_id"]
    assert all(HISTORY_EVENT_FIELDS <= event.keys() for event in history)


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
    assert HISTORY_EVENT_FIELDS <= history_event.keys()
    assert history_event["task_id"] == payload["task_id"]
    assert history_event["event_type"] == "task_created"
    assert history_event["actor"] == payload["created_by"]
    assert history_event["authority_reference"] == payload["authority_binding_id"]
    assert history_event["drive_context_reference"] == payload["drive_context_id"]
    assert history_event["approval_reference"] == payload["approval_state"]
    assert history_event["result_state"] == payload["status"]
    assert_timestamp(history_event["timestamp"])


def test_update_task_state_and_append_history(client: TestClient) -> None:
    before_details = client.get("/api/tasks/task-001").json()
    before_history = client.get("/api/tasks/task-001/history").json()

    patch_response = client.patch(
        "/api/tasks/task-001",
        json={"status": "awaiting_operator_review", "approval_state": "requested"},
    )

    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["status"] == "awaiting_operator_review"
    assert patched["approval_state"] == "requested"
    assert patched["updated_at"] != before_details["updated_at"]
    assert_timestamp(patched["updated_at"])
    assert patched["history_count"] == before_details["history_count"] + 1

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
    assert HISTORY_EVENT_FIELDS <= event.keys()
    assert event["task_id"] == "task-001"
    assert event["authority_source"] == patched["authority_source"]
    assert event["authority_reference"] == patched["authority_source"]
    assert event["drive_context_reference"] == patched["drive_object_id"]
    assert event["approval_reference"] == patched["approval_state"]
    assert event["actor"] == patched["created_by"]
    assert event["result_state"] == "awaiting_operator_review"
    assert_timestamp(event["timestamp"])

    history_response = client.get("/api/tasks/task-001/history")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == len(before_history) + 2
    status_events = [
        item
        for item in history
        if item["event_type"] == "status_changed_to_awaiting_operator_review"
    ]
    assert len(status_events) == 1
    status_event = status_events[0]
    assert status_event["actor"] == patched["created_by"]
    assert status_event["authority_reference"] == patched["authority_source"]
    assert status_event["drive_context_reference"] == patched["drive_object_id"]
    assert status_event["approval_reference"] == patched["approval_state"]
    assert status_event["result_state"] == patched["status"]
    assert any(item["event_id"] == event["event_id"] for item in history)


def test_update_without_status_change_does_not_append_history(
    client: TestClient,
) -> None:
    before_details = client.get("/api/tasks/task-001").json()
    before_history = client.get("/api/tasks/task-001/history").json()

    response = client.patch(
        "/api/tasks/task-001",
        json={"approval_state": "approved"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["approval_state"] == "approved"
    assert payload["updated_at"] != before_details["updated_at"]
    assert payload["history_count"] == before_details["history_count"]

    history_response = client.get("/api/tasks/task-001/history")
    assert history_response.status_code == 200
    assert history_response.json() == before_history


def test_create_task_validation_errors_are_explicit(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "No", "task_type": "x"})

    assert response.status_code == 422
    error_fields = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "title") in error_fields
    assert ("body", "task_type") in error_fields


def test_update_task_validation_errors_are_explicit(client: TestClient) -> None:
    response = client.patch(
        "/api/tasks/task-001",
        json={"status": "not_a_real_state", "approval_state": "not_real"},
    )

    assert response.status_code == 422
    error_fields = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "status") in error_fields
    assert ("body", "approval_state") in error_fields


def test_append_history_validation_errors_are_explicit(client: TestClient) -> None:
    response = client.post(
        "/api/tasks/task-001/history",
        json={"event_type": "x", "summary": "No", "result_state": "x"},
    )

    assert response.status_code == 422
    error_fields = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "event_type") in error_fields
    assert ("body", "summary") in error_fields
    assert ("body", "result_state") in error_fields
