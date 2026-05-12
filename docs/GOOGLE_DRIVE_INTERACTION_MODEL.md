# Google Drive Interaction Model

## Назначение

Документ определяет canonical single-source flow для работы `docs-agent` с:

- Google Drive API
- Google Docs API
- Google Sheets API

Цель — обеспечить retrieval-first и verification-first дисциплину без конфликтов с restored stable baseline и без повторения stage30-подобных сценариев.

## Главный принцип

Работа с Google Drive объектами не должна строиться по схеме:

`нашли что-то похожее -> сразу пишем`

Правильная модель:

`intent -> candidate retrieval -> identity verification -> placement verification -> read -> decision -> bounded mutation -> post-mutation verification`

## Подтверждено фактами

- В текущем main уже присутствует рабочий read-oriented surface для docs-agent, однако canonical interaction model все еще полезна как design/reference layer.
- Текущий baseline чувствителен к risky runtime/cache layering.
- Любые write operations должны вводиться позже read-only слоя.

## Что является предположением

- Для задач docs-agent значимы не только content reads, но и placement/lifecycle checks.
- Registry/log/state verification для артефактов будет опираться и на Sheets, и на Drive metadata.
- Drive list view может давать stale или delayed картину и не должен считаться единственным источником истины.

## Canonical flow

### 1. Task intent classification
Определить тип задачи:
- locate
- verify
- read
- reconcile
- bounded update
- append
- package artifact
- state update
- move-check
- duplicate-check

### 2. Candidate retrieval
Получить кандидатов по:
- object id
- title/name
- mime type
- expected parent
- registry hints
- contextual filters

### 3. Identity verification
Подтвердить:
- object id
- object type
- exact or acceptable title match
- whether object is file or folder
- whether object is Doc / Sheet / other artifact

### 4. Placement verification
Подтвердить:
- current parent(s)
- source folder
- target folder
- expected folder placement
- move vs copy ambiguity
- duplicate ambiguity

### 5. Read phase
Прочитать только нужный bounded scope:
- file metadata
- folder placement
- Google Doc text
- Google Sheet structure / range / row
- state fields / registry row / lifecycle fields

### 6. Decision phase
Решение должно быть одним из:
- no-op
- bounded read complete
- bounded update required
- append required
- reconciliation required
- suspected stale view
- suspected delayed propagation
- permission issue
- wrong object

### 7. Mutation phase
Разрешена только минимальная bounded mutation:
- bounded Docs patch
- bounded Sheets append
- bounded Sheets update

Нельзя делать:
- broad rewrite
- batch mutation by default
- destructive move/copy/delete flows without explicit design

### 8. Post-mutation verification
После mutation обязательно проверить:
- тот же object id
- expected placement
- mutation applied
- state/registry consistent
- next safe step explicit

## Error taxonomy

Нужно различать:
- NotFound
- stale ID
- wrong object
- wrong parent
- permission issue
- delayed propagation
- stale list view
- quota exceeded / rate limit
- retryable platform issue

### Правило для 429/quota
`429 / RATE_LIMIT_EXCEEDED / quota exceeded` не трактовать как ложный `NotFound`.

## Mutation discipline

Для любой mutation операции:
1. verify identity
2. verify placement
3. mutate minimally
4. verify result
5. log state / result / next safe step

## Read-only first rule

Первая implementation итерация должна содержать только:
- auth/session init
- search files/folders
- get metadata
- get parents
- list folder contents
- read Docs
- read Sheets

Без mutation layer.

## Safe next step

После фиксации interaction model безопасный следующий шаг — implementation ветка `feature/drive-read-layer`, без bounded write layer.