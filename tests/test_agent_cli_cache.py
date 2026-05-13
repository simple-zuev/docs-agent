from __future__ import annotations

import agent_cli_cache


HEADER = ["Document ID", "Document Name", "Folder", "Link"]
ROW = ["DOC-0001", "Operating Prompt", "Cass", "https://docs.google.com/document/d/abc"]


def test_find_doc_any_payload_from_cache_matches_document_id(monkeypatch) -> None:
    monkeypatch.setattr(
        agent_cli_cache,
        "load_master_index_cache",
        lambda: {
            "fetched_at_epoch": agent_cli_cache.now_epoch_int(),
            "header": HEADER,
            "rows": [ROW],
        },
    )

    payload = agent_cli_cache.find_doc_any_payload_from_cache("DOC-0001")

    assert payload["ok"] is True
    assert payload["command"] == "find-doc-any"
    assert payload["matched_by"] == "Document ID"
    assert payload["summary"]["document_id"] == "DOC-0001"
    assert payload["summary"]["document_name"] == "Operating Prompt"
    assert payload["summary"]["folder"] == "Cass"
    assert payload["cache"]["used"] is True


def test_find_doc_any_payload_from_cache_matches_link_fragment(monkeypatch) -> None:
    monkeypatch.setattr(
        agent_cli_cache,
        "load_master_index_cache",
        lambda: {
            "fetched_at_epoch": agent_cli_cache.now_epoch_int(),
            "header": HEADER,
            "rows": [ROW],
        },
    )

    payload = agent_cli_cache.find_doc_any_payload_from_cache("document/d/abc")

    assert payload["ok"] is True
    assert payload["matched_by"] == "Link fragment"


def test_find_doc_any_payload_from_cache_returns_not_found(monkeypatch) -> None:
    monkeypatch.setattr(
        agent_cli_cache,
        "load_master_index_cache",
        lambda: {
            "fetched_at_epoch": agent_cli_cache.now_epoch_int(),
            "header": HEADER,
            "rows": [ROW],
        },
    )

    payload = agent_cli_cache.find_doc_any_payload_from_cache("missing")

    assert payload["ok"] is False
    assert payload["command"] == "find-doc-any"
    assert payload["error_type"] == "NotFound"
    assert payload["cache"]["used"] is True


def test_refresh_master_index_cache_saves_seed(monkeypatch) -> None:
    saved = []
    row = ["DOC-0001", "Operating Prompt", "type"]

    def fake_fetch_seed(query):
        assert query == "DOC-0001"
        return {
            "ok": True,
            "result": {
                "matches": [
                    {
                        "row_values": row,
                    }
                ]
            },
        }

    monkeypatch.setattr(agent_cli_cache, "save_master_index_cache", saved.append)
    monkeypatch.setattr(agent_cli_cache, "now_epoch_int", lambda: 123)

    payload = agent_cli_cache.refresh_master_index_cache(fake_fetch_seed)

    assert payload["ok"] is True
    assert payload["command"] == "master-index-cache-refresh"
    assert payload["rows_cached"] == 1
    assert saved[0]["fetched_at_epoch"] == 123
    assert saved[0]["rows"] == [row]


def test_extend_master_index_cache_appends_new_live_row(monkeypatch) -> None:
    saved = []
    cache = {
        "fetched_at_epoch": 1,
        "header": HEADER,
        "rows": [ROW],
    }
    new_row = ["DOC-0002", "Second Doc", "Cass", "https://example.test"]
    payload = {
        "ok": True,
        "result": {
            "matches": [
                {
                    "row_values": new_row,
                }
            ]
        },
    }

    monkeypatch.setattr(agent_cli_cache, "load_master_index_cache", lambda: cache)
    monkeypatch.setattr(agent_cli_cache, "save_master_index_cache", saved.append)
    monkeypatch.setattr(agent_cli_cache, "now_epoch_int", lambda: 456)

    agent_cli_cache.extend_master_index_cache_from_success(payload)

    assert saved[0]["rows"] == [ROW, new_row]
    assert saved[0]["fetched_at_epoch"] == 456
