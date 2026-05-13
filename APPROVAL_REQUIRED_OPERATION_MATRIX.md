# APPROVAL REQUIRED OPERATION MATRIX

## 1. Purpose

This document defines which operations require explicit approval in the first live `docs-agent` integration contour.

## 2. Core rule

If an action can:
- change a target artifact
- change publication state
- create ambiguity around source-of-truth
- affect canonical project structure
- affect naming/versioning discipline

then approval should be required unless explicitly exempted.

## 3. Approval-exempt operations

Approval is not required for:
- find
- open
- bounded read
- metadata inspection
- artifact-state inspection
- preview/package inspection
- doc-body-only preparation without target mutation
- opening authority references

## 4. Approval-required operations

Approval is required for:
- creating draft/review artifacts in Drive
- writing prepared body into a selected draft target
- uploading publication/export artifact into shared project location
- attaching artifact into publication path
- publishing or updating Slides-target outputs
- changing naming/version-sensitive artifacts
- any operation where source/target relation is unclear
- any operation where authority binding is unclear

## 5. Blocked instead of approval

The following should not be merely approval-gated in first rollout.
They should remain blocked:

- delete
- bulk rename
- bulk move
- recursive folder changes
- mutation of authority documents
- mutation of registries as default app flow

## 6. Final interpretation

In first live rollout, approval is for bounded, understandable, reviewable mutation only.

Approval is not a substitute for missing safety boundaries.
