# AGENT REPOSITORY MAP

## Main runtime files
- `agent_cli.py` — primary bounded operator entrypoint
- `docs_agent.py` — underlying Google Drive / Google Sheets command implementation layer

## Main support area
- `audits/` — audit artifacts, checkpoints, snapshots, conclusions

## Important runtime themes
- command dispatch and operator contract: `agent_cli.py`
- Google Drive / Sheets operations: `docs_agent.py`
- bounded mutation-preparation contour: `artifact-state`, `doc-body-only`
- degraded document-access runtime contour: `read-doc`, `get-file`, `read-doc-from-query`

## Repository working mode
- small reviewable PRs only
- audit-first when uncertainty exists
- production changes only when drift is isolated and justified
