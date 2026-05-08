#!/usr/bin/env bash
set -euo pipefail

python -m py_compile agent_cli.py >/dev/null
./scripts/regression_error_contract.sh >/dev/null
bash ./scripts/regression_exit_codes.sh >/dev/null

echo "smoke_quiet: OK"
