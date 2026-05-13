# PREVIEW COMPARE SPEC

## 1. Purpose

This document defines the minimum preview/compare behavior for the future `docs-agent` application.

## 2. Core rule

Preview and compare exist to support operator review.
They do not replace source validation or authority review.

## 3. Minimum preview modes

- source preview
- export preview
- publication-ready preview

## 4. Minimum compare modes

- source vs preview
- source vs export
- export vs publication target candidate

## 5. Minimum compare fields

- `compare_id`
- `task_id`
- `left_artifact_id`
- `right_artifact_id`
- `compare_type`
- `summary`
- `detected_issues[]`
- `review_status`

## 6. Review goals

Compare should help answer:
- does export still reflect source intent?
- is publish candidate the correct artifact?
- is the operator reviewing the right version?
- are obvious layout/content drifts visible?

## 7. Final interpretation

Preview/compare is a bounded review aid for operator confidence and package correctness.
