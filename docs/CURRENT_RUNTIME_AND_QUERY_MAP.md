# Current Runtime and Query Map

## Назначение

Документ фиксирует текущее состояние runtime/query surface `docs-agent` до начала доработок. Его задача — дать безопасную карту текущих путей исполнения, а не перепридумать архитектуру.

## Подтверждено фактами

### Baseline and repo state
- current stable baseline: restored stable baseline
- commit: `a8ab54b`
- local `main` и `origin/main` сверены и совпадают
- working tree clean

### Подтвержденные entrypoints
- `bash scripts/operator_start.sh`
- `bash scripts/preflight_check.sh`
- `python agent_cli.py doctor-lite`
- `python agent_cli.py doctor-lite --json`
- `python agent_cli.py status`

### Подтвержденные query routes
- `f`
- `o`
- `r`
- `q`

## Что пока является предположением

До code mapping как рабочие предположения:

- query routes и lookup logic в значительной степени сосредоточены в `agent_cli.py`;
- MASTER_INDEX path продолжает быть ключевым объектом lookup/runtime flow;
- часть cache-related logic и protection logic может быть смешана с query resolution path;
- точные boundaries между route dispatch, lookup helpers и cache helpers пока не зафиксированы в отдельном design map.

## Что должно быть снято до implementation

### 1. Entry map
Нужно зафиксировать:
- какие CLI команды являются основными для routine path;
- где route dispatch начинается;
- где route dispatch переходит в lookup layer;
- где route dispatch переходит в read/open/status behavior.

### 2. Query route map
По каждому из routes `f / o / r / q` нужно определить:
- purpose
- входной формат
- target resolution path
- зависимость от MASTER_INDEX
- возможные cache touchpoints
- возможные mutation touchpoints
- verification points

### 3. Lookup map
Нужно снять:
- текущие функции поиска документа
- текущие функции resolution по ID / title / query
- fallback logic
- error classification path
- coupling with Google APIs

### 4. Cache map
Нужно снять:
- какие cache-related helpers уже есть
- где используется MASTER_INDEX cache path
- где есть runtime-sensitive reuse
- где начинается риск повторения stage30 chain
- какие места нельзя трогать в первой итерации

### 5. Safety map
Нужно определить:
- unsafe mutation points
- mixed read/write paths
- fragile runtime areas
- routes, которые нельзя расширять без отдельной ветки и отдельной верификации

## Практическая цель карты

Нужна карта, отвечающая на вопросы:

1. Где именно живет текущая lookup logic?
2. Где query routes принимают решение?
3. Где cache coupling уже есть?
4. Где можно additively встроить Drive read layer?
5. Где можно встроить Diagram Engineering Mode как execution mode без governance fork?

## Ограничения

При снятии карты:
- не менять код;
- не делать refactor;
- не продолжать stage30 patch chain;
- не вводить новые runtime behaviors;
- не делать speculative architecture rewrite.

## Рекомендуемый deliverable

В следующей итерации документ должен быть дополнен фактической картой:

### Section A — Confirmed runtime facts
- route dispatch points
- entrypoints
- current helpers

### Section B — Lookup/cache graph
- functions
- call flow
- dependencies
- risk points

### Section C — Safe embedding zones
- where Drive read layer can be inserted
- where bounded write layer can be inserted later
- where Diagram Mode can be attached as execution path

### Section D — Do not touch zones
- fragile paths
- stage30-sensitive zones
- mixed cache/runtime areas

## Safe next step

После фиксации этого документа следующим безопасным шагом должна быть не реализация, а дополнение его фактической картой функций и route flow на основе repo inspection.