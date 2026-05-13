# ARTIFACT PACKAGE REVIEW SCREEN

## 1. Purpose

This document defines the minimum Artifact / Package Review screen for the future `docs-agent` operator application.

## 2. Screen role

This screen exists to review source/export/publication readiness before downstream use.

## 3. Minimum sections

### A. Source Section
Show:
- source artifacts
- source type
- source hash / identity
- canonical source marker

### B. Preview Section
Show:
- available previews
- current preview candidate
- preview freshness relative to source

### C. Export Section
Show:
- SVG / PNG / PDF artifacts
- traceability to source
- export completeness

### D. Publication Section
Show:
- selected publication target
- Slides target if present
- chosen publish artifact

### E. Review Summary
Show:
- package complete / incomplete
- blocking issues
- missing artifacts
- source/export mismatch warnings

## 4. Minimum review questions

The operator should be able to answer:
- do I have the source?
- do I have the correct exports?
- is the package complete for the target use?
- is Slides using the right artifact?
- is anything missing or stale?

## 5. Final interpretation

Package Review is the bounded quality gate before publication or handoff.
