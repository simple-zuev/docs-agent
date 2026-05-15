from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.repositories.sqlite_task_repository import SQLiteTaskRepository  # noqa: E402
from scripts.check_migrations import apply_migrations  # noqa: E402


def make_repository(tmp_path: Path) -> SQLiteTaskRepository:
    database_path = tmp_path / "operator.sqlite3"
    apply_migrations(database_path)
    return SQLiteTaskRepository(database_path)


def test_sqlite_repository_creates_task_with_default_history(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)

    task = repository.create_task("Prepare local persistence", "persistence_check")
    history = repository.list_history(task["task_id"])

    assert task["task_id"].startswith("task-")
    assert task["title"] == "Prepare local persistence"
    assert task["task_type"] == "persistence_check"
    assert task["status"] == "created"
    assert task["output_state"] == "none"
    assert task["approval_state"] == "not_required"
    assert task["authority_binding_id"] == "UNBOUND"
    assert task["drive_context_id"] == "unbound"
    assert task["safe_for_mutation"] is False
    assert len(history) == 1
    assert history[0]["event_type"] == "task_created"
    assert history[0]["result_state"] == "created"


def test_sqlite_repository_lists_and_reads_tasks(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    first = repository.create_task("First", "demo")
    second = repository.create_task("Second", "demo")

    listed_ids = {task["task_id"] for task in repository.list_tasks()}

    assert {first["task_id"], second["task_id"]} <= listed_ids
    assert repository.get_task(first["task_id"]) == first
    assert repository.get_task("missing-task") is None


def test_sqlite_repository_update_preserves_mock_patch_semantics(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    task = repository.create_task("Patch me", "demo")

    updated = repository.update_task(
        task["task_id"],
        {"approval_state": "approved", "notes": None, "safe_for_mutation": True},
    )

    assert updated is not None
    assert updated["approval_state"] == "approved"
    assert updated["notes"] == task["notes"]
    assert updated["safe_for_mutation"] is True
    assert updated["updated_at"] >= task["updated_at"]
    assert repository.update_task("missing-task", {"status": "blocked"}) is None


def test_sqlite_repository_appends_history_with_task_context(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    task = repository.create_task("History", "demo")
    repository.update_task(
        task["task_id"],
        {
            "authority_source": "AUTHORITY-TITLE",
            "drive_object_id": "drive-object",
            "approval_state": "requested",
        },
    )

    event = repository.append_history(
        task_id=task["task_id"],
        event_type="operator_note",
        summary="Operator reviewed SQLite repository behavior.",
        result_state="requested",
    )

    assert event is not None
    assert event["event_type"] == "operator_note"
    assert event["authority_source"] == "AUTHORITY-TITLE"
    assert event["authority_reference"] == "AUTHORITY-TITLE"
    assert event["drive_context_reference"] == "drive-object"
    assert event["approval_reference"] == "requested"
    assert event["result_state"] == "requested"
    assert event in repository.list_history(task["task_id"])
    assert (
        repository.append_history(
            "missing-task",
            "operator_note",
            "Missing task should not accept history.",
            "blocked",
        )
        is None
    )


def test_sqlite_repository_returns_copies_not_mutable_cached_refs(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    task = repository.create_task("Copy check", "demo")

    read_task = repository.get_task(task["task_id"])
    assert read_task is not None
    read_task["title"] = "mutated outside repository"
    assert repository.get_task(task["task_id"])["title"] == "Copy check"

    history = repository.list_history(task["task_id"])
    history[0]["summary"] = "mutated outside repository"
    assert repository.list_history(task["task_id"])[0]["summary"] != history[0]["summary"]
