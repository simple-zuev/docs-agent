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

run_case "usage missing query" 1 "$PYTHON_BIN" agent_cli.py q
run_case "open success" 0 "$PYTHON_BIN" agent_cli.py o "DOC-0002"
run_case "open not found" 2 "$PYTHON_BIN" agent_cli.py o "DOC-9999"
run_case "read success" 0 "$PYTHON_BIN" agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"
run_case "read not found" 2 "$PYTHON_BIN" agent_cli.py r "NON_EXISTENT_DOCUMENT_NAME"
run_case "ask read success" 0 "$PYTHON_BIN" agent_cli.py q "прочитай 00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"
run_case "ask read not found" 2 "$PYTHON_BIN" agent_cli.py q "прочитай NON_EXISTENT_DOCUMENT_NAME"
