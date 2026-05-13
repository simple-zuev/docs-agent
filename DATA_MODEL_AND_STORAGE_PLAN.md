# DATA MODEL AND STORAGE PLAN

## 1. Purpose

This document defines the minimum data/storage plan for the first `docs-agent` operator application.

## 2. Core distinction

Keep separate:
- project governance truth in `Cass`
- application execution state in app storage

## 3. Minimum persistent entities

- Task
- AuthorityDocumentReference
- AuthorityBinding
- DriveContext
- ApprovalRecord
- TaskHistoryEvent
- ExportPackage
- PublicationRecord

## 4. Minimum storage responsibilities

Store:
- task state
- authority bindings
- drive context snapshots
- approval records
- event history
- package/publication state

Do not store as local canonical truth:
- rewritten full governance corpus from `Cass`

## 5. Recommended early storage strategy

For first usable version:
- simple app database
- structured task/event tables
- explicit entity references
- minimal caching of authority metadata only

## 6. Final interpretation

Storage should support traceable execution, not local governance duplication.
