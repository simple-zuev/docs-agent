# Backend Persistence Readiness Plan

Status: Phase 2 planning artifact

This document defines the persistence-readiness direction for `operator_backend`.
It does not implement persistence, change runtime behavior, or authorize live
Google Drive / Google Docs task execution.

## Current State

The operator backend is currently a local mock-runtime API. It exposes task and
history endpoints, and its schema contract is documented in
`docs/OPERATOR_BACKEND_SCHEMA_CONTRACT.md`.

Current backend data is held in in-memory mock structures. That is acceptable for
local prototyping and API contract testing, but it is not a durable persistence
model.

## Phase 2 Objective

Phase 2 should prepare the backend for local durable task state without expanding
live Google behavior.

The objective is:

- preserve the current mock API contract while planning persistence;
- choose a local-first storage approach;
- define the minimum durable entities;
- define migration and rollback expectations;
- keep frontend and live Google execution out of the persistence planning PR.

## Non-Goals

This plan does not authorize:

- implementing a database in this PR;
- adding production persistence immediately;
- changing API field names;
- connecting backend handlers to live Google Drive / Google Docs;
- adding frontend/operator_app work;
- adding multi-user authentication or external deployment;
- promoting degraded document access commands.

## Storage Options

### Option A: SQLite for local MVP

SQLite is the preferred local MVP candidate because:

- it is simple to run on a single Mac;
- it avoids external service setup;
- it supports durable task/history state;
- it is easy to back up and inspect;
- it can support a later migration to PostgreSQL if repository/service boundaries
  are kept clean.

Risks:

- not suitable for multi-user production without careful constraints;
- limited concurrent-write model;
- file backup/restore discipline must be explicit.

### Option B: PostgreSQL for team/internal deployment

PostgreSQL is the likely later target for a team or deployed internal service.
It is not necessary for the local MVP unless multi-user persistence becomes an
immediate requirement.

Risks:

- more setup overhead;
- more moving parts for local operator use;
- can slow down the current local-product iteration.

### Recommendation

Use SQLite for the local persistence MVP, but design the repository layer so
PostgreSQL can be introduced later without rewriting the API surface.

## Minimum Durable Entities

### Task

Purpose: durable current state of an operator task.

Candidate fields:

- `task_id`
- `title`
- `task_type`
- `status`
- `output_state`
- `approval_state`
- `created_at`
- `updated_at`
- `created_by`
- `authority_binding_id`
- `drive_context_id`
- `notes`

Notes:

- `updated_at` means last task record mutation.
- `authority_binding_id` is the canonical authority field.
- `drive_context_id` is the canonical Drive context field.
- `notes` may remain optional / nullable.

### Task Detail Context

Purpose: optional richer context for task detail screens.

Candidate fields can remain on the task table for the local MVP or be split
later if they become normalized entities:

- `authority_source` or future `authority_title`
- `authority_topic`
- `relevant_section`
- `operator_hint`
- `drive_object_id`
- `drive_object_title`
- `object_role`
- `placement_state`
- `safe_for_mutation`

Guidance:

- do not add new detail fields before a concrete UI or execution need exists;
- avoid treating mock seed values as normalized production structures.

### History Event

Purpose: durable event-time trace of task changes and operator notes.

Candidate fields:

- `event_id`
- `task_id`
- `event_type`
- `actor`
- `summary`
- `timestamp`
- `result_state`
- `authority_reference` or future `authority_binding_id_at_event`
- `drive_context_reference` or future `drive_context_id_at_event`
- `approval_reference` or future `approval_state_at_event`

Guidance:

- history events should capture event-time state;
- `result_state` is event outcome, not always current task status;
- status changes currently append history events;
- non-status patches currently update `updated_at` without adding history.

### Approval Record (Future)

Purpose: model explicit approval requests if/when operator approval becomes a
first-class artifact.

Not required for local persistence MVP unless approval flows need independent
identity.

Possible fields later:

- `approval_id`
- `task_id`
- `requested_by`
- `approved_by`
- `approval_state`
- `requested_at`
- `resolved_at`
- `reason`

### Drive Context Record (Future)

Purpose: represent a Drive-bound object or context separately from the task if
live Google execution needs richer metadata.

Not required before controlled live execution is designed.

Possible fields later:

- `drive_context_id`
- `drive_object_id`
- `drive_object_title`
- `mime_type`
- `web_view_link`
- `parent_folder_id`
- `safe_for_mutation`

## Repository / Service Boundary

Before implementing persistence, introduce or define a repository boundary so
routes and services do not depend directly on mock globals.

Recommended shape:

- `TaskRepository` protocol/interface for task CRUD and history access;
- `MockTaskRepository` backed by current in-memory data;
- later `SQLiteTaskRepository` backed by durable storage;
- service functions depend on repository interface, not module globals.

Do not combine repository extraction with database implementation unless the
patch is still small and fully tested.

The detailed SQLite schema and migration planning artifact is
`docs/SQLITE_PERSISTENCE_SCHEMA_PLAN.md`.

## Migration Strategy

Suggested sequence:

1. Add repository boundary while keeping mock backend behavior unchanged.
2. Add tests proving current API behavior remains stable through the repository.
3. Add SQLite schema/migration plan in docs or migrations folder.
4. Add SQLite repository behind an explicit configuration flag.
5. Keep mock runtime as default until local persistence is validated.
6. Add import/export or seed bootstrap for local development.
7. Switch local default only after tests and runbook are updated.

## Rollback Strategy

Persistence implementation must be reversible:

- keep mock runtime available while SQLite is introduced;
- do not delete mock fixtures during first persistence PRs;
- keep schema migrations additive in early steps;
- document how to remove or reset the local SQLite database;
- do not mix persistence migration with live Google execution.

## Validation Expectations

Persistence-related PRs should use offline-safe validation only unless a later
phase explicitly authorizes live checks.

Expected commands:

```bash
make test-backend
make test-all
make check
git diff --check
```

Additional checks once SQLite exists:

```bash
# Example only; exact command should be introduced with the implementation.
python -m operator_backend.scripts.init_db --check
```

## Safety Boundaries

Persistence work must not:

- read, print, or snapshot local Google credentials;
- touch `token.json`, `client_secret.json`, `.env`, or credential folders;
- run live Google write commands;
- widen mutation capability;
- promote degraded document access commands;
- add frontend code in the same PR;
- change `AGENTS.md`, `.gitignore`, or secret handling without explicit approval.

## Recommended Phase 2 PR Sequence

1. Docs-only: add this persistence readiness plan.
2. Audit-only or test-only: identify repository boundary points and required
   behavior-preserving tests.
3. Production: introduce a repository interface while preserving mock runtime.
4. Test-only: add repository-level tests for mock behavior.
5. Docs-only: define SQLite schema and migration policy.
6. Production: add SQLite repository behind explicit opt-in config.
7. Docs/test: update runbook and validation for local persistence.

## Current Decision

The next implementation step should not be database code. The next safe step is
a small repository-boundary audit or implementation plan that identifies exactly
where `mock_store` should be isolated behind an interface while preserving the
current mock API contract.
