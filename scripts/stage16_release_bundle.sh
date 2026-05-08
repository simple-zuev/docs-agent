#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/AI/docs-agent"
cd "$ROOT"
source venv312/bin/activate

mkdir -p audits

echo "== py_compile =="
python -m py_compile agent_cli.py

echo
echo "== smoke_quiet =="
bash scripts/regression_smoke_quiet.sh

echo
echo "== operator_start =="
bash scripts/operator_start.sh >/dev/null

echo
echo "== structure snapshot =="
python scripts/review_agent_cli_structure.py > audits/agent_cli_structure_stage16.txt

cat > audits/release_bundle_stage16.txt <<'TXT'
Release Bundle — stage16

Component:
- agent_cli.py

Bundle contents:
- audits/current_release_status.txt
- audits/final_operator_runbook.txt
- audits/stage8_exit_codes.txt
- audits/stage10_summary.txt
- audits/stage11_release_summary.txt
- audits/stage12_summary.txt
- audits/stage13_summary.txt
- audits/stage14_summary.txt
- audits/stage15_summary.txt
- audits/agent_cli_structure_stage16.txt

Validated on bundle build:
- py_compile OK
- regression_smoke_quiet OK
- operator_start OK
- structure snapshot refreshed

Operational state:
- ready for controlled daily use

Entry points:
- bash scripts/operator_start.sh
- bash scripts/daily_run_check.sh
- bash scripts/regression_smoke_quiet.sh
TXT

cat > audits/preflight_check_stage16.txt <<'TXT'
Preflight Check — stage16

Run before starting work:
1. cd ~/AI/docs-agent
2. source venv312/bin/activate
3. bash scripts/preflight_check.sh

Expected result:
- status prints compact OK block
- smoke_quiet returns OK
- process exits with code 0
TXT

cat > audits/stage16_summary.txt <<'TXT'
Stage16 passed.

Done:
- preflight_check wrapper created
- release bundle file created
- structure snapshot refreshed
- final pre-start validation path added

Validated:
- py_compile OK
- regression_smoke_quiet OK
- operator_start OK
- structure snapshot generated

Operational state:
- ready for controlled daily use
- release bundle assembled in audits/
TXT

echo "stage16_release_bundle: OK"
