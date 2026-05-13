# INSTRUCTION PANEL UI STATES

## 1. Purpose

This document defines the minimum UI states for the Instruction Panel.

## 2. Core rule

The panel must always remain reference-oriented.
It must not behave like an embedded full policy copy.

## 3. Minimum states

### State A — Bound / Ready
Show:
- authoritative source
- topic
- relevant section
- last modified
- operator hint
- open in Drive

### State B — Bound with Supporting Sources
Show:
- primary authority
- supporting authority list
- why primary source applies

### State C — Missing Binding
Show:
- no authority binding yet
- task cannot be interpreted as authority-complete
- prompt to bind source before risky actions

### State D — Stale / Needs Refresh
Show:
- authority exists
- last modified should be rechecked or refreshed
- execution can continue only if allowed by task type

### State E — Error Loading Reference
Show:
- reference unavailable
- do not replace with guessed local rule text
- prompt operator to open/check source manually

## 4. Copy rule

Preferred language:
- authoritative source
- why this applies
- project governance remains in `Cass`

Avoid:
- local policy override language
- “this panel is the source of truth”

## 5. Final interpretation

Instruction Panel states should preserve authority clarity under all task conditions.
