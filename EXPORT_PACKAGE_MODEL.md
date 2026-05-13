# EXPORT PACKAGE MODEL

## 1. Purpose

This document defines the minimum export package model for the future `docs-agent` application.

It exists to make diagram/document publication outputs structured rather than ad hoc.

## 2. Core rule

An export package should preserve the relationship between:
- source
- preview
- exports
- publication target
- authority/task context

## 3. Minimum package fields

- `package_id`
- `task_id`
- `source_ids[]`
- `preview_ids[]`
- `export_ids[]`
- `publication_target_ids[]`
- `authority_binding_id`
- `package_status`
- `created_at`
- `notes`

## 4. Minimum package types

- `minimal_package`
- `standard_package`
- `review_package`
- `publication_package`

## 5. Recommended package content

### Minimal package
- source
- one preview/export artifact

### Standard package
- source
- SVG
- PNG

### Review package
- source
- SVG or PNG
- PDF

### Publication package
- source
- selected publish-ready artifact
- publication target binding
- traceability metadata

## 6. Package rule

Never treat a package as complete if:
- source is missing
- exports cannot be traced to source
- publication target has no bound artifact
- authority/task context is missing

## 7. Final interpretation

Export package is the structured output bundle for bounded operator workflows.
