# IMPLEMENTATION PLAN

## 1. Purpose

This document defines the implementation plan for the first usable `docs-agent` operator application.

It translates the existing governance/model/flow/UI specs into a practical build sequence.

## 2. Build principle

Build in thin, reviewable vertical slices.

Do not attempt full feature completeness before the first usable shell exists.

## 3. Phase order

### Phase 1 — app shell foundation
- app shell layout
- task list / queue
- task details workspace
- instruction panel placeholder
- approval panel placeholder
- history panel placeholder

### Phase 2 — authority-aware task runtime
- task entity persistence
- authority binding loading
- instruction panel live data
- task state transitions
- basic audit history

### Phase 3 — structured Drive runtime
- Drive object classification
- file/document/source/export role detection
- drive context loading into task workspace
- safe-for-mutation / placement state visibility

### Phase 4 — bounded document/diagram workflows
- doc-body-only task execution
- artifact-state task execution
- Mermaid source-first flow
- `.drawio` source-first flow
- export package creation flow

### Phase 5 — publication / review layer
- preview/compare
- Slides publication flow
- approval gating for publication-sensitive steps
- package review screen

## 4. Recommended delivery strategy

Deliver first usable version after:
- Phase 1
- minimal subset of Phase 2
- minimal subset of Phase 3

This first version should already allow:
- task creation
- task inspection
- authority visibility
- basic Drive context visibility
- bounded operator navigation

## 5. Non-goals for first implementation wave

Do not include initially:
- full autonomous all-file-operations mode
- broad write automation
- multi-user collaboration
- deep automation
- full diff engine
- full Slides authoring runtime

## 6. Final interpretation

The implementation plan should preserve bounded launch discipline while enabling a real first operator application.
