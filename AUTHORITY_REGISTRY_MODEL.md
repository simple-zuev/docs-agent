# AUTHORITY REGISTRY MODEL

## 1. Purpose

This document defines the minimum authority-aware application model for `docs-agent`.

It exists to ensure that the application:

- does not silently duplicate project governance from `Cass`
- can show which source is authoritative for a given task/workflow
- can bind execution behavior to the correct project-level instruction source
- can remain usable without becoming a parallel policy repository

This is an application-model document, not a replacement for `Cass` governance.

## 2. Core principle

Use this rule by default:

- `Cass` provides project governance authority
- the application provides execution/orchestration behavior
- the authority registry links task/workflow execution to the correct authoritative source

## 3. Minimum entities

### 3.1 AuthorityDocument

Represents an authoritative project document or registry from `Cass`.

Fields:

- `authority_document_id`
- `title`
- `google_drive_file_id`
- `document_kind`
- `authority_scope`
- `status`
- `last_modified_time`
- `source_folder`
- `is_registry`
- `is_primary_authority`

Recommended examples of `document_kind`:

- `runtime_charter`
- `runtime_profile`
- `workflow_standard`
- `diagram_standard`
- `terminology_standard`
- `naming_standard`
- `registry`
- `other`

### 3.2 AuthorityBinding

Represents the binding between an app task/workflow and a governing source.

Fields:

- `binding_id`
- `task_type`
- `authority_document_id`
- `authority_topic`
- `relevant_section`
- `binding_role`
- `execution_note`
- `approval_required`
- `active`

Recommended examples of `binding_role`:

- `primary_authority`
- `supporting_authority`
- `registry_reference`
- `execution_constraint`

### 3.3 InstructionReference

Represents the operator-visible reference used during task execution.

Fields:

- `authority_document_id`
- `title`
- `authority_topic`
- `relevant_section`
- `last_modified_time`
- `google_drive_file_id`
- `open_url`
- `operator_hint`

## 4. Minimum task binding model

The application should be able to bind at least these task classes:

- `startup_check`
- `find_document`
- `open_document`
- `read_document`
- `inspect_artifact`
- `prepare_doc_body`
- `prepare_diagram_package`
- `publish_to_slides`
- `review_export_package`
- `lifecycle_proposal`

## 5. Recommended initial bindings

### Startup and operating mode
- `startup_check`
  - authority: `00_AGENT_RUNTIME_CHARTER_АСТЦВ`
  - supporting authority: `00_ACTIVE_RUNTIME_PROFILE_АСТЦВ`

### Document workflow
- `find_document`
- `open_document`
- `read_document`
- `prepare_doc_body`
  - authority: `00_AI_OPERATING_AND_DOCUMENT_WORKFLOW_STANDARD_АСТЦВ`

### Diagram workflow
- `prepare_diagram_package`
- `review_export_package`
- `publish_to_slides`
  - authority: `00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ`
  - supporting authority: workflow/runtime docs where relevant

### Terminology and naming validation
- `lifecycle_proposal`
- document/diagram-related naming or term-sensitive tasks
  - supporting authority: terminology/naming standards and registries

## 6. UI contract: Instruction Panel

The application should expose an Instruction Panel for each relevant task/workflow.

Minimum fields shown to the operator:

- `authoritative source`
- `authority topic`
- `relevant section`
- `last modified`
- `why this source applies`
- `open in Drive`

Optional but recommended:

- `supporting authority`
- `registry references`
- `execution note`
- `approval requirement`

## 7. Behavior rule for the Instruction Panel

The Instruction Panel must not present itself as a new canonical policy source.

It should behave as:

- a live authority reference
- a task-to-authority binding view
- an execution-context helper

It should not behave as:

- a replacement governance repository
- a hidden fork of `Cass`
- a local rewritten copy of full project rules

## 8. Application behavior enabled by this model

This model makes the following possible without expanding runtime scope:

- show task-specific governing source
- explain why a source is authoritative
- expose current authority freshness via `last_modified_time`
- connect app execution semantics to project governance
- reduce operator drift and incorrect local interpretation

## 9. What this model does not imply

This model does not imply:

- broad autonomous interpretation of all `Cass` docs
- full document ingestion into local policy state
- replacement of `Cass` as governance layer
- automatic section-level legal/policy reasoning across all documents
- runtime expansion or baseline expansion by itself

## 10. Implementation priority

This model should be implemented before:

- broadening operator UI scope too far
- adding deeper automation on top of task flows
- adding richer publication workflows without authority awareness

## 11. Final interpretation

The authority registry is the bridge between:

- project governance in `Cass`
- application execution in `docs-agent`

This bridge should stay thin, explicit, and reference-oriented.
