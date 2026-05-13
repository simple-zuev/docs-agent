# AGENT CURRENT CHECKPOINT

## 1. Current operating mode

The repository is currently ready for **assisted bounded mode**.

This means:
- the agent may be used for controlled inspection, lookup, state classification, and bounded document-body preparation;
- the agent must not be treated as ready for broad autonomous file operations;
- the operator remains responsible for final mutation decisions.

## 2. Runtime state confirmed

The following command surfaces were runtime-validated on the current main baseline:

- status --json
- repo-state --json
- doctor --json
- find-doc-id
- find-doc-name
- find-link
- find-doc-any / f
- artifact-state
- doc-body-only --profile exchange-docs

Confirmed runtime properties:
- main is clean and aligned with origin/main
- mutation from main is blocked by guardrail
- safety/config control plane is healthy
- lookup and artifact classification surfaces are healthy
- bounded document-body preparation works in safe non-writing mode
- structured error contracts are present

## 3. Usable assisted bounded contour

Treat the following as the current usable baseline:

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
- open-doc-from-query / o
- read-doc-from-query / r
- doc-body-only --profile exchange-docs

Default working style:
- inspect first
- diagnose second
- prefer state and lookup before mutation
- use bounded document preparation instead of direct write by default
- keep main clean

## 4. Degraded / non-baseline contour

The following commands are available and may be functionally useful, but must not be treated as baseline for launch:

- open-doc-from-query / o
- read-doc-from-query / r

## 5. Helper surface

The following supported supported helper surface exists, but should not replace explicit bounded workflows:

- ask / q
- assemble-context

## 6. Launch decision

### Current decision
**GO** for assisted bounded launch.

### Conditions
Launch is valid only under these constraints:
- operator-supervised usage
- bounded contour only
- no broad autonomous mutation
- no promotion of degraded commands to baseline
- no mutation from main
- write operations remain controlled and explicitly reviewed

## 7. Not ready yet

The repository is not yet ready for:

- full autonomous all-file-operations mode
- broad read/open/get-file baseline usage
- broad write autonomy across arbitrary documents/files
- launch claims that treat helper/degraded surface as production baseline

## 8. Remaining hardening work

The main remaining hardening issue is the deep verification gate:

- regression_smoke_explain.sh remains nondeterministic in some runs
- regression_exit_codes.sh currently mixes:
  - bounded baseline checks
  - degraded document-access checks
  - helper/query checks

This means the current deep smoke path is not yet a clean bounded launch gate.

## 9. Next technical milestone

Next bounded milestone:

- separate bounded baseline verification from degraded/helper verification
- make the smoke gate deterministic for the assisted bounded contour
- keep degraded/helper checks visible but non-blocking for bounded launch

## 9A. Next promotion candidate

The previously selected promotion candidate `get-file` has now been validated for bounded baseline inclusion.

Reason:
- direct and narrower contract
- repeated successful controlled runtime evidence
- explicit and predictable metadata-oriented behavior

The next content-bearing route `read-doc` has now also been validated for bounded baseline inclusion.

Reason:
- repeated successful controlled runtime evidence
- stable direct contract shape
- explicit truncation behavior
- explicit non-retryable negative-path behavior


## 10. Practical operator rule

Until the next milestone is completed, use this rule:

- rely on status / repo-state / doctor / find-* / artifact-state / doc-body-only(exchange-docs)
- do not widen the launch contour based only on incidental success of o / r / q / get-file / read-doc
