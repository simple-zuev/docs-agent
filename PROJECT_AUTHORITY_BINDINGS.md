# PROJECT AUTHORITY BINDINGS

## 1. Purpose

This document defines the authority model between:

- project governance/instruction documents in Google Drive `Cass`
- application/repository execution documents in `docs-agent`

Its purpose is to prevent policy duplication and governance drift.

Core rule:

- `Cass` remains the authoritative governance/instruction layer for project work.
- `docs-agent` remains the execution/orchestration/operator layer for bounded use of the agent and tools.
- Repository docs in `docs-agent` must not silently replace or fork project authority already established in `Cass`.

## 2. Primary authority principle

Use this interpretation by default:

- `Cass` = project authority / source-of-truth for project instructions, workflow standards, document governance, diagram governance, terminology, naming, lifecycle, and release discipline
- `docs-agent` = application execution layer for operator-supervised task handling, retrieval, bounded preparation, approvals, and auditability

This means:

- if a rule already exists in `Cass`, the application should reference or bind to it rather than duplicate it as a second canonical rule source
- application docs may describe app behavior, runtime contour, UI/operator behavior, and bounded execution semantics
- application docs must avoid presenting duplicated governance text as an independent project-level standard

## 3. Binding table

| Task / concern | Cass authority source | Authority role | What app may keep locally | What app must not duplicate |
|---|---|---|---|---|
| Runtime startup hierarchy | `00_AGENT_RUNTIME_CHARTER_АСТЦВ` | project runtime governance | app startup behavior, supported command contour, app launch guardrails | project-wide runtime authority hierarchy as an independent parallel standard |
| Active operating profile | `00_ACTIVE_RUNTIME_PROFILE_АСТЦВ` | active bounded operating authority | bounded baseline interpretation for the app, current supported app contour | separate conflicting startup/operating policy for the project |
| AI/document workflow | `00_AI_OPERATING_AND_DOCUMENT_WORKFLOW_STANDARD_АСТЦВ` | project workflow authority | app-side task execution behavior, operator flow, execution hints | full project document workflow standard as a second canonical copy |
| Diagram/layout governance | `00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ` | project diagram governance | app-side diagram handling behavior, preview/export/publish flow | parallel canonical diagram policy or layout standard |
| Terminology / glossary | `00_TERMINOLOGY_AND_LANGUAGE_STANDARD_АСТЦВ`, `00_TERMINOLOGY_AND_GLOSSARY_ENFORCEMENT_STANDARD_АСТЦВ` | naming/terminology authority | validations, hints, references | local competing terminology standard |
| File naming / versioning | `00_FILE_NAMING_AND_VERSIONING_STANDARD_АСТЦВ` | file governance authority | checks, warnings, UI hints | app-local replacement naming policy |
| Lifecycle / archive / registry discipline | `MASTER_INDEX`, `Change Log`, lifecycle-related governance docs in `Cass` | project state authority | app task log, execution audit log, local task state | replacement project lifecycle/source-of-truth registry |
| Diagram source/export relation | `00_DIAGRAM_LAYOUT_STANDARD_АСТЦВ` and related workflow docs | source/export authority | package model, preview/export state, source linkage in app | separate canonical rule set for source-of-truth and export semantics |
| Slides publication interpretation | diagram/workflow governance in `Cass` | publication interpretation authority | app publication flow, target selection, approval gating | declaring Slides as canonical project editing source by app policy |

## 4. Application-local documents and their proper role

The following repository artifacts are application-local execution overlays:

- `AGENT_CURRENT_CHECKPOINT.md`
- `AGENT_RELEASE_CHECKPOINT.md`
- `RELEASE_SUMMARY_BOUNDED_2026-05-13.md`
- `DIAGRAM_FORMAT_SUPPORT.md`
- `DIAGRAM_WORKFLOW_CONTOUR.md`
- `README.md`
- operator-facing docs inside `docs/`

These should be interpreted as:

- app/runtime/execution documentation
- bounded contour explanations
- operator guidance for using the app/CLI
- release interpretation for the application itself

These should **not** be interpreted as replacing `Cass` project governance.

## 5. Required documentation rule for docs-agent

When a repository document in `docs-agent` describes:

- runtime authority
- document workflow
- diagram workflow
- diagram source/export semantics
- publication/presentation semantics
- lifecycle/mutation discipline

it should do so in one of these two forms only:

### Allowed form A — app execution interpretation
The document explains how the application behaves.

### Allowed form B — authority-aware binding
The document explicitly references that project authority remains in `Cass`.

The following form should be avoided:

### Disallowed form
A repo document restates existing `Cass` governance as if the repo document itself were the primary project-level source-of-truth.

## 6. Thin binding rule

For topics already governed in `Cass`, app docs should prefer thin binding language such as:

- "This app follows the project authority defined in `Cass`."
- "This document describes application-side execution behavior only."
- "For project governance, refer to the authoritative document in `Cass`."
- "This app does not replace project policy on this topic."

## 7. Audit interpretation

Current audit conclusion:

- `Cass` already contains an authority layer for runtime, workflow, and diagram governance
- `docs-agent` contains valuable execution-layer docs, but some diagram/workflow language overlaps with `Cass`
- the correct next state is not more policy duplication
- the correct next state is authority-aware execution documentation

## 8. Practical implementation rule for the app

The application should eventually expose, for each task/workflow:

- authoritative source document
- authority topic
- last modified time
- relevant section or bound interpretation
- local execution behavior
- approval requirement if applicable

This keeps the app aligned with `Cass` while preserving execution usability.

## 9. Final rule

Use this rule by default:

- `Cass` governs the project
- `docs-agent` executes within that governance
- app docs may explain behavior
- app docs must not fork authority
