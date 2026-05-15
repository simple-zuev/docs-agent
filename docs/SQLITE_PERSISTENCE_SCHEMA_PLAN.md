# SQLite Persistence Schema Plan

Status: Phase 2 planning artifact only

This document defines the proposed local SQLite persistence schema and migration
approach for `operator_backend`. It does not implement SQLite, add migrations,
add a database file, change backend API schemas, or authorize live Google Drive
or Google Docs execution.

## Scope

The storage target for the local MVP is SQLite. PostgreSQL remains the likely
later target for shared or deployed use if the repository boundary remains
stable.

This plan assumes the current repository contract:

- `TaskRepository` defines task and history access.
- `MockTaskRepository` remains the default runtime backend.
- A future `SQLiteTaskRepository` must be introduced behind explicit
  configuration after schema and migration tests exist.

## Database Location

The SQLite database should live under a local ignored runtime data path, not
under tracked source.

Recommended default pattern:

- `var/operator_backend/operator_backend.sqlite3`

Rules:

- the directory and database file must be local runtime artifacts;
- the database file must not be committed;
- production data, Google exports, OAuth tokens, service account keys, and
  browser/session caches must never be stored in the repository;
- configuration should allow an operator to choose a different local path before
  SQLite becomes usable.

## Tables

The local MVP should start with two durable tables:

- `tasks`
- `task_history_events`

Two future tables are documented but not required for the first SQLite
implementation:

- `approval_records`
- `drive_context_records`

### `tasks`

Purpose: durable current state for an operator task.

Columns:

- `task_id TEXT PRIMARY KEY`
- `title TEXT NOT NULL`
- `task_type TEXT NOT NULL`
- `status TEXT NOT NULL`
- `output_state TEXT NOT NULL`
- `approval_state TEXT NOT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`
- `created_by TEXT NOT NULL`
- `authority_binding_id TEXT NOT NULL`
- `drive_context_id TEXT NOT NULL`
- `notes TEXT NOT NULL DEFAULT ''`
- `authority_source TEXT NOT NULL DEFAULT ''`
- `authority_topic TEXT NOT NULL DEFAULT ''`
- `relevant_section TEXT NOT NULL DEFAULT ''`
- `operator_hint TEXT NOT NULL DEFAULT ''`
- `drive_object_id TEXT NOT NULL DEFAULT ''`
- `drive_object_title TEXT NOT NULL DEFAULT ''`
- `object_role TEXT NOT NULL DEFAULT ''`
- `placement_state TEXT NOT NULL DEFAULT ''`
- `safe_for_mutation INTEGER NOT NULL DEFAULT 0`

Notes:

- `safe_for_mutation` should be stored as `0` or `1` and mapped to/from boolean
  at the repository boundary.
- Detail-only fields are included on `tasks` for the local MVP to avoid early
  normalization. They can be split later only when a concrete need appears.
- `history_count` is not stored. It remains a computed convenience field based
  on `task_history_events`.

Recommended indexes:

- `idx_tasks_status` on `(status)`
- `idx_tasks_updated_at` on `(updated_at)`
- `idx_tasks_task_type` on `(task_type)`
- `idx_tasks_authority_binding_id` on `(authority_binding_id)`
- `idx_tasks_drive_context_id` on `(drive_context_id)`

### `task_history_events`

Purpose: durable event-time trace for task status changes and operator notes.

Columns:

- `event_id TEXT PRIMARY KEY`
- `task_id TEXT NOT NULL`
- `event_type TEXT NOT NULL`
- `actor TEXT NOT NULL`
- `summary TEXT NOT NULL`
- `authority_source TEXT NOT NULL DEFAULT ''`
- `authority_reference TEXT NOT NULL DEFAULT ''`
- `drive_context_reference TEXT NOT NULL DEFAULT ''`
- `approval_reference TEXT NOT NULL DEFAULT ''`
- `timestamp TEXT NOT NULL`
- `result_state TEXT NOT NULL`
- `FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE`

Notes:

- history reference fields are event-time snapshots;
- `result_state` is an event outcome, not necessarily the current task status;
- current service behavior appends history for status changes;
- current service behavior does not append history for non-status patches.

Recommended indexes:

- `idx_task_history_events_task_id_timestamp` on `(task_id, timestamp)`
- `idx_task_history_events_event_type` on `(event_type)`
- `idx_task_history_events_timestamp` on `(timestamp)`

### Future `approval_records`

Purpose: optional future table if approval requests become first-class records.

Columns:

- `approval_id TEXT PRIMARY KEY`
- `task_id TEXT NOT NULL`
- `requested_by TEXT NOT NULL`
- `approved_by TEXT`
- `approval_state TEXT NOT NULL`
- `requested_at TEXT NOT NULL`
- `resolved_at TEXT`
- `reason TEXT NOT NULL DEFAULT ''`
- `FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE`

Recommended indexes:

- `idx_approval_records_task_id` on `(task_id)`
- `idx_approval_records_approval_state` on `(approval_state)`
- `idx_approval_records_requested_at` on `(requested_at)`

Do not add this table in the first SQLite PR unless an explicit approval-flow
need exists.

### Future `drive_context_records`

Purpose: optional future table for Drive-bound context metadata if controlled
live Google execution later needs richer references.

Columns:

- `drive_context_id TEXT PRIMARY KEY`
- `drive_object_id TEXT NOT NULL`
- `drive_object_title TEXT NOT NULL DEFAULT ''`
- `mime_type TEXT NOT NULL DEFAULT ''`
- `web_view_link TEXT NOT NULL DEFAULT ''`
- `parent_folder_id TEXT NOT NULL DEFAULT ''`
- `safe_for_mutation INTEGER NOT NULL DEFAULT 0`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Recommended indexes:

- `idx_drive_context_records_drive_object_id` on `(drive_object_id)`
- `idx_drive_context_records_parent_folder_id` on `(parent_folder_id)`

Do not add this table in the first SQLite PR unless a controlled Drive context
design has been accepted.

## Enum And Value Strategy

SQLite should store enum-like fields as `TEXT` values aligned with the current
API contract:

- `tasks.status`
- `tasks.output_state`
- `tasks.approval_state`
- `task_history_events.event_type`
- `task_history_events.result_state`

The first SQLite implementation should validate these values in Python through
the existing service/model contract rather than introducing early database
`CHECK` constraints. Database-level constraints can be added later if the enum
contract is stable and migration behavior is well tested.

Unknown future values should not be silently normalized. Repository reads should
return stored values, and API response validation should continue to catch
values that do not fit the current public contract.

## Timestamp Strategy

Timestamps should be stored as UTC ISO-8601 strings ending in `Z`, matching the
current mock-runtime API shape.

Rules:

- `created_at` is set once when a task is created;
- `updated_at` changes only when the task record changes;
- history `timestamp` is event creation time;
- history `timestamp` does not automatically replace task `updated_at`;
- repository code should use one timestamp helper so generated strings remain
  deterministic in shape.

Do not store local timezone timestamps in the database.

## Migration Strategy

A future implementation should add a simple migrations folder after this plan is
accepted. This planning PR does not create that folder.

Migration rules:

- no automatic destructive migrations;
- additive migrations first;
- every migration should be named, ordered, and reviewable;
- migration application should be explicit, not hidden inside normal API
  startup until the behavior is validated;
- failed migrations should leave a clear error and avoid partial silent success;
- rollback should be documented per migration when data loss is possible.

Recommended future migration sequence:

1. create `tasks`;
2. create `task_history_events`;
3. add indexes;
4. add optional future tables only after their workflows exist.

## Seed And Bootstrap Strategy

Mock seed data import should be optional and operator-initiated. It is useful for
local development but must not become production data.

Rules:

- do not commit production data;
- do not commit private Google Drive exports;
- do not infer durable schema decisions from exact mock seed strings;
- import should be idempotent or clearly documented as reset-only;
- bootstrap should fail clearly if the target database already contains data and
  the command would overwrite it.

## Backup And Reset Strategy

Because SQLite is file-backed, backup and reset behavior must be explicit.

Recommended approach:

- stop the backend before copying or replacing the database file;
- back up by copying the `.sqlite3` file to an operator-controlled location;
- reset by moving or deleting the local runtime database file;
- never reset automatically from API startup;
- never mix reset behavior with live Google commands.

The first SQLite implementation should document the exact reset command only
after the database path and configuration mechanism exist.

## Repository Integration Plan

Future SQLite work should add `SQLiteTaskRepository` as a second implementation
of the existing `TaskRepository` protocol.

Integration rules:

- `MockTaskRepository` remains default until SQLite is fully validated;
- SQLite must be enabled by explicit configuration;
- routes should not open database connections directly;
- services should continue to depend on the repository boundary;
- repository methods should return copies or fresh dictionaries so callers
  cannot mutate cached internal state;
- missing tasks should continue to return `None` from the repository and `404`
  from the service layer;
- status-change history behavior should remain in the service unless a later
  domain-service change is explicitly approved.

## Future Validation Expectations

SQLite implementation PRs should keep the current API behavior stable and add
repository-specific tests.

Required validation should include:

- existing backend API tests;
- current repository boundary tests;
- SQLite repository CRUD and history tests using a temporary local database;
- copy/no accidental mutation behavior tests;
- migration apply/check tests;
- explicit opt-in configuration tests;
- `make test-backend`;
- `make test-all`;
- `make check`;
- `git diff --check`.

The validation path must stay offline-safe unless a later phase explicitly
authorizes live Google checks.

## Safety Boundaries

Persistence work must not:

- store Google credentials in SQLite;
- read, print, snapshot, or migrate OAuth tokens, service account keys, API keys,
  `.env` files, browser/session caches, or `~/.codex/auth.json`;
- run live Google Drive or Google Docs commands;
- widen mutation capability;
- promote `read-doc`, `get-file`, or `read-doc-from-query`;
- add frontend or `operator_app` work in the same PR;
- change API response field names or public response shapes.

## Recommended Next PRs

1. SQLite configuration path docs and tests: define how an operator opts into a
   local database path while keeping mock runtime as default.
2. Migration folder scaffold: add explicit migration files and migration
   validation commands without changing the default backend.
3. SQLite repository implementation: add `SQLiteTaskRepository` behind explicit
   opt-in configuration with temporary-database tests and API contract
   preservation checks.
