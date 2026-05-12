# AGENT CLI Tool Contract

## 1. Purpose

This document defines the observed command-line contract for `agent_cli.py`.

It is intended for:
- external AI agents and wrappers;
- human operators;
- contract reviewers;
- future contract/regression test coverage.

This document is documentation-first and reflects the currently observed CLI behavior.
It does not expand CLI surface and does not imply undocumented guarantees beyond what is stated here.

## 2. Scope and current status

Runtime model:
- `agent_cli.py` = active CLI entrypoint
- `docs_agent.py` = canonical runtime
- `docs_agent_v2.py` = migration/alignment target

This contract covers:
- top-level commands and aliases;
- argument shape;
- output modes;
- observed error behavior;
- exit code semantics;
- compatibility notes for wrappers.

Out of scope:
- internal orchestration design;
- future CLI redesign;
- undocumented internal helper APIs.

## 3. Global CLI invariants

### 3.1 Entry point
Canonical entry point:

`python agent_cli.py <command> [arguments] [--json where supported]`

### 3.2 Output modes
Observed output modes:
- compact human-readable output;
- JSON output when the command path supports `--json`.

Wrappers should prefer JSON mode where supported.

### 3.3 Help / usage behavior
Observed current behavior:
- `python agent_cli.py --help` is **not** a dedicated help-flag path;
- it is currently treated as an unknown command;
- CLI prints:
  - `ok: False`
  - `command: usage`
  - `error_type: UsageError`
  - `error_message: Unknown command: --help`
  - followed by usage text.

Wrappers must not assume POSIX-style `--help` support unless explicitly revalidated.

### 3.4 Positional argument discipline
Many commands reject unexpected positional arguments and return `UsageError`.

### 3.5 Read-only vs higher-level orchestration
This CLI exposes both:
- direct retrieval/query commands;
- higher-level orchestration helpers such as `assemble-context`, `doc-body-only`, and `artifact-state`.

Wrappers should treat orchestration-style commands as higher-level, more policy-sensitive entry points.

## 4. Exit code semantics

Observed constants:
- `0` = OK
- `1` = usage error
- `2` = not found
- `3` = auth error
- `4` = network error
- `5` = internal error
- `130` = interrupted

Wrappers should branch on exit code first, then inspect JSON/error payload when available.

## 5. Command catalog

### 5.1 Status and diagnostics
- `status`
- `repo-state`
- `rs` (alias of `repo-state`)
- `doctor-lite`
- `diagnose-lite` (alias of `doctor-lite`)
- `doctor`
- `diagnose` (alias of `doctor`)

### 5.2 Context assembly and artifact inspection
- `assemble-context`
- `doc-body-only`
- `artifact-state`

### 5.3 Registry / lookup commands
- `find-doc-id`
- `find-doc-name`
- `find-link`
- `find-doc-any`
- `f` (alias of `find-doc-any`)
- `open-doc-from-query`
- `o` (alias of `open-doc-from-query`)
- `read-doc-from-query`
- `r` (alias of `read-doc-from-query`)

### 5.4 Direct object access
- `get-file`
- `read-doc`

### 5.5 Natural-language routing
- `ask`
- `q` (alias of `ask`)

## 6. Per-command schemas

---

### 6.1 `status`

**Purpose**  
Return CLI/runtime/config/safety status snapshot.

**Forms**
- `python agent_cli.py status`
- `python agent_cli.py status --json`

**Arguments**
- optional: `--json`
- positional arguments: not accepted

**Output**
- human-readable compact status
- JSON payload in `--json` mode

**Notes**
- foundational diagnostic command
- safe first command for wrappers

---

### 6.2 `repo-state` / `rs`

**Purpose**  
Return repository working tree / branch safety snapshot.

**Forms**
- `python agent_cli.py repo-state`
- `python agent_cli.py repo-state --json`
- `python agent_cli.py rs`
- `python agent_cli.py rs --json`

**Arguments**
- optional: `--json`
- positional arguments: not accepted

**Output**
- human-readable compact repo state
- JSON payload in `--json` mode

---

### 6.3 `doctor-lite` / `diagnose-lite`

**Purpose**  
Run lightweight startup diagnostics.

**Forms**
- `python agent_cli.py doctor-lite`
- `python agent_cli.py doctor-lite --json`
- `python agent_cli.py diagnose-lite`
- `python agent_cli.py diagnose-lite --json`

**Arguments**
- optional: `--json`
- positional arguments: not accepted

**Checks**
- environment
- status
- master index lookup

**Output**
- compact summary
- JSON diagnostic payload in `--json` mode

**Notes**
- preferred quick health-check before routine work
- lighter than `doctor`

---

### 6.4 `doctor` / `diagnose`

**Purpose**  
Run extended diagnostics.

**Forms**
- `python agent_cli.py doctor`
- `python agent_cli.py doctor --json`
- `python agent_cli.py diagnose`
- `python agent_cli.py diagnose --json`

**Arguments**
- optional: `--json`
- positional arguments: not accepted

**Checks**
- environment
- status
- master index lookup
- smoke probe

**Output**
- compact summary
- JSON diagnostic payload in `--json` mode

**Notes**
- deeper than `doctor-lite`
- may involve smoke script execution

---

### 6.5 `assemble-context`

**Purpose**  
Build higher-level context package for downstream drafting / document work.

**Forms**
- `python agent_cli.py assemble-context --profile <profile>`
- `python agent_cli.py assemble-context --json --profile <profile>`

**Arguments**
- required: `--profile <profile>`
- optional: `--json`

**Output**
- human-readable or JSON payload depending on mode

**Notes**
- orchestration-oriented command
- wrappers should treat output as policy-sensitive assembled context

---

### 6.6 `doc-body-only`

**Purpose**  
Prepare document body output without direct final artifact mutation.

**Forms**
- `python agent_cli.py doc-body-only --profile <profile> --document-type <type> --title <title>`
- `python agent_cli.py doc-body-only --json --profile <profile> --document-type <type> --title <title>`

**Arguments**
- required: `--profile <profile>`
- required: `--document-type <type>`
- required: `--title <title>`
- optional: `--json`

**Output**
- human-readable or JSON payload depending on mode

**Notes**
- draft-first / mutation-avoiding path
- suitable when source resolution is incomplete

---

### 6.7 `artifact-state`

**Purpose**  
Inspect file/artifact classification and review status.

**Forms**
- `python agent_cli.py artifact-state --file-id <google_drive_file_id>`
- `python agent_cli.py artifact-state --json --file-id <google_drive_file_id>`

**Arguments**
- required: `--file-id <google_drive_file_id>`
- optional: `--json`

**Output**
- human-readable or JSON payload

---

### 6.8 `find-doc-id`

**Purpose**  
Lookup registry entry by exact document ID.

**Form**
- `python agent_cli.py find-doc-id <DOC-XXXX>`

**Arguments**
- required positional: document ID

**Output**
- human-readable output

**Compatibility note**
- no explicit `--json` form observed in usage text for this direct command

---

### 6.9 `find-doc-name`

**Purpose**  
Lookup registry entry by exact document name.

**Form**
- `python agent_cli.py find-doc-name <document name>`

**Arguments**
- required positional: document name

**Output**
- human-readable output

---

### 6.10 `find-link`

**Purpose**  
Lookup registry entry by Drive ID or URL fragment.

**Form**
- `python agent_cli.py find-link <drive_id_or_url_fragment>`

**Arguments**
- required positional: link fragment or Drive ID

**Output**
- human-readable output

---

### 6.11 `find-doc-any` / `f`

**Purpose**  
Multi-strategy lookup by document ID, document name, or link fragment.

**Forms**
- `python agent_cli.py find-doc-any <query>`
- `python agent_cli.py find-doc-any --json <query>`
- `python agent_cli.py f <query>`
- `python agent_cli.py f --json <query>`

**Arguments**
- required positional: `<query>`
- optional: `--json`

**Output**
- compact human-readable lookup result
- JSON payload in `--json` mode

**Notes**
- preferred general lookup entry point
- wrappers should prefer this over narrower lookup commands when uncertain

---

### 6.12 `open-doc-from-query` / `o`

**Purpose**  
Resolve a query, then open/expose the linked document target.

**Forms**
- `python agent_cli.py open-doc-from-query <query>`
- `python agent_cli.py open-doc-from-query --json <query>`
- `python agent_cli.py o <query>`
- `python agent_cli.py o --json <query>`

**Arguments**
- required positional: `<query>`
- optional: `--json`

**Output**
- human-readable result
- JSON payload in `--json` mode

---

### 6.13 `read-doc-from-query` / `r`

**Purpose**  
Resolve a query, then read the matched Google Doc.

**Forms**
- `python agent_cli.py read-doc-from-query <query>`
- `python agent_cli.py read-doc-from-query --json <query>`
- `python agent_cli.py r <query>`
- `python agent_cli.py r --json <query>`

**Arguments**
- required positional: `<query>`
- optional: `--json`

**Output**
- human-readable result
- JSON payload in `--json` mode

---

### 6.14 `get-file`

**Purpose**  
Fetch file metadata/content envelope by Google Drive file ID.

**Form**
- `python agent_cli.py get-file <google_drive_file_id>`

**Arguments**
- required positional: file ID

**Output**
- human-readable result

**Compatibility note**
- JSON support is not declared in observed usage text for this command and should not be assumed without revalidation

---

### 6.15 `read-doc`

**Purpose**  
Read Google Doc by direct Google Doc ID.

**Form**
- `python agent_cli.py read-doc <google_doc_id>`

**Arguments**
- required positional: Google Doc ID

**Output**
- human-readable result

**Compatibility note**
- JSON support is not declared in observed usage text for this command and should not be assumed without revalidation

---

### 6.16 `ask` / `q`

**Purpose**  
Natural-language routing helper that maps a free-text query to a lower-level command path.

**Forms**
- `python agent_cli.py ask <free text query>`
- `python agent_cli.py ask --json <free text query>`
- `python agent_cli.py q <query>`
- `python agent_cli.py q --json <query>`

**Arguments**
- required positional: free-text query
- optional: `--json`

**Output**
- compact human-readable routed result
- JSON payload in `--json` mode

**Observed routed targets**
- `status`
- `find-doc-any`
- `get-file`
- `read-doc-from-query`

**Wrapper note**
- use for operator convenience, not as the primary deterministic integration path when the target command is already known

## 7. Error contract

## 7.1 Common payload fields
Observed/common fields across JSON-oriented command paths may include:
- `ok`
- `command`
- `error_type`
- `error_message`
- `retryable`
- `auth_related`
- `network_related`
- `next_step`
- `diagnosis`
- `likely_cause`
- `recommended_action`
- `_debug`

Wrappers must tolerate partial presence and should not require every field on every command.

## 7.2 Common error categories
Observed categories include:
- `UsageError`
- `NotFound`
- `LinkParseError`
- `TimeoutExpired`
- `JSONDecodeError`
- `EmptyOutput`
- `SmokeCheckFailed`
- `ScriptNotFound`
- command-specific internal error classes

## 8. Wrapper guidance

External wrappers should generally follow this order:
1. `status --json`
2. `doctor-lite --json` when quick readiness check is needed
3. deterministic lower-level command (`find-doc-any`, `read-doc-from-query`, etc.)
4. `doctor --json` for deeper diagnosis if behavior becomes unstable

Recommended wrapper rules:
- prefer JSON-capable commands when available;
- do not assume `--help` support;
- do not assume undocumented JSON support on direct commands that are not declared here;
- treat `ask` as convenience routing, not as a strict contract boundary for automation-critical flows.

## 9. Stability and compatibility notes

### 9.1 Stability tier
This contract documents the **currently observed** CLI behavior.
It should be treated as:
- stable enough for narrow wrapper planning;
- not yet a versioned public API.

### 9.2 Known gaps
Known gaps intentionally preserved in this stage:
- no standardized `--help` flag path;
- some commands are documented from observed dispatch rather than a dedicated formal parser spec;
- duplicate dispatch branches may exist in `main()` and are out of scope here;
- not every command has an explicitly observed JSON mode.

### 9.3 Change policy for subsequent work
Subsequent changes should prefer:
- additive contract clarification;
- explicit compatibility notes;
- no silent CLI surface expansion.

## 10. Source of truth for this revision

This contract revision is based on:
- observed `usage()` output in `agent_cli.py`;
- observed `main()` dispatch branches in `agent_cli.py`;
- audit snapshot: `audits/agent_cli_contract_coverage_2026-05-12.md`.
