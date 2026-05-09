from pathlib import Path
import re
import sys

p = Path("docs_agent.py")
src = p.read_text(encoding="utf-8")

if "def read_sheet_values(" in src or '@app.command("read-sheet-values")' in src:
    print("read-sheet-values already exists")
    sys.exit(0)

anchor = "def get_default_test_folder_name():"
if anchor not in src:
    print("anchor not found")
    sys.exit(1)

block = r'''

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
'''

src = src.replace(anchor, block + "\n" + anchor, 1)

p.write_text(src, encoding="utf-8")
print("patched", p)
