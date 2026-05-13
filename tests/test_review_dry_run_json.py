from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_AGENT = ROOT / "docs_agent.py"
VENV312_PYTHON = ROOT / "venv312" / "bin" / "python"
PYTHON = VENV312_PYTHON if VENV312_PYTHON.exists() else Path(sys.executable)


def run_docs_agent_json(*args: str) -> dict:
    result = subprocess.run(
        [str(PYTHON), str(DOCS_AGENT), *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_create_draft_doc_dry_run_json_contract() -> None:
    payload = run_docs_agent_json(
        "create-draft-doc",
        "CONTRACT_AUDIT_DRY_RUN",
        "--dry-run",
        "--json-output",
    )

    assert payload["ok"] is True
    assert payload["command"] == "create-draft-doc"
    assert payload["dry_run"] is True
    assert payload["target_folder"] == "13_Черновики_и_review"
    assert payload["title"] == "CONTRACT_AUDIT_DRY_RUN"
    assert payload["write_mode_required"] is True
    assert payload["next_safe_step"]


def test_append_review_note_dry_run_json_contract() -> None:
    payload = run_docs_agent_json(
        "append-review-note",
        "DRY_RUN_DOC_ID",
        "Contract audit note",
        "--dry-run",
        "--json-output",
    )

    assert payload["ok"] is True
    assert payload["command"] == "append-review-note"
    assert payload["dry_run"] is True
    assert payload["document_id"] == "DRY_RUN_DOC_ID"
    assert payload["target_folder"] == "13_Черновики_и_review"
    assert payload["note_chars"] == len("Contract audit note")
    assert payload["write_mode_required"] is True
    assert payload["next_safe_step"]


def test_write_draft_doc_dry_run_json_contract() -> None:
    payload = run_docs_agent_json(
        "write-draft-doc",
        "DRY_RUN_DOC_ID",
        "Contract audit body",
        "--dry-run",
        "--json-output",
    )

    assert payload["ok"] is True
    assert payload["command"] == "write-draft-doc"
    assert payload["dry_run"] is True
    assert payload["document_id"] == "DRY_RUN_DOC_ID"
    assert payload["target_folder"] == "13_Черновики_и_review"
    assert payload["body_chars"] == len("Contract audit body")
    assert payload["write_mode_required"] is True
    assert payload["next_safe_step"]
