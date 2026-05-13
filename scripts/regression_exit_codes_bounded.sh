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

run_case() {
  local title="$1"
  local expected="$2"
  shift 2

  echo "== $title =="
  set +e
  "$@"
  rc=$?
  set -e
  echo "exit_code=$rc expected=$expected"
  if [[ "$rc" -ne "$expected" ]]; then
    echo "FAIL: $title"
    exit 1
  fi
}

run_case "usage no command" 1 "$PYTHON_BIN" agent_cli.py
run_case "status success" 0 "$PYTHON_BIN" agent_cli.py status
run_case "repo-state success" 0 "$PYTHON_BIN" agent_cli.py repo-state
