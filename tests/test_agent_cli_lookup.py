from __future__ import annotations

import agent_cli_lookup


ROW = [
    "DOC-0001",
    "Operating Prompt",
    "type",
    "baseline",
    "class",
    "status",
    "folder",
    "owner",
    "purpose",
    "adr",
    "cadence",
    "date",
    "criticality",
    "description",
    "https://docs.google.com/document/d/doc_google_id_1234567890",
]


def test_extract_google_id_from_link_accepts_google_doc_link() -> None:
    assert (
        agent_cli_lookup.extract_google_id_from_link(
            "https://docs.google.com/document/d/doc_google_id_1234567890/edit"
        )
        == "doc_google_id_1234567890"
    )


def test_normalize_query_for_lookup_strips_repeated_prefixes() -> None:
    assert (
        agent_cli_lookup.normalize_query_for_lookup("прочитай документ DOC-0001")
        == "DOC-0001"
    )


def test_build_find_doc_success_payload_preserves_summary_contract() -> None:
    result = {"matches": [{"row_values": ROW}]}

    payload = agent_cli_lookup.build_find_doc_success_payload(
        query="DOC-0001",
        matched_by="Document ID",
        result=result,
        attempts=[],
    )

    assert payload["ok"] is True
    assert payload["command"] == "find-doc-any"
    assert payload["summary"] == {
        "document_id": "DOC-0001",
        "document_name": "Operating Prompt",
        "link": "https://docs.google.com/document/d/doc_google_id_1234567890",
    }


def test_find_doc_any_payload_live_tries_id_name_then_link() -> None:
    calls = []

    def fake_runner(args):
        calls.append(args)
        if args[3] == "Document ID":
            return {"ok": True, "matches_found": 0}
        if args[3] == "Document Name":
            return {"ok": True, "matches_found": 1, "matches": [{"row_values": ROW}]}
        raise AssertionError("link lookup should not run after name match")

    payload = agent_cli_lookup.find_doc_any_payload_live(
        "Operating Prompt", fake_runner
    )

    assert calls == [
        [
            "find-row-by-column",
            agent_cli_lookup.MASTER_INDEX_ID,
            agent_cli_lookup.MASTER_INDEX_SHEET,
            "Document ID",
            "Operating Prompt",
        ],
        [
            "find-row-by-column",
            agent_cli_lookup.MASTER_INDEX_ID,
            agent_cli_lookup.MASTER_INDEX_SHEET,
            "Document Name",
            "Operating Prompt",
        ],
    ]
    assert payload["ok"] is True
    assert payload["matched_by"] == "Document Name"


def test_read_doc_from_query_payload_returns_link_parse_error(monkeypatch) -> None:
    def fake_find_doc_any_payload(_query, _diagnose, _runner):
        return {
            "ok": True,
            "matched_by": "Document ID",
            "summary": {
                "document_id": "DOC-0001",
                "document_name": "Operating Prompt",
                "link": "not-a-google-link",
            },
        }

    monkeypatch.setattr(
        agent_cli_lookup, "find_doc_any_payload", fake_find_doc_any_payload
    )

    payload = agent_cli_lookup.read_doc_from_query_payload(
        "DOC-0001", lambda _payload: ("", "", ""), lambda _args: {}
    )

    assert payload["ok"] is False
    assert payload["command"] == "read-doc-from-query"
    assert payload["error_type"] == "LinkParseError"
