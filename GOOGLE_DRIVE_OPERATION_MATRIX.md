# GOOGLE DRIVE OPERATION MATRIX

## 1. Purpose

This document defines the minimum allowed-operation matrix for the first live Google Drive integration in `docs-agent`.

It exists to prevent the first live runtime from expanding into uncontrolled Drive mutation.

This is an application execution-control document, not a replacement for project governance in `Cass`.

## 2. Core interpretation

First live integration must be:
- bounded
- operator-supervised
- authority-aware
- approval-aware
- rollout-limited

It must not be:
- broad autonomous Drive runtime
- unrestricted mutation layer
- full file management agent by default

## 3. Object roles

Use these minimum roles:

- authority_document
- source_document
- source_diagram
- export_artifact
- publication_target
- draft_review_artifact
- registry_reference
- folder_container

## 4. Allowed operations in first live rollout

### Always allowed
- load authority reference metadata
- open Drive link
- find document/object in approved scope
- read document metadata
- read bounded document content
- inspect artifact placement/state
- prepare doc body without direct mutation
- load source/export/publication context
- load package review context

### Allowed only in bounded review/draft contour
- create draft/review document
- create review/export package artifact
- attach export artifact to task/package state
- place prepared content into explicitly selected draft target

### Not included in first live rollout
- delete file
- delete folder
- recursive move
- recursive rename
- bulk move
- bulk rename
- broad folder restructuring
- mutation of authority documents
- mutation of registries as application default behavior
- silent overwrite of canonical project artifacts

## 5. Operation matrix

| Operation | First live rollout status | Conditions |
|---|---|---|
| Find file/document | Allowed | approved scope only |
| Open link | Allowed | operator-visible |
| Read metadata | Allowed | approved scope only |
| Read bounded content | Allowed | supported document types and bounded routes only |
| Inspect artifact state | Allowed | structured role detection required |
| Prepare document body | Allowed | no direct mutation |
| Create draft/review artifact | Limited allowed | explicit target + task scope |
| Write prepared body into draft target | Limited allowed | explicit approval and target clarity |
| Upload export artifact | Limited allowed | package-bound and review-aware |
| Publish to Slides target | Limited allowed later | only through explicit publication flow |
| Rename canonical artifact | Not allowed by default | separate rollout only |
| Move canonical artifact | Not allowed by default | separate rollout only |
| Delete any artifact | Not allowed | outside first rollout |
| Bulk operations | Not allowed | outside first rollout |

## 6. Final rule

If an operation changes structure, identity, or canonical project state, it should be excluded from first live rollout unless separately approved and explicitly added.
