# Codex handoff for docs-agent

## Current situation

The project is being prepared for controlled Codex-assisted development.

The repository uses an audit-heavy development style:
- small feature branches;
- audit artifacts under audits/;
- narrow PRs;
- explicit command-surface checks;
- conservative runtime behavior changes.

## Current operating decision

Approved mode: Path A.

Codex may help with:
- reading and understanding repository structure;
- preparing audit artifacts;
- proposing narrow fixes;
- running lint, help, and status checks;
- producing pull requests.

Codex must not:
- perform broad autonomous rewrites;
- claim degraded Google Drive commands are reliable without proof;
- commit secrets;
- mutate live Google Docs unless explicitly authorized;
- skip audit artifacts for risky runtime changes.

## Known degraded or risky areas

Treat these as degraded unless a later PR proves otherwise:
- read-doc
- get-file
- read-doc-from-query

Preferred safe surfaces:
- repo-state
- lookup/navigation commands
- artifact-state
- doc-body-only

## Recommended first Codex task

Read-only task:

Inspect AGENTS.md, docs/CODEX_HANDOFF.md, agent_cli.py, and recent audit files. Do not modify files. Produce a concise engineering assessment of the next safest PR for mutation result/output contract alignment.

## Recommended second Codex task

Audit-only task:

Create an audit artifact that maps mutation-related commands to their result/output envelopes. Do not change runtime behavior. Identify the narrowest production fix if a mismatch is found.

## Recommended third Codex task

Narrow production task:

Apply only the smallest contract-alignment fix identified by the audit. Run help, repo-state, ruff check, and ruff format check. Produce a PR with validation output.
