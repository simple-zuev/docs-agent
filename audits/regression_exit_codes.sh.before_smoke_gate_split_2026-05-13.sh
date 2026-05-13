#!/usr/bin/env bash
set -euo pipefail

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

run_case "usage no command" 1 python agent_cli.py
run_case "usage missing query" 1 python agent_cli.py q
run_case "find success" 0 python agent_cli.py f "DOC-0001"
run_case "find not found" 2 python agent_cli.py f "DOC-9999"
run_case "open success" 0 python agent_cli.py o "DOC-0002"
run_case "open not found" 2 python agent_cli.py o "DOC-9999"
run_case "read success" 0 python agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"
run_case "read not found" 2 python agent_cli.py r "NON_EXISTENT_DOCUMENT_NAME"
run_case "ask read success" 0 python agent_cli.py q "прочитай 00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"
run_case "ask read not found" 2 python agent_cli.py q "прочитай NON_EXISTENT_DOCUMENT_NAME"
run_case "status success" 0 python agent_cli.py status
