# Command Reference

## Routine

operator_start
- bash scripts/operator_start.sh

preflight_check
- bash scripts/preflight_check.sh

doctor-lite
- python agent_cli.py doctor-lite
- python agent_cli.py doctor-lite --json

live-google-probe
- python agent_cli.py live-google-probe
- python agent_cli.py live-google-probe --json

## Deep

doctor
- python agent_cli.py doctor
- python agent_cli.py doctor --json

regression_smoke_explain
- bash scripts/regression_smoke_explain.sh

## Assisted bounded mode: usable contour

status
- python agent_cli.py status
- python agent_cli.py status --json

repo-state
- python agent_cli.py repo-state
- python agent_cli.py repo-state --json
- python agent_cli.py rs
- python agent_cli.py rs --json

doctor
- python agent_cli.py doctor
- python agent_cli.py doctor --json
- python agent_cli.py diagnose
- python agent_cli.py diagnose --json

live-google-probe
- python agent_cli.py live-google-probe
- python agent_cli.py live-google-probe --json

assemble-context
- python agent_cli.py assemble-context --profile "<profile>"
- python agent_cli.py assemble-context --json --profile "<profile>"

find-doc-id
- python agent_cli.py find-doc-id "DOC-0001"

find-doc-name
- python agent_cli.py find-doc-name "Document Name"

find-link
- python agent_cli.py find-link "drive_id_or_url_fragment"

find-doc-any
- python agent_cli.py find-doc-any "DOC-0001"
- python agent_cli.py find-doc-any --json "DOC-0001"
- python agent_cli.py f "DOC-0001"
- python agent_cli.py f --json "DOC-0001"

artifact-state
- python agent_cli.py artifact-state --file-id "<google_drive_file_id>"
- python agent_cli.py artifact-state --json --file-id "<google_drive_file_id>"

open-doc-from-query
- python agent_cli.py open-doc-from-query "DOC-0002"
- python agent_cli.py open-doc-from-query --json "DOC-0002"
- python agent_cli.py o "DOC-0002"
- python agent_cli.py o --json "DOC-0002"

doc-body-only
- python agent_cli.py doc-body-only --profile "<profile>" --document-type "<type>" --title "<title>"
- python agent_cli.py doc-body-only --json --profile "<profile>" --document-type "<type>" --title "<title>"

## Degraded contour

get-file
- python agent_cli.py get-file "<google_drive_file_id>"

read-doc
- python agent_cli.py read-doc "<google_doc_id>"

read-doc-from-query
- python agent_cli.py read-doc-from-query "DOC-0002"
- python agent_cli.py read-doc-from-query --json "DOC-0002"
- python agent_cli.py r "DOC-0002"
- python agent_cli.py r --json "DOC-0002"


## Supported helper surface

ask
- python agent_cli.py ask "прочитай DOC-0002"
- python agent_cli.py ask --json "прочитай DOC-0002"
- python agent_cli.py q "прочитай DOC-0002"
- python agent_cli.py q --json "прочитай DOC-0002"

## Notes

- In assisted bounded mode, usable baseline commands are:
  - status
  - repo-state / rs
  - doctor / diagnose
  - live-google-probe
  - find-doc-id
  - find-doc-name
  - find-link
  - find-doc-any / f
  - artifact-state
  - open-doc-from-query / o
  - doc-body-only
- The following commands are available in CLI but should not be treated as baseline by default:
  - get-file
  - read-doc
  - read-doc-from-query / r
- Supported helper surface exists, but should not replace direct bounded inspection flow by default:
  - ask / q
- `doctor-lite` and `doctor` may be cache-backed. Use `live-google-probe` when the operator needs an explicit live Google/OAuth check.

## Exit codes

- 0 success
- 1 usage error
- 2 not found
- 3 auth error
- 4 network/retryable error
- 5 internal error
- 130 interrupted
