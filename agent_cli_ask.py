from __future__ import annotations

from collections.abc import Callable

from agent_cli_lookup import looks_like_google_id, normalize_query_for_lookup


def is_status_query(query_lower: str) -> bool:
    return any(
        x in query_lower
        for x in [
            "status",
            "статус",
            "mode",
            "режим",
            "config",
            "конфиг",
            "безопас",
        ]
    )


def is_read_query(query_lower: str) -> bool:
    return any(
        x in query_lower
        for x in [
            "read",
            "прочитай",
            "read-doc",
            "content",
            "содержимое",
            "текст документа",
        ]
    )


def build_ask_result(query: str, routed_to: str, result: dict, **extra) -> dict:
    payload = {
        "ok": bool(result.get("ok")),
        "command": "ask",
        "query": query,
        "routed_to": routed_to,
        "result": result,
    }
    payload.update(extra)
    return payload


def ask_status_payload(query: str, status_payload: Callable[[], dict]) -> dict:
    result = status_payload()
    return build_ask_result(query, "status", result)


def ask_read_payload(
    query: str,
    lookup_query: str,
    read_doc_from_query_payload: Callable[[str], dict],
) -> dict:
    result = read_doc_from_query_payload(lookup_query)
    return build_ask_result(query, "read-doc-from-query", result)


def ask_google_id_payload(
    query: str,
    lookup_query: str,
    find_doc_any_payload: Callable[[str], dict],
    run_docs_agent_with_retry: Callable[[list[str]], dict],
) -> dict:
    found = find_doc_any_payload(lookup_query)
    if found.get("ok"):
        return build_ask_result(query, "find-doc-any", found)

    file_result = run_docs_agent_with_retry(["get-file", lookup_query])
    return {
        "ok": bool(file_result.get("ok")),
        "command": "ask",
        "query": query,
        "routed_to": "get-file",
        "result": file_result,
        "fallback_from": found,
    }


def ask_find_payload(
    query: str,
    lookup_query: str,
    find_doc_any_payload: Callable[[str], dict],
) -> dict:
    found = find_doc_any_payload(lookup_query)
    return build_ask_result(query, "find-doc-any", found)


def ask_payload(
    query: str,
    *,
    status_payload: Callable[[], dict],
    read_doc_from_query_payload: Callable[[str], dict],
    find_doc_any_payload: Callable[[str], dict],
    run_docs_agent_with_retry: Callable[[list[str]], dict],
) -> dict:
    q = query.strip()
    ql = q.lower()
    lookup_query = normalize_query_for_lookup(q)

    if is_status_query(ql):
        return ask_status_payload(query, status_payload)

    if is_read_query(ql):
        return ask_read_payload(query, lookup_query, read_doc_from_query_payload)

    if looks_like_google_id(lookup_query):
        return ask_google_id_payload(
            query, lookup_query, find_doc_any_payload, run_docs_agent_with_retry
        )

    return ask_find_payload(query, lookup_query, find_doc_any_payload)
