# Project Status

## Текущий baseline

- main after mock operator backend contract baseline through PR #137

## Git status

- репозиторий инициализирован
- GitHub remote подключен
- ветка main синхронизирована
- onboarding documentation package добавлен
- local test gates доступны через `make test-cli`, `make test-backend`, `make test-all`

## Что подтверждено

### Routine path
Подтверждено как рабочее:
- bash scripts/operator_start.sh
- bash scripts/preflight_check.sh
- python agent_cli.py doctor-lite
- python agent_cli.py live-google-probe --json
- python agent_cli.py status
- основные lookup/navigation routes f / o
- helper route q доступен, но не заменяет direct bounded inspection flow

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

### Operator backend
Подтверждено:
- FastAPI mock runtime exposes health, task list/details, task create, task update, history list, and history append routes
- backend task responses include documented trace fields: created/updated metadata, authority binding, Drive context, approval state, notes, and history count
- backend history responses include actor, authority, Drive context, approval, timestamp, and result-state trace fields
- task status changes append history events
- missing-task and validation error envelopes are pinned by API contract tests
- backend tests run through `make test-backend`

Ограничения:
- backend readiness is mock-runtime only
- production persistence is not complete
- live Google-backed task execution is not complete
- live Google Drive / Google Docs mutation behavior is not expanded by this baseline
- read-doc, get-file, and read-doc-from-query remain degraded by default

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
- mock operator backend contract iteration

Система пока не идеальна для:
- частых серийных deep checks
- безоглядочного масштабирования без cache/memoization
- production backend persistence or live Google-backed task execution
- live Google-backed operator task execution

## Следующий инженерный приоритет

- MASTER_INDEX cache + memoization
- stage28 adds minimal lookup cache in agent_cli for repeated find_doc_any queries

## Stage29 note

- added MASTER_INDEX disk cache path with TTL-based reuse
- doctor-lite confirmed healthy with cache-backed MASTER_INDEX lookup

## Live Google probe note

- added read-only `live-google-probe`
- the probe bypasses MASTER_INDEX cache and verifies live Google/OAuth through DOC-0001 lookup
- this does not change Google Drive / Google Docs mutation behavior
- read-doc, get-file, and read-doc-from-query remain degraded/non-baseline by default

## Baseline restore note

Current stable baseline:
- commit 2e04da3

What happened:
- experimental stage30 runtime cache activation path was attempted
- runtime issues were discovered during duplicate-removal and full-sheet cache activation
- working agent_cli.py was restored from local backup
- hotfix was pushed to origin/main

Current recommendation:
- treat current main as restored stable baseline
- do not continue patching stage30 runtime on top of the current file state
- if full-sheet cache work resumes, do it as a clean refactor in a separate iteration

Stable now:
- GitHub sync
- onboarding and operations docs
- routine path via doctor-lite
- restored runtime baseline
- local CLI and operator backend test gates
- mock backend API contract coverage

Not fully completed:
- full-sheet stage30 runtime cache activation
- live backend persistence
- live authority / Drive resolution inside backend task handlers
