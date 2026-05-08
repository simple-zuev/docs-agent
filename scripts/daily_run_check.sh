#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

echo "== status =="
python agent_cli.py status

echo
echo "== smoke =="
bash scripts/regression_smoke_quiet.sh

echo
echo "daily_run_check: OK"
