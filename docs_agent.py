import json
from pathlib import Path


import typer
import yaml
from datetime import datetime
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

app = typer.Typer()

BASE = Path.home() / "AI" / "docs-agent"
CLIENT_SECRET = BASE / "config" / "client_secret.json"
TOKEN_FILE = BASE / "config" / "token.json"
CACHE_DIR = BASE / "cache"
REPORTS_DIR = BASE / "reports"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
]

CHANGE_LOG_ID = "1-6F5MCJR2EkP74pROsYXsPMmu1zPwp82hl0mDi9U3EQ"



CONFIG_PATH = BASE / "config" / "config.yml"

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def config_get(path, default=None):
    cfg = load_config()
    cur = cfg
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def is_readonly_mode():
    return config_get("safety.mode", "readonly") == "readonly"

def is_default_dry_run():
    return bool(config_get("safety.default_dry_run", True))

def ensure_write_allowed(operation_name: str, target: str = ""):
    if is_readonly_mode():
        suffix = f" Target: {target}" if target else ""
        raise RuntimeError(f"Write operation blocked in readonly mode: {operation_name}.{suffix}")

def ensure_master_index_write_allowed():
    if bool(config_get("safety.forbid_master_index_write", True)):
        raise RuntimeError("Master Index write is forbidden by config")

def get_master_index_id():
    return config_get("documents.master_index_spreadsheet_id")

def get_master_index_sheet():
    return config_get("documents.master_index_sheet_name", "MASTER_INDEX")

def get_change_log_id():
    return config_get("documents.change_log_spreadsheet_id", CHANGE_LOG_ID)

def get_change_log_sheet():
    return config_get("documents.change_log_sheet_name", "Change Log Lite")



def normalize_jsonable(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)

def emit_json(payload: dict):
    print(json.dumps(payload, ensure_ascii=False, indent=2))

@app.command("read-sheet-values")
def read_sheet_values(
    spreadsheet_id: str,
    sheet_name: str,
    json_output: bool = typer.Option(False, "--json-output"),
):
    """
    Read all values from a Google Sheet tab and optionally return JSON.
    """
    try:
        service = get_sheets_service()
        rng = f"'{sheet_name}'!A:ZZ"
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=rng,
            )
            .execute()
        )
        values = result.get("values", []) or []

        payload = {
            "ok": True,
            "command": "read-sheet-values",
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "range": rng,
            "values": values,
            "rows_count": len(values),
        }

        if json_output:
            emit_json(payload)
            return

        print(f"ok: {payload['ok']}")
        print(f"command: {payload['command']}")
        print(f"spreadsheet_id: {spreadsheet_id}")
        print(f"sheet_name: {sheet_name}")
        print(f"rows_count: {len(values)}")

    except Exception as exc:
        payload = {
            "ok": False,
            "command": "read-sheet-values",
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }

        text_blob = f"{exc.__class__.__name__}: {exc}".lower()
        if (
            "429" in text_blob
            or "quota exceeded" in text_blob
            or "rate limit" in text_blob
            or "rate_limit_exceeded" in text_blob
            or "read requests per minute per user" in text_blob
            or "too many requests" in text_blob
        ):
            payload["retryable"] = True
            payload["network_related"] = True
            payload["auth_related"] = False
        elif (
            "permission" in text_blob
            or "forbidden" in text_blob
            or "unauthorized" in text_blob
            or "insufficient authentication scopes" in text_blob
        ):
            payload["retryable"] = False
            payload["network_related"] = False
            payload["auth_related"] = True
        else:
            payload["retryable"] = False
            payload["network_related"] = False
            payload["auth_related"] = False

        if json_output:
            emit_json(payload)
            raise typer.Exit(code=1)

        print(f"ok: {payload['ok']}")
        print(f"command: {payload['command']}")
        print(f"error_type: {payload['error_type']}")
        print(f"error_message: {payload['error_message']}")
        raise typer.Exit(code=1)

def get_default_test_folder_name():
    if bool(config_get("safety.office_as_default_test_folder", True)):
        return config_get("folders.office_name", "200_Офис")
    return config_get("folders.temp_name", "98_Временное")




def should_dry_run(dry_run: bool = False):
    return dry_run or is_default_dry_run()

def print_dry_run(payload: dict):
    print("DRY RUN OK")
    print(json.dumps(payload, ensure_ascii=False, indent=2))




def get_safety_mode():
    return config_get("safety.mode", "readonly")

def set_safety_mode_value(mode: str):
    if mode not in {"readonly", "write"}:
        raise RuntimeError(f"Unsupported safety mode: {mode}")

    cfg = load_config()
    if "safety" not in cfg or not isinstance(cfg["safety"], dict):
        cfg["safety"] = {}

    cfg["safety"]["mode"] = mode

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

def is_write_mode():
    return get_safety_mode() == "write"




def is_confirm_required():
    return bool(config_get("safety.require_confirm_for_write", True))

def ensure_confirmed(confirm: bool, operation_name: str):
    if is_write_mode() and is_confirm_required() and not confirm:
        raise RuntimeError(
            f"Write operation requires explicit confirmation in write mode: {operation_name}. "
            f"Run with --confirm after a dry-run preview."
        )




def emit_output(json_output: bool, payload: dict, human_lines=None):
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if human_lines:
        for line in human_lines:
            print(line)




def classify_error(exc: Exception):
    name = exc.__class__.__name__
    msg = str(exc)

    retryable = False
    auth_related = False
    network_related = False

    if isinstance(exc, HttpError):
        status = getattr(getattr(exc, "resp", None), "status", None)
        if status in {408, 409, 425, 429, 500, 502, 503, 504}:
            retryable = True
        if status in {401, 403}:
            auth_related = True

    if name in {"SSLEOFError", "TimeoutError", "ConnectionResetError"}:
        retryable = True
        network_related = True

    if "EOF occurred in violation of protocol" in msg:
        retryable = True
        network_related = True

    if "refresh" in msg.lower() or "token" in msg.lower():
        auth_related = True

    return {
        "error_type": name,
        "error_message": msg,
        "retryable": retryable,
        "auth_related": auth_related,
        "network_related": network_related,
    }

def emit_error(json_output: bool, command: str, exc: Exception):
    payload = {
        "ok": False,
        "command": command,
        **classify_error(exc),
    }

    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise typer.Exit(code=1)

    raise exc


def get_creds():
    if TOKEN_FILE.exists():
        return Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds

def services():
    creds = get_creds()
    return {
        "drive": build("drive", "v3", credentials=creds),
        "docs": build("docs", "v1", credentials=creds),
        "sheets": build("sheets", "v4", credentials=creds),
    }

def list_children(drive, folder_id, page_size=1000):
    items = []
    page_token = None
    while True:
        res = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id,name,mimeType,webViewLink,modifiedTime,createdTime)",
            pageSize=page_size,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        items.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return sorted(items, key=lambda x: x["name"])

def find_folder(drive, name, parent_id: Optional[str] = None):
    q = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    res = drive.files().list(
        q=q,
        fields="files(id,name,mimeType,webViewLink,modifiedTime,createdTime)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    if not files:
        raise RuntimeError(f"Folder not found: {name}")
    return files[0]



def get_sheet_values(sheets, spreadsheet_id: str, range_a1: str):
    return sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_a1,
    ).execute().get("values", [])


def get_sheet_header_map(sheets, spreadsheet_id: str, sheet_name: str, header_row: int = 1):
    values = get_sheet_values(sheets, spreadsheet_id, f"'{sheet_name}'!A{header_row}:ZZ{header_row}")
    if not values:
        raise RuntimeError(f"Header row not found: spreadsheet={spreadsheet_id} sheet={sheet_name} row={header_row}")

    header = values[0]
    mapping = {}
    for idx, name in enumerate(header, start=1):
        if name and name not in mapping:
            mapping[name] = idx
    return header, mapping


def get_sheet_rows(sheets, spreadsheet_id: str, sheet_name: str):
    return get_sheet_values(sheets, spreadsheet_id, f"'{sheet_name}'!A:ZZ")


def col_to_a1(col_num: int) -> str:
    out = ""
    n = col_num
    while n > 0:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def pad_row(row, size: int):
    row = list(row)
    if len(row) < size:
        row.extend([""] * (size - len(row)))
    return row[:size]


def find_rows_by_column(rows, header_map, column_name: str, match_value: str, header_row: int = 1):
    if column_name not in header_map:
        raise RuntimeError(f"Column not found: {column_name}")

    idx0 = header_map[column_name] - 1
    matches = []

    for row_num, row in enumerate(rows, start=1):
        if row_num < header_row + 1:
            continue
        value = row[idx0] if idx0 < len(row) else ""
        if value == match_value:
            matches.append({
                "row_number": row_num,
                "row_values": row,
            })
    return matches


def find_rows_by_link_fragment(rows, header_map, fragment: str, link_column: str = "Link", header_row: int = 1):
    if link_column not in header_map:
        raise RuntimeError(f"Column not found: {link_column}")

    idx0 = header_map[link_column] - 1
    matches = []

    for row_num, row in enumerate(rows, start=1):
        if row_num < header_row + 1:
            continue
        value = row[idx0] if idx0 < len(row) else ""
        if fragment in value:
            matches.append({
                "row_number": row_num,
                "row_values": row,
            })
    return matches

def get_file_meta(drive, file_id: str):
    return drive.files().get(
        fileId=file_id,
        fields="id,name,mimeType,webViewLink,modifiedTime,parents",
        supportsAllDrives=True,
    ).execute()

def append_log(sheets, action, obj, from_, to, reason, impact="Low", status="Done", notes=""):
    now = datetime.now()
    change_id = f"CHG-{now.strftime('%Y-%m-%d-%H%M%S')}-LOCAL"
    row = [
        change_id,
        now.strftime("%Y-%m-%d"),
        action,
        obj,
        from_,
        to,
        reason,
        impact,
        status,
        notes,
    ]
    result = sheets.spreadsheets().values().append(
        spreadsheetId=CHANGE_LOG_ID,
        range="'Change Log Lite'!A:J",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
    return change_id, result.get("updates", {}).get("updatedRange")

@app.command()
def audit():
    """Read-only scan Cass and save snapshot/report."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    s = services()
    drive = s["drive"]

    cass = find_folder(drive, "Cass")
    top = list_children(drive, cass["id"])

    snapshot = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cass": cass,
        "top_level": top,
    }

    out = CACHE_DIR / "cass_snapshot.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    report = REPORTS_DIR / f"cass_audit_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    lines = [
        "Cass audit report",
        f"Generated: {snapshot['generated_at']}",
        f"Cass ID: {cass['id']}",
        "",
        "Top-level Cass items:",
    ]
    for item in top:
        lines.append(f"- {item['name']} | {item['mimeType']} | {item['id']}")
    report.write_text("\n".join(lines), encoding="utf-8")

    print(f"Audit OK")
    print(f"Snapshot: {out}")
    print(f"Report: {report}")

@app.command("create-temp-doc")
def create_temp_doc():
    """Create staging test document in default test folder (config; usually Cass / 200_Офис) and log it."""
    ensure_write_allowed("create-temp-doc", target=get_default_test_folder_name())
    s = services()
    drive = s["drive"]
    docs = s["docs"]
    sheets = s["sheets"]

    cass = find_folder(drive, "Cass")
    temp = find_folder(drive, get_default_test_folder_name(), cass["id"])

    title = f"ASTCV_DOCS_AGENT_TEMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    created = drive.files().create(
        body={
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [temp["id"]],
        },
        fields="id,name,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    docs.documents().batchUpdate(
        documentId=created["id"],
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": (
                            "ASTCV Docs Agent temporary staging document.\n"
                            "Файл создан внутри Cass / 98_Временное.\n"
                            "Canonical-документы не изменялись.\n"
                        ),
                    }
                }
            ]
        },
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Create",
        obj=title,
        from_="Local docs-agent",
        to="Cass / 98_Временное",
        reason="Проверка CLI create-temp-doc и автоматической записи Change Log Lite",
        impact="Low",
        status="Done",
        notes=f"URL: {created.get('webViewLink')}",
    )

    print("CREATE TEMP DOC OK")
    print(f"Name: {created['name']}")
    print(f"ID: {created['id']}")
    print(f"URL: {created.get('webViewLink')}")
    print(f"Change Log: {change_id} | {updated_range}")

@app.command("append-log")
def append_log_cmd(
    action: str = "Test",
    obj: str = "Manual CLI test",
    reason: str = "Manual Change Log Lite test from docs_agent.py",
):
    """Append one row to Change Log Lite."""
    ensure_write_allowed("append-log", target=get_change_log_sheet())
    s = services()
    sheets = s["sheets"]
    change_id, updated_range = append_log(
        sheets=sheets,
        action=action,
        obj=obj,
        from_="Local docs-agent",
        to="Change Log Lite",
        reason=reason,
        impact="Low",
        status="Done",
        notes="Manual CLI append-log command",
    )
    print("APPEND LOG OK")
    print(f"Change ID: {change_id}")
    print(f"Updated range: {updated_range}")

@app.command("create-staging-copy")
def create_staging_copy(
    file_id: str,
    target_folder: str = "13_Черновики_и_review",
):
    """Copy existing Drive file into staging/review folder and log it."""
    ensure_write_allowed("create-staging-copy", target=target_folder)
    ensure_write_allowed("create-staging-copy", target=target_folder)
    if should_dry_run(dry_run):
        print_dry_run({
            "command": "create-doc-in-folder",
            "target_folder": target_folder,
            "title_prefix": title_prefix,
            "write_mode_required": True
        })
        return

    s = services()
    drive = s["drive"]
    sheets = s["sheets"]

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, target_folder, cass["id"])

    source = drive.files().get(
        fileId=file_id,
        fields="id,name,mimeType,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    copy_name = f"STAGING_COPY__{source['name']}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    copied = drive.files().copy(
        fileId=file_id,
        body={
            "name": copy_name,
            "parents": [target["id"]],
        },
        fields="id,name,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Copy",
        obj=copy_name,
        from_=source.get("webViewLink", file_id),
        to=f"Cass / {target_folder}",
        reason="Создание staging-копии для безопасного редактирования без изменения canonical-документа",
        impact="Low",
        status="Done",
        notes=f"Source: {source['name']} | Copy URL: {copied.get('webViewLink')}",
    )

    print("CREATE STAGING COPY OK")
    print(f"Source name: {source['name']}")
    print(f"Source ID: {source['id']}")
    print(f"Copy name: {copied['name']}")
    print(f"Copy ID: {copied['id']}")
    print(f"Copy URL: {copied.get('webViewLink')}")
    print(f"Target folder: Cass / {target_folder}")
    print(f"Change Log: {change_id} | {updated_range}")

@app.command("patch-doc")
def patch_doc(
    document_id: str,
    text_to_insert: str = "\n\n[PATCH TEST] Тестовое изменение staging-документа через Google Docs API.\n",
):
    """Append text to a Google Doc and log the operation. Use only for staging/review docs."""
    ensure_write_allowed("patch-doc", target=document_id)
    s = services()
    docs = s["docs"]
    drive = s["drive"]
    sheets = s["sheets"]

    meta = drive.files().get(
        fileId=document_id,
        fields="id,name,mimeType,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    doc = docs.documents().get(documentId=document_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    docs.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": end_index},
                        "text": text_to_insert,
                    }
                }
            ]
        },
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Patch",
        obj=meta["name"],
        from_="Local docs-agent",
        to=meta.get("webViewLink", document_id),
        reason="Тестовая правка staging-документа через Google Docs API",
        impact="Low",
        status="Done",
        notes=f"Document ID: {document_id}",
    )

    print("PATCH DOC OK")
    print(f"Document: {meta['name']}")
    print(f"ID: {document_id}")
    print(f"URL: {meta.get('webViewLink')}")
    print(f"Inserted chars: {len(text_to_insert)}")
    print(f"Change Log: {change_id} | {updated_range}")

@app.command("create-doc-in-folder")
def create_doc_in_folder(
    target_folder: str,
    title_prefix: str = "ASTCV_DOCS_AGENT_OFFICE_TEST",
    dry_run: bool = False,
    confirm: bool = False,
):
    """Create Google Doc in selected top-level Cass folder and log it."""
    if should_dry_run(dry_run):
        print_dry_run({
            "command": "create-doc-in-folder",
            "target_folder": target_folder,
            "title_prefix": title_prefix,
            "write_mode_required": True
        })
        return

    ensure_write_allowed("create-doc-in-folder", target=target_folder)
    ensure_confirmed(confirm, "create-doc-in-folder")
    s = services()
    drive = s["drive"]
    docs = s["docs"]
    sheets = s["sheets"]

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, target_folder, cass["id"])

    title = f"{title_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    created = drive.files().create(
        body={
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [target["id"]],
        },
        fields="id,name,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    docs.documents().batchUpdate(
        documentId=created["id"],
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": (
                            "Тестовый документ ASTCV Docs Agent.\n"
                            f"Папка: Cass / {target_folder}.\n"
                            "Назначение: проверка создания файлов в выбранной папке Cass.\n"
                            "Canonical-документы не изменялись.\n"
                        ),
                    }
                }
            ]
        },
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Create",
        obj=title,
        from_="Local docs-agent",
        to=f"Cass / {target_folder}",
        reason="Проверка создания документа в выбранной папке Cass через CLI docs_agent.py",
        impact="Low",
        status="Done",
        notes=f"URL: {created.get('webViewLink')}",
    )

    print("CREATE DOC IN FOLDER OK")
    print(f"Folder: Cass / {target_folder}")
    print(f"Name: {created['name']}")
    print(f"ID: {created['id']}")
    print(f"URL: {created.get('webViewLink')}")
    print(f"Change Log: {change_id} | {updated_range}")

@app.command("list-folder")
def list_folder_cmd(
    folder_name: str,
):
    """List items in selected top-level Cass folder."""
    s = services()
    drive = s["drive"]

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, folder_name, cass["id"])
    items = list_children(drive, target["id"])

    print(f"LIST FOLDER OK")
    print(f"Folder: Cass / {folder_name}")
    print(f"Folder ID: {target['id']}")
    print("")
    if not items:
        print("- empty")
        return

    for item in items:
        print(f"- {item['name']} | {item['mimeType']} | {item['id']} | {item.get('webViewLink', '')}")

def extract_text(elements):
    out = []
    for value in elements:
        para = value.get("paragraph")
        if not para:
            continue

        for elem in para.get("elements", []):
            text_run = elem.get("textRun")
            if text_run and "content" in text_run:
                out.append(text_run["content"])

    return "".join(out)

@app.command("read-doc")
def read_doc(
    document_id: str,
    max_chars: int = 4000,
    json_output: bool = False,
):
    """Read Google Doc text content."""
    try:
        s = services()
        docs = s["docs"]
        drive = s["drive"]

        meta = drive.files().get(
            fileId=document_id,
            fields="id,name,mimeType,webViewLink,modifiedTime",
            supportsAllDrives=True,
        ).execute()

        doc = docs.documents().get(documentId=document_id).execute()

        content = doc.get("body", {}).get("content", [])
        text_content = extract_text(content)

        truncated = False
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "\n\n...[TRUNCATED]..."
            truncated = True

        payload = {
            "ok": True,
            "command": "read-doc",
            "document_id": document_id,
            "meta": meta,
            "content": text_content,
            "truncated": truncated,
            "max_chars": max_chars,
        }

        emit_output(
            json_output,
            payload,
            human_lines=[
                "READ DOC OK",
                f"Name: {meta['name']}",
                f"ID: {meta['id']}",
                f"Modified: {meta.get('modifiedTime')}",
                f"URL: {meta.get('webViewLink')}",
                "",
                "----- DOCUMENT CONTENT BEGIN -----",
                text_content,
                "----- DOCUMENT CONTENT END -----",
            ],
        )
    except Exception as exc:
        emit_error(json_output, "read-doc", exc)

@app.command("replace-doc-text")
def replace_doc_text(
    document_id: str,
    old_text: str,
    new_text: str,
):
    """Replace exact text fragment in Google Doc and log operation."""
    ensure_write_allowed("replace-doc-text", target=document_id)
    ensure_write_allowed("replace-doc-text", target=document_id)
    s = services()
    docs = s["docs"]
    drive = s["drive"]
    sheets = s["sheets"]

    meta = drive.files().get(
        fileId=document_id,
        fields="id,name,mimeType,webViewLink,modifiedTime",
        supportsAllDrives=True,
    ).execute()

    docs.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": [
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": old_text,
                            "matchCase": True,
                        },
                        "replaceText": new_text,
                    }
                }
            ]
        },
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Replace Text",
        obj=meta["name"],
        from_=old_text,
        to=new_text,
        reason="Точечная замена текста через Google Docs API",
        impact="Low",
        status="Done",
        notes=f"Document ID: {document_id} | URL: {meta.get('webViewLink')}",
    )

    print("REPLACE DOC TEXT OK")
    print(f"Document: {meta['name']}")
    print(f"ID: {document_id}")
    print(f"URL: {meta.get('webViewLink')}")
    print(f"Old text: {old_text}")
    print(f"New text: {new_text}")
    print(f"Change Log: {change_id} | {updated_range}")

@app.command("replace-doc-text-safe")
def replace_doc_text_safe(
    document_id: str,
    old_text: str,
    new_text: str,
    backup_folder: str = "13_Черновики_и_review",
    dry_run: bool = False,
    confirm: bool = False,
):
    """Backup document, then replace exact text fragment and log operation."""
    if should_dry_run(dry_run):
        print_dry_run({
            "command": "replace-doc-text-safe",
            "document_id": document_id,
            "old_text": old_text,
            "new_text": new_text,
            "backup_folder": backup_folder,
            "write_mode_required": True
        })
        return

    ensure_write_allowed("replace-doc-text-safe", target=document_id)
    ensure_confirmed(confirm, "replace-doc-text-safe")
    s = services()
    docs = s["docs"]
    drive = s["drive"]
    sheets = s["sheets"]

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, backup_folder, cass["id"])

    meta = drive.files().get(
        fileId=document_id,
        fields="id,name,mimeType,webViewLink,modifiedTime",
        supportsAllDrives=True,
    ).execute()

    backup_name = f"BACKUP_BEFORE_REPLACE__{meta['name']}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    backup = drive.files().copy(
        fileId=document_id,
        body={
            "name": backup_name,
            "parents": [target["id"]],
        },
        fields="id,name,webViewLink",
        supportsAllDrives=True,
    ).execute()

    docs.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": [
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": old_text,
                            "matchCase": True,
                        },
                        "replaceText": new_text,
                    }
                }
            ]
        },
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Safe Replace Text",
        obj=meta["name"],
        from_=old_text,
        to=new_text,
        reason="Точечная замена текста с предварительным backup документа",
        impact="Medium",
        status="Done",
        notes=f"Backup: {backup.get('webViewLink')} | Document: {meta.get('webViewLink')}",
    )

    print("SAFE REPLACE DOC TEXT OK")
    print(f"Document: {meta['name']}")
    print(f"Document ID: {document_id}")
    print(f"Document URL: {meta.get('webViewLink')}")
    print(f"Backup: {backup['name']}")
    print(f"Backup ID: {backup['id']}")
    print(f"Backup URL: {backup.get('webViewLink')}")
    print(f"Change Log: {change_id} | {updated_range}")


@app.command("verify-doc-text")
def verify_doc_text(
    document_id: str,
    text_to_find: str,
):
    """Verify whether exact text fragment exists in Google Doc."""
    s = services()
    docs = s["docs"]
    drive = s["drive"]

    meta = drive.files().get(
        fileId=document_id,
        fields="id,name,mimeType,webViewLink,modifiedTime",
        supportsAllDrives=True,
    ).execute()

    doc = docs.documents().get(documentId=document_id).execute()
    content = doc.get("body", {}).get("content", [])
    text_content = extract_text(content)

    count = text_content.count(text_to_find)
    found = count > 0

    print("VERIFY DOC TEXT OK")
    print(f"Name: {meta['name']}")
    print(f"ID: {meta['id']}")
    print(f"Modified: {meta.get('modifiedTime')}")
    print(f"URL: {meta.get('webViewLink')}")
    print(f"Search text: {text_to_find}")
    print(f"Found: {found}")
    print(f"Count: {count}")


@app.command("export-doc")
def export_doc(
    document_id: str,
    out_path: str,
    export_format: str = "docx",
):
    """Export Google Doc to local file. Supported: docx, pdf, txt."""
    s = services()
    drive = s["drive"]

    meta = drive.files().get(
        fileId=document_id,
        fields="id,name,mimeType,webViewLink,modifiedTime",
        supportsAllDrives=True,
    ).execute()

    mime_map = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "txt": "text/plain",
    }

    export_format = export_format.lower()
    if export_format not in mime_map:
        raise typer.BadParameter("export_format must be one of: docx, pdf, txt")

    request = drive.files().export_media(
        fileId=document_id,
        mimeType=mime_map[export_format],
    )

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with out_file.open("wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print("EXPORT DOC OK")
    print(f"Name: {meta['name']}")
    print(f"ID: {meta['id']}")
    print(f"Format: {export_format}")
    print(f"Output: {out_file}")
    print(f"URL: {meta.get('webViewLink')}")


@app.command("upload-file-to-folder")
def upload_file_to_folder(
    local_path: str,
    folder_name: str,
    target_name: Optional[str] = None,
    dry_run: bool = False,
    confirm: bool = False,
):
    """Upload local file into selected top-level Cass folder."""
    src = Path(local_path)

    if should_dry_run(dry_run):
        print_dry_run({
            "command": "upload-file-to-folder",
            "local_path": str(src),
            "folder_name": folder_name,
            "target_name": target_name or src.name,
            "write_mode_required": True
        })
        return

    ensure_write_allowed("upload-file-to-folder", target=folder_name)
    ensure_confirmed(confirm, "upload-file-to-folder")
    s = services()
    drive = s["drive"]
    sheets = s["sheets"]

    src = Path(local_path)
    if not src.exists():
        raise typer.BadParameter(f"Local file not found: {src}")

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, folder_name, cass["id"])

    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(src), resumable=True)
    file_name = target_name or src.name

    created = drive.files().create(
        body={
            "name": file_name,
            "parents": [target["id"]],
        },
        media_body=media,
        fields="id,name,mimeType,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Upload File",
        obj=created["name"],
        from_=str(src),
        to=f"Cass / {folder_name}",
        reason="Загрузка локального файла в папку Cass через docs-agent",
        impact="Low",
        status="Done",
        notes=f"File ID: {created['id']} | URL: {created.get('webViewLink')}",
    )

    print("UPLOAD FILE OK")
    print(f"Local path: {src}")
    print(f"Uploaded name: {created['name']}")
    print(f"File ID: {created['id']}")
    print(f"Folder: Cass / {folder_name}")
    print(f"Target folder ID: {target['id']}")
    print(f"Created parents: {created.get('parents', [])}")
    print(f"URL: {created.get('webViewLink')}")
    print(f"Change Log: {change_id} | {updated_range}")


@app.command("move-file-with-log")
def move_file_with_log(
    file_id: str,
    target_folder_name: str,
    reason: str,
    dry_run: bool = False,
    confirm: bool = False,
):
    """Move Drive file into selected top-level Cass folder and write Change Log Lite."""
    if should_dry_run(dry_run):
        print_dry_run({
            "command": "move-file-with-log",
            "file_id": file_id,
            "target_folder_name": target_folder_name,
            "reason": reason,
            "write_mode_required": True
        })
        return

    ensure_write_allowed("move-file-with-log", target=target_folder_name)
    ensure_confirmed(confirm, "move-file-with-log")
    s = services()
    drive = s["drive"]
    sheets = s["sheets"]

    if not reason.strip():
        raise typer.BadParameter("Reason must not be empty")

    if file_id.startswith("REPLACE_") or file_id == "FILE_ID":
        raise typer.BadParameter("Replace placeholder file_id with a real Google Drive file ID")

    cass = find_folder(drive, "Cass")
    target = find_folder(drive, target_folder_name, cass["id"])

    meta_before = get_file_meta(drive, file_id)
    old_parents = meta_before.get("parents", [])
    remove_parents = ",".join(old_parents) if old_parents else None

    updated = drive.files().update(
        fileId=file_id,
        addParents=target["id"],
        removeParents=remove_parents,
        fields="id,name,mimeType,webViewLink,parents",
        supportsAllDrives=True,
    ).execute()

    meta_after = get_file_meta(drive, file_id)
    parents_after = meta_after.get("parents", [])

    if target["id"] not in parents_after:
        raise RuntimeError(
            f"Move verification failed: target folder {target['id']} not found in parents {parents_after}"
        )

    change_id, updated_range = append_log(
        sheets=sheets,
        action="Move File",
        obj=updated["name"],
        from_=",".join(old_parents) if old_parents else "",
        to=target["id"],
        reason=reason,
        impact="Medium",
        status="Done",
        notes=f"File ID: {updated['id']} | URL: {updated.get('webViewLink')} | Cass folder: {target_folder_name}",
    )

    print("MOVE FILE OK")
    print(f"File: {updated['name']}")
    print(f"File ID: {updated['id']}")
    print(f"Old parents: {old_parents}")
    print(f"New parents (update response): {updated.get('parents', [])}")
    print(f"New parents (verified): {parents_after}")
    print(f"Target folder: Cass / {target_folder_name}")
    print(f"Target folder ID: {target['id']}")
    print(f"URL: {updated.get('webViewLink')}")
    print(f"Change Log: {change_id} | {updated_range}")


@app.command("get-file")
def get_file(
    file_id: str,
    json_output: bool = False,
):
    """Read Drive file metadata including parents."""
    try:
        s = services()
        drive = s["drive"]

        meta = get_file_meta(drive, file_id)
        payload = {
            "ok": True,
            "command": "get-file",
            "file_id": file_id,
            "file": meta,
        }

        emit_output(
            json_output,
            payload,
            human_lines=[
                "GET FILE OK",
                json.dumps(meta, ensure_ascii=False, indent=2),
            ],
        )
    except Exception as exc:
        emit_error(json_output, "get-file", exc)


@app.command("list-folder-by-id")
def list_folder_by_id(
    folder_id: str,
):
    """List items in folder by exact Drive folder ID."""
    s = services()
    drive = s["drive"]

    meta = drive.files().get(
        fileId=folder_id,
        fields="id,name,mimeType,webViewLink,modifiedTime,parents",
        supportsAllDrives=True,
    ).execute()

    items = list_children(drive, folder_id)

    print("LIST FOLDER BY ID OK")
    print(f"Folder: {meta['name']}")
    print(f"Folder ID: {meta['id']}")
    print("")

    for item in items:
        print(f"- {item['name']} | {item['mimeType']} | {item['id']} | {item.get('webViewLink', '')}")


@app.command("read-sheet-header")
def read_sheet_header(
    spreadsheet_id: str,
    sheet_name: str,
    header_row: int = 1,
):
    """Read sheet header row and print header map."""
    s = services()
    sheets = s["sheets"]

    header, mapping = get_sheet_header_map(
        sheets=sheets,
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        header_row=header_row,
    )

    print("READ SHEET HEADER OK")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Sheet: {sheet_name}")
    print(f"Header row: {header_row}")
    print("")
    print("Header values:")
    for i, value in enumerate(header, start=1):
        print(f"{i:03d} | {col_to_a1(i)} | {value}")

    print("")
    print("Header map:")
    print(json.dumps(mapping, ensure_ascii=False, indent=2))


@app.command("get-sheet-rows")
def get_sheet_rows_cmd(
    spreadsheet_id: str,
    sheet_name: str,
    max_rows: int = 20,
):
    """Read first N rows from sheet."""
    s = services()
    sheets = s["sheets"]

    rows = get_sheet_rows(sheets, spreadsheet_id, sheet_name)

    print("GET SHEET ROWS OK")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Sheet: {sheet_name}")
    print(f"Total rows fetched: {len(rows)}")
    print("")

    for row_num, row in enumerate(rows[:max_rows], start=1):
        print(f"ROW {row_num}: {json.dumps(row, ensure_ascii=False)}")


@app.command("find-row-by-column")
def find_row_by_column(
    spreadsheet_id: str,
    sheet_name: str,
    column_name: str,
    match_value: str,
    header_row: int = 1,
    json_output: bool = False,
):
    """Find rows by exact column value match."""
    try:
        s = services()
        sheets = s["sheets"]

        rows = get_sheet_rows(sheets, spreadsheet_id, sheet_name)
        header, mapping = get_sheet_header_map(sheets, spreadsheet_id, sheet_name, header_row=header_row)

        matches = find_rows_by_column(
            rows=rows,
            header_map=mapping,
            column_name=column_name,
            match_value=match_value,
            header_row=header_row,
        )

        payload = {
            "ok": True,
            "command": "find-row-by-column",
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "column_name": column_name,
            "match_value": match_value,
            "header_row": header_row,
            "matches_found": len(matches),
            "matches": matches,
        }

        human_lines = [
            "FIND ROW BY COLUMN OK",
            f"Spreadsheet ID: {spreadsheet_id}",
            f"Sheet: {sheet_name}",
            f"Column: {column_name}",
            f"Match value: {match_value}",
            f"Matches found: {len(matches)}",
            "",
        ]
        for item in matches:
            human_lines.append(f"ROW {item['row_number']}: {json.dumps(item['row_values'], ensure_ascii=False)}")

        emit_output(json_output, payload, human_lines=human_lines)
    except Exception as exc:
        emit_error(json_output, "find-row-by-column", exc)


@app.command("append-master-index-row")
def append_master_index_row(
    spreadsheet_id: str,
    sheet_name: str,
    payload_json: str,
):
    """Append one row into Master Index-like sheet using header names from JSON payload."""
    ensure_write_allowed("append-master-index-row", target=f"{spreadsheet_id}/{sheet_name}")
    ensure_master_index_write_allowed()
    s = services()
    sheets = s["sheets"]

    payload = json.loads(payload_json)
    if not isinstance(payload, dict):
        raise typer.BadParameter("payload_json must be a JSON object")

    header, mapping = get_sheet_header_map(sheets, spreadsheet_id, sheet_name, header_row=1)
    row = [""] * len(header)

    unknown = [k for k in payload.keys() if k not in mapping]
    if unknown:
        raise RuntimeError(f"Unknown columns in payload: {unknown}")

    for key, value in payload.items():
        row[mapping[key] - 1] = "" if value is None else str(value)

    result = sheets.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A:ZZ",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    print("APPEND MASTER INDEX ROW OK")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Sheet: {sheet_name}")
    print("Payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Updated range: {result.get('updates', {}).get('updatedRange')}")
    print(f"Updated rows: {result.get('updates', {}).get('updatedRows')}")


@app.command("update-master-index-row")
def update_master_index_row(
    spreadsheet_id: str,
    sheet_name: str,
    match_column: str,
    match_value: str,
    payload_json: str,
):
    """Update exactly one row in Master Index-like sheet by matching one column."""
    ensure_write_allowed("update-master-index-row", target=f"{spreadsheet_id}/{sheet_name}")
    ensure_master_index_write_allowed()
    s = services()
    sheets = s["sheets"]

    payload = json.loads(payload_json)
    if not isinstance(payload, dict):
        raise typer.BadParameter("payload_json must be a JSON object")

    rows = get_sheet_rows(sheets, spreadsheet_id, sheet_name)
    header, mapping = get_sheet_header_map(sheets, spreadsheet_id, sheet_name, header_row=1)

    matches = find_rows_by_column(
        rows=rows,
        header_map=mapping,
        column_name=match_column,
        match_value=match_value,
        header_row=1,
    )

    if len(matches) == 0:
        raise RuntimeError(f"No rows found for {match_column}={match_value}")

    if len(matches) > 1:
        raise RuntimeError(f"More than one row found for {match_column}={match_value}: {len(matches)}")

    target = matches[0]
    row_num = target["row_number"]
    current_row = pad_row(target["row_values"], len(header))

    unknown = [k for k in payload.keys() if k not in mapping]
    if unknown:
        raise RuntimeError(f"Unknown columns in payload: {unknown}")

    new_row = list(current_row)
    for key, value in payload.items():
        new_row[mapping[key] - 1] = "" if value is None else str(value)

    end_col = col_to_a1(len(header))
    target_range = f"'{sheet_name}'!A{row_num}:{end_col}{row_num}"

    result = sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=target_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_row]},
    ).execute()

    print("UPDATE MASTER INDEX ROW OK")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"Sheet: {sheet_name}")
    print(f"Match column: {match_column}")
    print(f"Match value: {match_value}")
    print(f"Row number: {row_num}")
    print("")
    print("Old row:")
    print(json.dumps(current_row, ensure_ascii=False, indent=2))
    print("")
    print("Patch payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("")
    print("New row:")
    print(json.dumps(new_row, ensure_ascii=False, indent=2))
    print("")
    print(f"Updated range: {result.get('updatedRange')}")
    print(f"Updated cells: {result.get('updatedCells')}")


@app.command("find-row-by-link-fragment")
def find_row_by_link_fragment(
    spreadsheet_id: str,
    sheet_name: str,
    fragment: str,
    link_column: str = "Link",
    header_row: int = 1,
    json_output: bool = False,
):
    """Find rows where link column contains a fragment, e.g. Drive file ID."""
    try:
        s = services()
        sheets = s["sheets"]

        rows = get_sheet_rows(sheets, spreadsheet_id, sheet_name)
        header, mapping = get_sheet_header_map(sheets, spreadsheet_id, sheet_name, header_row=header_row)

        matches = find_rows_by_link_fragment(
            rows=rows,
            header_map=mapping,
            fragment=fragment,
            link_column=link_column,
            header_row=header_row,
        )

        payload = {
            "ok": True,
            "command": "find-row-by-link-fragment",
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "fragment": fragment,
            "link_column": link_column,
            "header_row": header_row,
            "matches_found": len(matches),
            "matches": matches,
        }

        human_lines = [
            "FIND ROW BY LINK FRAGMENT OK",
            f"Spreadsheet ID: {spreadsheet_id}",
            f"Sheet: {sheet_name}",
            f"Link column: {link_column}",
            f"Fragment: {fragment}",
            f"Matches found: {len(matches)}",
            "",
        ]
        for item in matches:
            human_lines.append(f"ROW {item['row_number']}: {json.dumps(item['row_values'], ensure_ascii=False)}")

        emit_output(json_output, payload, human_lines=human_lines)
    except Exception as exc:
        emit_error(json_output, "find-row-by-link-fragment", exc)


@app.command("show-config-status")
def show_config_status(
    json_output: bool = False,
):
    """Show effective config and safety mode."""
    try:
        payload = {
            "ok": True,
            "command": "show-config-status",
            "safety_mode": config_get("safety.mode", "readonly"),
            "default_dry_run": config_get("safety.default_dry_run", True),
            "forbid_master_index_write": config_get("safety.forbid_master_index_write", True),
            "forbid_delete": config_get("safety.forbid_delete", True),
            "default_test_folder": get_default_test_folder_name(),
            "master_index_spreadsheet_id": get_master_index_id(),
            "master_index_sheet_name": get_master_index_sheet(),
            "change_log_spreadsheet_id": get_change_log_id(),
            "change_log_sheet_name": get_change_log_sheet(),
            "identity_note": config_get("identity_model.registry_identity_note"),
        }
        emit_output(
            json_output,
            payload,
            human_lines=[
                "CONFIG STATUS OK",
                json.dumps(payload, ensure_ascii=False, indent=2),
            ],
        )
    except Exception as exc:
        emit_error(json_output, "show-config-status", exc)


@app.command("show-safety-mode")
def show_safety_mode(
    json_output: bool = False,
):
    """Show current safety mode from config."""
    try:
        payload = {
            "ok": True,
            "command": "show-safety-mode",
            "mode": get_safety_mode(),
            "default_dry_run": is_default_dry_run(),
            "forbid_master_index_write": config_get("safety.forbid_master_index_write", True),
            "forbid_delete": config_get("safety.forbid_delete", True),
            "default_test_folder": get_default_test_folder_name(),
        }
        emit_output(
            json_output,
            payload,
            human_lines=[
                "SAFETY MODE OK",
                json.dumps(payload, ensure_ascii=False, indent=2),
            ],
        )
    except Exception as exc:
        emit_error(json_output, "show-safety-mode", exc)


@app.command("set-safety-mode")
def set_safety_mode(
    mode: str,
):
    """Set safety mode in config: readonly or write."""
    old_mode = get_safety_mode()
    set_safety_mode_value(mode)

    print("SET SAFETY MODE OK")
    print(json.dumps({
        "old_mode": old_mode,
        "new_mode": mode,
        "config_path": str(CONFIG_PATH),
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    app()

class AgentConfig:
    raw: dict

    @property
    def default_dry_run(self) -> bool:
        return bool(self.raw.get("safety", {}).get("default_dry_run", False))

    @property
    def retries(self) -> int:
        return int(self.raw.get("google_api", {}).get("retries", 5))

    @property
    def initial_backoff_sec(self) -> float:
        return float(self.raw.get("google_api", {}).get("initial_backoff_sec", 1.0))

    @property
    def max_backoff_sec(self) -> float:
        return float(self.raw.get("google_api", {}).get("max_backoff_sec", 16.0))

    @property
    def qps_limit(self) -> float:
        return float(self.raw.get("google_api", {}).get("qps_limit", 4.0))

def load_config(path: str = CONFIG_PATH_DEFAULT) -> AgentConfig:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"config not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AgentConfig(raw=raw)
