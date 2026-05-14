# Google API Operating Notes

## Scope

Этот файл описывает практику работы docs-agent с:
- Google Sheets API
- Google Drive API

## Главная проблема

Для docs-agent узким местом является не Drive API, а Sheets API:
- MASTER_INDEX lookup
- repeated column-based searches
- quota-sensitive deep diagnostics

## Правила

1. Routine path должен использовать минимальное число Sheets lookup.
2. Deep path не должен запускаться сериями без паузы.
3. Ошибки:
   - 429
   - RATE_LIMIT_EXCEEDED
   - quota exceeded
   - User rate limit exceeded
   должны интерпретироваться как network/retryable.
4. Такие ошибки не должны деградировать в ложный NotFound.
5. Следующий шаг после текущего патча:
   - добавить MASTER_INDEX cache
   - добавить memoization repeated lookup
   - перейти к one-fetch local filtering

## Практика запуска

Routine:
- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- python agent_cli.py doctor-lite

Live OAuth/network check:
- python agent_cli.py live-google-probe --json

Deep:
- python agent_cli.py doctor
- bash scripts/regression_smoke_explain.sh

## Cooldown

После heavy deep run:
- подождать 60-90 секунд перед новым quota-sensitive run

## Cache-backed vs live checks

- doctor-lite и doctor могут подтверждать MASTER_INDEX через локальный cache.
- `cache_backed=true` полезен для routine readiness, но не доказывает текущий live OAuth/DNS.
- live-google-probe обходит cache и выполняет read-only lookup DOC-0001 в MASTER_INDEX.
- Не запускать live-google-probe сериями без необходимости: это настоящий Google Sheets lookup.
