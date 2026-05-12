import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path.home() / "AI" / "docs-agent"
DOCS_AGENT = BASE / "docs_agent.py"
PYTHON_BIN = sys.executable
MASTER_INDEX_ID = "1hyWNNzsIHRLGJ65urOQUA0x_kOqCP61OkXcM3MMyedw"
MASTER_INDEX_SHEET = "MASTER_INDEX"

EXIT_OK = 0
EXIT_USAGE_ERROR = 1
EXIT_NOT_FOUND = 2
EXIT_AUTH_ERROR = 3
EXIT_NETWORK_ERROR = 4
EXIT_INTERNAL_ERROR = 5
EXIT_INTERRUPTED = 130

COL_DOCUMENT_ID = 0
COL_DOCUMENT_NAME = 1
COL_LINK = 14

DOCS_AGENT_TIMEOUT_SEC = 60


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


MASTER_INDEX_CACHE_DIR = BASE / "cache" / "master_index"
MASTER_INDEX_CACHE_FILE = MASTER_INDEX_CACHE_DIR / "master_index_cache.json"
MASTER_INDEX_CACHE_TTL_SEC = 90


def now_epoch_int() -> int:
    import time

    return int(time.time())


def ensure_master_index_cache_dir() -> None:
    MASTER_INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_cell(v):
    if v is None:
        return ""
    return str(v).strip()


def safe_lower(v):
    return normalize_cell(v).lower()


def _cache_header_index(header):
    m = {}
    for i, name in enumerate(header):
        key = normalize_cell(name)
        if key:
            m[key] = i
    return m


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
    import json

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
    import json

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


def refresh_master_index_cache_via_docs_agent():
    seed = find_doc_any_payload_live("DOC-0001")
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
    t = tuple(row)
    if t in existing:
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


def summarize_payload_ok(payload: dict | None) -> bool:
    return isinstance(payload, dict) and bool(payload.get("ok"))


def safe_error_type(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return payload.get("error_type")


def safe_error_message(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    return payload.get("error_message")


def build_doctor_summary(
    *, env_ok: bool, status_ok: bool, master_index_ok: bool, smoke_ok: bool
) -> str:
    if env_ok and status_ok and master_index_ok and smoke_ok:
        return "CLI выглядит работоспособным: окружение, status, доступ к MASTER_INDEX и smoke-проверка прошли успешно."
    failed = []
    if not env_ok:
        failed.append("окружение")
    if not status_ok:
        failed.append("status")
    if not master_index_ok:
        failed.append("MASTER_INDEX")
    if not smoke_ok:
        failed.append("smoke")
    failed_text = ", ".join(failed)
    return f"Обнаружены проблемы в следующих зонах: {failed_text}."


def diagnose_payload_failure(payload: dict | None) -> tuple[str, str, str]:
    if not isinstance(payload, dict):
        return (
            "unknown",
            "Не удалось интерпретировать результат проверки.",
            "Повтори команду и проверь целостность CLI-вывода.",
        )

    if payload_contains_quota_or_rate_limit(payload):
        return (
            "network",
            "Похоже на временную внешнюю проблему или превышение квоты Google API.",
            "Подожди 60-90 секунд, сократи quota-sensitive запросы и повтори doctor/smoke.",
        )

    error_type = str(payload.get("error_type") or "")
    error_message = str(payload.get("error_message") or "")
    auth_related = bool(payload.get("auth_related"))
    network_related = bool(payload.get("network_related"))
    retryable = bool(payload.get("retryable"))

    attempts = payload.get("attempts") or []
    nested_messages = []
    nested_types = []
    if isinstance(attempts, list):
        for item in attempts:
            if isinstance(item, dict):
                et = str(item.get("error_type") or "")
                em = str(item.get("error_message") or "")
                if et:
                    nested_types.append(et)
                if em:
                    nested_messages.append(em)

    joined_text = " | ".join(
        [error_type, error_message] + nested_types + nested_messages
    ).lower()

    if auth_related:
        return (
            "auth",
            "Похоже на проблему авторизации или доступа к Google/API.",
            "Проверь учетные данные, токены, scopes и доступ к целевым объектам.",
        )

    if (
        network_related
        or retryable
        or "ssl" in joined_text
        or "eof occurred in violation of protocol" in joined_text
    ):
        return (
            "network",
            "Похоже на временную сетевую проблему или нестабильность внешнего API.",
            "Подожди и повтори проверку; если повторяется, проверь сеть и лимиты API.",
        )

    if error_type in {"NotFound", "LinkParseError"}:
        return (
            "not_found",
            "Похоже, CLI не смог найти документ или корректно извлечь идентификатор из ссылки.",
            "Проверь точный query/Document ID/ссылку и сначала выполни find-doc-any.",
        )

    if error_type in {
        "EmptyOutput",
        "JSONDecodeError",
        "TimeoutExpired",
        "SmokeCheckFailed",
    }:
        return (
            "internal",
            "Похоже на внутренний сбой CLI или дочернего docs_agent.py.",
            "Проверь debug-вывод, timeout, stdout/stderr и отдельно запусти status/doctor --json.",
        )

    return (
        "internal",
        "Похоже на внутренний сбой без точной классификации.",
        "Проверь debug-вывод и повтори диагностику через doctor --json.",
    )


def build_doctor_next_step(
    *, env_ok: bool, status_ok: bool, master_index_ok: bool, smoke_ok: bool
) -> str:
    if not env_ok:
        return "Проверь активацию venv и доступность python/agent_cli.py."
    if not status_ok:
        return "Сначала выполни python agent_cli.py status --json и проверь блоки safety/config."
    if not master_index_ok:
        return (
            "Проверь доступность MASTER_INDEX и повтори python agent_cli.py f DOC-0001."
        )
    if not smoke_ok:
        return "Запусти bash scripts/regression_smoke_quiet.sh отдельно и проверь, какой шаг падает."
    return "Можно начинать штатную работу."


def doctor_payload() -> dict:
    env = {
        "ok": bool(Path(PYTHON_BIN).exists() and DOCS_AGENT.exists() and BASE.exists()),
        "details": {
            "python_bin": str(PYTHON_BIN),
            "docs_agent_path": str(DOCS_AGENT),
            "base_path": str(BASE),
            "python_exists": Path(PYTHON_BIN).exists(),
            "docs_agent_exists": DOCS_AGENT.exists(),
            "base_exists": BASE.exists(),
        },
    }

    status = cmd_status_payload()
    master_index_lookup = find_doc_any_payload("DOC-0001")
    smoke_probe = run_smoke_explain_payload()

    checks = {
        "environment": env,
        "status": status,
        "master_index_lookup": master_index_lookup,
        "smoke_probe": smoke_probe,
    }

    failed = [k for k, v in checks.items() if not v.get("ok")]

    if not failed:
        return {
            "ok": True,
            "command": "doctor",
            "checks": checks,
            "summary": "CLI выглядит работоспособным: окружение, status, доступ к MASTER_INDEX и smoke-проверка прошли успешно.",
            "next_step": "Можно начинать штатную работу.",
            "diagnosis": "healthy",
            "likely_cause": "Проблем не обнаружено.",
            "recommended_action": "Можно начинать штатную работу.",
        }

    sample = checks[failed[0]]

    diagnosis = str(sample.get("diagnosis") or "internal")
    likely_cause = str(
        sample.get("likely_cause")
        or "Похоже на внутренний сбой CLI или дочернего docs_agent.py."
    )
    recommended_action = str(
        sample.get("recommended_action")
        or "Проверь debug-вывод и отдельно запусти doctor --json."
    )
    error_type = str(sample.get("error_type") or "DoctorCheckFailed")
    error_message = str(sample.get("error_message") or "doctor check failed")

    return {
        "ok": False,
        "command": "doctor",
        "checks": checks,
        "summary": f"Обнаружены проблемы в следующих зонах: {', '.join(failed)}.",
        "next_step": "Проверь diagnosis / likely_cause / recommended_action или запусти bash scripts/regression_smoke_explain.sh.",
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "error_type": error_type,
        "error_message": error_message,
        "retryable": bool(sample.get("retryable")),
        "auth_related": bool(sample.get("auth_related")),
        "network_related": bool(sample.get("network_related")),
    }


def doctor_lite_payload() -> dict:
    env = {
        "ok": bool(Path(PYTHON_BIN).exists() and DOCS_AGENT.exists() and BASE.exists()),
        "details": {
            "python_bin": str(PYTHON_BIN),
            "docs_agent_path": str(DOCS_AGENT),
            "base_path": str(BASE),
            "python_exists": Path(PYTHON_BIN).exists(),
            "docs_agent_exists": DOCS_AGENT.exists(),
            "base_exists": BASE.exists(),
        },
    }

    status = cmd_status_payload()
    master_index_lookup = find_doc_any_payload("DOC-0001")

    checks = {
        "environment": env,
        "status": status,
        "master_index_lookup": master_index_lookup,
    }

    failed = [k for k, v in checks.items() if not v.get("ok")]

    if not failed:
        return {
            "ok": True,
            "command": "doctor-lite",
            "checks": checks,
            "summary": "CLI выглядит работоспособным для рутинного старта: окружение, status и доступ к MASTER_INDEX проверены.",
            "next_step": "Можно начинать штатную работу. Для углубленной проверки при необходимости запусти doctor.",
            "diagnosis": "healthy",
            "likely_cause": "Проблем не обнаружено.",
            "recommended_action": "Можно начинать штатную работу.",
        }

    sample = checks[failed[0]]
    diagnosis = "internal"
    likely_cause = "Похоже на внутренний сбой CLI или дочернего docs_agent.py."
    recommended_action = "Проверь debug-вывод и отдельно запусти doctor --json."

    if sample.get("auth_related"):
        diagnosis = "auth"
        likely_cause = (
            "Похоже на проблему доступа, авторизации или прав к внешним сервисам."
        )
        recommended_action = "Проверь credentials, доступы и авторизацию."
    elif sample.get("network_related") or sample.get("retryable"):
        diagnosis = "network"
        likely_cause = "Похоже на временную сетевую проблему или квоту внешнего API."
        recommended_action = "Подожди 60-90 секунд и повтори doctor-lite/doctor."
    elif str(sample.get("error_type") or "") in {"NotFound", "LinkParseError"}:
        diagnosis = "not_found"
        likely_cause = "Похоже, обязательный объект не найден."
        recommended_action = "Проверь MASTER_INDEX и доступность ожидаемых объектов."

    return {
        "ok": False,
        "command": "doctor-lite",
        "checks": checks,
        "summary": f"Обнаружены проблемы в следующих зонах: {', '.join(failed)}.",
        "next_step": "Запусти doctor --json для расширенной диагностики.",
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "error_type": str(sample.get("error_type") or "DoctorLiteCheckFailed"),
        "error_message": str(sample.get("error_message") or "doctor-lite check failed"),
        "retryable": bool(sample.get("retryable")),
        "auth_related": bool(sample.get("auth_related")),
        "network_related": bool(sample.get("network_related")),
    }


def run_smoke_explain_payload() -> dict:
    script = BASE / "scripts" / "regression_smoke_explain.sh"
    if not script.exists():
        return build_error_payload(
            command="smoke-explain",
            error_type="ScriptNotFound",
            error_message="scripts/regression_smoke_explain.sh not found.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    cmd = ["bash", str(script)]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCS_AGENT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return build_error_payload(
            command="smoke-explain",
            error_type="TimeoutExpired",
            error_message=f"regression_smoke_explain.sh timed out after {DOCS_AGENT_TIMEOUT_SEC} seconds.",
            retryable=True,
            auth_related=False,
            network_related=True,
        )
    except Exception as exc:
        return build_error_payload(
            command="smoke-explain",
            error_type=exc.__class__.__name__,
            error_message=f"Failed to run regression_smoke_explain.sh: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    blob = f"{stdout}\n{stderr}".lower()

    diagnosis = "healthy"
    likely_cause = "Проблем не обнаружено."
    recommended_action = "Можно продолжать работу."

    if proc.returncode != 0:
        diagnosis = "internal"
        likely_cause = "Похоже на внутренний сбой smoke-проверки."
        recommended_action = "Запусти bash scripts/regression_smoke_explain.sh отдельно и проверь первый failing step."

        if (
            "quota" in blob
            or "429" in blob
            or "rate limit" in blob
            or "rate_limit" in blob
        ):
            diagnosis = "network"
            likely_cause = (
                "Похоже на временную внешнюю проблему или превышение квоты API."
            )
            recommended_action = "Подожди 60-90 секунд и повтори doctor/smoke."
        elif (
            "auth" in blob
            or "forbidden" in blob
            or "permission" in blob
            or "unauthorized" in blob
        ):
            diagnosis = "auth"
            likely_cause = (
                "Похоже на проблему доступа или авторизации к внешним сервисам."
            )
            recommended_action = "Проверь credentials, токены и права доступа."

    payload = {
        "ok": proc.returncode == 0,
        "command": "smoke-explain",
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "diagnosis": diagnosis,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "_debug": {
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
        },
    }

    if proc.returncode != 0:
        payload.update(
            {
                "error_type": "SmokeCheckFailed",
                "error_message": "regression_smoke_explain.sh returned non-zero exit code.",
                "retryable": diagnosis == "network",
                "auth_related": diagnosis == "auth",
                "network_related": diagnosis == "network",
            }
        )

    return payload


def print_compact_find(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: find-doc-any")
    print(f"query: {payload.get('query')}")
    summary = payload.get("summary") or {}
    if summary:
        print(f"document_id: {summary.get('document_id')}")
        print(f"document_name: {summary.get('document_name')}")
        print(f"link: {summary.get('link')}")


def print_compact_open(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: open-doc-from-query")
    print(f"query: {payload.get('query')}")
    print(f"google_object_id: {payload.get('google_object_id')}")
    summary = payload.get("summary") or {}
    if summary:
        print(f"document_id: {summary.get('document_id')}")
        print(f"document_name: {summary.get('document_name')}")
        print(f"link: {summary.get('link')}")


def print_compact_read(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: read-doc-from-query")
    print(f"query: {payload.get('query')}")
    summary = payload.get("summary") or {}
    if summary:
        print(f"document_id: {summary.get('document_id')}")
        print(f"document_name: {summary.get('document_name')}")
        print(f"link: {summary.get('link')}")

    read_result = payload.get("read_result") or {}
    content = read_result.get("content", "")
    if content:
        print("")
        print("content_preview:")
        preview = content[:1200]
        print(preview)
        if read_result.get("truncated") or len(content) > 1200:
            print("")
            print("[truncated]")


def print_compact_status(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: status")

    safety = payload.get("safety") or {}
    config = payload.get("config") or {}

    print(f"mode: {safety.get('mode')}")
    print(f"default_dry_run: {safety.get('default_dry_run')}")
    print(f"forbid_master_index_write: {safety.get('forbid_master_index_write')}")
    print(f"forbid_delete: {safety.get('forbid_delete')}")
    print(f"default_test_folder: {safety.get('default_test_folder')}")
    print(f"master_index_sheet: {config.get('master_index_sheet_name')}")
    print(f"master_index_id: {config.get('master_index_spreadsheet_id')}")
    print(f"change_log_sheet: {config.get('change_log_sheet_name')}")
    print(f"change_log_id: {config.get('change_log_spreadsheet_id')}")


def print_compact_doctor_lite(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: doctor-lite")
    print(
        f"environment_ok: {(payload.get('checks') or {}).get('environment', {}).get('ok')}"
    )
    print(f"status_ok: {(payload.get('checks') or {}).get('status', {}).get('ok')}")
    print(
        f"master_index_ok: {(payload.get('checks') or {}).get('master_index_lookup', {}).get('ok')}"
    )
    print(f"summary: {payload.get('summary')}")
    print(f"next_step: {payload.get('next_step')}")
    print(f"diagnosis: {payload.get('diagnosis')}")
    print(f"likely_cause: {payload.get('likely_cause')}")
    print(f"recommended_action: {payload.get('recommended_action')}")
    if not payload.get("ok"):
        print(f"error_type: {payload.get('error_type')}")
        print(f"error_message: {payload.get('error_message')}")


def print_compact_doctor(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: doctor")

    checks = payload.get("checks") or {}
    env_check = checks.get("environment") or {}
    status_check = checks.get("status") or {}
    mi_check = checks.get("master_index_lookup") or {}
    smoke_check = checks.get("smoke_probe") or {}

    print(f"environment_ok: {env_check.get('ok')}")
    print(f"status_ok: {status_check.get('ok')}")
    print(f"master_index_ok: {mi_check.get('ok')}")
    print(f"smoke_ok: {smoke_check.get('ok')}")
    print(f"summary: {payload.get('summary')}")
    print(f"next_step: {payload.get('next_step')}")

    if payload.get("diagnosis"):
        print(f"diagnosis: {payload.get('diagnosis')}")
    if payload.get("likely_cause"):
        print(f"likely_cause: {payload.get('likely_cause')}")
    if payload.get("recommended_action"):
        print(f"recommended_action: {payload.get('recommended_action')}")

    if not payload.get("ok"):
        print(f"error_type: {payload.get('error_type')}")
        print(f"error_message: {payload.get('error_message')}")


def is_retryable_network_error(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    if payload.get("network_related") is True and payload.get("retryable") is True:
        return True

    err = str(payload.get("error_type") or "")
    msg = str(payload.get("error_message") or "")

    retryable_error_types = {
        "SSLEOFError",
        "TimeoutError",
        "ConnectionResetError",
        "ServerNotFoundError",
    }

    if err in retryable_error_types:
        return True

    msg_upper = msg.upper()
    if "EOF" in msg_upper or "SSL" in msg_upper or "TIMEOUT" in msg_upper:
        return True

    return False


def run_docs_agent_with_retry(
    args: list[str], retries: int = 3, sleep_sec: float = 1.0
) -> dict:
    import time

    attempts = []
    last = None

    for attempt in range(1, retries + 1):
        payload = run_docs_agent(args)
        attempts.append(
            {
                "attempt": attempt,
                "ok": payload.get("ok"),
                "error_type": payload.get("error_type"),
                "error_message": payload.get("error_message"),
            }
        )
        last = payload

        if payload.get("ok"):
            payload["_retry"] = {
                "used": attempt > 1,
                "attempt_count": attempt,
                "attempts": attempts,
            }
            return payload

        if attempt < retries and is_retryable_network_error(payload):
            time.sleep(sleep_sec)
            continue

        break

    if isinstance(last, dict):
        last["_retry"] = {
            "used": len(attempts) > 1,
            "attempt_count": len(attempts),
            "attempts": attempts,
        }
    return last


def run_docs_agent(args: list[str]) -> dict:
    cmd = [PYTHON_BIN, str(DOCS_AGENT)] + args + ["--json-output"]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCS_AGENT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as exc:
        return build_error_payload(
            command="subprocess",
            error_type="TimeoutExpired",
            error_message=f"docs_agent.py timed out after {DOCS_AGENT_TIMEOUT_SEC} seconds.",
            retryable=True,
            auth_related=False,
            network_related=True,
            _debug={
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
                "stdout_preview": (exc.stdout or "")[:500] if exc.stdout else "",
                "stderr_preview": (exc.stderr or "")[:500] if exc.stderr else "",
            },
        )
    except Exception as exc:
        return build_error_payload(
            command="subprocess",
            error_type=exc.__class__.__name__,
            error_message=f"Failed to start docs_agent.py: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "cmd": cmd,
            },
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if not stdout:
        return build_error_payload(
            command="subprocess",
            error_type="EmptyOutput",
            error_message="No stdout from docs_agent.py.",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "returncode": proc.returncode,
                "stderr": stderr,
                "stdout_preview": stdout[:500],
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            },
        )

    try:
        data = json.loads(stdout)
    except Exception as exc:
        return build_error_payload(
            command="subprocess",
            error_type=exc.__class__.__name__,
            error_message="Failed to parse JSON output from docs_agent.py.",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "returncode": proc.returncode,
                "stderr": stderr,
                "stdout_preview": stdout[:1000],
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            },
        )

    if "_debug" not in data:
        data["_debug"] = {
            "returncode": proc.returncode,
            "stderr": stderr,
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
        }

    return data


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_compact_error_output(payload: dict) -> list[str]:
    lines: list[str] = []

    ok = payload.get("ok")
    command = payload.get("command")
    query = payload.get("query")
    error_type = str(payload.get("error_type") or "")
    error_message = str(payload.get("error_message") or "")
    retryable = bool(payload.get("retryable"))
    auth_related = bool(payload.get("auth_related"))
    network_related = bool(payload.get("network_related"))

    lines.append(f"ok: {ok}")
    lines.append(f"command: {command}")
    if query is not None:
        lines.append(f"query: {query}")
    lines.append(f"error_type: {error_type}")
    lines.append(f"error_message: {error_message}")
    lines.append(f"retryable: {retryable}")
    lines.append(f"auth_related: {auth_related}")
    lines.append(f"network_related: {network_related}")

    explanation = None
    next_step = None

    if error_type == "NotFound":
        explanation = "Похоже, документ или объект не найден в MASTER_INDEX по идентификатору, имени или фрагменту ссылки."
        next_step = "Проверь точное Document ID, точное имя документа или сначала выполни find-doc-any."
    elif error_type == "LinkParseError":
        explanation = (
            "CLI нашёл запись, но не смог извлечь корректный Google ID из ссылки."
        )
        next_step = "Проверь поле Link в MASTER_INDEX и формат ссылки на Google Docs/Sheets/Drive."
    elif auth_related:
        explanation = "Похоже, проблема связана с авторизацией или доступом к Google API / учётным данным."
        next_step = "Проверь активную авторизацию, credentials, токены и доступ к нужному Google Drive объекту."
    elif network_related and error_type == "TimeoutExpired":
        explanation = (
            "Вызов docs_agent.py превысил лимит ожидания и был прерван по таймауту."
        )
        next_step = "Повтори команду позже; если ошибка повторяется, проверь сеть, Google API и при необходимости увеличь timeout."
    elif network_related or retryable:
        explanation = (
            "Похоже, произошёл временный сетевой или нестабильный внешний сбой."
        )
        next_step = "Повтори команду; если ошибка повторяется, проверь сеть, доступ к Google API и stderr/_debug."
    elif error_type == "EmptyOutput":
        explanation = (
            "Внешний процесс docs_agent.py завершился без ожидаемого JSON-ответа."
        )
        next_step = "Проверь stderr/_debug, затем отдельно запусти docs_agent.py вручную и посмотри, почему stdout пустой."
    elif error_type == "JSONDecodeError":
        explanation = (
            "docs_agent.py вернул вывод, который не удалось разобрать как JSON."
        )
        next_step = "Проверь stdout_preview/stderr в _debug и убедись, что docs_agent.py печатает только валидный JSON."
    else:
        explanation = "Произошёл внутренний или нераспознанный сбой CLI/обёртки."
        next_step = "Проверь _debug, stderr и повтори сценарий через status / smoke / точечный вызов команды."

    lines.append(f"explanation: {explanation}")
    lines.append(f"next_step: {next_step}")
    return lines


def print_compact_error(payload: dict) -> None:
    print_human_lines(build_compact_error_output(payload))


def print_human_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


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


def cmd_status_payload() -> dict:
    safety = run_docs_agent_with_retry(["show-safety-mode"])
    config = run_docs_agent_with_retry(["show-config-status"])
    return {
        "ok": bool(safety.get("ok")) and bool(config.get("ok")),
        "command": "status",
        "safety": safety,
        "config": config,
    }


def cmd_status(json_output: bool = False) -> int:
    payload = cmd_status_payload()
    if json_output:
        print_json(payload)
    else:
        print_compact_status(payload)
    return resolve_command_exit_code(payload)


def cmd_doctor(json_output: bool = False) -> int:
    payload = doctor_payload()
    if json_output:
        print_json(payload)
    else:
        print_compact_doctor(payload)
    return resolve_command_exit_code(payload)


def cmd_find_doc_id(value: str) -> None:
    payload = run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document ID",
            value,
        ]
    )
    print_json(payload)


def cmd_find_doc_name(value: str) -> None:
    payload = run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document Name",
            value,
        ]
    )
    print_json(payload)


def cmd_find_link(value: str) -> None:
    payload = run_docs_agent_with_retry(
        [
            "find-row-by-link-fragment",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            value,
        ]
    )
    print_json(payload)


def cmd_get_file(file_id: str) -> None:
    payload = run_docs_agent_with_retry(
        [
            "get-file",
            file_id,
        ]
    )
    print_json(payload)


def cmd_read_doc(document_id: str) -> None:
    payload = run_docs_agent_with_retry(
        [
            "read-doc",
            document_id,
        ]
    )
    print_json(payload)


def _find_doc_any_payload_live_impl(query: str) -> dict:
    attempts = []

    by_id = run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document ID",
            query,
        ]
    )
    attempts.append(summarize_attempt("Document ID", by_id))
    if by_id.get("ok") and by_id.get("matches_found", 0) > 0:
        return build_find_doc_success_payload(
            query=query,
            matched_by="Document ID",
            result=by_id,
            attempts=attempts,
        )

    by_name = run_docs_agent_with_retry(
        [
            "find-row-by-column",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            "Document Name",
            query,
        ]
    )
    attempts.append(summarize_attempt("Document Name", by_name))
    if by_name.get("ok") and by_name.get("matches_found", 0) > 0:
        return build_find_doc_success_payload(
            query=query,
            matched_by="Document Name",
            result=by_name,
            attempts=attempts,
        )

    by_link = run_docs_agent_with_retry(
        [
            "find-row-by-link-fragment",
            MASTER_INDEX_ID,
            MASTER_INDEX_SHEET,
            query,
        ]
    )
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


def resolve_exit_code(payload: dict | None) -> int:
    if not isinstance(payload, dict):
        return EXIT_INTERNAL_ERROR

    if payload.get("ok") is True:
        return EXIT_OK

    error_type = str(payload.get("error_type") or "")
    retryable = bool(payload.get("retryable"))
    auth_related = bool(payload.get("auth_related"))
    network_related = bool(payload.get("network_related"))

    if auth_related:
        return EXIT_AUTH_ERROR

    if network_related or retryable:
        return EXIT_NETWORK_ERROR

    if error_type in {"NotFound", "LinkParseError"}:
        return EXIT_NOT_FOUND

    if error_type in {"EmptyOutput", "JSONDecodeError", "TimeoutExpired"}:
        return EXIT_INTERNAL_ERROR

    return EXIT_INTERNAL_ERROR


def find_doc_any_payload_live(query):
    return _find_doc_any_payload_live_impl(query)


def find_doc_any_payload(query):
    cached = find_doc_any_payload_from_cache(query)
    if isinstance(cached, dict) and cached.get("ok"):
        return cached

    if load_master_index_cache() is None:
        refresh_master_index_cache_via_docs_agent()
        cached = find_doc_any_payload_from_cache(query)
        if isinstance(cached, dict) and cached.get("ok"):
            return cached

    live = find_doc_any_payload_live(query)
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


def resolve_command_exit_code(payload: dict | None) -> int:
    if not isinstance(payload, dict):
        return EXIT_INTERNAL_ERROR

    if payload.get("ok") is True:
        return EXIT_OK

    if payload.get("command") == "ask":
        result = payload.get("result")
        if isinstance(result, dict):
            return resolve_exit_code(result)

    return resolve_exit_code(payload)


def print_usage_error(message: str) -> None:
    print("ok: False")
    print("command: usage")
    print("error_type: UsageError")
    print(f"error_message: {message}")
    print("")
    usage()


def build_error_payload(
    *,
    command: str,
    query: str | None = None,
    error_type: str,
    error_message: str,
    retryable: bool = False,
    auth_related: bool = False,
    network_related: bool = False,
    **extra,
) -> dict:
    payload = {
        "ok": False,
        "command": command,
        "error_type": error_type,
        "error_message": error_message,
        "retryable": retryable,
        "auth_related": auth_related,
        "network_related": network_related,
    }
    if query is not None:
        payload["query"] = query
    payload.update(extra)
    return payload


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


def open_doc_from_query_payload(query: str) -> dict:
    found = find_doc_any_payload(query)
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


def read_doc_from_query_payload(query: str) -> dict:
    found = find_doc_any_payload(query)
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


def cmd_find_doc_any(query: str, json_output: bool = False) -> int:
    payload = find_doc_any_payload(query)
    if json_output:
        print_json(payload)
    else:
        if payload.get("ok"):
            print_compact_find(payload)
        else:
            print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_open_doc_from_query(query: str, json_output: bool = False) -> int:
    payload = open_doc_from_query_payload(query)
    if json_output:
        print_json(payload)
    else:
        if payload.get("ok"):
            print_compact_open(payload)
        else:
            print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_read_doc_from_query(query: str, json_output: bool = False) -> int:
    payload = read_doc_from_query_payload(query)
    if json_output:
        print_json(payload)
    else:
        if payload.get("ok"):
            print_compact_read(payload)
        else:
            print_compact_error(payload)
    return resolve_command_exit_code(payload)


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


def ask_status_payload(query: str) -> dict:
    result = cmd_status_payload()
    return build_ask_result(query, "status", result)


def ask_read_payload(query: str, lookup_query: str) -> dict:
    result = read_doc_from_query_payload(lookup_query)
    return build_ask_result(query, "read-doc-from-query", result)


def ask_google_id_payload(query: str, lookup_query: str) -> dict:
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


def ask_find_payload(query: str, lookup_query: str) -> dict:
    found = find_doc_any_payload(lookup_query)
    return build_ask_result(query, "find-doc-any", found)


def ask_payload(query: str) -> dict:
    q = query.strip()
    ql = q.lower()
    lookup_query = normalize_query_for_lookup(q)

    if is_status_query(ql):
        return ask_status_payload(query)

    if is_read_query(ql):
        return ask_read_payload(query, lookup_query)

    if looks_like_google_id(lookup_query):
        return ask_google_id_payload(query, lookup_query)

    return ask_find_payload(query, lookup_query)


def build_compact_ask_output(payload: dict) -> list[str]:
    lines: list[str] = []
    ok = payload.get("ok", False)
    routed = payload.get("routed_to", "unknown")
    query = payload.get("query", "")

    lines.append(f"ok: {ok}")
    lines.append(f"route: {routed}")
    lines.append(f"query: {query}")

    if routed == "status":
        result = payload.get("result", {})
        safety = result.get("safety", {})
        config = result.get("config", {})
        lines.append(f"mode: {safety.get('mode')}")
        lines.append(f"default_test_folder: {safety.get('default_test_folder')}")
        lines.append(
            f"master_index: {config.get('master_index_sheet_name')} / {config.get('master_index_spreadsheet_id')}"
        )
        return lines

    if routed in {"find-doc-any", "get-file"}:
        result = payload.get("result", {})

        if not result.get("ok"):
            lines.append(f"error_type: {result.get('error_type')}")
            lines.append(f"error_message: {result.get('error_message')}")
            if result.get("error_type") == "NotFound":
                lines.append(
                    "explanation: По запросу ничего не найдено в индексе или в файловом поиске."
                )
                lines.append(
                    "next_step: Уточни идентификатор, имя документа или сначала выполни find-doc-any."
                )
            elif result.get("network_related") or result.get("retryable"):
                lines.append(
                    "explanation: Похоже на временный сетевой сбой при поиске."
                )
                lines.append("next_step: Повтори команду или проверь status --json.")
            else:
                lines.append("explanation: Поиск завершился ошибкой.")
                lines.append(
                    "next_step: Запусти команду в JSON-режиме и посмотри debug-поля."
                )
            return lines

        if result.get("command") == "find-doc-any":
            summary = result.get("summary", {})
            lines.append(f"document_id: {summary.get('document_id')}")
            lines.append(f"document_name: {summary.get('document_name')}")
            lines.append(f"link: {summary.get('link')}")
            return lines

        if result.get("command") == "get-file":
            f = result.get("file", {})
            lines.append(f"file_id: {f.get('id')}")
            lines.append(f"name: {f.get('name')}")
            lines.append(f"mime: {f.get('mimeType')}")
            lines.append(f"link: {f.get('webViewLink')}")
            return lines

    if routed == "read-doc-from-query":
        result = payload.get("result", {})
        if not result.get("ok"):
            error_type = str(result.get("error_type") or "")
            error_message = str(result.get("error_message") or "")
            retryable = bool(result.get("retryable"))
            auth_related = bool(result.get("auth_related"))
            network_related = bool(result.get("network_related"))

            lines.append(f"error_type: {error_type}")
            lines.append(f"error_message: {error_message}")

            explanation = None
            next_step = None

            if error_type == "NotFound":
                explanation = "CLI попытался найти документ для чтения, но не нашел его в MASTER_INDEX."
                next_step = "Проверь точное имя/Document ID или сначала выполни python agent_cli.py f <query>."
            elif error_type == "LinkParseError":
                explanation = "CLI нашёл запись для чтения, но не смог извлечь Google ID из ссылки."
                next_step = "Проверь link в MASTER_INDEX для найденного документа."
            elif auth_related:
                explanation = "Чтение документа не удалось из-за проблемы авторизации или прав доступа."
                next_step = (
                    "Проверь авторизацию Google API и права доступа к документу."
                )
            elif network_related and error_type == "TimeoutExpired":
                explanation = "Чтение документа прервано по таймауту при обращении к docs_agent.py или внешнему API."
                next_step = "Повтори команду позже; если ошибка повторяется, проверь сеть и доступность Google API."
            elif network_related or retryable:
                explanation = (
                    "Во время чтения документа произошёл временный сетевой сбой."
                )
                next_step = (
                    "Повтори команду; если сбой стабилен, проверь сеть и _debug."
                )
            elif error_type == "EmptyOutput":
                explanation = (
                    "docs_agent.py не вернул ожидаемый JSON при чтении документа."
                )
                next_step = "Проверь stderr/_debug и отдельно запусти docs_agent.py read-doc вручную."
            elif error_type == "JSONDecodeError":
                explanation = (
                    "Ответ docs_agent.py при чтении документа оказался невалидным JSON."
                )
                next_step = "Проверь stdout_preview/stderr в _debug."
            else:
                explanation = "Во время чтения документа произошёл внутренний или нераспознанный сбой."
                next_step = "Проверь _debug и повтори сценарий через status и точечный read-doc вызов."

            lines.append(f"explanation: {explanation}")
            lines.append(f"next_step: {next_step}")
            return lines

        summary = result.get("summary", {}) or {}
        read_result = result.get("read_result", {}) or {}
        content = read_result.get("content", "") or ""
        content_preview = content[:800]

        lines.append(f"document_id: {summary.get('document_id')}")
        lines.append(f"document_name: {summary.get('document_name')}")
        lines.append(f"link: {summary.get('link')}")
        lines.append("")
        lines.append("content_preview:")
        lines.append(content_preview)
        if read_result.get("truncated"):
            lines.append("")
            lines.append("[truncated]")
        return lines

    if not ok:
        result = payload.get("result", {})
        lines.append(
            f"error_type: {result.get('error_type') or payload.get('error_type')}"
        )
        lines.append(
            f"error_message: {result.get('error_message') or payload.get('error_message')}"
        )
        lines.append("explanation: Запрос маршрутизирован, но завершился ошибкой.")
        lines.append("next_step: Повтори команду в JSON-режиме и проверь debug-поля.")
        return lines

    lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
    return lines


def cmd_doctor_lite(json_output: bool = False) -> int:
    payload = doctor_lite_payload()
    if json_output:
        print_json(payload)
    else:
        print_compact_doctor_lite(payload)
    return resolve_command_exit_code(payload)


def cmd_ask(query: str, json_output: bool = False) -> int:
    payload = ask_payload(query)
    if json_output:
        print_json(payload)
    else:
        print_human_lines(build_compact_ask_output(payload))
    return resolve_command_exit_code(payload)


def parse_json_flag(argv: list[str]) -> tuple[bool, list[str]]:
    json_output = False
    args = argv[:]
    if args and args[0] == "--json":
        json_output = True
        args = args[1:]
    return json_output, args


def require_query_args(
    argv: list[str], allow_json_flag: bool = False
) -> tuple[bool, list[str]] | None:
    args = argv[:]
    if allow_json_flag:
        _, args = parse_json_flag(args)
    if not args:
        return None
    return True, args


def handle_query_command(
    argv: list[str],
    handler,
    *,
    allow_json_flag: bool = False,
) -> int:
    if allow_json_flag:
        json_output, args = parse_json_flag(argv)
    else:
        json_output, args = False, argv[:]

    if not args:
        print_usage_error("Missing query argument.")
        return EXIT_USAGE_ERROR

    value = " ".join(args)
    if allow_json_flag:
        return handler(value, json_output=json_output)
    return handler(value)


def run_query_command(
    argv: list[str],
    handler,
) -> int:
    json_output, args = parse_json_flag(argv)
    if not args:
        usage()
        return 1
    value = " ".join(args)
    handler(value, json_output=json_output)
    return 0


def usage() -> None:
    print(
        "Usage:\n"
        "  python agent_cli.py status [--json]\n"
        "  python agent_cli.py doctor [--json]        | diagnose [--json]\n"
        "  python agent_cli.py find-doc-id <DOC-XXXX>\n"
        "  python agent_cli.py find-doc-name <document name>\n"
        "  python agent_cli.py find-link <drive_id_or_url_fragment>\n"
        "  python agent_cli.py find-doc-any [--json] <query>        | f [--json] <query>\n"
        "  python agent_cli.py open-doc-from-query [--json] <query> | o [--json] <query>\n"
        "  python agent_cli.py read-doc-from-query [--json] <query> | r [--json] <query>\n"
        "  python agent_cli.py get-file <google_drive_file_id>\n"
        "  python agent_cli.py read-doc <google_doc_id>\n"
        "  python agent_cli.py ask [--json] <free text query>       | q [--json] <query>\n"
        "\n"
        "Examples:\n"
        "  python agent_cli.py status\n"
        "  python agent_cli.py status --json\n"
        "  python agent_cli.py f DOC-0001\n"
        "  python agent_cli.py o DOC-0002\n"
        "  python agent_cli.py r DOC-0002\n"
        '  python agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"\n'
        '  python agent_cli.py q "прочитай DOC-0002"\n'
        '  python agent_cli.py q --json "прочитай 00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"\n'
        "  python agent_cli.py doctor\n"
        "  python agent_cli.py doctor --json\n"
    )


def run_query_handler(argv: list[str], handler) -> int:
    json_output, args = parse_json_flag(argv)
    if not args:
        usage()
        return 1

    value = " ".join(args)
    handler(value, json_output=json_output)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print_usage_error("Missing command.")
        return EXIT_USAGE_ERROR

    cmd = sys.argv[1]
    argv = sys.argv[2:]

    try:
        if cmd == "status":
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("status does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_status(json_output=json_output)

        if cmd in {"doctor-lite", "diagnose-lite"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("doctor-lite does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_doctor_lite(json_output=json_output)

        if cmd in {"doctor", "diagnose"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("doctor does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_doctor(json_output=json_output)

        if cmd in {"doctor", "diagnose"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("doctor does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_doctor(json_output=json_output)

        if cmd == "find-doc-id":
            if len(argv) < 1:
                print_usage_error("Missing DOC-XXXX argument.")
                return EXIT_USAGE_ERROR
            cmd_find_doc_id(argv[0])
            return EXIT_OK

        if cmd == "find-doc-name":
            return handle_query_command(argv, cmd_find_doc_name)

        if cmd == "find-link":
            return handle_query_command(argv, cmd_find_link)

        if cmd in {"find-doc-any", "f"}:
            return handle_query_command(argv, cmd_find_doc_any, allow_json_flag=True)

        if cmd in {"open-doc-from-query", "o"}:
            return handle_query_command(
                argv, cmd_open_doc_from_query, allow_json_flag=True
            )

        if cmd in {"read-doc-from-query", "r"}:
            return handle_query_command(
                argv, cmd_read_doc_from_query, allow_json_flag=True
            )

        if cmd == "get-file":
            if len(argv) < 1:
                print_usage_error("Missing google_drive_file_id argument.")
                return EXIT_USAGE_ERROR
            cmd_get_file(argv[0])
            return EXIT_OK

        if cmd == "read-doc":
            if len(argv) < 1:
                print_usage_error("Missing google_doc_id argument.")
                return EXIT_USAGE_ERROR
            cmd_read_doc(argv[0])
            return EXIT_OK

        if cmd in {"ask", "q"}:
            return handle_query_command(argv, cmd_ask, allow_json_flag=True)

        print_usage_error(f"Unknown command: {cmd}")
        return EXIT_USAGE_ERROR

    except KeyboardInterrupt:
        print_json(
            {
                "ok": False,
                "command": cmd,
                "error_type": "KeyboardInterrupt",
                "error_message": "Interrupted by user",
                "retryable": True,
                "auth_related": False,
                "network_related": False,
            }
        )
        return EXIT_INTERRUPTED


if __name__ == "__main__":
    raise SystemExit(main())
