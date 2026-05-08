#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

python -m py_compile agent_cli.py >/dev/null
./scripts/regression_error_contract.sh >/dev/null
bash ./scripts/regression_exit_codes.sh >/dev/null
bash ./scripts/regression_smoke_quiet.sh >/dev/null
python scripts/review_agent_cli_structure.py > audits/agent_cli_structure_stage11_release.txt

echo "stage11_release_check: OK"
