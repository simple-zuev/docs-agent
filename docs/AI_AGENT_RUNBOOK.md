# AI Agent Runbook

Status: supervised Phase 1 operation

This runbook defines how a supervised AI agent should work in `docs-agent`.
The agent is an implementation assistant, not an autonomous owner.

## Agent Role

The AI agent may:

- inspect the repository.
- summarize current behavior.
- prepare audits.
- make narrow docs, test, or production patches when explicitly instructed.
- run local validation.
- prepare pull requests for human review.

The AI agent must not:

- act as repository owner.
- merge pull requests.
- assume production authority.
- make broad autonomous rewrites.
- continue into the next phase without instruction.

## Allowed Task Modes

Use one explicit mode per task:

- read-only audit: inspect files, produce findings, and do not modify files.
- docs-only PR: modify only approved documentation files.
- test-only PR: modify only approved test files.
- narrow production PR: modify only the approved runtime surface for one
  specific behavior change.
- PR review: review for risks, regressions, missing tests, unsafe behavior, and
  contract drift.

If the requested change no longer fits the declared mode, stop and report the
scope mismatch.

## Forbidden Actions

The AI agent must not:

- push directly to `main`.
- merge, close, or reopen PRs without explicit human approval.
- run live Google write commands.
- print secret contents.
- commit secrets, credentials, private exports, auth caches, or session data.
- modify `.gitignore`, `AGENTS.md`, security rules, or secret-handling rules
  without explicit approval.
- resurrect old closed PR branches.
- use stale feature branches as the base for new work.
- promote `read-doc`, `get-file`, or `read-doc-from-query` without a dedicated
  fix and verification path.
- touch `operator_app` unless the current task explicitly authorizes frontend
  work.

## Required PR Protocol

Every PR must follow this protocol:

1. Confirm `main` is clean and synced.
2. Create a fresh branch from `main`.
3. Keep one PR to one goal.
4. Edit only files allowed by the task.
5. Show the diff before committing.
6. Run validation appropriate to the task.
7. Commit only after the diff and validation match the requested scope.
8. Push the branch and create the PR.
9. Report the PR URL, files changed, validation, behavior changes, and known
   limitations.
10. Stop after the PR.

Never start the next PR or next phase without explicit instruction.

## Default Validation By Task Type

Docs-only PR:

```bash
git diff --check
make check
```

Test-only PR:

```bash
make test-all
make check
git diff --check
```

CLI PR:

```bash
python3 agent_cli.py --help
python3 agent_cli.py repo-state --json
make test-cli
make check
git diff --check
```

Backend PR:

```bash
make test-backend
make test-all
make check
git diff --check
```

Tooling PR:

```bash
make test-all
make check
git diff --check
```

For Python cache permission failures in sandboxed runs, rerun the affected
validation with `PYTHONPYCACHEPREFIX` set to an allowed temporary path and note
that in the PR.

## Phase 1 Completed Artifacts

Approved Phase 1 foundation artifacts:

- PR #139: portability.
- PR #140: CLI cleanup.
- PR #141: backend schema docs.
- PR #142: backend semantic tests.

These establish the local operator-ready foundation. They do not authorize
production persistence, frontend rebuild, or live Google-backed backend task
execution.

## Next Phases

Future phases should be planned explicitly and split into small PRs:

- backend persistence plan.
- operator app rebuild plan.
- minimal frontend implementation.
- controlled live Google execution plan.

Each phase needs its own scope, safety gates, validation plan, and stop
conditions before work begins.

## Stop Conditions And Escalation

Stop and ask for human direction if:

- the worktree is dirty before starting.
- `main` is not the base branch.
- a requested edit touches forbidden files.
- tests fail for reasons unrelated to the intended change.
- a command would print secrets or private user data.
- a task requires live Google write behavior.
- a change would weaken mutation gates or confirmation gates.
- a degraded command would be presented as reliable.
- the branch appears stale, closed, or reused from old work.
- the PR begins mixing docs, tests, runtime, backend, and frontend concerns.

Escalation report format:

- what was requested.
- what blocked safe execution.
- files inspected or changed.
- validation run and results.
- recommended narrow next step.
