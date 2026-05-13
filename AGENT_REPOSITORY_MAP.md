# AGENT REPOSITORY MAP

## 1. Purpose of the repository

This repository provides a controlled CLI and related operational artifacts for working with the project document contour in assisted bounded mode.

## 2. Key repository zones

### Runtime / CLI
- `agent_cli.py`
- `docs_agent.py`
- `scripts/`

### Operational documentation
- `README.md`
- `docs/`
- `AGENT_CURRENT_CHECKPOINT.md` (when present on the active branch)
- `AGENT_OPERATING_PROMPT.md`
- `AGENT_COMMAND_POLICY.md`
- `AGENT_REPOSITORY_MAP.md`

### Audit artifacts
- `audits/`

## 3. Practical role of key files

### `agent_cli.py`
Primary bounded operator-facing CLI surface.

### `docs_agent.py`
Underlying document/runtime command execution layer.

### `scripts/`
Operational and regression scripts.
Important distinction:
- some scripts are launch-blocking bounded verification tools;
- some scripts are extended or diagnostic only.

### `docs/COMMAND_REFERENCE.md`
Reference for command surface documentation.

### `docs/HUMAN_OPERATOR_GUIDE.md`
Operator-facing usage guidance.

### `docs/AI_AGENT_GUIDE.md`
AI/agent-facing operational guidance.

### `audits/`
Review snapshots, audit notes, before/after artifacts, and bounded change evidence.

## 4. Governance interpretation

Repository source of truth should be interpreted in this order:

1. branch-local authority files
   - `AGENT_CURRENT_CHECKPOINT.md`
   - `AGENT_OPERATING_PROMPT.md`
   - `AGENT_COMMAND_POLICY.md`
   - `AGENT_REPOSITORY_MAP.md`
2. bounded runtime evidence
3. command reference / operator docs
4. older historical audit artifacts

## 5. Current launch boundary summary

Current intended launch boundary:
- assisted bounded mode only

Current non-goal:
- full autonomous all-file-operations mode

## 6. Working rule for future changes

Prefer one bounded wave per problem class:
- governance/docs
- smoke/verification hardening
- command contract alignment
- runtime contour hardening

Do not combine multiple problem classes in one change set unless explicitly justified.
