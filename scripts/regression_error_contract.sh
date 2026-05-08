#!/usr/bin/env bash
set -euo pipefail

echo "== open compact missing doc =="
python agent_cli.py o "DOC-9999" || true

echo "== open json missing doc =="
python agent_cli.py o --json "DOC-9999" || true

echo "== read compact missing doc =="
python agent_cli.py r "NON_EXISTENT_DOCUMENT_NAME" || true

echo "== read json missing doc =="
python agent_cli.py r --json "NON_EXISTENT_DOCUMENT_NAME" || true

echo "== ask compact missing doc =="
python agent_cli.py q "прочитай NON_EXISTENT_DOCUMENT_NAME" || true

echo "== ask json missing doc =="
python agent_cli.py q --json "прочитай NON_EXISTENT_DOCUMENT_NAME" || true
