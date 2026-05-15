from __future__ import annotations

from typing import Any, Protocol

from app.data import mock_store


class TaskRepository(Protocol):
    def list_tasks(self) -> list[dict[str, Any]]: ...

    def get_task(self, task_id: str) -> dict[str, Any] | None: ...

    def create_task(self, title: str, task_type: str) -> dict[str, Any]: ...

    def update_task(
        self, task_id: str, patch: dict[str, Any]
    ) -> dict[str, Any] | None: ...

    def list_history(self, task_id: str) -> list[dict[str, Any]]: ...

    def append_history(
        self, task_id: str, event_type: str, summary: str, result_state: str
    ) -> dict[str, Any] | None: ...


class MockTaskRepository:
    def list_tasks(self) -> list[dict[str, Any]]:
        return mock_store.list_tasks()

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return mock_store.get_task(task_id)

    def create_task(self, title: str, task_type: str) -> dict[str, Any]:
        return mock_store.create_task(title=title, task_type=task_type)

    def update_task(self, task_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        return mock_store.update_task(task_id, patch)

    def list_history(self, task_id: str) -> list[dict[str, Any]]:
        return mock_store.list_history(task_id)

    def append_history(
        self, task_id: str, event_type: str, summary: str, result_state: str
    ) -> dict[str, Any] | None:
        return mock_store.append_history(
            task_id=task_id,
            event_type=event_type,
            summary=summary,
            result_state=result_state,
        )
