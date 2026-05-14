# docs-agent

Локальный CLI-агент для работы с документным контуром проекта АСТЦВ в Google Drive / Google Docs / Google Sheets.

## Что это такое

docs-agent — это локальный инструмент, который помогает:
- искать документы по MASTER_INDEX;
- открывать и читать документы по Document ID, имени или свободному запросу;
- выполнять рутинную и углубленную диагностику локального окружения;
- сопровождать документный контур проекта без потери управляемости и прозрачности.

## Для кого

- оператор документации;
- владелец или руководитель проекта;
- инженер, поддерживающий локальный CLI;
- ИИ-ассистент, которому нужно быстро подключиться к репозиторию и понять правила работы.

## Текущий baseline

- stage27-reconciled

## Быстрый старт

cd ~/AI/docs-agent
source venv312/bin/activate
bash scripts/operator_start.sh

## Основные entrypoints

Routine:
- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- python agent_cli.py doctor-lite
- python agent_cli.py doctor-lite --json

Live Google/OAuth check:
- python agent_cli.py live-google-probe
- python agent_cli.py live-google-probe --json

Deep:
- python agent_cli.py doctor
- python agent_cli.py doctor --json
- bash scripts/regression_smoke_explain.sh

## Основные CLI-команды

Usable assisted bounded baseline:
- python agent_cli.py status
- python agent_cli.py status --json
- python agent_cli.py repo-state
- python agent_cli.py repo-state --json
- python agent_cli.py doctor
- python agent_cli.py doctor --json
- python agent_cli.py live-google-probe --json
- python agent_cli.py f "DOC-0001"
- python agent_cli.py o "DOC-0002"
- python agent_cli.py artifact-state --file-id "<google_drive_file_id>"
- python agent_cli.py doc-body-only --profile "exchange-docs" --document-type "note" --title "example_title"

Available but non-baseline by default:
- python agent_cli.py r "DOC-0002"
- python agent_cli.py get-file "<google_drive_file_id>"
- python agent_cli.py read-doc "<google_doc_id>"
- python agent_cli.py q "прочитай DOC-0002"

## Ключевая operational-модель

- doctor-lite — основной ежедневный entrypoint
- live-google-probe — ручная read-only проверка live Google/OAuth без cache
- doctor — углубленная диагностика
- doctor-lite/doctor могут проходить через cache-backed MASTER_INDEX lookup; смотри `cache_backed` и `live_google_verified`
- deep checks quota-sensitive
- итоговые выводы по deep path лучше подтверждать reconciliation run при нестабильности

## Основные документы

- docs/INSTALLATION.md
- docs/HUMAN_OPERATOR_GUIDE.md
- docs/TROUBLESHOOTING.md
- docs/AI_AGENT_GUIDE.md
- docs/COMMAND_REFERENCE.md
- docs/CONFIG_REFERENCE.md
- docs/SECURITY_AND_SECRETS.md
- docs/CHANGE_CONTROL.md
- docs/REPOSITORY_RULES.md
- docs/ARCHITECTURAL_NOTES.md
- docs/ROADMAP.md

## Важно

В репозиторий нельзя коммитить:
- config/token.json
- config/client_secret.json
- другие credentials / secrets / tokens
- локальные временные write-test файлы с чувствительным контекстом

## Следующий технический шаг

- MASTER_INDEX cache + memoization

## Поддержка диаграмм и форматов

Текущий repository contour дополнительно формализует поддержку:

- Mermaid
- draw.io / `.drawio`
- SVG
- PNG
- PDF
- Google Slides

Правило:
- Mermaid и `.drawio` — preferred editable sources
- SVG / PNG / PDF — export artifacts
- Google Slides — presentation layer

## Diagram workflow contour

Current supported diagram workflow:

1. maintain source in `Mermaid` or `.drawio`
2. review source before export
3. export into `SVG` / `PNG` / `PDF` as needed
4. use Google Slides as presentation layer when needed
5. retain canonical source separately from publish artifacts
