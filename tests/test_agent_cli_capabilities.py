from __future__ import annotations

import agent_cli


def test_capabilities_separates_baseline_from_degraded(monkeypatch) -> None:
    monkeypatch.setattr(
        agent_cli,
        "cmd_status_payload",
        lambda: {
            "ok": True,
            "safety": {
                "forbid_master_index_write": True,
                "forbid_delete": True,
            },
        },
    )

    payload = agent_cli.capabilities_payload()
    categories = payload["categories"]

    assert "read-doc" in categories["read_only"]
    assert "get-file" in categories["read_only"]
    assert "read-doc-from-query" in categories["read_only"]

    assert "read-doc" not in categories["assisted_bounded_baseline"]
    assert "get-file" not in categories["assisted_bounded_baseline"]
    assert "read-doc-from-query" not in categories["assisted_bounded_baseline"]

    assert categories["degraded"] == [
        "get-file",
        "read-doc",
        "read-doc-from-query",
    ]
    assert categories["helper_surface"] == ["ask"]
    assert any("read_only is descriptive" in note for note in payload["notes"])
