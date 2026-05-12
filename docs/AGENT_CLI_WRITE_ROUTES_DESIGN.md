# AGENT_CLI_WRITE_ROUTES_DESIGN

## 1. Purpose

Expose bounded draft workflow write commands through `agent_cli.py` without introducing new mutation semantics.

## 2. Objective

Surface these commands in a controlled operator-facing form:

- `create-draft-doc`
- `write-draft-doc`
- `append-review-note`

## 3. Safety boundary

Must:
- reuse existing `docs_agent.py` bounded write commands
- keep explicit argument contracts
- preserve existing review-scope validation
- preserve explicit confirmation discipline where applicable
- keep operator-visible behavior predictable

Must not:
- add canonical mutation
- change existing write semantics
- broaden target scope
- add hidden automation

## 4. Minimal command surface

Planned `agent_cli.py` routes:

- `create-draft-doc --title <title> [--dry-run] --confirm`
- `write-draft-doc --document-id <id> --body-file <path> [--dry-run] --confirm`
- `append-review-note --document-id <id> --note-file <path> [--dry-run] --confirm`

## 5. Preferred implementation approach

Use `run_docs_agent_with_retry(...)` and thin wrappers only.
Prefer file-based body/note input at the CLI layer to avoid shell quoting fragility.

## 6. Verification

Required checks:
- `pre-commit`
- `py_compile`
- `agent_cli.py status --json`
- `agent_cli.py doctor-lite --json`

## 7. Next safe step

Implement the thinnest possible wrappers and usage text updates in `agent_cli.py`.
