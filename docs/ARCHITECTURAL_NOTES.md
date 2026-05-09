# Architectural Notes

## Общая идея

Архитектурно docs-agent — это локальный orchestration CLI над Google APIs и локальными operational scripts.

## Основные слои

CLI layer:
- agent_cli.py

Integration layer:
- docs_agent.py
- частично docs_agent_v2.py

Operations layer:
- scripts/

Evidence and audit layer:
- audits/

Documentation layer:
- docs/

## Ключевое ограничение архитектуры

Главная внешняя зависимость:
- Google Sheets API

Главный quota-sensitive объект:
- MASTER_INDEX

## Главный технический долг

Сейчас lookup path еще слишком чувствителен к repeated API calls.

## Рациональные предложения

1. Добавить MASTER_INDEX cache
2. Добавить in-process memoization
3. По возможности перейти от repeated strategy lookups к one-fetch local filtering
4. Оставить doctor-lite дешевым и стабильным
