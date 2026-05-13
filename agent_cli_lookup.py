from __future__ import annotations

import re
from collections.abc import Callable

from agent_cli_cache import (
    extend_master_index_cache_from_success,
    find_doc_any_payload_from_cache,
    load_master_index_cache,
    refresh_master_index_cache,
)
from agent_cli_output import build_error_payload


MASTER_INDEX_ID = "1hyWNNzsIHRLGJ65urOQUA0x_kOqCP61OkXcM3MMyedw"
MASTER_INDEX_SHEET = "MASTER_INDEX"

COL_DOCUMENT_ID = 0
COL_DOCUMENT_NAME = 1
COL_LINK = 14


def is_quota_or_rate_limit_error_text(value: str | None) -> bool:
    s = (value or "").lower()
    markers = [
        "429",
        "quota exceeded",
        "rate limit exceeded",
        "rate_limit_exceeded",
        "user rate limit exceeded",
        "read requests per minute per user",
        "too many requests",
        "resource exhausted",
    ]
    return any(marker in s for marker in markers)


def payload_contains_quota_or_rate_limit(payload) -> bool:
    if payload is None:
        return False

    stack = [payload]
    seen = set()

    while stack:
        item = stack.pop()
        ident = id(item)
        if ident in seen:
            continue
        seen.add(ident)

        if isinstance(item, dict):
            for v in item.values():
                if isinstance(v, str) and is_quota_or_rate_limit_error_text(v):
                    return True
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(item, list):
            for v in item:
                if isinstance(v, str) and is_quota_or_rate_limit_error_text(v):
                    return True
                if isinstance(v, (dict, list)):
                    stack.append(v)

    return False


def extract_first_match_value(payload: dict, idx: int):
    matches = payload.get("matches") or []
    if not matches:
        return None
    row = matches[0].get("row_values") or []
    if idx < len(row):
        return row[idx]
    return None


def summarize_attempt(strategy: str, payload: dict) -> dict:
    return {
        "strategy": strategy,
        "ok": payload.get("ok"),
        "matches_found": payload.get("matches_found", 0),
        "error_type": payload.get("error_type"),
        "error_message": payload.get("error_message"),
        "debug": payload.get("_debug", {}),
    }


def extract_google_id_from_link(link: str | None) -> str | None:
    if not link:
        return None

    patterns = [
        r"/document/d/([a-zA-Z0-9_-]+)",
        r"/spreadsheets/d/([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"/folders/([a-zA-Z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, link)
        if m:
            return m.group(1)

    if re.fullmatch(r"[a-zA-Z0-9_-]{20,}", link):
        return link

    return None


def looks_like_google_id(value: str) -> bool:
    return re.fullmatch(r"[a-zA-Z0-9_-]{20,}", value) is not None


def normalize_query_for_lookup(query: str) -> str:
    q = query.strip()

    prefixes = [
        "прочитай ",
        "read ",
        "read-doc ",
        "открой ",
        "open ",
        "show ",
        "покажи ",
        "найди ",
        "find ",
        "документ ",
        "doc ",
    ]

    ql = q.lower()
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if ql.startswith(prefix):
                q = q[len(prefix) :].strip()
                ql = q.lower()
                changed = True

    return q


def find_doc_id_payload(value: str, run_docs_agent_with_retry: Callable) -> dict:
    return run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document ID",
            value,
        ]
    )


def find_doc_name_payload(value: str, run_docs_agent_with_retry: Callable) -> dict:
    return run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document Name",
            value,
        ]
    )


def find_link_payload(value: str, run_docs_agent_with_retry: Callable) -> dict:
    return run_docs_agent_with_retry(
        [
            "find-row-by-link-fragment",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            value,
        ]
    )


def _find_doc_any_payload_live_impl(
    query: str, run_docs_agent_with_retry: Callable
) -> dict:
    attempts = []

    by_id = find_doc_id_payload(query, run_docs_agent_with_retry)
    attempts.append(summarize_attempt("Document ID", by_id))
    if by_id.get("ok") and by_id.get("matches_found", 0) > 0:
        return build_find_doc_success_payload(
            query=query,
            matched_by="Document ID",
            result=by_id,
            attempts=attempts,
        )

    by_name = find_doc_name_payload(query, run_docs_agent_with_retry)
    attempts.append(summarize_attempt("Document Name", by_name))
    if by_name.get("ok") and by_name.get("matches_found", 0) > 0:
        return build_find_doc_success_payload(
            query=query,
            matched_by="Document Name",
            result=by_name,
            attempts=attempts,
        )

    by_link = find_link_payload(query, run_docs_agent_with_retry)
    attempts.append(summarize_attempt("Link fragment", by_link))
    if by_link.get("ok") and by_link.get("matches_found", 0) > 0:
        return build_find_doc_success_payload(
            query=query,
            matched_by="Link fragment",
            result=by_link,
            attempts=attempts,
        )

    return build_error_payload(
        command="find-doc-any",
        query=query,
        error_type="NotFound",
        error_message="No matches found by Document ID, Document Name, or Link fragment.",
        attempts=attempts,
    )


def find_doc_any_payload_live(query, run_docs_agent_with_retry: Callable):
    return _find_doc_any_payload_live_impl(query, run_docs_agent_with_retry)


def find_doc_any_payload(
    query,
    diagnose_payload_failure: Callable[[dict | None], tuple[str, str, str]],
    run_docs_agent_with_retry: Callable,
):
    cached = find_doc_any_payload_from_cache(query)
    if isinstance(cached, dict) and cached.get("ok"):
        return cached

    if load_master_index_cache() is None:
        refresh_master_index_cache(
            lambda seed_query: find_doc_any_payload_live(
                seed_query, run_docs_agent_with_retry
            )
        )
        cached = find_doc_any_payload_from_cache(query)
        if isinstance(cached, dict) and cached.get("ok"):
            return cached

    live = find_doc_any_payload_live(query, run_docs_agent_with_retry)
    if isinstance(live, dict) and live.get("ok"):
        extend_master_index_cache_from_success(live)
        return live

    if payload_contains_quota_or_rate_limit(live):
        diagnosis, likely_cause, recommended_action = diagnose_payload_failure(live)
        live["diagnosis"] = diagnosis
        live["likely_cause"] = likely_cause
        live["recommended_action"] = recommended_action
        live["retryable"] = True
        live["network_related"] = True

    return live


def build_doc_summary(result: dict) -> dict:
    return {
        "document_id": extract_first_match_value(result, COL_DOCUMENT_ID),
        "document_name": extract_first_match_value(result, COL_DOCUMENT_NAME),
        "link": extract_first_match_value(result, COL_LINK),
    }


def build_find_doc_success_payload(
    *,
    query: str,
    matched_by: str,
    result: dict,
    attempts: list[dict],
) -> dict:
    return {
        "ok": True,
        "command": "find-doc-any",
        "query": query,
        "matched_by": matched_by,
        "result": result,
        "summary": build_doc_summary(result),
        "attempts": attempts,
    }


def open_doc_from_query_payload(
    query: str,
    diagnose_payload_failure: Callable[[dict | None], tuple[str, str, str]],
    run_docs_agent_with_retry: Callable,
) -> dict:
    found = find_doc_any_payload(
        query, diagnose_payload_failure, run_docs_agent_with_retry
    )
    if not found.get("ok"):
        return found

    link = (found.get("summary") or {}).get("link")
    google_id = extract_google_id_from_link(link)

    return {
        "ok": True,
        "command": "open-doc-from-query",
        "query": query,
        "matched_by": found.get("matched_by"),
        "summary": found.get("summary"),
        "google_object_id": google_id,
        "find_result": found,
    }


def read_doc_from_query_payload(
    query: str,
    diagnose_payload_failure: Callable[[dict | None], tuple[str, str, str]],
    run_docs_agent_with_retry: Callable,
) -> dict:
    found = find_doc_any_payload(
        query, diagnose_payload_failure, run_docs_agent_with_retry
    )
    if not found.get("ok"):
        return found

    link = (found.get("summary") or {}).get("link")
    google_id = extract_google_id_from_link(link)

    if not google_id:
        return build_error_payload(
            command="read-doc-from-query",
            query=query,
            error_type="LinkParseError",
            error_message="Could not extract Google document ID from link.",
            summary=found.get("summary"),
        )

    read_result = run_docs_agent_with_retry(["read-doc", google_id])

    return {
        "ok": bool(read_result.get("ok")),
        "command": "read-doc-from-query",
        "query": query,
        "matched_by": found.get("matched_by"),
        "summary": found.get("summary"),
        "google_object_id": google_id,
        "find_result": found,
        "read_result": read_result,
    }
