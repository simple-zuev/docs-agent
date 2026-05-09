# Project Status

## Текущий baseline

- restored stable baseline
- commit: a8ab54b
- current main считать restored stable baseline

## Git status

- репозиторий инициализирован
- GitHub remote подключен
- ветка main синхронизирована
- onboarding documentation package добавлен

## Что подтверждено

### Routine path
Подтверждено как рабочее:
- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- python agent_cli.py doctor-lite
- python agent_cli.py status
- основные query routes f / o / r / q

### Documentation
Подтверждено наличие:
- README.md
- human/operator docs
- AI agent docs
- troubleshooting docs
- config/security/change-control docs
- architectural notes
- roadmap

### Git / repository
Подтверждено:
- baseline сохранен в GitHub
- curated commits выполнены
- чувствительный config не попал в git

## Что остается чувствительным

### Deep diagnostic path
- python agent_cli.py doctor
- bash scripts/regression_smoke_explain.sh

Эти сценарии остаются quota-sensitive и могут давать нестабильный результат при внешнем давлении на Google APIs.

## Главные ограничения

1. Главная внешняя зависимость — Google Sheets API
2. Главный quota-sensitive объект — MASTER_INDEX
3. Deep diagnostic path дороже routine path
4. При нестабильном deep результате нужен reconciliation run
5. config/ остается строго локальным контуром

## Практический вывод

Система готова для:
- controlled daily use
- routine operations
- controlled Git-based evolution

Система пока не идеальна для:
- частых серийных deep checks
- безоглядочного масштабирования без clean cache refactor

## Следующий инженерный приоритет

- не продолжать patching старого stage30 runtime path
- подготовить clean refactor plan для MASTER_INDEX cache в отдельной ветке
- сначала зафиксировать branch strategy
- выписать карту текущих lookup/cache функций
- определить canonical single-source cache flow
- потом делать clean implementation

## Stage29 note

- added MASTER_INDEX disk cache path with TTL-based reuse
- doctor-lite confirmed healthy with cache-backed MASTER_INDEX lookup

## Baseline restore note

Current stable baseline:
- commit a8ab54b

What happened:
- experimental stage30 runtime cache activation path was attempted
- runtime issues were discovered during duplicate-removal and full-sheet cache activation
- working agent_cli.py was restored from local backup
- hotfix was pushed to origin/main
- documentation note for restored baseline was committed in GitHub

Current recommendation:
- treat current main as restored stable baseline
- do not continue patching stage30 runtime on top of the current file state
- if full-sheet cache work resumes, do it as a clean refactor in a separate iteration
- prefer a separate branch for any new serious cache/runtime work

Stable now:
- GitHub sync
- onboarding and operations docs
- routine path via doctor-lite
- restored runtime baseline

Not fully completed:
- full-sheet stage30 runtime cache activation
- canonical clean refactor for MASTER_INDEX cache flow
