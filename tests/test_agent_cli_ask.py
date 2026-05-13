from __future__ import annotations

import agent_cli_ask


def test_ask_payload_routes_status_query() -> None:
    payload = agent_cli_ask.ask_payload(
        "покажи статус",
        status_payload=lambda: {"ok": True, "command": "status"},
        read_doc_from_query_payload=lambda _query: {"ok": False},
        find_doc_any_payload=lambda _query: {"ok": False},
        run_docs_agent_with_retry=lambda _args: {"ok": False},
    )

    assert payload["ok"] is True
    assert payload["command"] == "ask"
    assert payload["routed_to"] == "status"
    assert payload["result"]["command"] == "status"


def test_ask_payload_routes_read_query_with_normalized_lookup() -> None:
    seen = []

    def fake_read(query):
        seen.append(query)
        return {"ok": True, "command": "read-doc-from-query", "query": query}

    payload = agent_cli_ask.ask_payload(
        "прочитай документ DOC-0001",
        status_payload=lambda: {"ok": False},
        read_doc_from_query_payload=fake_read,
        find_doc_any_payload=lambda _query: {"ok": False},
        run_docs_agent_with_retry=lambda _args: {"ok": False},
    )

    assert seen == ["DOC-0001"]
    assert payload["ok"] is True
    assert payload["routed_to"] == "read-doc-from-query"


def test_ask_payload_falls_back_to_get_file_for_google_id() -> None:
    calls = []

    def fake_find(query):
        calls.append(("find", query))
        return {"ok": False, "command": "find-doc-any", "query": query}

    def fake_runner(args):
        calls.append(("runner", args))
        return {"ok": True, "command": "get-file"}

    google_id = "abc12345678901234567890"
    payload = agent_cli_ask.ask_payload(
        google_id,
        status_payload=lambda: {"ok": False},
        read_doc_from_query_payload=lambda _query: {"ok": False},
        find_doc_any_payload=fake_find,
        run_docs_agent_with_retry=fake_runner,
    )

    assert calls == [
        ("find", google_id),
        ("runner", ["get-file", google_id]),
    ]
    assert payload["ok"] is True
    assert payload["routed_to"] == "get-file"
    assert payload["fallback_from"]["command"] == "find-doc-any"


def test_ask_payload_routes_general_query_to_find() -> None:
    payload = agent_cli_ask.ask_payload(
        "Operating Prompt",
        status_payload=lambda: {"ok": False},
        read_doc_from_query_payload=lambda _query: {"ok": False},
        find_doc_any_payload=lambda query: {
            "ok": True,
            "command": "find-doc-any",
            "query": query,
        },
        run_docs_agent_with_retry=lambda _args: {"ok": False},
    )

    assert payload["ok"] is True
    assert payload["routed_to"] == "find-doc-any"
    assert payload["result"]["query"] == "Operating Prompt"
