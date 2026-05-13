from __future__ import annotations

from copy import deepcopy
from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

TASKS: dict[str, dict[str, Any]] = {
    "task-001": {
        "task_id": "task-001",
        "title": "Prepare diagram package for exchange overview",
        "task_type": "prepare_diagram_package",
        "status": "in_progress",
        "output_state": "preview_ready",
        "approval_state": "required",
        "authority_source": "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ",
        "authority_topic": "diagram source/export/layout rules",
        "relevant_section": "source-of-truth / export expectations",
        "operator_hint": "Retain Mermaid/.drawio source as canonical editable artifact.",
        "drive_object_id": "obj-001",
        "drive_object_title": "exchange_architecture.drawio",
        "object_role": "source_diagram",
        "placement_state": "source_bound",
        "safe_for_mutation": False,
    },
    "task-002": {
        "task_id": "task-002",
        "title": "Read operating prompt document",
        "task_type": "read_document",
        "status": "completed",
        "output_state": "none",
        "approval_state": "not_required",
        "authority_source": "00_AI_OPERATING_AND_DOCUMENT_WORKFLOW_STANDARD_АСТЦВ",
        "authority_topic": "document workflow / output discipline",
        "relevant_section": "bounded read / operator workflow",
        "operator_hint": "Use explicit bounded routes and preserve authority awareness.",
        "drive_object_id": "obj-002",
        "drive_object_title": "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ",
        "object_role": "source_document",
        "placement_state": "verified",
        "safe_for_mutation": False,
    },
}

HISTORY: dict[str, list[dict[str, Any]]] = {
    "task-001": [
        {
            "event_id": "evt-001",
            "task_id": "task-001",
            "event_type": "task_created",
            "summary": "Task created for diagram package preparation.",
            "authority_source": "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ",
            "timestamp": "2026-05-13T11:12:00Z",
            "result_state": "created",
        },
        {
            "event_id": "evt-002",
            "task_id": "task-001",
            "event_type": "preview_ready",
            "summary": "Preview generated from canonical source.",
            "authority_source": "00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ",
            "timestamp": "2026-05-13T11:21:00Z",
            "result_state": "preview_ready",
        },
    ],
    "task-002": [
        {
            "event_id": "evt-003",
            "task_id": "task-002",
            "event_type": "read_completed",
            "summary": "Bounded read completed successfully.",
            "authority_source": "00_AI_OPERATING_AND_DOCUMENT_WORKFLOW_STANDARD_АСТЦВ",
            "timestamp": "2026-05-13T10:55:00Z",
            "result_state": "completed",
        }
    ],
}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def list_tasks() -> list[dict[str, Any]]:
    return [deepcopy(v) for v in TASKS.values()]


def get_task(task_id: str) -> dict[str, Any] | None:
    task = TASKS.get(task_id)
    return deepcopy(task) if task else None


def create_task(title: str, task_type: str) -> dict[str, Any]:
    task_id = f"task-{uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "title": title,
        "task_type": task_type,
        "status": "created",
        "output_state": "none",
        "approval_state": "not_required",
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
    TASKS[task_id] = task
    HISTORY[task_id] = [
        {
            "event_id": f"evt-{uuid4().hex[:8]}",
            "task_id": task_id,
            "event_type": "task_created",
            "summary": f"Task created: {title}",
            "authority_source": "UNBOUND",
            "timestamp": now_iso(),
            "result_state": "created",
        }
    ]
    return deepcopy(task)


def update_task(task_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    if task_id not in TASKS:
        return None
    TASKS[task_id].update({k: v for k, v in patch.items() if v is not None})
    return deepcopy(TASKS[task_id])


def list_history(task_id: str) -> list[dict[str, Any]]:
    return deepcopy(HISTORY.get(task_id, []))


def append_history(
    task_id: str, event_type: str, summary: str, result_state: str
) -> dict[str, Any] | None:
    task = TASKS.get(task_id)
    if not task:
        return None
    event = {
        "event_id": f"evt-{uuid4().hex[:8]}",
        "task_id": task_id,
        "event_type": event_type,
        "summary": summary,
        "authority_source": task["authority_source"],
        "timestamp": now_iso(),
        "result_state": result_state,
    }
    HISTORY.setdefault(task_id, []).append(event)
    return deepcopy(event)
