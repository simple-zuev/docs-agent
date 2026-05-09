# Cache Strategy

## Назначение

Stage29 вводит кэш для MASTER_INDEX с целью:

- уменьшить давление на Google Sheets API;
- сократить число повторных lookup;
- повысить устойчивость doctor-lite и routine path;
- сохранить fallback на live lookup.

## Что кэшируется

На текущем этапе:
- локальный snapshot данных MASTER_INDEX для повторных lookup;
- результаты успешных live lookup расширяют локальный cache set.

## Поведение

1. CLI сначала пытается ответить из cache.
2. Если cache отсутствует или query не найден, выполняется live lookup.
3. Успешный live lookup добавляется в cache.
4. При quota/rate-limit ошибках fallback-классификация должна быть:
   - diagnosis = network
   - retryable = true
   - network_related = true

## TTL

Текущий TTL:
- 90 секунд

## Ограничения текущей реализации

Stage29 — это переходный шаг:
- есть cache path;
- есть disk cache;
- есть reuse successful lookup;
- но это ещё не полный one-fetch всего MASTER_INDEX через единичное чтение листа.

## Следующий шаг

Stage30:
- единичное чтение полного MASTER_INDEX;
- полноценный local filtering по всем строкам;
- negative cache;
- explicit cooldown/throttle budget.
