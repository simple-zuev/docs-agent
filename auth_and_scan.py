from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE = Path.home() / "AI" / "docs-agent"
CLIENT_SECRET = BASE / "config" / "client_secret.json"
TOKEN_FILE = BASE / "config" / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
]

def get_credentials():
    if TOKEN_FILE.exists():
        return Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds

def list_children(drive, folder_id, page_size=100):
    return drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id,name,mimeType,webViewLink,modifiedTime)",
        pageSize=page_size,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute().get("files", [])

def find_folder(drive, name):
    res = drive.files().list(
        q=f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id,name,mimeType,webViewLink,modifiedTime)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return res.get("files", [])

def main():
    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)
    sheets = build("sheets", "v4", credentials=creds)

    print("OAuth OK")
    print("Searching Cass...")

    cass_candidates = find_folder(drive, "Cass")
    if not cass_candidates:
        print("Cass folder not found")
        return

    cass = cass_candidates[0]
    print(f"Cass: {cass['name']} | {cass['id']} | {cass.get('webViewLink')}")

    top = sorted(list_children(drive, cass["id"]), key=lambda x: x["name"])

    print("\nTop-level Cass items:")
    for item in top:
        print(f"- {item['name']} | {item['mimeType']} | {item['id']}")

    mgmt = next((x for x in top if x["name"] == "00_Управление_проектом"), None)
    if not mgmt:
        print("\n00_Управление_проектом not found")
        return

    print(f"\nManagement folder: {mgmt['name']} | {mgmt['id']}")

    mgmt_items = sorted(list_children(drive, mgmt["id"], page_size=200), key=lambda x: x["name"])

    print("\nKey management files found:")
    target_names = [
        "00_MASTER_INDEX_АСТЦВ_v3",
        "00_REPOSITORY_CHANGE_LOG_АСТЦВ",
        "00_AI_AGENT_LAUNCH_INSTRUCTION_АСТЦВ",
        "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ",
        "00_DAILY_OPERATIONS_CHECKLIST_АСТЦВ",
    ]

    found = {}
    for name in target_names:
        item = next((x for x in mgmt_items if x["name"] == name), None)
        if item:
            found[name] = item
            print(f"OK: {name} | {item['mimeType']} | {item['id']}")
        else:
            print(f"MISSING: {name}")

    if "00_MASTER_INDEX_АСТЦВ_v3" in found:
        master_id = found["00_MASTER_INDEX_АСТЦВ_v3"]["id"]
        meta = sheets.spreadsheets().get(spreadsheetId=master_id).execute()
        print("\nMaster Index sheets:")
        for s in meta.get("sheets", []):
            p = s["properties"]
            gp = p.get("gridProperties", {})
            print(f"- {p['title']} | rows={gp.get('rowCount')} | cols={gp.get('columnCount')}")

    if "00_REPOSITORY_CHANGE_LOG_АСТЦВ" in found:
        log_id = found["00_REPOSITORY_CHANGE_LOG_АСТЦВ"]["id"]
        meta = sheets.spreadsheets().get(spreadsheetId=log_id).execute()
        print("\nChange Log sheets:")
        for s in meta.get("sheets", []):
            p = s["properties"]
            gp = p.get("gridProperties", {})
            print(f"- {p['title']} | rows={gp.get('rowCount')} | cols={gp.get('columnCount')}")

        result = sheets.spreadsheets().values().get(
            spreadsheetId=log_id,
            range="'Change Log Lite'!A1:J30"
        ).execute()

        print("\nChange Log Lite first rows:")
        for row in result.get("values", [])[:10]:
            print(" | ".join(row))

if __name__ == "__main__":
    main()
