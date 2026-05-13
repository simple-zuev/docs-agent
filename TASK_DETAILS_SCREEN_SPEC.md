# TASK DETAILS SCREEN SPEC

## 1. Purpose

This document defines the minimum Task Details / Workspace screen for the future `docs-agent` operator application.

## 2. Screen role

This is the main working screen for a selected task.

It should unify:
- task identity
- current state
- authority binding visibility
- current Drive/artifact context
- output status
- next allowed action

## 3. Minimum sections

### A. Task Header
Show:
- task title
- task type
- task status
- created / updated timestamps

### B. Authority Summary
Show:
- authority source title
- authority topic
- last modified
- open authority

### C. Current Context
Show:
- primary object
- object kind
- placement state
- safe-for-mutation signal

### D. Output State
Show:
- current output state
- preview/package/publication readiness
- warnings if incomplete

### E. Action Rail
Show only bounded next actions relevant to state.

Examples:
- request preview
- prepare export package
- request approval
- review package
- mark task complete

### F. Risk / Warning Area
Show:
- blocked reasons
- approval missing
- authority binding missing
- package incomplete
- incorrect source/export relation

## 4. Design rule

The screen should help the operator answer:
- what task am I in?
- what governs it?
- what object am I touching?
- what can I do next safely?
- what blocks me?

## 5. Final interpretation

Task Details is the operational center of the application.
