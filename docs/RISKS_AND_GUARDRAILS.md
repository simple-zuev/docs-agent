# Risks and Guardrails

## Назначение

Документ фиксирует основные риски программы доработки `docs-agent` и guardrails, которые не должны нарушаться при реализации Google Drive integration и Diagram Engineering Mode.

## Confirmed facts

- current stable baseline = restored stable baseline
- commit: `a8ab54b`
- старая stage30 patch chain не должна продолжаться
- `main` нельзя использовать как рабочую ветку для этой программы изменений
- local vs origin reconciliation обязателен перед mutation

## Main risks

### 1. Stage30 recurrence risk
Риск повторить историю broken runtime/cache patch path через новый многошаговый patch train.

### 2. Read-write mixing risk
Риск смешать retrieval, mutation, registry state changes и diagram automation в одной итерации.

### 3. Scope explosion risk
Риск попытаться одновременно сделать:
- repo safety
- Drive integration
- bounded writes
- artifact state model
- diagram mode
- render/QA

### 4. Governance fork risk
Риск встроить Diagram Engineering Mode как отдельный агент или отдельную decision logic.

### 5. Truth drift risk
Риск считать GitHub, local repo, Drive list view или registry единственным источником истины.

### 6. Artifact state drift risk
Риск работать со схемами и package artifacts без explicit states и transitions.

### 7. Blind mutation risk
Риск делать Docs/Sheets/Drive mutations без identity and placement verification.

## Guardrails

### Guardrail 1. No stage30 continuation
Нельзя продолжать старую stage30 patch chain.

### Guardrail 2. No direct main writes
Нельзя писать в `main` напрямую.

### Guardrail 3. Design-first before code
Сначала design packet, потом первая implementation ветка.

### Guardrail 4. Local-first reconciliation
Перед любой записью в GitHub:
- verify repo path
- check local HEAD
- fetch origin
- compare local vs origin
- inspect changed files

### Guardrail 5. Read-only before write
Сначала Drive read-only layer, потом bounded writes.

### Guardrail 6. Verification-first Drive mutations
Любая mutation требует:
1. identity verification
2. placement verification
3. bounded mutation
4. post-mutation verification

### Guardrail 7. No broad rewrites by default
Нельзя делать broad Docs rewrites или wide Sheets mutations как default path.

### Guardrail 8. Diagram mode without governance fork
Diagram Engineering Mode должен быть execution mode inside current agent, а не отдельный governance branch.

### Guardrail 9. Explicit state model before trust in previews
Preview нельзя считать финальным результатом без explicit states and verdicts.

### Guardrail 10. Recovery mode after repeated preview failures
После двух failed previews подряд normal regeneration loop блокируется.

## Required pre-mutation commands

```bash
git status
git log --oneline --decorate -n 5
git rev-parse HEAD
git fetch origin
git rev-parse origin/main
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
```

Если есть локальные изменения, дополнительно:

```bash
git diff --stat
git diff --name-status
```

## Retry guardrail

`429 / RATE_LIMIT_EXCEEDED / quota exceeded` трактуются как retryable/platform issue.

Их нельзя автоматически классифицировать как `NotFound`.

## Safe next step

После фиксации guardrails следующая безопасная реализация — `feature/repo-state-safety`, а не runtime/cache refactor.