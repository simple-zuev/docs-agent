import json
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE = Path.home() / "AI" / "docs-agent"
TOKEN_FILE = BASE / "config" / "token.json"
CACHE_DIR = BASE / "cache"
REPORTS_DIR = BASE / "reports"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
]

KEY_FILES = [
    "00_MASTER_INDEX_АСТЦВ_v3",
    "00_REPOSITORY_CHANGE_LOG_АСТЦВ",
    "00_AI_AGENT_LAUNCH_INSTRUCTION_АСТЦВ",
    "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ",
    "00_DAILY_OPERATIONS_CHECKLIST_АСТЦВ",
    "00_AGENT_RUNTIME_CHARTER_АСТЦВ",
    "00_RUNTIME_HEALTH_AND_DRIFT_MODEL_АСТЦВ",
]

EXPECTED_TOP_FOLDERS = [
    "00_Управление_проектом",
    "01_Регуляторика_и_правовая_модель",
    "02_Продуктовая_модель",
    "03_Пользовательские_сценарии",
    "04_Техническое_задание",
    "05_Архитектура_и_интеграции",
    "06_Комплаенс_AML_Риски",
    "07_Финансы_налоги_бухгалтерия",
    "08_Операционная_модель",
    "09_Документы_для_лицензирования",
    "10_Аналитика_рынка",
    "11_Схемы_и_диаграммы",
    "12_Шаблоны",
    "13_Черновики_и_review",
    "14_Экспорт_PDF_DOCX",
    "98_Временное",
    "99_Архив",
]

def service():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    return build("drive", "v3", credentials=creds)

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

def find_cass(drive):
    res = drive.files().list(
        q="name = 'Cass' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id,name,mimeType,webViewLink,modifiedTime,createdTime)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    if not files:
        raise RuntimeError("Cass folder not found")
    return files[0]

def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    drive = service()
    cass = find_cass(drive)
    top = list_children(drive, cass["id"])

    snapshot = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cass": cass,
        "top_level": top,
        "folders": {},
        "checks": {
            "missing_top_folders": [],
            "extra_top_items": [],
            "key_files": {},
            "warnings": [],
        },
    }

    top_names = {x["name"] for x in top}

    for expected in EXPECTED_TOP_FOLDERS:
        if expected not in top_names:
            snapshot["checks"]["missing_top_folders"].append(expected)

    for item in top:
        if item["mimeType"] == "application/vnd.google-apps.folder":
            snapshot["folders"][item["name"]] = {
                "id": item["id"],
                "items": list_children(drive, item["id"]),
            }
        else:
            snapshot["checks"]["extra_top_items"].append(item["name"])

    mgmt = snapshot["folders"].get("00_Управление_проектом")
    if mgmt:
        mgmt_names = {x["name"]: x for x in mgmt["items"]}
        for key in KEY_FILES:
            snapshot["checks"]["key_files"][key] = {
                "present": key in mgmt_names,
                "id": mgmt_names[key]["id"] if key in mgmt_names else None,
                "mimeType": mgmt_names[key]["mimeType"] if key in mgmt_names else None,
                "modifiedTime": mgmt_names[key]["modifiedTime"] if key in mgmt_names else None,
            }
    else:
        snapshot["checks"]["warnings"].append("00_Управление_проектом not found")

    out = CACHE_DIR / "cass_snapshot.json"
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    report = REPORTS_DIR / f"cass_audit_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    lines = []
    lines.append("Cass audit report")
    lines.append(f"Generated: {snapshot['generated_at']}")
    lines.append(f"Cass ID: {cass['id']}")
    lines.append("")
    lines.append("Top-level folders/items:")
    for item in top:
        lines.append(f"- {item['name']} | {item['mimeType']} | {item['id']}")

    lines.append("")
    lines.append("Missing expected top folders:")
    if snapshot["checks"]["missing_top_folders"]:
        for x in snapshot["checks"]["missing_top_folders"]:
            lines.append(f"- {x}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Key governance files:")
    for name, data in snapshot["checks"]["key_files"].items():
        status = "OK" if data["present"] else "MISSING"
        lines.append(f"- {status}: {name} | {data.get('mimeType')} | {data.get('id')}")

    report.write_text("\n".join(lines), encoding="utf-8")

    print(f"Snapshot saved: {out}")
    print(f"Report saved: {report}")
    print("Audit OK")

if __name__ == "__main__":
    main()
