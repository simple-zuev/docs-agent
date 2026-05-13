# APP SHELL SPEC

## 1. Purpose

This document defines the minimum operator console / app shell for the future `docs-agent` application.

The app shell is the top-level operator workspace for authority-aware bounded execution.

It should unify:

- task intake
- current task context
- authority visibility
- action controls
- approvals
- task history
- bounded output flow

## 2. Shell goals

The app shell should make it possible to:

- start a task in a controlled way
- see what authority source governs the task
- inspect task state and current artifact context
- execute bounded actions
- request or record approvals when needed
- review outcomes without losing traceability

## 3. Minimum layout zones

Recommended minimum app shell zones:

### A. Task Intake
Where the operator starts or selects a task.

### B. Task Workspace
The main execution area for the current task.

### C. Instruction Panel
The authority-aware panel defined in `INSTRUCTION_PANEL_CONTRACT.md`.

### D. Approval / Risk Panel
Shows approval requirements, blocked actions, and mutation discipline.

### E. Artifact / Drive Context Panel
Shows current file/folder/artifact state.

### F. Task History / Audit Panel
Shows previous actions and current task event history.

## 4. Minimum shell view model

Minimum app shell state:

- `session_id`
- `active_task_id`
- `active_task_type`
- `active_task_state`
- `authority_reference`
- `drive_context`
- `approval_state`
- `history_items[]`
- `current_output_state`
- `warnings[]`

## 5. Operator design rule

The shell should be:

- authority-aware
- bounded by default
- task-centered
- stateful
- review-friendly

The shell should not be:

- an unstructured chat-only surface
- a hidden autonomous mutation console
- a replacement governance repository

## 6. Minimum shell actions

The shell should support at least:

- `create_task`
- `open_task`
- `view_authority`
- `inspect_drive_context`
- `request_preview`
- `request_export_package`
- `request_approval`
- `record_decision`
- `view_task_history`

## 7. Final interpretation

The app shell is the controlled operator surface that binds:
- task execution
- authority awareness
- bounded actions
- review/auditability
