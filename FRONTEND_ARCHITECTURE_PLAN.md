# FRONTEND ARCHITECTURE PLAN

## 1. Purpose

This document defines the minimum frontend architecture plan for the first `docs-agent` operator application UI.

## 2. Core rule

Frontend should be task-centered and authority-aware.

Do not design it as a generic chat wrapper.

## 3. Recommended frontend modules

- `app_shell`
- `task_queue`
- `task_workspace`
- `instruction_panel`
- `approval_panel`
- `artifact_package_review`
- `task_history_panel`

## 4. Minimum shared frontend state

- current session
- selected task
- task list
- task detail state
- authority reference state
- drive context state
- approval state
- package review state
- history state

## 5. Recommended first UI delivery

Initial frontend version should implement:
- left task navigation
- center task workspace
- right authority/approval/context panels
- simple top status bar

## 6. UI rule

Prefer:
- clear panels
- explicit blocked states
- explicit next actions
- low ambiguity

Avoid:
- overloaded dashboard density
- hidden risk states
- burying authority info

## 7. Final interpretation

Frontend should make bounded execution obvious and safe.
