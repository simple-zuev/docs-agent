# docs-agent

Локальный CLI-агент для работы с проектной документацией АСТЦВ, MASTER_INDEX и связанными диагностическими и операционными проверками.

## Текущий статус

Текущий baseline:
- stage27-reconciled

## Основные entrypoints

- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- python agent_cli.py doctor-lite
- python agent_cli.py doctor
- bash scripts/regression_smoke_explain.sh
