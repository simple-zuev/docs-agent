from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


TaskStatus = Literal[
    "created",
    "authority_bound",
    "context_loaded",
    "in_progress",
    "awaiting_approval",
    "awaiting_operator_review",
    "completed",
    "blocked",
    "cancelled",
]

OutputState = Literal[
    "none",
    "preview_ready",
    "body_prepared",
    "export_package_ready",
    "publication_ready",
    "published",
    "review_note_required",
]

ApprovalState = Literal["not_required", "required", "requested", "approved", "rejected"]


class TaskSummary(BaseModel):
    task_id: str
    title: str
    task_type: str
    status: TaskStatus
    output_state: OutputState
    approval_state: ApprovalState


class TaskDetails(TaskSummary):
    authority_source: str
    authority_topic: str
    relevant_section: str
    operator_hint: str
    drive_object_id: str
    drive_object_title: str
    object_role: str
    placement_state: str
    safe_for_mutation: bool
    history_count: int = 0


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=3)
    task_type: str = Field(min_length=3)


class UpdateTaskStateRequest(BaseModel):
    status: TaskStatus | None = None
    output_state: OutputState | None = None
    approval_state: ApprovalState | None = None


class HistoryEvent(BaseModel):
    event_id: str
    task_id: str
    event_type: str
    actor: str
    summary: str
    authority_source: str
    authority_reference: str
    drive_context_reference: str
    approval_reference: str
    timestamp: str
    result_state: str


class AppendHistoryRequest(BaseModel):
    event_type: str = Field(min_length=2)
    summary: str = Field(min_length=3)
    result_state: str = Field(min_length=2)
