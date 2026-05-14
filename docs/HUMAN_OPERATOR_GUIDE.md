# Human Operator Guide

## 1. Назначение

Этот документ нужен человеку-оператору, который использует docs-agent ежедневно.

## 2. Ежедневный старт

cd ~/AI/docs-agent
source venv312/bin/activate
bash scripts/operator_start.sh

Ожидаемый результат:
- doctor-lite возвращает healthy
- если вывод показывает `cache_backed: True`, это routine-ready, но не отдельное подтверждение live Google/OAuth
- можно начинать штатную работу

## 3. Routine preflight

bash scripts/preflight_check.sh

Для явной проверки live Google/OAuth без локального cache:
- python agent_cli.py live-google-probe
- python agent_cli.py live-google-probe --json

## 4. Основные команды

Usable assisted bounded baseline

Проверить статус:
- python agent_cli.py status
- python agent_cli.py status --json
- python agent_cli.py repo-state
- python agent_cli.py repo-state --json
- python agent_cli.py doctor
- python agent_cli.py doctor --json
- python agent_cli.py live-google-probe --json

Найти документ:
- python agent_cli.py f "DOC-0001"

Открыть документ через navigation/query-routing:
- python agent_cli.py o "DOC-0002"

Проверить артефакт:
- python agent_cli.py artifact-state --file-id "<google_drive_file_id>"

Подготовить тело документа:
- python agent_cli.py doc-body-only --profile "exchange-docs" --document-type "note" --title "example_title"

Available but non-baseline by default

Получить метаданные файла:
- python agent_cli.py get-file "<google_drive_file_id>"

Прочитать документ напрямую:
- python agent_cli.py read-doc "<google_doc_id>"

Прочитать документ через query-routing:
- python agent_cli.py r "DOC-0002"

Supported helper surface:
- python agent_cli.py q "прочитай DOC-0002"

## 5. Диагностика

Быстрая:
- python agent_cli.py doctor-lite
- python agent_cli.py doctor-lite --json

Live Google/OAuth:
- python agent_cli.py live-google-probe
- python agent_cli.py live-google-probe --json

Глубокая:
- python agent_cli.py doctor
- python agent_cli.py doctor --json

Explainable smoke:
- bash scripts/regression_smoke_explain.sh

## 6. Практические правила

1. Для ежедневной работы использовать только doctor-lite.
2. live-google-probe запускать, когда нужно отличить cache-backed readiness от live Google/OAuth доступности.
3. doctor запускать, когда нужна углубленная диагностика.
4. Не делать подряд много quota-sensitive прогонов.
5. Если deep path дал спорный результат — подождать 60-90 секунд и повторить.
6. Итоговые выводы делать по одному сохраненному JSON snapshot.

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

## Диаграммы и форматы артефактов

Для задач по схемам и диаграммам использовать такую модель:

- Mermaid и `.drawio` — основные редактируемые исходники
- SVG / PNG / PDF — форматы экспорта и публикации
- Google Slides — presentation layer по умолчанию

По умолчанию не считать PNG / PDF / Slides первичным редактируемым source-of-truth.

## Контур работы с диаграммами

Минимально поддержанный workflow:

1. исходник в `Mermaid` или `.drawio`
2. проверка исходника до публикации
3. экспорт в `SVG` / `PNG` / `PDF`
4. при необходимости публикация через Google Slides
5. сохранение исходника отдельно от publish-артефакта

Не считать Slides / PNG / PDF заменой основного редактируемого исходника по умолчанию.
