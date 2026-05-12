# agent_cli contract coverage snapshot — 2026-05-12

## Scope
Documentation-first expansion of CLI contract without changing CLI surface.

## Observed facts
- `AGENT_CLI_TOOL_CONTRACT.md` is absent in the current branch baseline.
- `agent_cli.py --help` does not implement a standard help flag path.
- `agent_cli.py --help` currently returns `UsageError` with `Unknown command: --help`, then prints usage text.
- `usage()` exposes a large part of the command surface.
- `main()` dispatch exposes additional observed commands and aliases not fully captured by the ad-hoc help snapshot.

## Observed commands
- status
- repo-state
- rs
- doctor-lite
- diagnose-lite
- doctor
- diagnose
- assemble-context
- doc-body-only
- artifact-state
- find-doc-id
- find-doc-name
- find-link
- find-doc-any
- f
- open-doc-from-query
- o
- read-doc-from-query
- r
- get-file
- read-doc
- ask
- q

## Observed documentation gaps to close
1. Explicit command catalog is not documented in a dedicated contract file.
2. Per-command argument schema is not documented in one place.
3. Alias coverage is incomplete unless taken from `main()`.
4. Current `--help` behavior must be documented as observed behavior.
5. JSON vs compact human-readable output mode must be documented.
6. Exit code semantics should be explicitly documented.
7. Stability / compatibility notes should be included so wrappers do not assume undocumented behavior.

## Out of scope for this step
- CLI surface changes
- orchestration refactor
- help flag implementation
- command deduplication in `main()`
