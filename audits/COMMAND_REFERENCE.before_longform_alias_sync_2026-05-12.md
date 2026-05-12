# Command Reference

## Routine

operator_start
- bash scripts/operator_start.sh

preflight_check
- bash scripts/preflight_check.sh

doctor-lite
- python agent_cli.py doctor-lite
- python agent_cli.py doctor-lite --json

## Deep

doctor
- python agent_cli.py doctor
- python agent_cli.py doctor --json

regression_smoke_explain
- bash scripts/regression_smoke_explain.sh

## Work commands

status
- python agent_cli.py status
- python agent_cli.py status --json

find
- python agent_cli.py f "DOC-0001"
- python agent_cli.py find-doc-any "DOC-0001"

open
- python agent_cli.py o "DOC-0002"

read
- python agent_cli.py r "DOC-0002"
- python agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"

ask
- python agent_cli.py q "прочитай DOC-0002"

## Exit codes

- 0 success
- 1 usage error
- 2 not found
- 3 auth error
- 4 network/retryable error
- 5 internal error
- 130 interrupted
