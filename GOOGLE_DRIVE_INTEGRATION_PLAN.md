# GOOGLE DRIVE INTEGRATION PLAN

## 1. Purpose

This document defines the minimum Google Drive integration plan for the first `docs-agent` operator application.

## 2. Core rule

Drive integration should be structured, authority-aware, and bounded.

## 3. Minimum integration responsibilities

- open/load authoritative source references
- classify file/document/artifact roles
- load source/export/publication context
- support bounded task flows
- expose placement and readiness context

## 4. Required early capabilities

### A. Authority reference loading
Needed for:
- Instruction Panel
- authority freshness
- open in Drive links

### B. Document/object lookup
Needed for:
- find/open/read flows
- task context binding

### C. Structured artifact inspection
Needed for:
- source vs export interpretation
- package review
- publication readiness

### D. Publication target identification
Needed for:
- Slides publication flow
- target selection and auditability

## 5. Integration rule

Drive integration must not flatten all objects into one undifferentiated search result model.

It should preserve object role:
- authority document
- source
- export
- publication target
- registry reference

## 6. Final interpretation

Drive integration is a structured application layer, not just raw file access.
