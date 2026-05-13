# LOCAL OPERATOR COMFORT PROFILE

## 1. Purpose

This document defines the minimum operator comfort profile for local `docs-agent` deployment on a working laptop.

Primary target environment:
- MacBook Pro M4
- 16 GB RAM
- 512 GB SSD
- operator continues normal work in parallel with the application

This document exists to ensure that the local app remains:
- responsive
- low-friction
- non-intrusive
- bounded in resource usage
- suitable for daily parallel operator work

This is an application runtime comfort profile, not a replacement for project governance in `Cass`.

## 2. Core principle

The operator must be able to continue normal laptop work while the application is running.

Local app behavior should prefer:
- foreground-first execution
- visible heavy work
- bounded background activity
- explicit operator-triggered heavy actions
- quick recovery and cancellation

The local app should not behave like:
- a noisy background batch processor
- an uncontrolled render farm
- a constant rescanner/poller
- a hidden resource hog

## 3. Default comfort mode

The default local runtime mode should be:

- low-background-activity
- bounded concurrency
- UI-responsive
- cancellation-friendly
- cache-disciplined

This mode should be the default profile for daily work.

## 4. Heavy job concurrency limits

Recommended default limits:

- heavy render/export jobs: `1` at a time
- preview generation jobs: `1` at a time
- parallel heavy jobs above `1`: disabled by default
- enhanced parallelism: operator-enabled only

Interpretation:
- the app should not start multiple heavy preview/export jobs by default
- if multiple jobs are queued, they should run serially unless the operator explicitly changes the profile

## 5. Background activity limits

By default, the app should avoid:

- broad background rescans
- aggressive refresh loops
- constant polling of Drive state
- speculative export generation
- automatic prefetching of large artifacts

Allowed by default:

- lightweight UI refresh
- explicit operator-triggered refresh
- bounded task-state refresh
- minimal authority metadata refresh

## 6. UI responsiveness rule

The app shell must remain responsive during heavy operations.

Required behavior:
- heavy jobs run asynchronously
- visible progress state
- visible queued/running/completed state
- cancel action for long-running tasks
- no blocking of the main UI thread

The operator should still be able to:
- switch tasks
- inspect authority
- review history
- cancel work
- continue non-heavy task navigation

## 7. Memory comfort rule

The app should avoid memory creep.

Required behavior:
- do not keep many large previews in memory simultaneously
- lazy-load large preview/export artifacts
- release preview memory after task switch when possible
- avoid automatic parallel loading of large files

Interpretation:
- artifact-heavy screens should stay review-friendly without behaving like full in-memory asset workspaces

## 8. SSD and cache comfort rule

The local SSD should not be consumed silently by derived artifacts.

Recommended default behavior:
- preview files expire automatically
- temp export files expire automatically
- bounded cache directory
- cleanup on startup or periodic cleanup
- explicit retention only for task/package-important artifacts

Recommended implementation stance:
- treat previews as disposable by default
- treat temp exports as disposable unless retained by package state
- separate persistent task metadata from disposable render artifacts

## 9. Quiet mode

The app should support a `quiet mode` or equivalent low-impact profile.

Quiet mode should mean:
- single heavy job only
- reduced refresh frequency
- no automatic large preview preloading
- no background artifact preparation
- minimal notifications
- no non-essential polling

This mode should be preferred during normal laptop multitasking.

## 10. Enhanced mode

If later introduced, enhanced mode should be explicit and reversible.

Enhanced mode may allow:
- higher concurrency
- more aggressive preview/export handling
- faster refresh

But it must:
- be opt-in
- show visible warning that resource usage may increase
- not become the silent default

## 11. Operator-visible comfort signals

The app should show the operator:

- current comfort mode
- active heavy jobs count
- queued jobs count
- background activity status
- cache usage summary
- long-running task indicator

The operator should not need to guess why the laptop feels busy.

## 12. Practical comfort rules

Use these rules by default:

- start heavy jobs only on explicit operator intent
- serialize heavy work unless explicitly overridden
- prefer preview over full export unless export is needed
- prefer source review before generating multiple exports
- cancel stale work instead of letting it accumulate
- do not auto-create large batches of derived artifacts

## 13. Final interpretation

A local deployment is acceptable for daily operator use only if:
- the app stays responsive
- heavy work stays bounded
- background work stays quiet
- storage stays controlled
- operator retains control

## 14. Final rule

Use this rule by default:

- operator comfort is a runtime requirement
- bounded safety alone is not enough
- local app must remain usable alongside normal laptop work
