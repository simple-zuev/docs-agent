# LOCAL RUNTIME GUARDRAILS

## 1. Purpose

This document defines the minimum local runtime guardrails for the future `docs-agent` application when deployed on a local operator machine.

Primary target environment:
- macOS
- MacBook Pro M4
- 16 GB RAM
- 512 GB SSD

These guardrails exist to keep local deployment:
- bounded
- reviewable
- quota-safe
- storage-safe
- governance-safe

This is an application runtime-control document, not a replacement for project governance in `Cass`.

## 2. Core principle

Local runtime must be treated as:
- operator-supervised
- bounded by default
- authority-aware
- mutation-restricted
- storage-disciplined

Local runtime must not be treated as:
- unrestricted autonomous Drive agent
- broad file-system or Drive mutation executor
- silent governance interpreter

## 3. Scope guardrails

The local app should operate only within explicitly allowed scope.

Allowed by default:
- approved project folders
- approved task/workflow types
- authority-bound tasks
- bounded source/export/publication flows

Not allowed by default:
- full Google Drive traversal
- unrestricted repository-wide mutation
- uncontrolled access outside approved project scope
- bulk restructuring across arbitrary folders
- implicit scope expansion based on discovery alone

Recommended implementation:
- allowlist of root folders
- task-to-scope binding
- explicit object-role classification before mutation-capable actions

## 4. Mutation guardrails

Default mutation stance:
- read first
- classify before write
- prepare before write
- approve before sensitive write
- log before and after mutation

Allowed bounded mutation-preparation subset:
- artifact-state
- doc-body-only --profile exchange-docs

This means:
- classification-before-write is allowed
- bounded document-body preparation is allowed

This does not mean:
- broad write autonomy
- arbitrary overwrite across Drive
- recursive mutation of project structure
- automatic approval bypass

Blocked by default:
- delete
- bulk rename
- bulk move
- recursive folder restructuring
- overwrite of canonical authority documents
- silent mutation of project registries
- mutation from ambiguous task context

## 5. Approval guardrails

The local app must expose explicit approval gates for:
- publication-sensitive actions
- structure-changing actions
- naming/versioning-sensitive actions
- any action touching canonical project artifacts
- any action with unclear authority binding

Minimum approval rule:
- if the operator cannot clearly see source, target, authority, and impact, the action should remain blocked

## 6. Drive object guardrails

Drive objects must not be treated as one flat file list.

Minimum object roles:
- authority document
- source artifact
- export artifact
- publication target
- registry reference
- draft/review artifact

Before any mutation-capable flow, the app should know:
- object role
- parent placement
- source/export relation
- approval status
- authority binding relevance

## 7. Resource guardrails for local machine

Even on capable local hardware, resource usage must remain bounded.

Recommended local limits:
- no more than 1–2 heavy preview/export jobs in parallel
- no large batch export by default
- bounded queue for render jobs
- explicit cancellation for long-running tasks
- no uncontrolled background sweeps across Drive

Reason:
- preserve responsiveness
- reduce quota pressure
- reduce accidental parallel mutation
- avoid memory/storage creep

## 8. Storage and cache guardrails

Local SSD usage must remain disciplined.

Required controls:
- bounded cache directory
- TTL for preview/export artifacts
- cleanup of temp files
- separation of canonical source vs derived exports
- clear distinction between persistent task records and disposable render artifacts

Recommended default stance:
- derived artifacts are disposable unless explicitly retained by task/package state
- previews should expire automatically
- large exports should not accumulate silently

## 9. Network and quota guardrails

Google Drive and related integrations should remain quota-safe.

Required behavior:
- retry only when error is explicitly retryable
- bounded retry count
- exponential backoff for quota/network-sensitive operations
- no uncontrolled polling loops
- no broad rescan loops by default

Do not assume:
- quota is effectively infinite
- retry is always safe
- repeated read/write loops are harmless

## 10. UI/runtime safety signals

The local app should make safety state visible.

Minimum visible signals:
- current scope
- authority source
- object role
- approval state
- safe-for-mutation status
- blocked reason
- task history / last action

The operator should not need to guess whether an action is safe.

## 11. Logging and auditability guardrails

All meaningful actions should remain traceable.

Minimum logging:
- task id
- object id
- action type
- approval state
- authority reference
- timestamp
- result status

Local audit log must not replace project registries in `Cass`.
It is execution evidence, not project governance source-of-truth.

## 12. Local deployment interpretation

A local deployment on MacBook Pro M4 / 16 GB / 512 GB is viable for the first operator version if:
- scope remains bounded
- mutation remains guarded
- cache remains bounded
- exports remain controlled
- approvals remain explicit
- Drive operations remain structured

It is not a justification for:
- broad autonomous Drive mutation
- unlimited caching or export accumulation
- universal background automation
- silent policy substitution

## 13. Final rule

Use this rule by default:

- local app may assist
- operator remains responsible
- governance remains in `Cass`
- runtime stays bounded
- mutation stays controlled
