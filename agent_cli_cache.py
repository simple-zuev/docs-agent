from __future__ import annotations

import json
import time
from typing import Callable

from agent_cli_output import build_error_payload
from agent_cli_subprocess import BASE


MASTER_INDEX_CACHE_DIR = BASE / "cache" / "master_index"
MASTER_INDEX_CACHE_FILE = MASTER_INDEX_CACHE_DIR / "master_index_cache.json"
MASTER_INDEX_CACHE_TTL_SEC = 90


def now_epoch_int() -> int:
    return int(time.time())


def ensure_master_index_cache_dir() -> None:
    MASTER_INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_cell(value):
    if value is None:
        return ""
    return str(value).strip()


def safe_lower(value):
    return normalize_cell(value).lower()


def _cache_header_index(header):
    result = {}
    for i, name in enumerate(header):
        key = normalize_cell(name)
        if key:
            result[key] = i
    return result


def _row_value_by_name(row, idx_map, column_name):
    idx = idx_map.get(column_name)
    if idx is None:
        return ""
    if idx >= len(row):
        return ""
    return normalize_cell(row[idx])


def _build_find_doc_any_success_from_cache(query, row, row_number, header):
    idx_map = _cache_header_index(header)
    document_id = _row_value_by_name(row, idx_map, "Document ID")
    document_name = _row_value_by_name(row, idx_map, "Document Name")
    link = _row_value_by_name(row, idx_map, "Link")
    folder = _row_value_by_name(row, idx_map, "Folder")

    matched_by = None
    q = normalize_cell(query)
    ql = q.lower()

    if safe_lower(document_id) == ql:
        matched_by = "Document ID"
    elif safe_lower(document_name) == ql:
        matched_by = "Document Name"
    elif ql and ql in safe_lower(link):
        matched_by = "Link fragment"
    else:
        matched_by = "Cache local search"

    return {
        "ok": True,
        "command": "find-doc-any",
        "query": q,
        "matched_by": matched_by,
        "result": {
            "ok": True,
            "command": "master-index-cache-local-search",
            "matches_found": 1,
            "matches": [
                {
                    "row_number": row_number,
                    "row_values": row,
                }
            ],
        },
        "summary": {
            "document_id": document_id,
            "document_name": document_name,
            "link": link,
            "folder": folder,
        },
        "attempts": [
            {
                "strategy": matched_by,
                "ok": True,
                "matches_found": 1,
                "error_type": None,
                "error_message": None,
            }
        ],
        "cache": {
            "used": True,
            "cache_file": str(MASTER_INDEX_CACHE_FILE),
            "ttl_sec": MASTER_INDEX_CACHE_TTL_SEC,
        },
    }


def _build_find_doc_any_not_found_from_cache(query):
    return {
        "ok": False,
        "command": "find-doc-any",
        "query": normalize_cell(query),
        "error_type": "NotFound",
        "error_message": "No matches found by Document ID, Document Name, or Link fragment.",
        "retryable": False,
        "auth_related": False,
        "network_related": False,
        "explanation": "Похоже, документ или объект не найден в MASTER_INDEX по идентификатору, имени или фрагменту ссылки.",
        "next_step": "Проверь точное Document ID, точное имя документа или сначала выполни find-doc-any.",
        "attempts": [
            {
                "strategy": "MASTER_INDEX cache local search",
                "ok": False,
                "matches_found": 0,
                "error_type": "NotFound",
                "error_message": "No matches found by Document ID, Document Name, or Link fragment.",
            }
        ],
        "cache": {
            "used": True,
            "cache_file": str(MASTER_INDEX_CACHE_FILE),
            "ttl_sec": MASTER_INDEX_CACHE_TTL_SEC,
        },
    }


def load_master_index_cache():
    if not MASTER_INDEX_CACHE_FILE.exists():
        return None
    try:
        data = json.loads(MASTER_INDEX_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None

    fetched_at = int(data.get("fetched_at_epoch") or 0)
    if fetched_at <= 0:
        return None

    age = now_epoch_int() - fetched_at
    if age > MASTER_INDEX_CACHE_TTL_SEC:
        return None

    header = data.get("header") or []
    rows = data.get("rows") or []
    if not isinstance(header, list) or not isinstance(rows, list) or not header:
        return None

    return data


def save_master_index_cache(payload):
    ensure_master_index_cache_dir()
    MASTER_INDEX_CACHE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _parse_master_index_rows_from_live_result(live_result):
    result = (live_result or {}).get("result") or {}
    matches = result.get("matches") or []
    if not matches:
        return None

    row_values = matches[0].get("row_values") or []
    if not isinstance(row_values, list) or len(row_values) < 3:
        return None

    return row_values


def refresh_master_index_cache(fetch_seed: Callable[[str], dict]):
    seed = fetch_seed("DOC-0001")
    if not isinstance(seed, dict) or not seed.get("ok"):
        return seed

    row = _parse_master_index_rows_from_live_result(seed)
    if not row:
        return build_error_payload(
            command="master-index-cache-refresh",
            error_type="CacheSeedParseError",
            error_message="Could not parse initial MASTER_INDEX cache seed.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    header_guess = [
        "Document ID",
        "Document Name",
        "Type",
        "Baseline",
        "Status Class",
        "Status",
        "Folder",
        "Owner",
        "Purpose",
        "ADR",
        "Review Cadence",
        "Last Review Date",
        "Criticality",
        "Description",
        "Link",
    ]

    save_master_index_cache(
        {
            "fetched_at_epoch": now_epoch_int(),
            "header": header_guess,
            "rows": [row],
            "mode": "stage29-seed-cache",
        }
    )

    return {
        "ok": True,
        "command": "master-index-cache-refresh",
        "rows_cached": 1,
        "cache_file": str(MASTER_INDEX_CACHE_FILE),
        "mode": "stage29-seed-cache",
    }


def extend_master_index_cache_from_success(payload):
    cache = load_master_index_cache()
    if cache is None:
        return

    row = _parse_master_index_rows_from_live_result(payload)
    if not row:
        return

    rows = cache.get("rows") or []
    existing = {tuple(r) for r in rows if isinstance(r, list)}
    row_tuple = tuple(row)
    if row_tuple in existing:
        return

    rows.append(row)
    cache["rows"] = rows
    cache["fetched_at_epoch"] = now_epoch_int()
    save_master_index_cache(cache)


def find_doc_any_payload_from_cache(query):
    cache = load_master_index_cache()
    if cache is None:
        return None

    header = cache.get("header") or []
    rows = cache.get("rows") or []

    q = normalize_cell(query)
    ql = q.lower()

    idx_map = _cache_header_index(header)

    for i, row in enumerate(rows, start=2):
        if not isinstance(row, list):
            continue

        document_id = _row_value_by_name(row, idx_map, "Document ID")
        document_name = _row_value_by_name(row, idx_map, "Document Name")
        link = _row_value_by_name(row, idx_map, "Link")

        if safe_lower(document_id) == ql:
            return _build_find_doc_any_success_from_cache(q, row, i, header)

        if safe_lower(document_name) == ql:
            return _build_find_doc_any_success_from_cache(q, row, i, header)

        if ql and ql in safe_lower(link):
            return _build_find_doc_any_success_from_cache(q, row, i, header)

    return _build_find_doc_any_not_found_from_cache(q)
