# INSTRUCTION PANEL CONTRACT

## 1. Purpose

This document defines the minimum Instruction Panel contract for the future `docs-agent` operator application.

The Instruction Panel is the UI component that shows which source in `Cass` governs the current task/workflow.

It is intended to reduce policy drift and prevent the application from becoming a hidden second rule repository.

## 2. Panel role

The Instruction Panel should:

- identify the authoritative source for the current task
- identify the topic governed by that source
- explain why the source applies
- expose freshness and traceability
- help the operator open the real source in Google Drive

The panel should not:

- restate full governance documents as local app policy
- become a full embedded replacement for `Cass`
- hide the distinction between authority and execution

## 3. Minimum fields

The minimum Instruction Panel should display:

- `authoritative source`
- `authority topic`
- `relevant section`
- `last modified`
- `operator hint`
- `open in Drive`

## 4. Optional fields

Recommended optional fields:

- `supporting source`
- `registry reference`
- `approval required`
- `execution constraint`
- `source folder`
- `binding role`

## 5. Example view model

Recommended view model:

- `task_id`
- `task_type`
- `authority_document_title`
- `authority_document_id`
- `authority_topic`
- `relevant_section`
- `last_modified_time`
- `operator_hint`
- `open_url`
- `approval_required`
- `supporting_sources[]`

## 6. Task usage examples

### Example A — prepare_doc_body
Show:
- source: `00_AI_OPERATING_AND_DOCUMENT_WORKFLOW_STANDARD_АСТЦВ`
- topic: document workflow / output discipline
- section: relevant task/output section
- note: app prepares body only; project workflow authority remains in `Cass`

### Example B — prepare_diagram_package
Show:
- source: `00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ`
- topic: diagram source/export/layout rules
- section: source-of-truth / export expectations
- note: app packages source and exports; project diagram policy remains in `Cass`

### Example C — startup_check
Show:
- source: `00_AGENT_RUNTIME_CHARTER_АСТЦВ`
- supporting source: `00_ACTIVE_RUNTIME_PROFILE_АСТЦВ`
- topic: operating mode / bounded runtime
- note: app runtime behavior follows the current bounded profile

## 7. UX rule

The Instruction Panel should be:

- visible by default for governed workflows
- concise
- reference-oriented
- easy to open in the real source

It should not dominate the task workspace with long duplicated text.

## 8. Copy style rule

Preferred wording style:

- "Authoritative source"
- "Why this applies"
- "Open source instruction"
- "Project governance remains in `Cass`"

Avoid wording such as:

- "This app policy says..."
- "This local document overrides..."
- "This panel is the canonical rule source..."

## 9. Final interpretation

The Instruction Panel is not a policy repository.

It is a live binding surface between:
- project authority
- current task execution
- operator decision support
