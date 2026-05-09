# Implementation Phases and Acceptance

## Назначение

Документ определяет поэтапную последовательность реализации, deliverables, acceptance criteria и verification discipline для safe extension `docs-agent`.

## Главный принцип

Реализация идет не как один большой upgrade, а как controlled program of changes.

Последовательность обязательна:
1. design-first packet
2. repo safety
3. Drive read-only
4. bounded write layer
5. artifact state model
6. diagram mode core
7. render and QA

## Phase 0 — Design-first packet

### Deliverables
- `docs/IMPLEMENTATION_PACKET_OVERVIEW.md`
- `docs/CURRENT_RUNTIME_AND_QUERY_MAP.md`
- `docs/GOOGLE_DRIVE_INTERACTION_MODEL.md`
- `docs/ARTIFACT_STATE_MODEL.md`
- `docs/DIAGRAM_ENGINEERING_MODE_EMBEDDING.md`
- `docs/IMPLEMENTATION_PHASES_AND_ACCEPTANCE.md`
- `docs/RISKS_AND_GUARDRAILS.md`

### Acceptance criteria
- current facts explicitly separated from assumptions and recommendations;
- branch strategy fixed;
- canonical Drive interaction flow fixed;
- diagram embedding model fixed;
- v1 scope limited;
- non-goals explicitly listed.

## Phase 1 — Repo safety foundation

### Recommended branch
- `feature/repo-state-safety`

### Target
Реализовать `repo_state.py` и safety envelope для future mutations.

### Minimum scope
- verify repo path
- git status snapshot
- local vs origin reconciliation
- changed files inspection
- branch safety checks

### Acceptance criteria
- агент умеет доказать, что работает в корректном repo;
- агент умеет показать local vs origin state;
- unsafe mutation без reconciliation блокируется;
- working baseline не затронут.

## Phase 2 — Google Drive read-only layer

### Recommended branch
- `feature/drive-read-layer`

### Target
Реализовать `drive_api.py` только в read-only режиме.

### Minimum scope
- auth/session init
- search files/folders
- get metadata
- get parents
- list folder contents
- read Google Doc text
- read Sheet structure/ranges/rows

### Acceptance criteria
- можно найти файл/папку;
- можно верифицировать identity;
- можно верифицировать parent/placement;
- можно прочитать Docs;
- можно прочитать Sheets;
- различаются NotFound / stale / permission / quota cases.

## Phase 3 — Google Drive bounded write layer

### Recommended branch
- `feature/drive-bounded-write-layer`

### Target
Добавить только bounded mutation.

### Minimum scope
- bounded Docs patch update
- bounded Sheets append
- bounded Sheets update
- post-mutation verification

### Explicit exclusions
- broad rewrite
- batch mutation by default
- schema-changing spreadsheet operations
- wide artifact move/copy flows

### Acceptance criteria
- mutation всегда bounded;
- identity and placement verified before mutation;
- post-mutation verification mandatory;
- no blind retries.

## Phase 4 — Artifact registry states

### Recommended branch
- `feature/artifact-registry-states`

### Target
Ввести explicit lifecycle states.

### Minimum scope
- preview state
- semantic verdict
- visual verdict
- release readiness
- recovery mode
- allowed transitions

### Acceptance criteria
- state surface explicit;
- invalid transitions blocked or detectable;
- diagram artifacts no longer rely on implicit readiness.

## Phase 5 — Diagram mode core

### Recommended branch
- `feature/diagram-mode-core`

### Target
Встроить Diagram Engineering Mode как execution route.

### Minimum scope
- task detection
- diagram classification
- semantic definition
- structural spec
- wireframe/layout requirement
- routing plan
- label budget check
- artifact package contract

### Acceptance criteria
- diagram tasks classified explicitly;
- medium/high complexity diagrams require wireframe stage;
- semantic and visual control are separate;
- artifact package fields explicit.

## Phase 6 — Diagram render and QA

### Recommended branch
- `feature/diagram-render-qa`

### Target
Добавить controlled source/render/QA layer.

### Minimum scope
- Mermaid source generation
- draw.io-compatible structural spec generation
- preview handling
- semantic QA checklist
- visual QA checklist
- recovery mode enforcement

### Acceptance criteria
- preview != release by default;
- semantic pass separate from visual pass;
- after two failed previews normal regeneration loop blocked;
- remediation path explicit.

## Verification discipline

После каждого meaningful code change:
- `python -m py_compile ...`
- `bash scripts/operator_start.sh`
- `bash scripts/preflight_check.sh`
- при необходимости `python agent_cli.py doctor-lite --json`

### Additional smoke by phase

#### Drive read-only
- search smoke
- metadata smoke
- docs read smoke
- sheets read smoke

#### bounded write
- bounded docs patch smoke
- bounded sheet append/update smoke
- post-write verification smoke

#### diagram mode
- classification smoke
- state transition smoke
- recovery smoke

## Not in v1

- deep runtime/cache refactor
- full-sheet MASTER_INDEX redesign
- continuation of stage30 chain
- broad Docs rewrites
- wide Sheets batch mutation
- autonomous preview regeneration loops
- destructive artifact migrations
- governance fork

## Safe next step

После завершения design packet безопасный следующий шаг — открыть `feature/repo-state-safety`, а не переходить сразу к Drive writes или diagram rendering.