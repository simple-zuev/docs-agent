# DRAWIO PIPELINE SPEC

## 1. Purpose

This document defines the minimum `.drawio` pipeline for the future `docs-agent` application.

It describes how `.drawio` source should move through:
- intake
- validation
- preview
- export packaging
- publication preparation

## 2. Core rule

`.drawio` should be treated as a canonical editable diagram source.

Rendered outputs should not replace `.drawio` source-of-truth by default.

## 3. Minimum pipeline stages

1. source intake
2. source validation
3. preview generation
4. export generation
5. package assembly
6. optional publication handoff

## 4. Source intake

Accepted source:
- `.drawio` XML / draw.io editable artifact

Minimum metadata:
- `task_id`
- `source_id`
- `diagram_title`
- `diagram_scope`
- `authority_binding_id`
- `source_hash`

## 5. Validation requirements

Before preview/export:
- file opens as editable source
- structural completeness
- semantic correspondence to requested task
- naming consistency
- layout/readability sanity

## 6. Preview requirements

Preview should:
- derive from current `.drawio` source
- remain linked to current source hash
- be treated as review artifact, not source replacement

## 7. Export requirements

Supported downstream outputs:
- SVG
- PNG
- PDF

## 8. Package requirements

Recommended `.drawio` package:
- `.drawio` source
- preview artifact
- chosen exports
- task metadata
- authority reference

## 9. Publication handoff

If publication is needed:
- publish export artifact to Slides/publication flow
- keep `.drawio` retained as canonical editable source

## 10. Final interpretation

`.drawio` pipeline is a source-first bounded workflow.
