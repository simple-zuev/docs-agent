# AI Agent Guide

## 1. Назначение

Этот документ предназначен для ИИ-ассистента, который подключается к репозиторию docs-agent.

Задача ИИ:
- быстро понять структуру;
- определить canonical entrypoints;
- работать безопасно;
- не ломать baseline;
- не коммитить secrets;
- корректно интерпретировать quota-sensitive поведение.

## 2. Суть проекта

docs-agent — локальный CLI для работы с документным репозиторием АСТЦВ в Google Workspace.

Основные функции:
- поиск по MASTER_INDEX
- открытие/чтение документов
- routine/deep diagnostics
- explainable smoke
- operational сопровождение документного контура

## 3. Что считать источником истины

По запуску и эксплуатации:
- README.md
- docs/HUMAN_OPERATOR_GUIDE.md
- docs/TROUBLESHOOTING.md

По правилам изменений:
- docs/CHANGE_CONTROL.md
- docs/REPOSITORY_RULES.md
- docs/SECURITY_AND_SECRETS.md

По quota/rate-limit:
- docs/GOOGLE_API_OPERATING_NOTES.md
- docs/QUOTA_AND_RATE_LIMIT_POLICY.md

## 4. Обязательные правила для ИИ

1. Не коммитить config/, secrets, tokens, client secrets.
2. Не выводить и не публиковать содержимое токенов/секретов.
3. Не считать quota-sensitive deep failure стабильной поломкой без reconciliation.
4. Не добавлять в baseline локальные write-test файлы без отдельного решения.
5. Не делать destructive refactor без явной необходимости.
6. Не ломать существующий CLI contract без отдельной задачи.
7. doctor-lite должен оставаться routine-safe.
8. 429 / RATE_LIMIT_EXCEEDED / quota exceeded должны трактоваться как network/retryable.
9. Предпочитать additive changes вместо breaking changes.
10. Перед Git sync разделять baseline files, experiments и sensitive local config.

## 5. Operational workflow для ИИ

1. Проверить:
- git status
- git log --oneline --decorate -n 5

2. Проверить routine health:
- bash scripts/operator_start.sh

3. При проблеме:
- python agent_cli.py doctor-lite --json
- затем при необходимости python agent_cli.py doctor --json

4. Работать через snapshots, а не через хаотические повторы.

5. Документировать:
- что сделано
- что подтверждено
- что не подтверждено
- какие ограничения остаются

## 6. Рациональные инженерные замечания

1. Главный технический приоритет — уменьшить Google Sheets API pressure.
2. Лучший следующий improvement — MASTER_INDEX cache + memoization.
3. Deep diagnostics нужно проектировать как дорогой путь, а routine path — как дешевый.
4. audits/ полезен, но его надо курировать, чтобы не превратить baseline в шумовой архив.
