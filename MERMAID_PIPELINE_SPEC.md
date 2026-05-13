# MERMAID PIPELINE SPEC

## 1. Purpose

This document defines the minimum Mermaid pipeline for the future `docs-agent` application.

It describes how Mermaid source should move through:
- intake
- validation
- preview
- export packaging
- publication preparation

This is an application execution spec, not a replacement for project diagram governance in `Cass`.

## 2. Core rule

Mermaid should be treated as a canonical editable diagram source.

Exports derived from Mermaid should not replace Mermaid source-of-truth by default.

## 3. Minimum pipeline stages

1. source intake
2. source validation
3. preview generation
4. export generation
5. package assembly
6. optional publication handoff

## 4. Source intake

Accepted source:
- Mermaid text

Minimum metadata:
- `task_id`
- `source_id`
- `diagram_title`
- `diagram_scope`
- `authority_binding_id`
- `source_hash`

## 5. Validation requirements

Before preview/export:
- syntax validity
- semantic correspondence to requested task
- naming consistency
- layout direction sanity
- authority-aware scope check when relevant

## 6. Preview requirements

Preview should:
- render from the current Mermaid source
- be traceable to current source hash
- be treated as preview, not final publication artifact

## 7. Export requirements

Supported downstream outputs:
- SVG
- PNG
- PDF

Rule:
- export only from validated source state
- keep source hash linked to exports
- preserve relation between source and derived outputs

## 8. Package requirements

Recommended Mermaid package:
- Mermaid source
- preview artifact
- chosen exports
- task metadata
- authority reference

## 9. Publication handoff

If publication is needed:
- publish exported artifact, not raw Mermaid source, into downstream presentation flow by default
- retain Mermaid as canonical editable artifact

## 10. Final interpretation

Mermaid pipeline is a source-first bounded workflow.
