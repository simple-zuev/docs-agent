#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

python -m py_compile agent_cli.py

./scripts/smoke_cli.sh

echo "== negative pack =="
python agent_cli.py || true
python agent_cli.py f || true
python agent_cli.py f --json || true
python agent_cli.py o || true
python agent_cli.py o --json || true
python agent_cli.py r || true
python agent_cli.py r --json || true
python agent_cli.py q || true
python agent_cli.py q --json || true
