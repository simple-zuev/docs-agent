from __future__ import annotations

from collections.abc import Callable

from agent_cli_doctor import diagnose_payload_failure
from agent_cli_lookup import MASTER_INDEX_ID, MASTER_INDEX_SHEET, find_doc_id_payload
from agent_cli_output import build_error_payload


def live_google_probe_payload(
    run_docs_agent_with_retry: Callable[[list[str]], dict],
) -> dict:
    probe = find_doc_id_payload("DOC-0001", run_docs_agent_with_retry)
    live_google_verified = bool(
        isinstance(probe, dict)
        and probe.get("ok")
        and int(probe.get("matches_found") or 0) > 0
    )

    if live_google_verified:
        return {
            "ok": True,
            "command": "live-google-probe",
            "scope": "read-only",
            "target": "MASTER_INDEX",
            "spreadsheet_id": MASTER_INDEX_ID,
            "sheet_name": MASTER_INDEX_SHEET,
            "probe_query": "DOC-0001",
            "live_google_verified": True,
            "cache_bypassed": True,
            "result": {
                "command": probe.get("command"),
                "matches_found": probe.get("matches_found"),
            },
            "summary": "Live Google/OAuth probe reached MASTER_INDEX and found DOC-0001.",
            "next_step": "Live lookup path is available for assisted bounded read-only operations.",
        }

    diagnosis, likely_cause, recommended_action = diagnose_payload_failure(probe)
    error_type = "LiveGoogleProbeFailed"
    error_message = "Live Google/OAuth probe did not verify MASTER_INDEX access."
    if isinstance(probe, dict):
        error_type = str(probe.get("error_type") or error_type)
        error_message = str(probe.get("error_message") or error_message)

    return build_error_payload(
        command="live-google-probe",
        error_type=error_type,
        error_message=error_message,
        retryable=diagnosis == "network",
        auth_related=diagnosis == "auth",
        network_related=diagnosis == "network",
        scope="read-only",
        target="MASTER_INDEX",
        spreadsheet_id=MASTER_INDEX_ID,
        sheet_name=MASTER_INDEX_SHEET,
        probe_query="DOC-0001",
        live_google_verified=False,
        cache_bypassed=True,
        result=probe,
        diagnosis=diagnosis,
        likely_cause=likely_cause,
        recommended_action=recommended_action,
        next_step=recommended_action,
    )
