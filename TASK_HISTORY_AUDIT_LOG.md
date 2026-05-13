# TASK HISTORY AUDIT LOG

## 1. Purpose

This document defines the minimum task history / audit log model for the future `docs-agent` application.

The app needs an execution log even though project truth remains in `Cass` registries.

## 2. Core distinction

Use this distinction:

- project governance / lifecycle truth remains in `Cass`
- application execution history remains in the app task history / audit log

The app audit log must not pretend to replace project registries.

## 3. Minimum event fields

- `event_id`
- `task_id`
- `timestamp`
- `event_type`
- `actor`
- `summary`
- `authority_reference`
- `drive_context_reference`
- `approval_reference`
- `result_state`

## 4. Minimum event types

Recommended event types:

- `task_created`
- `authority_bound`
- `drive_context_loaded`
- `preview_requested`
- `preview_ready`
- `export_package_ready`
- `approval_requested`
- `approval_granted`
- `approval_rejected`
- `publication_requested`
- `task_completed`
- `task_blocked`

## 5. Minimum UI behavior

The app should let the operator:

- view ordered task history
- see key decisions and approvals
- understand why the current state was reached
- distinguish task history from project registry truth

## 6. Final interpretation

Task history is the execution memory of the app.
It supports traceability without replacing project governance records.
