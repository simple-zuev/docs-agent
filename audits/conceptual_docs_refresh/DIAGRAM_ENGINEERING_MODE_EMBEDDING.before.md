# Diagram Engineering Mode Embedding

## Назначение

Документ определяет, как Diagram Engineering Mode должен встраиваться в `docs-agent` без governance fork и без конфликта с restored stable baseline.

## Главный принцип

Diagram Engineering Mode — это не отдельный агент.

Это специальный execution mode внутри текущего `docs-agent`, который:
- работает в controlled operator model;
- использует тот же safety discipline;
- использует тот же repo/Git/Drive reconciliation подход;
- не создает отдельную governance logic.

## Подтверждено фактами

- Для diagram tasks уже существует явная потребность в source/preview/QA/state workflow.
- Preview не должен считаться финальным результатом по умолчанию.
- Diagram task требует separate semantic and visual control.

## Что является предположением

- Текущий baseline не содержит formal diagram execution route как отдельный documented mode.
- Для diagram lifecycle потребуется связь с artifact registry и explicit states.

## Why no governance fork

Если сделать Diagram Engineering Mode отдельным автономным агентом, возникнут:
- отдельные правила принятия решений;
- отдельная state logic;
- отдельная safety model;
- отдельная mutation discipline.

Это создаст governance fork и конфликт с existing operator/runtime discipline.

## Correct embedding model

Diagram Engineering Mode должен быть встроен как:
- task classification route;
- specialized execution path;
- artifact/state aware flow;
- retrieval-first and existing-artifact-first behavior.

## Trigger conditions

Mode должен активироваться, если задача распознана как:
- diagram task
- architecture diagram task
- integration flow task
- governance flow task
- participant flow task
- diagram QA task
- artifact package task
- preview/remediation/recovery task

## Pipeline

Для diagram task execution mode обязан проходить стадии:

1. task detection
2. diagram classification
3. source retrieval
4. semantic definition
5. structural spec
6. wireframe layout
7. routing plan
8. label budget check
9. source generation
10. preview generation
11. semantic QA
12. visual QA
13. state assignment
14. artifact package output

## Classification contract

Для каждой схемы mode обязан определить:
- `diagram_type`
- `diagram_intent`
- `complexity_class`
- `main_flow_direction`
- `target_artifact_state`

Примеры diagram_type:
- Participant Flow
- Architecture Context
- Integration Flow
- Governance Flow

Complexity:
- Low
- Medium
- High

## Key rules

Diagram mode обязан соблюдать:
- Five-Second Comprehension Rule
- Node Integrity Rule
- One Figure One Thought Rule
- Orthogonal Routing Default Rule
- Perpendicular Entry Rule
- Anti-Collision Rule
- Single Direction Rule
- One Main Story Rule
- Zone Balance Rule
- Support and External Separation Rule
- Semantic Pass Does Not Equal Visual Pass Rule
- Wireframe Before Preview Rule
- Layout Budget Rule
- Consecutive Preview Failure Escalation Rule
- Single Language Rule

## Mandatory quality separation

### Semantic QA
Проверяет:
- смысл
- корректность сущностей
- соответствие source-of-truth
- логическую полноту

### Visual QA
Проверяет:
- читаемость
- collisions
- routing
- padding
- visual hierarchy
- five-second comprehension

### Rule
Semantic pass не равен visual pass.

## Wireframe rule

Для `Medium` и `High` complexity diagrams preview запрещен без wireframe/layout stage.

## Recovery rule

После двух failed previews подряд:
- normal regeneration loop запрещен;
- mode фиксирует root cause;
- входит в recovery mode;
- требует revised layout/wireframe remediation;
- блокирует normal preview generation до recovery completion.

## Artifact package contract

Diagram task output обязан включать:
- source
- preview
- semantic verdict
- visual verdict
- preview state
- release readiness
- next safe step

## Safe integration boundary

В первой итерации Diagram Engineering Mode должен добавляться как:
- classification logic
- semantic/structural/wireframe/spec discipline
- artifact package contract

А не как full autonomous rendering engine.

## Safe next step

После фиксации embedding model безопасный следующий шаг — design and limited implementation of `diagram_mode.py`, `diagram_states.py` and `diagram_rules.py` boundaries, без aggressive render automation.