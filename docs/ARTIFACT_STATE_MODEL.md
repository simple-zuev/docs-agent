# Artifact State Model

## Назначение

Документ определяет явную state-модель для artifact lifecycle внутри `docs-agent`, прежде всего для diagram-related артефактов и связанных package outputs.

Цель — исключить неявные состояния, drift и ложную интерпретацию preview как готового результата.

## Главный принцип

Каждый значимый artifact должен иметь явные поля состояния.

Минимально должны быть зафиксированы:
- preview state
- semantic verdict
- visual verdict
- release readiness
- recovery mode

## Подтверждено фактами

- Явная artifact state model как отдельный актуальный reference document в main пока не закреплена.
- Diagram tasks требуют separate semantic and visual control.
- Preview не должен считаться равным release-ready артефакту.

## Что является предположением

- State model будет храниться или отражаться в artifact registry / operational sheet / package metadata.
- Часть state surface может понадобиться и для недиаграммных package artifacts.

## Required state groups

### Preview state
- Not generated
- Draft preview
- Preview rejected
- Preview approved for iteration
- Release-ready visual

### Semantic verdict
- Not reviewed
- Passed semantic review
- Failed semantic review
- Reconciliation required

### Visual verdict
- Not reviewed
- Passed visual QA
- Failed visual QA
- Remediation required

### Release readiness
- Not ready
- Ready for iteration
- Ready for controlled review
- Release-ready

### Recovery mode
- No
- Active
- Completed

## Core rules

### Rule 1. Semantic pass does not equal visual pass
Семантическое прохождение не означает визуальное прохождение.

### Rule 2. Preview does not equal release
Сгенерированный preview не означает готовность артефакта.

### Rule 3. Release-ready requires explicit states
`Release-ready` допускается только если:
- semantic verdict passed
- visual verdict passed
- preview state compatible with release
- recovery mode not active

### Rule 4. Recovery blocks normal loop
Если recovery mode = Active, обычный regeneration loop запрещен до завершения recovery step.

## Recovery rule

После двух failed previews подряд:
- normal regeneration loop запрещен;
- root cause должен быть зафиксирован;
- recovery mode переводится в `Active`;
- требуется revised layout / wireframe remediation;
- normal preview generation блокируется до recovery completion.

## Recommended transition logic

### Preview state transitions
- Not generated -> Draft preview
- Draft preview -> Preview rejected
- Draft preview -> Preview approved for iteration
- Preview approved for iteration -> Release-ready visual
- Preview rejected -> Draft preview only after remediation

### Semantic verdict transitions
- Not reviewed -> Passed semantic review
- Not reviewed -> Failed semantic review
- Failed semantic review -> Reconciliation required
- Reconciliation required -> Passed semantic review after correction

### Visual verdict transitions
- Not reviewed -> Passed visual QA
- Not reviewed -> Failed visual QA
- Failed visual QA -> Remediation required
- Remediation required -> Passed visual QA after correction

### Release readiness transitions
- Not ready -> Ready for iteration
- Ready for iteration -> Ready for controlled review
- Ready for controlled review -> Release-ready

### Recovery mode transitions
- No -> Active
- Active -> Completed
- Completed -> No only after new stable cycle or explicit closeout logic

## Invalid transition examples

Нельзя:
- Not generated -> Release-ready visual
- Not reviewed semantic -> Release-ready
- Not reviewed visual -> Release-ready
- Failed visual QA -> Release-ready
- Recovery Active -> normal preview accepted without remediation

## Usage model

При diagram/artifact task агент должен выдавать package, содержащий:
- source
- preview
- semantic verdict
- visual verdict
- preview state
- release readiness
- next safe step

## Safe next step

State model должен быть сначала зафиксирован в design packet и только затем отражаться в implementation artifacts и registry fields.