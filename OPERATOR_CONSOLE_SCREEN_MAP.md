# OPERATOR CONSOLE SCREEN MAP

## 1. Purpose

This document defines the minimum screen map for the future `docs-agent` operator application.

It translates the existing shell/task/authority/approval specs into concrete operator-facing screens.

## 2. Core principle

The UI should be task-centered, authority-aware, and bounded by default.

## 3. Minimum screens

### Screen 1 — Task Intake / Queue
Purpose:
- create task
- select task
- inspect current queue / recent work

Minimum blocks:
- task creation entry
- recent tasks list
- task filters
- quick authority hint

### Screen 2 — Task Details / Workspace
Purpose:
- main execution screen for a selected task

Minimum blocks:
- task header
- task state
- current output state
- action area
- warnings / blocked state

### Screen 3 — Instruction Panel
Purpose:
- show authoritative source and why it applies

Minimum blocks:
- authority source
- topic
- relevant section
- last modified
- open in Drive
- supporting sources

### Screen 4 — Approval Panel
Purpose:
- show approval requirement and decision path

Minimum blocks:
- approval status
- required / not required
- reason
- decision history
- approve / reject action placeholders

### Screen 5 — Artifact / Package Review
Purpose:
- inspect source/export/publication package

Minimum blocks:
- source artifacts
- preview artifacts
- export artifacts
- publication targets
- package completeness / warnings

### Screen 6 — Task History / Audit
Purpose:
- show ordered execution history for a task

Minimum blocks:
- event stream
- event timestamps
- event type
- authority reference
- approval reference
- result state

## 4. Navigation model

Recommended primary navigation:
- Tasks
- Workspace
- Authority
- Approval
- Package Review
- History

## 5. Final interpretation

The operator console should behave as a structured execution workspace, not a generic chat UI.
