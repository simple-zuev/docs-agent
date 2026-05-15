#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/.." && pwd))"
cd "$ROOT"

python3 -m ruff check tests/test_smoke_syntax.py
python3 -m ruff format --check tests/test_smoke_syntax.py
python3 -m pytest tests/test_smoke_syntax.py
python3 -m compileall tests
