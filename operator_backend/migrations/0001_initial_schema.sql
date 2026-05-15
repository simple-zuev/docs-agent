-- Operator backend local SQLite schema scaffold
-- Status: Phase 2 scaffold only
--
-- This file documents the initial SQLite schema planned for local operator
-- backend persistence. It is not executed by the application yet.
--
-- Safety boundaries:
-- - Do not store credentials or private Google data in these tables.
-- - Do not run this migration automatically during API startup until explicitly
--   approved and tested.
-- - Mock runtime remains the default backend until a later opt-in persistence
--   implementation is accepted.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    output_state TEXT NOT NULL,
    approval_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    authority_binding_id TEXT NOT NULL,
    drive_context_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    authority_source TEXT NOT NULL DEFAULT '',
    authority_topic TEXT NOT NULL DEFAULT '',
    relevant_section TEXT NOT NULL DEFAULT '',
    operator_hint TEXT NOT NULL DEFAULT '',
    drive_object_id TEXT NOT NULL DEFAULT '',
    drive_object_title TEXT NOT NULL DEFAULT '',
    object_role TEXT NOT NULL DEFAULT '',
    placement_state TEXT NOT NULL DEFAULT '',
    safe_for_mutation INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tasks_status
    ON tasks (status);

CREATE INDEX IF NOT EXISTS idx_tasks_updated_at
    ON tasks (updated_at);

CREATE INDEX IF NOT EXISTS idx_tasks_task_type
    ON tasks (task_type);

CREATE INDEX IF NOT EXISTS idx_tasks_authority_binding_id
    ON tasks (authority_binding_id);

CREATE INDEX IF NOT EXISTS idx_tasks_drive_context_id
    ON tasks (drive_context_id);

CREATE TABLE IF NOT EXISTS task_history_events (
    event_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    summary TEXT NOT NULL,
    authority_source TEXT NOT NULL DEFAULT '',
    authority_reference TEXT NOT NULL DEFAULT '',
    drive_context_reference TEXT NOT NULL DEFAULT '',
    approval_reference TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL,
    result_state TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_task_history_events_task_id_timestamp
    ON task_history_events (task_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_task_history_events_event_type
    ON task_history_events (event_type);

CREATE INDEX IF NOT EXISTS idx_task_history_events_timestamp
    ON task_history_events (timestamp);
