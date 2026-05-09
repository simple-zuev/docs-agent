# Config Reference

## Важно

Этот документ описывает назначение локального config/, но не должен содержать реальные secrets.

## Локальные файлы

Ожидаются:
- config/config.yml
- config/client_secret.json
- config/token.json

## Назначение

config.yml хранит:
- пути
- имена ключевых папок
- идентификаторы документов и листов
- safety settings
- runtime settings

client_secret.json:
- OAuth client credentials для локальной авторизации

token.json:
- локальный access/refresh token для Google API

## Правила

1. config/ не коммитится
2. client_secret.json не публикуется
3. token.json не публикуется
4. при утечке секреты ротируются

## Важные поля в config.yml

safety:
- mode
- default_dry_run
- forbid_master_index_write
- forbid_delete

documents:
- master_index_spreadsheet_id
- master_index_sheet_name
- change_log_spreadsheet_id
- change_log_sheet_name

runtime:
- export_dir
- reports_dir
- cache_dir

## Рекомендации

1. Держать mode=readonly как baseline
2. Не менять safety flags без осознанной причины
3. Не хранить secrets вне локального контура
