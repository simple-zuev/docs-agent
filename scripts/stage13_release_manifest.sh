#!/usr/bin/env bash
set -euo pipefail

mkdir -p audits

python -m py_compile agent_cli.py >/dev/null
bash scripts/regression_smoke_quiet.sh >/dev/null
python scripts/review_agent_cli_structure.py > audits/agent_cli_structure_stage13.txt

cat > audits/release_manifest_stage13.txt <<'TXT'
Release Manifest — stage13

Component:
- agent_cli.py

Operational state:
- ready for controlled daily use

Validated capabilities:
- status
- find-doc-any
- open-doc-from-query
- read-doc-from-query
- ask

Supported output modes:
- compact human output
- json output where supported by command contract

Exit code contract:
- 0 success
- 1 usage error
- 2 not found
- 3 auth error
- 4 network/retryable error
- 5 internal error
- 130 interrupted

Stability notes:
- read flow unified
- compact error output implemented
- compact status output implemented
- status --json supported
- help/examples polished
- quiet smoke wrapper available

Audit artifacts:
- audits/stage8_exit_codes.txt
- audits/stage10_summary.txt
- audits/stage11_release_summary.txt
- audits/stage12_summary.txt
- audits/agent_cli_structure_stage13.txt
TXT

cat > audits/operator_checklist_stage13.txt <<'TXT'
Operator Checklist

Before daily use:
1. cd ~/AI/docs-agent
2. source venv312/bin/activate
3. python agent_cli.py status

Recommended smoke checks:
- python agent_cli.py f "DOC-0001"
- python agent_cli.py o "DOC-0002"
- python agent_cli.py r "DOC-0002"
- python agent_cli.py q "прочитай DOC-0002"

If something looks wrong:
- bash scripts/regression_smoke_quiet.sh
- python agent_cli.py status --json
- inspect latest file in audits/
TXT

cat > audits/stage13_summary.txt <<'TXT'
Stage13 passed.

Done:
- release manifest created
- operator checklist created
- structure snapshot refreshed

Validated:
- py_compile OK
- regression_smoke_quiet OK
- structure snapshot generated

Release state:
- ready for controlled daily use
- release artifacts fixed in audits/
TXT

echo "stage13_release_manifest: OK"
