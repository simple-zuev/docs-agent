# SLIDES PUBLICATION FLOW

## 1. Purpose

This document defines the minimum Google Slides publication flow for the future `docs-agent` application.

## 2. Core rule

Google Slides is treated as a publication/presentation target, not as canonical source-of-truth for diagram logic/layout by default.

## 3. Minimum publication flow

1. select source-bound task output
2. verify source/export linkage
3. choose publish-ready artifact
4. bind to Slides target
5. perform operator-supervised publication step
6. record publication event in task history

## 4. Minimum publication fields

- `publication_id`
- `task_id`
- `source_id`
- `export_artifact_id`
- `slides_target_id`
- `approval_state`
- `published_at`
- `published_by`
- `status`

## 5. Publication preconditions

Before publication:
- source exists
- export exists
- source/export linkage is valid
- approval state is acceptable if required
- target Slides context is identified

## 6. Publication rule

Publish exported artifact to Slides.
Do not treat Slides content as the primary canonical source after publication.

## 7. Final interpretation

Slides publication is a controlled downstream handoff from source-governed work.
