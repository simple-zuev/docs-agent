# Design-First Implementation Packet Overview

## Назначение

Настоящий packet определяет безопасную программу доработки `docs-agent` для встраивания:

- Google Drive API integration
- Google Docs API integration
- Google Sheets API integration
- Diagram Engineering Mode

без конфликта с restored stable baseline на commit `a8ab54b` и без продолжения старой stage30 patch chain.

## Главный продуктовый приоритет

`docs-agent` в первую очередь должен стать корректной и удобной рабочей средой для ИИ-агентов проекта АСТЦВ, которые работают с:

- документным контуром проекта
- Google Drive / Docs / Sheets
- registry и operational sheets
- diagram artifacts и lifecycle states
- локальным repo
- Git/GitHub

## Текущее состояние

### Подтверждено фактами

- current stable baseline: restored stable baseline
- commit: `a8ab54b`
- current `main` считать restored stable baseline
- local `main` и `origin/main` сверены и совпадают
- working tree clean
- routine path рабочий
- `doctor-lite` healthy
- Git/GitHub sync работает
- старая stage30 patch chain продолжаться не должна

### Подтверждено как рабочее

- `bash scripts/operator_start.sh`
- `bash scripts/preflight_check.sh`
- `python agent_cli.py doctor-lite`
- `python agent_cli.py doctor-lite --json`
- `python agent_cli.py status`
- query routes: `f / o / r / q`

## Что является предположением

До снятия runtime/query map как рабочие предположения рассматриваются:

- lookup/cache logic в значительной степени сосредоточена в `agent_cli.py` и связанных helper paths;
- query routes `f / o / r / q` используют существующие MASTER_INDEX-oriented lookup paths;
- полноценного модульного Drive layer в текущем baseline нет;
- Diagram Engineering Mode пока не оформлен как formal execution mode с explicit state discipline.

## Что является рекомендацией

- не смешивать repo safety, Drive integration, mutation layer и diagram automation в одном implementation pass;
- начать с design-first packet и read-only integration;
- не затрагивать deep runtime/cache refactor в первой итерации;
- встроить Diagram Engineering Mode как execution mode внутри текущего агента, а не как отдельный governance fork.

## Основные риски

1. Повторение stage30 сценария через новый patch train.
2. Смешение read-layer и write-layer.
3. Scope explosion первой итерации.
4. Governance fork при неверном встраивании diagram mode.
5. Drift источника истины между local repo, GitHub, Drive list view и registry.
6. Artifact state drift без явной transition model.

## Safe next step

Не менять runtime/code path. Сначала:

1. зафиксировать design packet;
2. снять current runtime and query map;
3. определить canonical Google Drive interaction flow;
4. определить embedding model для Diagram Engineering Mode;
5. ограничить additive implementation scope v1;
6. только затем открыть первую implementation ветку.

## Branch strategy

### Design-first ветка
- `design/drive-diagram-implementation-packet`

### Последующие implementation ветки
- `feature/repo-state-safety`
- `feature/drive-read-layer`
- `feature/drive-bounded-write-layer`
- `feature/artifact-registry-states`
- `feature/diagram-mode-core`
- `feature/diagram-render-qa`

## Что входит в v1

- `repo_state.py`
- read-only Drive layer
- design/spec layer для diagram mode
- explicit artifact state model

## Что не входит в v1

- deep runtime/cache refactor
- full-sheet MASTER_INDEX redesign
- broad Docs rewrites
- wide Sheets batch mutation
- autonomous regeneration loops
- destructive artifact moves
- governance fork

## Packet structure

- `docs/IMPLEMENTATION_PACKET_OVERVIEW.md`
- `docs/CURRENT_RUNTIME_AND_QUERY_MAP.md`
- `docs/GOOGLE_DRIVE_INTERACTION_MODEL.md`
- `docs/ARTIFACT_STATE_MODEL.md`
- `docs/DIAGRAM_ENGINEERING_MODE_EMBEDDING.md`
- `docs/IMPLEMENTATION_PHASES_AND_ACCEPTANCE.md`
- `docs/RISKS_AND_GUARDRAILS.md`
