# AGENT RELEASE CHECKPOINT

## 1. Release status

The repository is now ready for **assisted bounded integration release**.

This release status means:
- the bounded operator-supervised contour is established and documented;
- the bounded baseline has runtime evidence and repository-level governance support;
- the repository is not being presented as ready for full autonomous all-file-operations mode.

## 2. Current bounded baseline

The current assisted bounded baseline is:

- status
- repo-state / rs
- doctor / diagnose
- find-doc-id
- find-doc-name
- find-link
- find-doc-any / f
- artifact-state
- get-file
- read-doc
- doc-body-only --profile exchange-docs

## 3. What this release allows

This release allows:
- bounded operator-supervised inspection
- bounded lookup and state classification
- direct metadata access through get-file
- direct bounded document read through read-doc
- safe document-body preparation through doc-body-only
- controlled branch-based improvement waves

## 4. What this release does not allow

This release does not allow:
- full autonomous all-file-operations mode
- broad autonomous mutation across arbitrary files/documents
- promotion of query-routed document-access paths into baseline without separate hardening
- broad capability claims based on helper/query routes

## 5. Non-baseline routes

The following routes may be available and useful, but remain outside the current bounded baseline:

- open-doc-from-query / o
- read-doc-from-query / r
- ask / q

## 6. Release interpretation

### GO
- assisted bounded integration release

### NO-GO
- full autonomous all-file-operations release

## 7. Operator rule

Use the bounded baseline by default.
Do not widen operating assumptions based on incidental success outside the bounded baseline.

## 8. Next capability frontier

The next capability frontier should be assessed separately and explicitly.
Likely next candidates:
- open-doc-from-query / o
- read-doc-from-query / r

No frontier promotion is included in this release checkpoint.
