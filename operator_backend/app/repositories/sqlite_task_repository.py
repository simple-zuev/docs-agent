from __future__ import annotations

import sqlite3
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

TASK_COLUMNS = [
    "task_id",
    "title",
    "task_type",
    "status",
    "output_state",
    "approval_state",
    "created_at",
    "updated_at",
    "created_by",
    "authority_binding_id",
    "drive_context_id",
    "notes",
    "authority_source",
    "authority_topic",
    "relevant_section",
    "operator_hint",
    "drive_object_id",
    "drive_object_title",
    "object_role",
    "placement_state",
    "safe_for_mutation",
]

HISTORY_COLUMNS = [
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
]


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SQLiteTaskRepository:
    """Opt-in SQLite implementation of the task repository boundary.

    This class is not used by the backend runtime default. Callers must create it
    explicitly with a database path whose schema has already been migrated.
    """

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def list_tasks(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY created_at, task_id"
            ).fetchall()
        return [self._task_from_row(row) for row in rows]

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
        return self._task_from_row(row) if row else None

    def create_task(self, title: str, task_type: str) -> dict[str, Any]:
        task_id = f"task-{uuid4().hex[:8]}"
        timestamp = now_iso()
        task = {
            "task_id": task_id,
            "title": title,
            "task_type": task_type,
            "status": "created",
            "output_state": "none",
            "approval_state": "not_required",
            "created_at": timestamp,
            "updated_at": timestamp,
            "created_by": "operator_backend",
            "authority_binding_id": "UNBOUND",
            "drive_context_id": "unbound",
            "notes": "",
            "authority_source": "UNBOUND",
            "authority_topic": "authority binding pending",
            "relevant_section": "to be resolved",
            "operator_hint": "Bind authority source before mutation-capable steps.",
            "drive_object_id": "unbound",
            "drive_object_title": "unbound",
            "object_role": "unclassified",
            "placement_state": "unknown",
            "safe_for_mutation": False,
        }

        with self._connect() as connection:
            self._insert_task(connection, task)
            self._insert_history(
                connection,
                {
                    "event_id": f"evt-{uuid4().hex[:8]}",
                    "task_id": task_id,
                    "event_type": "task_created",
                    "actor": "operator_backend",
                    "summary": f"Task created: {title}",
                    "authority_source": "UNBOUND",
                    "authority_reference": "UNBOUND",
                    "drive_context_reference": "unbound",
                    "approval_reference": "not_required",
                    "timestamp": timestamp,
                    "result_state": "created",
                },
            )
            connection.commit()
        return deepcopy(task)

    def update_task(self, task_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        existing = self.get_task(task_id)
        if existing is None:
            return None

        changes = {key: value for key, value in patch.items() if value is not None}
        if changes:
            changes["updated_at"] = now_iso()
            assignments = ", ".join(f"{key} = ?" for key in changes)
            values = [self._to_storage_value(key, value) for key, value in changes.items()]
            with self._connect() as connection:
                connection.execute(
                    f"UPDATE tasks SET {assignments} WHERE task_id = ?",
                    [*values, task_id],
                )
                connection.commit()
        return self.get_task(task_id)

    def list_history(self, task_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM task_history_events
                WHERE task_id = ?
                ORDER BY timestamp, event_id
                """,
                (task_id,),
            ).fetchall()
        return [self._history_from_row(row) for row in rows]

    def append_history(
        self, task_id: str, event_type: str, summary: str, result_state: str
    ) -> dict[str, Any] | None:
        task = self.get_task(task_id)
        if task is None:
            return None

        event = {
            "event_id": f"evt-{uuid4().hex[:8]}",
            "task_id": task_id,
            "event_type": event_type,
            "actor": "operator_backend",
            "summary": summary,
            "authority_source": task["authority_source"],
            "authority_reference": task["authority_source"],
            "drive_context_reference": task["drive_object_id"],
            "approval_reference": task["approval_state"],
            "timestamp": now_iso(),
            "result_state": result_state,
        }
        with self._connect() as connection:
            self._insert_history(connection, event)
            connection.commit()
        return deepcopy(event)

    def _insert_task(self, connection: sqlite3.Connection, task: dict[str, Any]) -> None:
        placeholders = ", ".join("?" for _ in TASK_COLUMNS)
        columns = ", ".join(TASK_COLUMNS)
        values = [self._to_storage_value(column, task[column]) for column in TASK_COLUMNS]
        connection.execute(
            f"INSERT INTO tasks ({columns}) VALUES ({placeholders})",
            values,
        )

    def _insert_history(
        self, connection: sqlite3.Connection, event: dict[str, Any]
    ) -> None:
        placeholders = ", ".join("?" for _ in HISTORY_COLUMNS)
        columns = ", ".join(HISTORY_COLUMNS)
        values = [event[column] for column in HISTORY_COLUMNS]
        connection.execute(
            f"INSERT INTO task_history_events ({columns}) VALUES ({placeholders})",
            values,
        )

    def _task_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        task = dict(row)
        task["safe_for_mutation"] = bool(task["safe_for_mutation"])
        return deepcopy(task)

    def _history_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return deepcopy(dict(row))

    def _to_storage_value(self, key: str, value: Any) -> Any:
        if key == "safe_for_mutation":
            return 1 if value else 0
        return value
