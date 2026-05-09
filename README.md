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

- restored stable baseline
- commit: a8ab54b
- current main считать restored stable baseline

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

Deep:
- python agent_cli.py doctor
- python agent_cli.py doctor --json
- bash scripts/regression_smoke_explain.sh

## Основные CLI-команды

- python agent_cli.py status
- python agent_cli.py status --json
- python agent_cli.py f "DOC-0001"
- python agent_cli.py o "DOC-0002"
- python agent_cli.py r "DOC-0002"
- python agent_cli.py q "прочитай DOC-0002"

## Ключевая operational-модель

- doctor-lite — основной ежедневный entrypoint
- doctor — углубленная диагностика
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
- docs/PROJECT_STATUS.md
- docs/KNOWN_LIMITATIONS.md
- docs/CACHE_STRATEGY.md

## Важно

В репозиторий нельзя коммитить:
- config/token.json
- config/client_secret.json
- другие credentials / secrets / tokens
- локальные временные write-test файлы с чувствительным контекстом

## Следующий технический шаг

- не продолжать старую цепочку stage30-патчей поверх текущего file state
- следующий серьезный шаг делать только как clean refactor
- предпочтительно в отдельной ветке
- сначала зафиксировать branch strategy, карту lookup/cache функций и canonical single-source cache flow
