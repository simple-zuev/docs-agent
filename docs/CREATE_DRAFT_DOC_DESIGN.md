# CREATE_DRAFT_DOC_DESIGN

## 1. Purpose

Add a minimal safe `create-draft-doc` workflow for review-scoped document creation.

## 2. Objective

The command should create a new Google Doc only inside the approved review scope and return a machine-readable result suitable for agent workflows.

## 3. Safety boundary

Must:
- create only in `13_Черновики_и_review`
- require explicit confirmation
- use bounded existing write surface where possible
- return created artifact metadata
- avoid canonical mutation

Must not:
- write body into an existing document
- mutate canonical artifacts
- move existing artifacts
- update MASTER_INDEX
- introduce broad write abstractions in this iteration

## 4. Minimal command contract

Planned command surface:
- `docs_agent.py create-draft-doc`
- optionally later `agent_cli.py artifact-state` integration reuse

Expected result fields:
- `ok`
- `command`
- `target_folder`
- `title`
- `created_artifact`
- `artifact_state`
- `next_safe_step`

## 5. Expected workflow

1. validate write mode / confirm discipline
2. resolve review folder
3. create document in review folder
4. optionally place minimal boilerplate marker text
5. return metadata and next safe step

## 6. Preferred implementation approach

Prefer reusing existing bounded helper behavior already proven by:
- `create-doc-in-folder`
- review-scope folder resolution
- existing change-log append flow

## 7. Next safe step

Implement the thinnest possible `create-draft-doc` on top of existing bounded create flow, then verify:
- `py_compile`
- `pre-commit`
- `agent_cli.py status --json`
- `agent_cli.py doctor-lite --json`

