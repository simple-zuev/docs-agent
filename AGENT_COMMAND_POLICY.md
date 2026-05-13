# AGENT COMMAND POLICY

## Use by default
- status
- repo-state
- doctor
- find-doc-id
- find-doc-name
- find-link
- find-doc-any
- artifact-state
- doc-body-only

## Degraded by default
- read-doc
- get-file
- read-doc-from-query
- r

## Default decision order
1. inspect state
2. locate target
3. decide whether lookup/navigation is enough
4. if write-preparation is needed, use artifact-state or doc-body-only
5. if degraded path is encountered, stop and report

## Current command guidance
- `f --json <query>` is supported
- `f --help` is supported
- do not assume trailing `--json` form is part of the contract
