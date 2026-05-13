#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate

echo "== step: py_compile =="
set +e
python -m py_compile agent_cli.py >/dev/null 2>&1
rc=$?
set -e
echo "rc=$rc"
if [[ "$rc" -ne 0 ]]; then
  echo "diagnosis: internal"
  echo "likely_cause: Ошибка синтаксиса или структурная ошибка в agent_cli.py."
  echo "recommended_action: Запусти python -m py_compile agent_cli.py без перенаправления и исправь traceback."
  exit 1
fi

echo
echo "== step: regression_error_contract =="
set +e
./scripts/regression_error_contract.sh >/dev/null 2>&1
rc=$?
set -e
echo "rc=$rc"
if [[ "$rc" -ne 0 ]]; then
  echo "diagnosis: internal"
  echo "likely_cause: Нарушен контракт обработки ошибок CLI."
  echo "recommended_action: Запусти ./scripts/regression_error_contract.sh без >/dev/null и посмотри первый падающий кейс."
  exit 1
fi

echo
echo "== step: regression_exit_codes_bounded =="
bounded_gate_log="$(mktemp)"
set +e
bash ./scripts/regression_exit_codes_bounded.sh >"$bounded_gate_log" 2>&1
rc=$?
set -e
echo "rc=$rc"
if [[ "$rc" -ne 0 ]]; then
  echo "diagnosis: internal"
  echo "likely_cause: Нарушен контракт bounded exit codes."
  echo "recommended_action: Проверь полный вывод bounded gate ниже и найди первый FAIL."
  echo
  echo "---- bounded gate output start ----"
  cat "$bounded_gate_log"
  echo "---- bounded gate output end ----"
  rm -f "$bounded_gate_log"
  exit 1
fi
rm -f "$bounded_gate_log"

echo
echo "smoke_explain: OK"
