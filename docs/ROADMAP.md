# Roadmap

## Текущий этап

- baseline сохранен в git и GitHub
- routine path стабилизирован
- deep path объясним, но quota-sensitive
- документационный пакет добавлен

## Ближайшие шаги

1. MASTER_INDEX cache + memoization
- stage28 adds minimal lookup cache in agent_cli for repeated find_doc_any queries
2. Улучшение deep diagnostics
3. Курирование audits
4. Нормализация docs_agent_v2

## Рациональные предложения

1. Не расширять функциональность быстрее, чем стабилизируется доступ к MASTER_INDEX
2. Не усложнять baseline без необходимости
3. Сначала reliability, потом features

## After Stage29

Completed:
- disk-backed MASTER_INDEX cache path

Next:
- full sheet fetch
- local filtering over full registry
- negative cache
- explicit throttle budget
