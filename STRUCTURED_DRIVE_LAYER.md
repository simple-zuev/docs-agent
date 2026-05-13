# STRUCTURED DRIVE LAYER

## 1. Purpose

This document defines the minimum structured Google Drive layer for the future `docs-agent` application.

The app should not treat Drive as a flat list of files.
It should treat Drive objects as typed context with role and relation.

## 2. Core principle

Every relevant Drive object should be interpreted through structured context such as:
- source
- export
- draft
- presentation target
- registry reference
- folder context
- authority source

## 3. Minimum object kinds

Recommended object kinds:

- `authority_document`
- `registry`
- `source_document`
- `source_diagram`
- `export_artifact`
- `draft_artifact`
- `presentation_target`
- `folder`
- `unknown`

## 4. Minimum Drive context fields

- `drive_context_id`
- `primary_object_id`
- `primary_object_kind`
- `parent_folder_id`
- `related_source_ids[]`
- `related_export_ids[]`
- `related_registry_ids[]`
- `placement_status`
- `safe_for_mutation`
- `notes`

## 5. Minimum context questions

The app should be able to answer:

- what object is this?
- what role does it play?
- is it source or export?
- where is it placed?
- is it correctly linked to source/export package?
- is it safe for downstream write-adjacent handling?
- does it require approval before next step?

## 6. Practical object interpretation

Examples:

### Source diagram
- canonical editable artifact
- expected to have downstream export artifacts

### Export artifact
- derived from source
- not primary source-of-truth by default

### Authority document
- governance source from `Cass`
- not an app-local editable policy object

### Presentation target
- publication destination such as Google Slides
- not canonical source-of-truth

## 7. Final interpretation

Structured Drive layer is the object/relationship model that makes bounded execution safe and understandable.
