# Cache Strategy

## Назначение

Stage30 переводит кэширование MASTER_INDEX на более зрелую модель:

- полный fetch листа MASTER_INDEX одним чтением;
- локальный snapshot на диске;
- локальный поиск по всем строкам;
- fallback на live lookup.

## Что изменилось относительно Stage29

Stage29:
- seed / extension cache
- reuse successful lookup

Stage30:
- full sheet fetch
- rows_count
- локальный поиск по полному snapshot
- более полезная база для дальнейшего throttle/memoization слоя

## Поведение

1. При отсутствии или истечении TTL cache выполняется единичное чтение листа MASTER_INDEX.
2. Полный snapshot сохраняется в disk cache.
3. Поиск выполняется локально:
   - по Document ID
   - по Document Name
   - по Link fragment
4. Если cache path не сработал, CLI использует live fallback.

## TTL

- 90 секунд

## Следующий шаг

Stage31:
- in-process memoization
- negative cache
- throttle budget for quota-sensitive paths
