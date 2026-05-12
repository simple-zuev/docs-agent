# APPEND_REVIEW_NOTE_DESIGN

## 1. Purpose

Add a minimal safe `append-review-note` workflow for review-scoped draft documents.

## 2. Objective

The command should append a bounded review note only to an existing draft inside `13_Черновики_и_review` and return a clear operator result.

## 3. Safety boundary

Must:
- mutate only an existing document
- require explicit confirmation
- validate target parent folder membership in `13_Черновики_и_review`
- append note content only
- write bounded change-log entry
- avoid canonical mutation

Must not:
- update MASTER_INDEX
- move artifacts
- overwrite full canonical documents
- mutate targets outside review scope
- chain hidden promotion logic

## 4. Minimal command contract

Planned command surface:
- `docs_agent.py append-review-note`

Expected result fields in operator output:
- command
- target artifact metadata
- appended chars
- artifact state
- next safe step
- change log reference

## 5. Expected workflow

1. validate write mode / confirm discipline
2. read target metadata
3. validate target is inside `13_Черновики_и_review`
4. compute document end position
5. append bounded review note
6. append bounded change-log entry
7. return metadata and next safe step

## 6. Mutation strategy

Current bounded strategy:
- read document structure
- determine safe append index near end of body
- append formatted review note block
- do not rewrite existing body

## 7. Next safe step

After append:
- inspect resulting draft content
- optionally connect command to `agent_cli.py`
- optionally extend artifact-state to detect review-note activity
