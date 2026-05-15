# Operator Backend Migrations

Status: Phase 2 scaffold only

This folder contains reviewed SQLite migration files for future local operator
backend persistence work.

The presence of this folder does not enable SQLite persistence, create a
database, or change backend runtime behavior.

## Rules

- Migrations must be explicit and reviewable.
- Migrations must not run automatically during normal API startup until that
  behavior is separately approved and tested.
- Early migrations should be additive.
- Destructive migrations require a rollback and data-loss note.
- SQLite remains opt-in until a later implementation PR validates it.
- Mock runtime remains the default backend until explicitly changed.
- Migration files must not contain production data, Google Drive exports,
  credentials, tokens, or private user data.

## Current Files

- `0001_initial_schema.sql`: planned local SQLite schema for tasks and task
  history events.

## Validation Expectations

Future migration implementation PRs should validate migrations with a temporary
local database, not the operator's real runtime database.

Expected future checks:

```bash
make test-backend
make test-all
make check
git diff --check
```

## Safety Boundaries

Migration work must not:

- create or commit SQLite database files;
- read or write Google OAuth credentials;
- run live Google Drive or Google Docs commands;
- add frontend/operator_app work;
- promote degraded document-access commands;
- change public backend response shapes in the same PR.
