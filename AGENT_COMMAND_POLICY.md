# AGENT COMMAND POLICY

## 1. Current usable baseline

Treat the following as the current usable assisted bounded baseline:

- status
- repo-state / rs
- doctor / diagnose
- find-doc-id
- find-doc-name
- find-link
- find-doc-any / f
- artifact-state
- doc-body-only --profile exchange-docs

## 2. Default usage policy

Default preference order:

1. status / repo-state / doctor
2. find-doc-id / find-doc-name / find-link / find-doc-any
3. artifact-state
4. doc-body-only --profile exchange-docs

## 3. Degraded / non-baseline contour

The following commands are available and may be functionally useful, but must not be treated as baseline:

- open-doc-from-query / o
- read-doc-from-query / r
- get-file
- read-doc

## 4. Helper surface

The following helper/query surface exists, but must not replace explicit bounded workflows:

- ask / q
- assemble-context

## 5. Verification policy

Launch-blocking bounded smoke should remain aligned only to deterministic bounded checks.

External-sensitive lookup/document-access checks may be useful diagnostically, but should not redefine launch readiness unless they are explicitly stabilized and promoted through review.

## 6. Mutation policy

Do not use command success in degraded/helper surfaces as justification to:
- widen launch scope;
- claim broader readiness;
- treat those commands as production baseline.

## 7. Next promotion candidate

Current preferred candidate for future bounded promotion work:
- get-file

This does not change the current launch boundary.
It only records prioritization for a future bounded stabilization wave.

## 8. Branch discipline

- do not mutate from main
- use a feature branch for reviewable changes
- keep runtime/code and governance/docs waves separated unless explicitly justified
