#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/AI/docs-agent"

resolve_python_bin() {
  if [[ -n "${DOCS_AGENT_PYTHON:-}" && -x "${DOCS_AGENT_PYTHON}" ]]; then
    printf '%s\n' "${DOCS_AGENT_PYTHON}"
    return
  fi

  local candidates=(
    "$BASE/venv312/bin/python"
    "$BASE/.venv/bin/python"
    "$BASE/venv/bin/python"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  done

  printf '%s\n' "python3"
}

PYTHON_BIN="$(resolve_python_bin)"

echo "== lookup success candidate =="
set +e
"$PYTHON_BIN" agent_cli.py f "DOC-0001"
rc=$?
set -e
echo "lookup_success_rc=$rc"

echo
echo "== lookup not found candidate =="
set +e
"$PYTHON_BIN" agent_cli.py f "DOC-9999"
rc=$?
set -e
echo "lookup_not_found_rc=$rc"

echo
echo "lookup diagnostics complete"
