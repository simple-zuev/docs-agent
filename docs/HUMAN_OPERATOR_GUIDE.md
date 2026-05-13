# Human Operator Guide

## 1. Назначение

Этот документ нужен человеку-оператору, который использует docs-agent ежедневно.

## 2. Ежедневный старт

cd ~/AI/docs-agent
source venv312/bin/activate
bash scripts/operator_start.sh

Ожидаемый результат:
- doctor-lite возвращает healthy
- можно начинать штатную работу

## 3. Routine preflight

bash scripts/preflight_check.sh

## 4. Основные команды

Usable assisted bounded baseline

Проверить статус:
- python agent_cli.py status
- python agent_cli.py status --json
- python agent_cli.py repo-state
- python agent_cli.py repo-state --json
- python agent_cli.py doctor
- python agent_cli.py doctor --json

Найти документ:
- python agent_cli.py f "DOC-0001"

Проверить артефакт:
- python agent_cli.py artifact-state --file-id "<google_drive_file_id>"

Получить метаданные файла:
- python agent_cli.py get-file "<google_drive_file_id>"

Прочитать документ напрямую:
- python agent_cli.py read-doc "<google_doc_id>"

Подготовить тело документа:
- python agent_cli.py doc-body-only --profile "exchange-docs" --document-type "note" --title "example_title"

Available but non-baseline by default

Открыть документ через query-routing:
- python agent_cli.py o "DOC-0002"

Прочитать документ через query-routing:
- python agent_cli.py r "DOC-0002"

Supported helper surface:
- python agent_cli.py q "прочитай DOC-0002"

## 5. Диагностика

Быстрая:
- python agent_cli.py doctor-lite
- python agent_cli.py doctor-lite --json

Глубокая:
- python agent_cli.py doctor
- python agent_cli.py doctor --json

Explainable smoke:
- bash scripts/regression_smoke_explain.sh

## 6. Практические правила

1. Для ежедневной работы использовать только doctor-lite.
2. doctor запускать, когда нужна углубленная диагностика.
3. Не делать подряд много quota-sensitive прогонов.
4. Если deep path дал спорный результат — подождать 60-90 секунд и повторить.
5. Итоговые выводы делать по одному сохраненному JSON snapshot.

## 7. Главные риски для оператора

- quota pressure на Google Sheets API
- ложная интерпретация внешнего quota failure как внутренней поломки
- случайный коммит чувствительного локального config
- избыточные deep проверки подряд

## 8. Что не делать

Нельзя:
- коммитить config/
- вставлять токены и секреты в GitHub, issues, commits
- считать один нестабильный deep failure доказательством постоянной поломки
- запускать хаотические длинные цепочки диагностик без паузы

## 9. Где смотреть артефакты

- audits/ — результаты проверок, snapshots, status notes
- docs/ — документация
- scripts/ — operational и regression scripts
