# APPROVAL PANEL UI STATES

## 1. Purpose

This document defines the minimum UI states for the Approval Panel.

## 2. Minimum states

### State A — Not Required
Show:
- approval not required
- reason why current task/action is allowed without extra approval

### State B — Required
Show:
- approval required
- why it is required
- what action is blocked

### State C — Requested / Pending
Show:
- approval requested
- timestamp
- requester
- pending status
- blocked actions remain disabled

### State D — Approved
Show:
- approved status
- who approved
- when approved
- what action is now enabled

### State E — Rejected
Show:
- rejected status
- rejection reason
- next recovery path

### State F — Expired
Show:
- prior approval expired
- task needs renewed decision before proceeding

## 3. UX rule

The panel should make it impossible to miss:
- whether approval is needed
- what is blocked
- what decision exists
- whether old approval is no longer valid

## 4. Final interpretation

Approval panel is the action gate for bounded execution discipline.
