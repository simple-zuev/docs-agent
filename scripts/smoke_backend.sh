#!/bin/zsh
set -euo pipefail

cd /Users/zuevvladimir/AI/docs-agent/operator_backend
source .venv/bin/activate

python -m pytest /Users/zuevvladimir/AI/docs-agent/tests/api/test_tasks_api.py -q
