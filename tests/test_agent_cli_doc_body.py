from __future__ import annotations

import agent_cli_doc_body


def test_assemble_context_rejects_unsupported_profile() -> None:
    payload = agent_cli_doc_body.assemble_context_payload(
        "unknown",
        capabilities_payload=lambda: {"ok": True},
        status_payload=lambda: {"ok": True},
        find_doc_any_payload_from_cache=lambda _query: {"ok": False},
    )

    assert payload["ok"] is False
    assert payload["command"] == "assemble-context"
    assert payload["error_type"] == "UnsupportedProfile"
    assert payload["profile"] == "unknown"


def test_assemble_context_uses_cache_only_lookup_and_marks_partial() -> None:
    calls = []

    def fake_cache(query):
        calls.append(query)
        if query == "DOC-0001":
            return {
                "ok": True,
                "matched_by": "Document ID",
                "summary": {"document_id": "DOC-0001"},
            }
        return {"ok": False}

    payload = agent_cli_doc_body.assemble_context_payload(
        "exchange-docs",
        capabilities_payload=lambda: {"ok": True, "command": "capabilities"},
        status_payload=lambda: {
            "ok": True,
            "config": {
                "change_log_spreadsheet_id": "sheet-1",
                "change_log_sheet_name": "Change Log Lite",
            },
        },
        find_doc_any_payload_from_cache=fake_cache,
    )

    assert payload["ok"] is True
    assert payload["command"] == "assemble-context"
    assert payload["context_summary"]["partial_context"] is True
    assert payload["recommended_generation_mode"] == "doc-body-only"
    assert "DOC-0001" in calls
    assert "КБ ТЗ v2" in calls
    assert any(
        item["query"] == "Change Log Lite" and item["matched_by"] == "config"
        for item in payload["resolved_sources"]
    )


def test_assemble_context_treats_empty_cache_payload_as_miss() -> None:
    def fake_cache(query):
        if query == "DOC-0001":
            return None
        return {"ok": False}

    payload = agent_cli_doc_body.assemble_context_payload(
        "exchange-docs",
        capabilities_payload=lambda: {"ok": True},
        status_payload=lambda: {"ok": True, "config": {}},
        find_doc_any_payload_from_cache=fake_cache,
    )

    assert payload["ok"] is True
    assert payload["context_summary"]["partial_context"] is True
    assert any(
        item["query"] == "DOC-0001" and item["reason"] == "CacheMiss"
        for item in payload["unresolved_sources"]
    )


def test_doc_body_only_payload_builds_body_without_mutation() -> None:
    context_payload = {
        "ok": True,
        "context_summary": {
            "resolved_count": 2,
            "unresolved_count": 1,
            "partial_context": True,
        },
        "unresolved_sources": [{"query": "КБ ТЗ v2"}],
    }

    payload = agent_cli_doc_body.doc_body_only_payload(
        "exchange-docs",
        "architecture-note",
        "Draft Architecture Note",
        assemble_context_payload=lambda _profile: context_payload,
    )

    assert payload["ok"] is True
    assert payload["command"] == "doc-body-only"
    assert payload["context_snapshot"]["partial_context"] is True
    assert payload["unresolved_dependencies"] == ["КБ ТЗ v2"]
    assert "Документ подготовлен в режиме doc-body-only." in payload["body"]
    assert "## Контекст" in payload["body"]
