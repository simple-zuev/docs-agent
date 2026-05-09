from pathlib import Path
import re
import sys

p = Path("agent_cli.py")
src = p.read_text(encoding="utf-8")

anchor = "MASTER_INDEX_CACHE_TTL_SEC = 90"
if anchor not in src:
    print("stage29 cache anchor not found")
    sys.exit(1)

insert_after = anchor + "\n"

block = r'''
MASTER_INDEX_CACHE_MODE = "stage30-full-sheet-cache"

def _extract_spreadsheet_config_from_status():
    status = cmd_status_payload()
    config = (status or {}).get("config") or {}
    spreadsheet_id = config.get("master_index_spreadsheet_id")
    sheet_name = config.get("master_index_sheet_name") or "MASTER_INDEX"
    if spreadsheet_id and sheet_name:
        return str(spreadsheet_id), str(sheet_name)
    return None, None

def fetch_master_index_full_sheet_live():
    spreadsheet_id, sheet_name = _extract_spreadsheet_config_from_status()
    if not spreadsheet_id or not sheet_name:
        return build_error_payload(
            command="master-index-full-fetch",
            error_type="ConfigError",
            error_message="Could not resolve master index spreadsheet id/sheet name from status config.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    cmd = [
        str(PYTHON_BIN),
        str(DOCS_AGENT),
        "read-sheet-values",
        spreadsheet_id,
        sheet_name,
        "--json-output",
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCS_AGENT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return build_error_payload(
            command="master-index-full-fetch",
            error_type="TimeoutExpired",
            error_message=f"read-sheet-values timed out after {DOCS_AGENT_TIMEOUT_SEC} seconds.",
            retryable=True,
            auth_related=False,
            network_related=True,
        )
    except Exception as exc:
        return build_error_payload(
            command="master-index-full-fetch",
            error_type=exc.__class__.__name__,
            error_message=f"Failed to run read-sheet-values: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        payload = build_error_payload(
            command="master-index-full-fetch",
            error_type="SubprocessError",
            error_message=f"read-sheet-values returned rc={proc.returncode}",
            retryable=False,
            auth_related=False,
            network_related=False,
        )
        payload["_debug"] = {
            "stdout": stdout[:1000],
            "stderr": stderr[:1000],
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            "returncode": proc.returncode,
        }
        if payload_contains_quota_or_rate_limit({"stdout": stdout, "stderr": stderr}):
            payload["retryable"] = True
            payload["network_related"] = True
            payload["diagnosis"] = "network"
            payload["likely_cause"] = "Похоже на временную внешнюю проблему или превышение квоты Google API."
            payload["recommended_action"] = "Подожди 60-90 секунд, сократи quota-sensitive запросы и повтори попытку."
        return payload

    try:
        data = json.loads(stdout)
    except Exception as exc:
        payload = build_error_payload(
            command="master-index-full-fetch",
            error_type="JSONDecodeError",
            error_message=f"Could not parse read-sheet-values output: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
        )
        payload["_debug"] = {
            "stdout": stdout[:1000],
            "stderr": stderr[:1000],
            "cmd": cmd,
        }
        return payload

    values = data.get("values") or []
    if not isinstance(values, list) or not values:
        return build_error_payload(
            command="master-index-full-fetch",
            error_type="EmptySheet",
            error_message="MASTER_INDEX sheet returned no rows.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    header = values[0] if isinstance(values[0], list) else []
    rows = values[1:] if len(values) > 1 else []

    if not header:
        return build_error_payload(
            command="master-index-full-fetch",
            error_type="EmptyHeader",
            error_message="MASTER_INDEX sheet returned empty header row.",
            retryable=False,
            auth_related=False,
            network_related=False,
        )

    payload = {
        "ok": True,
        "command": "master-index-full-fetch",
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "header": header,
        "rows": rows,
        "rows_count": len(rows),
        "_debug": {
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            "returncode": proc.returncode,
        },
    }
    return payload

def refresh_master_index_cache_via_docs_agent():
    live = fetch_master_index_full_sheet_live()
    if not isinstance(live, dict) or not live.get("ok"):
        return live

    save_master_index_cache(
        {
            "fetched_at_epoch": now_epoch_int(),
            "header": live.get("header") or [],
            "rows": live.get("rows") or [],
            "mode": MASTER_INDEX_CACHE_MODE,
            "rows_count": live.get("rows_count") or 0,
        }
    )

    return {
        "ok": True,
        "command": "master-index-cache-refresh",
        "rows_cached": live.get("rows_count") or 0,
        "cache_file": str(MASTER_INDEX_CACHE_FILE),
        "mode": MASTER_INDEX_CACHE_MODE,
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
    cache["rows_count"] = len(rows)
    cache["fetched_at_epoch"] = now_epoch_int()
    save_master_index_cache(cache)
'''

if "MASTER_INDEX_CACHE_MODE = " not in src:
    src = src.replace(insert_after, insert_after + block + "\n", 1)

# remove old stage29 seed header_guess block if present by replacing old refresh function entirely
m = re.search(
    r"def refresh_master_index_cache_via_docs_agent\(\):\n(?P<body>.*?)(?=\ndef [A-Za-z_][A-Za-z0-9_]*\()",
    src,
    flags=re.DOTALL,
)
if not m:
    print("refresh_master_index_cache_via_docs_agent not found")
    sys.exit(1)

new_refresh = '''
def refresh_master_index_cache_via_docs_agent():
    live = fetch_master_index_full_sheet_live()
    if not isinstance(live, dict) or not live.get("ok"):
        return live

    save_master_index_cache(
        {
            "fetched_at_epoch": now_epoch_int(),
            "header": live.get("header") or [],
            "rows": live.get("rows") or [],
            "mode": MASTER_INDEX_CACHE_MODE,
            "rows_count": live.get("rows_count") or 0,
        }
    )

    return {
        "ok": True,
        "command": "master-index-cache-refresh",
        "rows_cached": live.get("rows_count") or 0,
        "cache_file": str(MASTER_INDEX_CACHE_FILE),
        "mode": MASTER_INDEX_CACHE_MODE,
    }
'''.strip() + "\n"
src = src[:m.start()] + new_refresh + src[m.end():]

p.write_text(src, encoding="utf-8")
print("patched", p)
