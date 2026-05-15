# Backend Repository Selection Plan

Status: Phase 2 planning artifact

This document defines how `operator_backend` should select between the current mock repository and the future SQLite repository.

It does not implement repository selection, change runtime defaults, create a database, run migrations, or enable SQLite in the backend runtime.

## Current State

The backend currently has:

- `MockTaskRepository` as the default runtime repository through `task_service`.
- `SQLiteTaskRepository` as an opt-in implementation that can be instantiated directly in tests or future tooling.
- migration validation tooling for temporary or in-memory SQLite databases.
- a configured future database path helper.

The backend default must remain mock until explicit opt-in repository selection is implemented and validated.

## Repository Kinds

The repository selection contract should support two values:

- `mock`
- `sqlite`

Recommended environment variable:

- `DOCS_AGENT_OPERATOR_REPOSITORY=mock`
- `DOCS_AGENT_OPERATOR_REPOSITORY=sqlite`

Default:

- `DOCS_AGENT_OPERATOR_REPOSITORY=mock`

Invalid values should fail with a clear configuration error. They must not silently fall back to `mock` or `sqlite`.

## SQLite Path

SQLite repository selection should use the existing database path helper:

- `DOCS_AGENT_OPERATOR_DB_PATH=/absolute/path/to/operator_backend.sqlite3`

If the variable is not set, the future default path remains:

- `var/operator_backend/operator_backend.sqlite3`

The database file is a local runtime artifact and must not be committed.

## Runtime Selection Rules

The first repository-selection implementation should follow these rules:

1. `mock` remains the default.
2. `sqlite` is explicit opt-in only.
3. Repository selection must not run migrations automatically.
4. Repository selection must not create a database file silently during normal backend startup.
5. If `sqlite` is selected and the database is missing or not migrated, the backend should fail clearly when the repository is used.
6. Routes should not know which repository implementation is selected.
7. Services should continue to use the repository boundary.
8. Public API response shapes must not change.

## Recommended Provider Shape

A future implementation may add a small provider with these responsibilities:

- resolve repository kind from environment;
- return `MockTaskRepository` by default;
- return `MockTaskRepository` for explicit `mock`;
- return `SQLiteTaskRepository(resolve_operator_db_path(...))` for explicit `sqlite`;
- raise a clear error for unknown values.

The provider may live in one of these locations:

- `operator_backend/app/repositories/provider.py`
- `operator_backend/app/config.py` for kind resolution plus repository provider in the repositories package.

The provider should remain small and testable.

## Test Requirements

The repository selection implementation should include tests for:

- default repository kind is `mock`;
- explicit `mock` returns `MockTaskRepository`;
- explicit `sqlite` returns `SQLiteTaskRepository`;
- invalid repository kind raises a clear error;
- SQLite path override is passed into `SQLiteTaskRepository`;
- default mock backend API tests still pass;
- no migration is run by repository selection;
- no database file is created by selecting or resolving the provider alone, unless SQLite itself is explicitly used in a test.

## Non-Goals For The First Selection PR

Do not include:

- SQLite migrations execution at startup;
- automatic database creation;
- SQLite as default runtime backend;
- frontend/operator_app changes;
- Google Drive or Google Docs execution changes;
- API field renames;
- persistence data import/export;
- auth/RBAC/CORS work.

## Safety Boundaries

Repository selection work must not:

- read, print, or store credentials;
- use Google OAuth tokens;
- run live Google commands;
- promote degraded document access commands;
- change mutation gates;
- create runtime data under tracked paths;
- mix frontend and backend changes.

## Recommended Next PR

Title: Add backend repository selection provider

Scope:

- add repository kind config helper;
- add repository provider;
- keep default as mock;
- add provider tests;
- do not run migrations;
- do not switch default to SQLite.

Validation:

- make test-backend
- make test-all
- make check
- git diff --check

## Decision

The next implementation should be repository selection provider only.

It should not make SQLite the default and should not perform automatic migration or database initialization.
