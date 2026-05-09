# Cache Strategy

## Цель

Снизить quota pressure на Google Sheets API без ломки текущего CLI-контракта.

## Что сделано на текущем этапе

В `agent_cli.py` добавлен минимальный lookup cache для `find_doc_any_payload()`:
- кэширует только успешные результаты;
- TTL = 90 секунд;
- хранится локально в `cache/agent_cli/`;
- используется для repeat lookup по одинаковому query.

## Почему это полезно

Это уменьшает повторные обращения к:
- `MASTER_INDEX`
- связанным lookup стратегиям

Особенно полезно для:
- `doctor-lite`
- `doctor`
- `find/open/read`, если в коротком окне повторяются одинаковые запросы

## Ограничения

1. Это не полный `MASTER_INDEX` cache.
2. Это не memoization на уровне всего `docs_agent.py`.
3. Ошибочные и неуспешные результаты не кэшируются.
4. Deep path все еще может быть quota-sensitive.

## Следующий шаг

Следующее улучшение:
- кэш самого `MASTER_INDEX` диапазона
- one-fetch local filtering
- in-process memoization
