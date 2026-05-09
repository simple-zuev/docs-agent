from pathlib import Path
import sys

p = Path("docs_agent.py")
src = p.read_text(encoding="utf-8")

if "def get_sheets_service():" in src:
    print("get_sheets_service already exists")
    sys.exit(0)

anchor = "def normalize_jsonable(value):"
if anchor not in src:
    print("anchor not found")
    sys.exit(1)

block = '''
def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)

'''.strip() + "\n\n"

src = src.replace(anchor, block + anchor, 1)

p.write_text(src, encoding="utf-8")
print("patched", p)
