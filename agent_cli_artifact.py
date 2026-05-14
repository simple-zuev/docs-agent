from __future__ import annotations

from collections.abc import Callable

from agent_cli_output import build_error_payload


REVIEW_FOLDER_ID = "1rZtuXOyThzFf_LFWaD4w5nHwuXCDIHQh"
OFFICE_FOLDER_ID = "1I8xbFY0sjdS4bVPICr4pOg7qkTftgHBv"


def artifact_state_payload(
    file_id: str,
    *,
    run_docs_agent_with_retry: Callable[[list[str]], dict],
    status_payload: Callable[[], dict],
) -> dict:
    file_payload = run_docs_agent_with_retry(["get-file", file_id])
    if not isinstance(file_payload, dict) or not file_payload.get("ok"):
        return build_error_payload(
            command="artifact-state",
            error_type=(file_payload or {}).get("error_type", "ArtifactLookupError"),
            error_message=(file_payload or {}).get(
                "error_message", "Failed to read artifact metadata."
            ),
            retryable=bool((file_payload or {}).get("retryable")),
            auth_related=bool((file_payload or {}).get("auth_related")),
            network_related=bool((file_payload or {}).get("network_related")),
            target_artifact={"file_id": file_id},
            lookup_result=file_payload,
        )

    file_meta = file_payload.get("file") or {}
    name = str(file_meta.get("name") or "")
    parents = file_meta.get("parents") or []

    default_test_folder = (
        (status_payload().get("safety") or {}).get("default_test_folder")
    ) or ""

    in_review_scope = REVIEW_FOLDER_ID in parents
    in_default_test_scope = OFFICE_FOLDER_ID in parents

    placement = {
        "parents": parents,
        "review_folder_id": REVIEW_FOLDER_ID,
        "office_folder_id": OFFICE_FOLDER_ID,
        "review_scope_by_parent_id": in_review_scope,
        "default_test_scope_by_parent_id": in_default_test_scope,
        "default_test_folder": default_test_folder,
    }

    artifact_state = "Unknown"
    review_status = "Needs classification"
    next_safe_step = "Review artifact placement and classify before write actions."

    if name.startswith("BACKUP_BEFORE_REPLACE__"):
        artifact_state = "Historical reference"
        review_status = "Not for direct mutation"
        next_safe_step = "Use as backup/reference only."
    elif name.startswith("STAGING_COPY__"):
        artifact_state = "Pending review"
        review_status = "Review required"
        next_safe_step = "Inspect staging artifact and decide whether body placement or review note is needed."
    elif in_review_scope:
        artifact_state = "Draft"
        review_status = "In review scope"
        next_safe_step = (
            "Safe candidate for bounded draft workflow after target validation."
        )
    elif in_default_test_scope:
        artifact_state = "Draft"
        review_status = "In default test scope"
        next_safe_step = "Validate whether this artifact should stay test-only or move into review workflow."
    elif name:
        artifact_state = "Canonical or non-review artifact"
        review_status = "Outside review scope"
        next_safe_step = (
            "Avoid bounded write until artifact scope is explicitly validated."
        )

    return {
        "ok": True,
        "command": "artifact-state",
        "target_artifact": {
            "file_id": file_id,
            "name": name,
            "mime_type": file_meta.get("mimeType"),
            "web_view_link": file_meta.get("webViewLink"),
        },
        "artifact_state": artifact_state,
        "review_status": review_status,
        "placement": placement,
        "next_safe_step": next_safe_step,
        "lookup_result": file_payload,
    }
