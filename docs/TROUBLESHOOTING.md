# Troubleshooting

## healthy

Значение:
- система выглядит работоспособной

Действие:
- можно продолжать работу

## network

Симптомы:
- network
- retryable = true
- 429
- RATE_LIMIT_EXCEEDED
- quota exceeded

Значение:
- quota pressure
- временный внешний сбой
- нестабильность Google API
- транспортная проблема

Действие:
1. Подождать 60-90 секунд
2. Повторить команду
3. Не запускать серийно deep checks
4. При повторении смотреть doctor --json

## auth

Значение:
- проблема доступа/авторизации

Действие:
- проверить локальный config/
- проверить токены
- проверить OAuth credentials
- проверить доступ к Google объектам

## not_found

Значение:
- документ или объект реально не найден либо запрос задан неверно

Действие:
- проверить Document ID
- проверить имя документа
- сначала выполнить find-doc-any

## internal

Значение:
- внутренний сбой CLI, smoke path или script logic

Действие:
- повторить с --json
- запустить bash scripts/regression_smoke_explain.sh
- посмотреть audits/

## doctor-lite зеленый, doctor красный

Значение:
- routine path жив
- deep path quota-sensitive или есть проблема в smoke/check flow

Действие:
- не считать систему сломанной автоматически
- сделать cooldown
- повторить deep run позже
- использовать reconciliation logic

## doctor-lite зеленый, но live_google_verified = false

Значение:
- routine path прошел через cache-backed MASTER_INDEX lookup
- live Google/OAuth не был подтвержден этим запуском

Действие:
- если нужна только routine readiness, можно продолжать
- если нужна live-проверка, выполнить python agent_cli.py live-google-probe --json
- если live-google-probe падает как auth/network, разбирать именно этот диагностический результат

## Git push / auth problem

Действие:
- проверить remote
- использовать PAT token вместо GitHub password
- убедиться, что repo существует

## Секреты показаны в терминале или чате

Значение:
- считать их потенциально скомпрометированными

Действие:
- перевыпустить секреты
- удалить старый token
- пройти OAuth заново
