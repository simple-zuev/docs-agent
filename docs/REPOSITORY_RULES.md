# Repository Rules

## Структура

- agent_cli.py — основной CLI
- docs_agent.py — основной интеграционный слой
- docs_agent_v2.py — альтернативный draft / расширенный вариант
- scripts/ — operational и regression scripts
- audits/ — артефакты проверок и status snapshots
- docs/ — документация
- backups/ — локальные backup файлы
- config/ — локальный чувствительный контур, не коммитится

## Что считается baseline

В baseline входят:
- рабочий CLI
- ключевые scripts
- operator docs
- AI docs
- curated audit/status files
- requirements

## Что не должно попадать в baseline без review

- локальные write-tests
- ad-hoc experiments
- промежуточные scratch scripts
- чувствительный config
- временные токены
- случайные выгрузки

## Правила Git

1. Не коммитить secrets
2. Не коммитить config/
3. Коммитить только curated changes
4. Перед push проверять git status
5. Перед add-review смотреть, нет ли локальных sensitive файлов
6. Для noisy artifacts использовать .gitignore

## Рациональные замечания

1. audits/ полезен, но требует дисциплины.
2. Если коммитить слишком много промежуточных артефактов, baseline станет трудно читаемым.
3. Документация должна оставаться входной точкой, а не свалкой статусов.
