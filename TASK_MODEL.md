# TASK MODEL

## 1. Purpose

This document defines the minimum task model for the future `docs-agent` application.

The task model is needed so that the app works as a structured operator system rather than a loose sequence of commands.

## 2. Core principle

Every meaningful operator action should happen inside a task.

A task should have:

- type
- state
- authority binding
- drive context
- output state
- approval state
- history

## 3. Minimum task fields

- `task_id`
- `task_type`
- `title`
- `status`
- `created_at`
- `updated_at`
- `created_by`
- `authority_binding_id`
- `drive_context_id`
- `approval_state`
- `output_state`
- `notes`

## 4. Minimum task types

The app should support at least:

- `startup_check`
- `find_document`
- `open_document`
- `read_document`
- `inspect_artifact`
- `prepare_doc_body`
- `prepare_diagram_package`
- `review_export_package`
- `publish_to_slides`
- `lifecycle_proposal`

## 5. Minimum task states

Recommended states:

- `created`
- `authority_bound`
- `context_loaded`
- `in_progress`
- `awaiting_approval`
- `awaiting_operator_review`
- `completed`
- `blocked`
- `cancelled`

## 6. Output state examples

Recommended output state values:

- `none`
- `preview_ready`
- `body_prepared`
- `export_package_ready`
- `publication_ready`
- `published`
- `review_note_required`

## 7. Task rule

A task must not lose:

- authority traceability
- source context
- approval state
- event history

## 8. Final interpretation

The task is the main execution object of the application.
