from __future__ import annotations

import uuid

import httpx


BASE_URL = "http://127.0.0.1:8000/api"


def test_list_tasks() -> None:
    response = httpx.get(f"{BASE_URL}/tasks", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    first = payload[0]
    assert "task_id" in first
    assert "title" in first
    assert "task_type" in first
    assert "status" in first
    assert "output_state" in first
    assert "approval_state" in first


def test_get_task_details() -> None:
    tasks = httpx.get(f"{BASE_URL}/tasks", timeout=5.0).json()
    task_id = tasks[0]["task_id"]

    response = httpx.get(f"{BASE_URL}/tasks/{task_id}", timeout=5.0)
    assert response.status_code == 200

    payload = response.json()
    assert payload["task_id"] == task_id
    assert "history_count" in payload
    assert "authority_source" in payload
    assert "drive_object_title" in payload


def test_get_task_history() -> None:
    tasks = httpx.get(f"{BASE_URL}/tasks", timeout=5.0).json()
    task_id = tasks[0]["task_id"]

    response = httpx.get(f"{BASE_URL}/tasks/{task_id}/history", timeout=5.0)
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        first = payload[0]
        assert "event_id" in first
        assert "event_type" in first
        assert "summary" in first
        assert "result_state" in first


def test_create_task() -> None:
    title = f"Smoke API task {uuid.uuid4().hex[:8]}"
    response = httpx.post(
        f"{BASE_URL}/tasks",
        json={"title": title, "task_type": "startup_check"},
        timeout=5.0,
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["title"] == title
    assert payload["task_type"] == "startup_check"
    assert payload["status"] == "created"
    assert payload["history_count"] == 1


def test_patch_task_updates_state_and_appends_history() -> None:
    title = f"Patch API task {uuid.uuid4().hex[:8]}"
    created = httpx.post(
        f"{BASE_URL}/tasks",
        json={"title": title, "task_type": "startup_check"},
        timeout=5.0,
    )
    assert created.status_code == 200
    task = created.json()
    task_id = task["task_id"]

    history_before = httpx.get(f"{BASE_URL}/tasks/{task_id}/history", timeout=5.0)
    assert history_before.status_code == 200
    before_items = history_before.json()
    before_count = len(before_items)

    patched = httpx.patch(
        f"{BASE_URL}/tasks/{task_id}",
        json={"status": "in_progress"},
        timeout=5.0,
    )
    assert patched.status_code == 200
    patched_payload = patched.json()
    assert patched_payload["status"] == "in_progress"
    assert patched_payload["history_count"] == before_count + 1

    history_after = httpx.get(f"{BASE_URL}/tasks/{task_id}/history", timeout=5.0)
    assert history_after.status_code == 200
    after_items = history_after.json()
    assert len(after_items) == before_count + 1
    assert after_items[-1]["event_type"] == "status_changed_to_in_progress"
    assert after_items[-1]["result_state"] == "in_progress"


def test_missing_task_returns_404() -> None:
    response = httpx.get(f"{BASE_URL}/tasks/task-does-not-exist", timeout=5.0)
    assert response.status_code == 404


def test_invalid_status_returns_422() -> None:
    title = f"Invalid status task {uuid.uuid4().hex[:8]}"
    created = httpx.post(
        f"{BASE_URL}/tasks",
        json={"title": title, "task_type": "startup_check"},
        timeout=5.0,
    )
    assert created.status_code == 200
    task_id = created.json()["task_id"]

    response = httpx.patch(
        f"{BASE_URL}/tasks/{task_id}",
        json={"status": "definitely_invalid_status"},
        timeout=5.0,
    )
    assert response.status_code == 422
