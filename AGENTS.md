# AGENTS.md

## Project identity

This repository contains docs-agent: a bounded CLI for Google Drive and Google Docs assisted operations.

The current objective is controlled ChatGPT/Codex-assisted operation, not broad autonomous rewriting.

## Current approved operating mode

Use Path A: assisted bounded mode.

Allowed primary surfaces:
- repo-state
- lookup/navigation commands
- artifact-state
- doc-body-only
- mutation-preparation flows only when explicitly requested

Treat the following as degraded by default until explicitly fixed and verified:
- read-doc
- get-file
- read-doc-from-query

## Safety rules

Never commit or expose:
- token.json
- .env
- OAuth client secrets
- service account keys
- API keys
- private Google Drive exports
- user personal data
- browser/session/auth caches
- ~/.codex/auth.json

Google Drive and Google Docs live mutations are high-risk. Default to read-only analysis or mutation-preparation unless the task explicitly authorizes a live mutation.

## Engineering rules

Work in small branches and small pull requests.

Before changing behavior:
- inspect the relevant command path;
- write or update an audit artifact under audits/ when the runtime contract is ambiguous;
- keep the patch narrow;
- avoid broad rewrites of agent_cli.py.

Prefer:
- contract alignment;
- explicit output envelopes;
- deterministic JSON behavior;
- stable CLI help and command surfaces;
- preservation of existing working commands.

Avoid:
- speculative refactors;
- large architecture rewrites;
- unrequested dependency additions;
- changing Google Drive behavior without a local or sandbox verification path.

## Validation commands

Use these commands where applicable:
- python3 agent_cli.py --help
- python3 agent_cli.py repo-state --json
- python3 -m ruff check agent_cli.py
- python3 -m ruff format --check agent_cli.py

If a virtual environment exists, activate it first:
- source /Users/zuevvladimir/AI/docs-agent/venv/bin/activate

## Pull request expectations

Every PR should include:
- a short problem statement;
- exact files changed;
- whether behavior changed;
- validation commands and outputs;
- known limitations;
- rollback note if the change touches runtime behavior.

## Review guidelines

When reviewing PRs, focus on:
- accidental widening of mutation capability;
- JSON/output contract drift;
- broken CLI command dispatch;
- silent failures;
- unsafe credential handling;
- changes that make degraded commands look reliable without proof.
