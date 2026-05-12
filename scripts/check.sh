#!/usr/bin/env bash
set -euo pipefail

cd /Users/zuevvladimir/AI/docs-agent

python3 -m ruff check tests/test_smoke_syntax.py
python3 -m ruff format --check tests/test_smoke_syntax.py
python3 -m pytest tests/test_smoke_syntax.py
python3 -m compileall tests
