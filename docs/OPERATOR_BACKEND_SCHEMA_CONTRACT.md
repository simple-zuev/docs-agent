# Operator Backend Schema Contract

Status: Phase 1 mock-runtime contract

This document defines the canonical field model for the current
`operator_backend` API surface. It is based on
`audits/operator_backend_schema_contract_audit_2026-05-15.txt` and is intended
to guide future backend and frontend work without changing runtime behavior.

## Current Status

The operator backend is currently a mock-runtime API only. Its task records,
history records, and example values are seed-backed development fixtures, not a
production persistence model.

The current API shape may be used as a local development contract, but mock
data details must not be treated as production schema decisions.

## Non-Goals

- No production persistence is defined by this contract.
- No live Google Drive or Google Docs task execution is defined by this
  contract.
- No frontend rebuild is authorized by this contract.
- No runtime schema migration is implied by this document.

## Task List / TaskSummary Fields

Task list responses should remain compact. `TaskSummary` is the canonical list
item shape for scanning tasks and should avoid detail-only trace fields unless a
list view has a concrete need.

Canonical list fields:

- `task_id`: stable task identifier.
- `title`: human-readable task title.
- `task_type`: task category or operation type.
- `status`: current task lifecycle state.
- `output_state`: current output state for the task.
- `approval_state`: current approval state for the task.
- `created_at`: task creation timestamp.
- `updated_at`: last task record mutation timestamp.
- `created_by`: actor that created the task.
- `authority_binding_id`: canonical task-level authority binding identifier.
- `drive_context_id`: canonical task-level Drive context identifier.

## Task Details / TaskDetails Fields

Task detail responses may include richer context needed by an operator detail
screen. `TaskDetails` includes all `TaskSummary` fields plus detail-only context
and convenience fields.

Canonical detail fields:

- all canonical `TaskSummary` fields.
- `notes`: operator-facing notes when present.
- `authority_source` or a future `authority_title`: human-readable authority
  label only when distinct from `authority_binding_id`.
- `authority_topic`: human-readable authority topic when present.
- `relevant_section`: human-readable section hint when present.
- `operator_hint`: mock/operator guidance when present.
- `drive_object_id`: detail-only Drive object identifier only when distinct from
  `drive_context_id`.
- `drive_object_title`: human-readable Drive object title when present.
- `object_role`: role of the bound object in the task.
- `placement_state`: current placement state when present.
- `safe_for_mutation`: current mutation safety signal when present.
- `history_count`: convenience count of history events for the task.

## HistoryEvent Fields

`HistoryEvent` represents an event-time trace. Its reference fields should
describe the state or binding captured when the event was created, not silently
reinterpret the current task record.

Canonical history fields:

- `event_id`: stable history event identifier.
- `task_id`: task associated with the event.
- `event_type`: event category, such as a status-change event.
- `actor`: actor that produced the event.
- `summary`: human-readable event summary.
- `timestamp`: event creation timestamp.
- `result_state`: event outcome.
- `authority_reference`: event-time authority reference.
- `drive_context_reference`: event-time Drive context reference.
- `approval_reference`: event-time approval reference only under the policy
  below.

## Authority Field Policy

`authority_binding_id` is the canonical task-level authority field. Backend,
frontend, and future persistence work should prefer this field when identifying
the authority binding attached to a task.

`authority_source` should be used only when it is a human-readable value and is
distinct from `authority_binding_id`, such as a title, name, or label. If it
duplicates the canonical id, it should be treated as mock-runtime residue and
not expanded into new contracts.

History authority fields have event-time semantics. `authority_reference`
should be interpreted as the authority binding captured at event creation time.
A future production cleanup may rename this to
`authority_binding_id_at_event`.

## Drive Context Field Policy

`drive_context_id` is the canonical task-level Drive context field. It identifies
the Drive context or object that the task is bound to at the task level.

`drive_object_id` should appear only in details and only when it is distinct
from `drive_context_id`, such as when a task-level context and a specific Drive
object need separate identifiers.

History Drive fields have event-time semantics. `drive_context_reference`
should be interpreted as the Drive context captured at event creation time. A
future production cleanup may rename this to `drive_context_id_at_event`.

## Approval Field Policy

`approval_state` is the canonical current task approval field.

`approval_reference` must not imply an external approval artifact, request id,
or review object unless such an artifact actually exists. In the current
mock-runtime model, it should be read as event-time approval state only.

A future production cleanup may rename event approval state to
`approval_state_at_event`, unless a real approval artifact id is introduced.

## Status And History Policy

`status` is the current lifecycle state of the task record.

`result_state` is the outcome recorded on a history event. It may equal a task
status for status-change events, but clients should not treat it as a required
mirror of the current task status.

`history_count` is a convenience detail field. The authoritative detailed
history source is the task history endpoint, not the count.

The current mock-runtime behavior records history for status changes. Non-status
patches may update the task record without producing a history event.

## `updated_at` Semantics

`updated_at` means the last mutation time of the task record.

It does not necessarily mean the timestamp of the latest history event. A task
record may be updated for approval, output, or other non-status fields without a
new history event under the current mock-runtime contract.

## Mock-Only / Seed-Only Fields

The following values are mock-runtime or seed-data details unless promoted by a
future schema decision:

- exact seed timestamps.
- exact seed document titles.
- exact seed notes text.
- seed-specific actor values.
- `notes` content.
- `authority_topic`.
- `relevant_section`.
- `operator_hint`.
- `drive_object_title`.
- `object_role`.
- `placement_state`.
- `safe_for_mutation`.

Tests and frontend work should avoid depending on exact seed values when the
semantic contract only requires a present value, an enum value, or a relationship
between fields.

## Frontend Guidance

Task list screens should use the compact list contract. They should avoid
depending on richer detail-only fields unless the API intentionally promotes
those fields into `TaskSummary`.

Task detail screens may use richer authority, Drive, approval, placement, and
history context from `TaskDetails` and the history endpoint.

Any frontend that uses this backend during Phase 1 must clearly show that the
system is in mock-runtime state. It must not imply production persistence, live
Google-backed task execution, or completed approval artifacts that do not exist.

## Future PR Sequence

Recommended order:

1. Test-only semantic contract cleanup: adjust backend tests to assert field
   presence, enums, and semantic relationships instead of exact seed data where
   appropriate.
2. Optional production schema cleanup: rename or remove ambiguous fields only
   after the canonical contract and compatibility expectations are accepted.
3. Persistence design later: define durable storage only after canonical names
   and event semantics are settled.
4. Frontend rebuild after canonical model acceptance: build UI against the
   accepted compact list and detail contracts, with mock-runtime state clearly
   visible.
