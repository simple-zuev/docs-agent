from __future__ import annotations

import agent_cli_live_probe


def test_live_google_probe_reports_verified_read_only_access() -> None:
    def fake_run(args):
        assert args[:4] == [
            "find-row-by-column",
            agent_cli_live_probe.MASTER_INDEX_ID,
            agent_cli_live_probe.MASTER_INDEX_SHEET,
            "Document ID",
        ]
        assert args[4] == "DOC-0001"
        return {
            "ok": True,
            "command": "find-row-by-column",
            "matches_found": 1,
        }

    payload = agent_cli_live_probe.live_google_probe_payload(fake_run)

    assert payload["ok"] is True
    assert payload["command"] == "live-google-probe"
    assert payload["scope"] == "read-only"
    assert payload["cache_bypassed"] is True
    assert payload["live_google_verified"] is True


def test_live_google_probe_classifies_auth_failure() -> None:
    def fake_run(_args):
        return {
            "ok": False,
            "command": "find-row-by-column",
            "error_type": "RefreshError",
            "error_message": "token expired",
            "auth_related": True,
        }

    payload = agent_cli_live_probe.live_google_probe_payload(fake_run)

    assert payload["ok"] is False
    assert payload["command"] == "live-google-probe"
    assert payload["auth_related"] is True
    assert payload["network_related"] is False
    assert payload["live_google_verified"] is False
    assert payload["cache_bypassed"] is True
