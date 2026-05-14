from __future__ import annotations

import agent_cli_doctor


def test_diagnose_payload_failure_detects_nested_quota_message() -> None:
    diagnosis, likely_cause, recommended_action = (
        agent_cli_doctor.diagnose_payload_failure(
            {
                "ok": False,
                "attempts": [
                    {
                        "error_type": "GoogleApiError",
                        "error_message": "429 quota exceeded",
                    }
                ],
            }
        )
    )

    assert diagnosis == "network"
    assert "квоты" in likely_cause
    assert "60-90" in recommended_action


def test_diagnose_payload_failure_detects_transport_dns_error() -> None:
    diagnosis, likely_cause, recommended_action = (
        agent_cli_doctor.diagnose_payload_failure(
            {
                "ok": False,
                "error_type": "TransportError",
                "error_message": "Unable to find the server at oauth2.googleapis.com",
            }
        )
    )

    assert diagnosis == "network"
    assert "сетевую" in likely_cause
    assert "повтори" in recommended_action.lower()


def test_doctor_lite_payload_reports_healthy_with_injected_checks() -> None:
    payload = agent_cli_doctor.doctor_lite_payload(
        status_payload=lambda: {"ok": True},
        find_doc_any_payload=lambda query: {"ok": True, "query": query},
    )

    assert payload["ok"] is True
    assert payload["command"] == "doctor-lite"
    assert payload["checks"]["status"] == {"ok": True}
    assert payload["checks"]["master_index_lookup"] == {
        "ok": True,
        "query": "DOC-0001",
    }
    assert payload["diagnosis"] == "healthy"
    assert payload["cache_backed"] is False
    assert payload["live_google_verified"] is True


def test_doctor_lite_payload_reports_cache_backed_lookup() -> None:
    payload = agent_cli_doctor.doctor_lite_payload(
        status_payload=lambda: {"ok": True},
        find_doc_any_payload=lambda query: {
            "ok": True,
            "query": query,
            "cache": {"used": True},
        },
    )

    assert payload["ok"] is True
    assert payload["cache_backed"] is True
    assert payload["live_google_verified"] is False
    assert "cache-backed" in payload["summary"]
    assert "live Google/OAuth не проверялся" in payload["next_step"]


def test_doctor_payload_uses_injected_status_lookup_and_smoke(monkeypatch) -> None:
    monkeypatch.setattr(
        agent_cli_doctor,
        "run_smoke_explain_payload",
        lambda: {"ok": True, "command": "smoke-explain"},
    )

    payload = agent_cli_doctor.doctor_payload(
        status_payload=lambda: {"ok": True, "command": "status"},
        find_doc_any_payload=lambda query: {
            "ok": True,
            "command": "find-doc-any",
            "query": query,
        },
    )

    assert payload["ok"] is True
    assert payload["command"] == "doctor"
    assert payload["checks"]["status"]["command"] == "status"
    assert payload["checks"]["master_index_lookup"]["query"] == "DOC-0001"
    assert payload["checks"]["smoke_probe"]["command"] == "smoke-explain"
    assert payload["cache_backed"] is False
    assert payload["live_google_verified"] is True
