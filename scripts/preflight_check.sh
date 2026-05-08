#!/usr/bin/env bash
set -euo pipefail

cd ~/AI/docs-agent
source venv312/bin/activate
mkdir -p audits

echo "== doctor-lite =="

set +e
python agent_cli.py doctor-lite --json > audits/latest_preflight_doctor_lite.json
doctor_lite_rc=$?
set -e

echo "doctor_lite_rc=$doctor_lite_rc"

python - <<'PY'
import json
from pathlib import Path

p = Path("audits/latest_preflight_doctor_lite.json")
data = json.loads(p.read_text(encoding="utf-8"))

print(f"ok: {data.get('ok')}")
print("route: doctor-lite")
print(f"diagnosis: {data.get('diagnosis')}")
print(f"likely_cause: {data.get('likely_cause')}")
print(f"recommended_action: {data.get('recommended_action')}")

checks = data.get("checks", {})
for key in ["environment", "status", "master_index_lookup"]:
    item = checks.get(key, {})
    print(f"{key}_ok: {item.get('ok')}")
PY

diag="$(python - <<'PY'
import json
from pathlib import Path
p = Path("audits/latest_preflight_doctor_lite.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(data.get("diagnosis") or "unknown")
PY
)"

echo
echo "== preflight decision =="

if [[ "$diag" == "healthy" ]]; then
  echo "preflight_check: OK"
  exit 0
fi

if [[ "$diag" == "network" ]]; then
  echo "preflight_check: WARN"
  echo "Причина похожа на временную внешнюю проблему или квоту API."
  echo "Для рутинного старта это не блокирующий сигнал."
  echo "Для глубокой диагностики позже запусти: python agent_cli.py doctor"
  exit 0
fi

echo "preflight_check: FAIL"
echo "Диагностика = $diag"
echo "Это блокирующий случай для ручной проверки."
exit 1
