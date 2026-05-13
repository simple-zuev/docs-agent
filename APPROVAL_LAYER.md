# APPROVAL LAYER

## 1. Purpose

This document defines the minimum approval layer for the future `docs-agent` application.

The approval layer exists to keep bounded execution disciplined and operator-supervised.

## 2. Core rule

No critical mutation-adjacent or publication-sensitive action should rely on implicit approval.

Approval should be explicit whenever:
- authority-sensitive work is involved
- publication/export decisions matter
- lifecycle changes are proposed
- write-adjacent transitions occur

## 3. Minimum approval fields

- `approval_id`
- `task_id`
- `approval_type`
- `requested_at`
- `requested_by`
- `status`
- `decision`
- `decided_at`
- `decided_by`
- `reason`

## 4. Recommended approval types

- `mutation_preparation_approval`
- `publication_approval`
- `lifecycle_change_approval`
- `artifact_replacement_approval`
- `high_risk_context_approval`

## 5. Minimum approval states

- `not_required`
- `required`
- `requested`
- `approved`
- `rejected`
- `expired`

## 6. Approval triggers

Recommended triggers:

- publication to Slides or external presentation target
- lifecycle/archive/replace proposals
- write-adjacent placement decisions
- governed output handoff into controlled downstream flow

## 7. UX rule

The application must show:
- whether approval is required
- why approval is required
- what action is blocked until approval exists

## 8. Final interpretation

Approval is not bureaucracy inside the app.
It is the control layer that keeps bounded execution aligned with governance and operator responsibility.
