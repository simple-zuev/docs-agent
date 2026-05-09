# Change Control

## Цель

Определить, как вносить изменения в docs-agent, не ломая рабочий baseline.

## Приоритеты изменений

Высокий приоритет:
- исправления, повышающие стабильность routine path
- исправления безопасности
- quota/rate-limit handling
- cache/memoization для MASTER_INDEX

Средний приоритет:
- улучшение explainability
- улучшение operator docs
- улучшение AI onboarding docs

Низкий приоритет:
- косметика
- вторичные refactors без эффекта на стабильность

## Правила изменений

1. Сначала диагностировать.
2. Потом фиксировать причину.
3. Потом делать минимальный патч.
4. Потом сохранять summary в audits/.
5. Потом только commit/push.

## Before commit checklist

- git status
- нет ли secrets
- нет ли config/
- понятно ли, зачем нужны новые файлы
- не добавляются ли случайные test artifacts

## After change checklist

- python -m py_compile agent_cli.py
- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- при необходимости python agent_cli.py doctor-lite --json
- deep smoke только по необходимости

## Рациональные замечания

1. Не надо спешить с большими рефакторингами.
2. Самый полезный следующий шаг — убрать лишнюю нагрузку на MASTER_INDEX.
3. Лучше 3 маленьких понятных коммита, чем 1 большой и шумный.
