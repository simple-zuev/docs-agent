from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.check_migrations import (  # noqa: E402
    apply_migrations,
    migration_files,
    sqlite_indexes,
    sqlite_tables,
)


def test_migration_files_are_ordered_and_present() -> None:
    files = migration_files()

    assert [path.name for path in files] == ["0001_initial_schema.sql"]


def test_initial_schema_migration_creates_expected_tables_and_indexes(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "migration-check.sqlite3"

    apply_migrations(database_path)

    assert sqlite_tables(database_path) == {"tasks", "task_history_events"}
    assert {
        "idx_tasks_status",
        "idx_tasks_updated_at",
        "idx_tasks_task_type",
        "idx_tasks_authority_binding_id",
        "idx_tasks_drive_context_id",
        "idx_task_history_events_task_id_timestamp",
        "idx_task_history_events_event_type",
        "idx_task_history_events_timestamp",
    } <= sqlite_indexes(database_path)


def test_initial_schema_columns_match_contract(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-columns.sqlite3"
    apply_migrations(database_path)

    with sqlite3.connect(database_path) as connection:
        task_columns = {
            row[1]: row[2]
            for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
        }
        history_columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(task_history_events)"
            ).fetchall()
        }

    assert task_columns == {
        "task_id": "TEXT",
        "title": "TEXT",
        "task_type": "TEXT",
        "status": "TEXT",
        "output_state": "TEXT",
        "approval_state": "TEXT",
        "created_at": "TEXT",
        "updated_at": "TEXT",
        "created_by": "TEXT",
        "authority_binding_id": "TEXT",
        "drive_context_id": "TEXT",
        "notes": "TEXT",
        "authority_source": "TEXT",
        "authority_topic": "TEXT",
        "relevant_section": "TEXT",
        "operator_hint": "TEXT",
        "drive_object_id": "TEXT",
        "drive_object_title": "TEXT",
        "object_role": "TEXT",
        "placement_state": "TEXT",
        "safe_for_mutation": "INTEGER",
    }
    assert history_columns == {
        "event_id": "TEXT",
        "task_id": "TEXT",
        "event_type": "TEXT",
        "actor": "TEXT",
        "summary": "TEXT",
        "authority_source": "TEXT",
        "authority_reference": "TEXT",
        "drive_context_reference": "TEXT",
        "approval_reference": "TEXT",
        "timestamp": "TEXT",
        "result_state": "TEXT",
    }


def test_foreign_key_delete_cascades_history(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-fk.sqlite3"
    apply_migrations(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO tasks (
                task_id, title, task_type, status, output_state, approval_state,
                created_at, updated_at, created_by, authority_binding_id,
                drive_context_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "task-001",
                "Task",
                "demo",
                "created",
                "none",
                "not_required",
                "2026-05-15T00:00:00Z",
                "2026-05-15T00:00:00Z",
                "test",
                "AUTHORITY",
                "drive-context",
            ),
        )
        connection.execute(
            """
            INSERT INTO task_history_events (
                event_id, task_id, event_type, actor, summary, timestamp, result_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "event-001",
                "task-001",
                "task_created",
                "test",
                "Task created.",
                "2026-05-15T00:00:00Z",
                "created",
            ),
        )
        connection.execute("DELETE FROM tasks WHERE task_id = ?", ("task-001",))
        history_count = connection.execute(
            "SELECT COUNT(*) FROM task_history_events"
        ).fetchone()[0]

    assert history_count == 0


def test_validation_helper_can_run_against_in_memory_database() -> None:
    apply_migrations(":memory:")
