# BACKEND ORCHESTRATION PLAN

## 1. Purpose

This document defines the minimum backend orchestration plan for the first `docs-agent` operator application.

## 2. Core principle

Backend should orchestrate bounded tasks rather than behave as a broad autonomous agent runtime.

## 3. Minimum backend responsibilities

- create/load/update tasks
- resolve authority bindings
- load structured Drive context
- execute bounded task handlers
- persist task history
- expose approval state
- return package/publication readiness state

## 4. Recommended bounded handlers

- `startup_check_handler`
- `find_document_handler`
- `open_document_handler`
- `read_document_handler`
- `inspect_artifact_handler`
- `prepare_doc_body_handler`
- `prepare_diagram_package_handler`
- `review_export_package_handler`
- `publish_to_slides_handler`

## 5. Orchestration rule

Handlers should:
- operate inside task scope
- preserve authority reference
- preserve auditability
- expose bounded next actions
- fail explicitly

## 6. Non-goal

Do not implement backend as:
- open-ended autonomous planner
- silent governance inference engine
- broad mutation executor

## 7. Final interpretation

Backend is the bounded task orchestration layer behind the operator app.
