from __future__ import annotations

import agent_cli_artifact


def status_payload():
    return {"ok": True, "safety": {"default_test_folder": "Default Test"}}


def test_artifact_state_payload_wraps_lookup_failure() -> None:
    payload = agent_cli_artifact.artifact_state_payload(
        "file-1",
        run_docs_agent_with_retry=lambda _args: {
            "ok": False,
            "error_type": "NotFound",
            "error_message": "missing",
        },
        status_payload=status_payload,
    )

    assert payload["ok"] is False
    assert payload["command"] == "artifact-state"
    assert payload["error_type"] == "NotFound"
    assert payload["target_artifact"] == {"file_id": "file-1"}


def test_artifact_state_payload_classifies_review_scope_draft() -> None:
    payload = agent_cli_artifact.artifact_state_payload(
        "file-1",
        run_docs_agent_with_retry=lambda _args: {
            "ok": True,
            "file": {
                "id": "file-1",
                "name": "Review Draft",
                "mimeType": "application/vnd.google-apps.document",
                "webViewLink": "https://example.test",
                "parents": [agent_cli_artifact.REVIEW_FOLDER_ID],
            },
        },
        status_payload=status_payload,
    )

    assert payload["ok"] is True
    assert payload["artifact_state"] == "Draft"
    assert payload["review_status"] == "In review scope"
    assert payload["placement"]["review_scope_by_parent_id"] is True


def test_artifact_state_payload_classifies_staging_copy_before_folder_scope() -> None:
    payload = agent_cli_artifact.artifact_state_payload(
        "file-1",
        run_docs_agent_with_retry=lambda _args: {
            "ok": True,
            "file": {
                "id": "file-1",
                "name": "STAGING_COPY__Review Draft",
                "parents": [agent_cli_artifact.REVIEW_FOLDER_ID],
            },
        },
        status_payload=status_payload,
    )

    assert payload["artifact_state"] == "Pending review"
    assert payload["review_status"] == "Review required"


def test_artifact_state_payload_classifies_backup_before_folder_scope() -> None:
    payload = agent_cli_artifact.artifact_state_payload(
        "file-1",
        run_docs_agent_with_retry=lambda _args: {
            "ok": True,
            "file": {
                "id": "file-1",
                "name": "BACKUP_BEFORE_REPLACE__Doc",
                "parents": [agent_cli_artifact.REVIEW_FOLDER_ID],
            },
        },
        status_payload=status_payload,
    )

    assert payload["artifact_state"] == "Historical reference"
    assert payload["review_status"] == "Not for direct mutation"


def test_artifact_state_payload_classifies_canonical_outside_review() -> None:
    payload = agent_cli_artifact.artifact_state_payload(
        "file-1",
        run_docs_agent_with_retry=lambda _args: {
            "ok": True,
            "file": {
                "id": "file-1",
                "name": "Canonical Doc",
                "parents": ["other-folder"],
            },
        },
        status_payload=status_payload,
    )

    assert payload["artifact_state"] == "Canonical or non-review artifact"
    assert payload["review_status"] == "Outside review scope"
    assert "Avoid bounded write" in payload["next_safe_step"]
