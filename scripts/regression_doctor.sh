#!/usr/bin/env bash
set -euo pipefail

echo "== doctor compact =="
python agent_cli.py doctor

echo
echo "== doctor json =="
python agent_cli.py doctor --json >/dev/null

echo
echo "doctor_regression: OK"
