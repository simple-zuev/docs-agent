# Local Release Checklist

Status: Phase 1 local operator-ready foundation

This checklist defines the practical local release gate for using `docs-agent`
with a human operator and a supervised AI agent. It is not an external
production release checklist.

## Release Status

The current target is a local operator-ready foundation:

- bounded CLI operation for assisted local work.
- documented backend mock-runtime schema contract.
- local test gates for CLI and backend behavior.
- supervised AI development through small PRs.

This release is not:

- an external production deployment.
- a production backend persistence release.
- a live Google-backed backend task execution release.
- an autonomous AI operation release.

## Required Git State

Before treating `main` as a local release baseline:

- `main` must be checked out.
- `main` must be synced with `origin/main`.
- `git status --short --branch` must be clean.
- there must be no open PRs unless they are intentionally current and understood.
- there must be no stale feature or `codex/*` branches that could be confused
  with the release baseline.

Do not release from a dirty branch, a stale PR branch, or an unreviewed local
state.

## Secret Safety

Tracked files must not contain:

- `token.json`.
- `client_secret.json`.
- OAuth client secrets.
- credentials files.
- `.env` files.
- service account keys.
- API keys.
- private Google Drive exports.
- browser, session, or auth caches.
- `auth.json`, including `~/.codex/auth.json`.

Ignored local credentials may exist for local operation, but they must not be
snapshotted, copied into docs, printed in logs, or committed.

Recommended tracked-secret scan:

```bash
git ls-files | grep -Ei '(^|/)(token|client_secret|credentials|service-account|service_account|auth)\.json$|(^|/)\.env$|key\.json$'
```

The command should return no tracked secret files. If it returns anything,
stop and investigate before continuing.

## Required Validation

Run these checks before declaring the local baseline ready:

```bash
git status --short --branch
git ls-files | grep -Ei '(^|/)(token|client_secret|credentials|service-account|service_account|auth)\.json$|(^|/)\.env$|key\.json$'
make test-cli
make test-backend
make test-all
make check
git diff --check
```

If the local sandbox blocks Python bytecode writes to the user cache, rerun the
affected Python validation with `PYTHONPYCACHEPREFIX` pointing at an allowed
temporary directory, for example:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/docs-agent-pycache make check
```

Document the cache redirection in PR notes when used.

## Current Safe Surfaces

These surfaces are part of the assisted bounded local baseline:

- `python agent_cli.py repo-state-local --json`
- `python agent_cli.py status`
- `python agent_cli.py status --json`
- `python agent_cli.py doctor-lite`
- `python agent_cli.py doctor-lite --json`
- `python agent_cli.py capabilities`
- `python agent_cli.py capabilities --json`
- lookup and navigation commands such as `find-doc-any` / `f` and
  `open-doc-from-query` / `o`.
- `python agent_cli.py artifact-state --json --file-id <google_drive_file_id>`
- `python agent_cli.py doc-body-only --json --profile <profile> --document-type <type> --title <title>`
- review-scoped dry-run JSON mutation commands when explicitly requested and
  kept in dry-run mode.

Use direct bounded inspection commands when available. Do not replace them with
general helper prompts.

## Degraded Or Non-Baseline Surfaces

Treat these as degraded by default until a later PR explicitly fixes and
verifies them:

- `read-doc`.
- `get-file`.
- `read-doc-from-query`.

Treat `ask` / `q` as a helper surface only. It is not a replacement for bounded
inspection, explicit lookup, or direct artifact-state checks.

Do not promote degraded commands in docs, tests, or operator flows without a
dedicated verification PR.

## Live Google Diagnostic Caution

`live-google-probe` is read-only and can verify live Google/OAuth access, but it
is not routine CI. It may depend on external Google API availability, quotas, and
local OAuth state.

Live Google write commands remain manual and approval-only. They must not be run
as part of local release validation unless the human owner explicitly authorizes
that exact write operation.

## Backend Status

The operator backend is mock-runtime only:

- the schema contract is documented in
  `docs/OPERATOR_BACKEND_SCHEMA_CONTRACT.md`.
- production persistence is not implemented.
- live Google-backed backend task execution is not implemented.
- backend tests protect the mock API contract and semantic relationships.

Do not treat mock seed data as production data or persistence design.

## Frontend / Operator App Status

`operator_app` is not part of the current local release baseline.

The old `operator_app` PR was closed. Any future frontend work should be rebuilt
later from current `main`, after the backend model is accepted and the intended
frontend scope is explicitly approved.

Do not revive stale frontend branches for this baseline.

## Stop Conditions

Stop the release process and escalate if any of these occur:

- tracked secrets are found.
- `main` is dirty or not synced with `origin/main`.
- required tests fail.
- validation unexpectedly depends on live Google services.
- mutation gates, confirmation gates, or write-mode behavior changed.
- degraded commands are promoted as reliable without proof.
- the PR scope becomes broad or mixes docs, tests, runtime, backend, and
  frontend concerns.
- local credentials, private Drive exports, or auth caches are printed or
  staged.

When in doubt, stop with a short report rather than widening the change.
