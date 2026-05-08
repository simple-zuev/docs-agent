# Quota and Rate Limit Policy

## Цель

Снизить вероятность ошибок:
- 429 RATE_LIMIT_EXCEEDED
- User rate limit exceeded
- quota exceeded
- временные transport / SSL / network failures

при работе с Google Sheets API и Google Drive API.

## Основной принцип

Приложение должно жить ниже официальных лимитов API и использовать:
- локальный кэш;
- дедупликацию одинаковых lookup;
- явное разделение routine и deep diagnostic path;
- retry только для retryable ошибок;
- cooldown между quota-sensitive deep runs.

## Практическая политика для docs-agent

### Sheets API

Для приложения считать рабочими лимитами:

- routine budget: до 30 read/min/user
- deep budget: до 45 read/min/user
- hard guardrail: начиная с 50 read/min/user включать локальный cooldown
- doctor-lite: максимум 1 обязательный MASTER_INDEX lookup
- doctor: максимум 1 обязательный MASTER_INDEX lookup + deep smoke orchestration

### Drive API

Для приложения считать рабочими лимитами:

- soft budget: до 100 req / 60 sec / user
- рабочий подход: не приближаться к официальным максимумам без необходимости

## Retry policy

Retry разрешен только для:
- 429
- quota exceeded
- RATE_LIMIT_EXCEEDED
- User rate limit exceeded
- SSL / временных транспортных ошибок
- временных network failures

Не retry:
- реальный NotFound
- явный Permission denied / auth failure
- некорректный запрос / validation failure

## Backoff policy

Использовать truncated exponential backoff с jitter:

- attempt 1: immediately
- attempt 2: 1-2 sec + jitter
- attempt 3: 4-5 sec + jitter
- attempt 4: 8-10 sec + jitter
- attempt 5: 16-20 sec + jitter

Практический ceiling:
- 32 sec

## Cooldown policy

После heavy quota-sensitive deep run:
- не запускать новый deep diagnostic 60-90 sec

Routine path:
- doctor-lite допустим чаще, но должен работать через кэш и минимальное число lookup.

## Классификация ошибок

Если в ошибке встречается что-то из:
- 429
- quota exceeded
- RATE_LIMIT_EXCEEDED
- User rate limit exceeded

то итоговая классификация должна быть:
- diagnosis = network
- retryable = true
- network_related = true

Такой кейс не должен маскироваться под:
- internal
- ложный NotFound

## Следующий обязательный шаг

Следующая итерация должна добавить:
1. MASTER_INDEX cache with TTL 60-120 sec
2. in-process memoization for repeated lookup
3. one-fetch local search over MASTER_INDEX instead of repeated sequential API lookups
