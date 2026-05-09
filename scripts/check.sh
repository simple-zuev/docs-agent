#!/bin/zsh
set -euo pipefail

ROOT="/Users/zuevvladimir/AI/docs-agent"
cd "$ROOT"

python3 -m ruff check .
python3 -m ruff format --check .
python3 -m pytest
python3 -m compileall "$ROOT"
