#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

python -m py_compile agent_cli.py

echo "== ask compact =="
python agent_cli.py q "статус"

echo "== ask json =="
python agent_cli.py q --json "статус"

echo "== find compact =="
python agent_cli.py f "DOC-0001"

echo "== find json =="
python agent_cli.py f --json "DOC-0001"

echo "== open compact =="
python agent_cli.py o "DOC-0002"

echo "== open json =="
python agent_cli.py o --json "DOC-0002"

echo "== read compact =="
python agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"

echo "== read json =="
python agent_cli.py r --json "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"
