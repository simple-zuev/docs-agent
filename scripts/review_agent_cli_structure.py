from pathlib import Path

text = Path("agent_cli.py").read_text(encoding="utf-8")

targets = [
    "import ",
    "def build_error_payload(",
    "def run_docs_agent(",
    "def run_docs_agent_with_retry(",
    "def extract_google_id_from_link(",
    "def normalize_query_for_lookup(",
    "def find_doc_any_payload(",
    "def open_doc_from_query_payload(",
    "def read_doc_from_query_payload(",
    "def is_status_query(",
    "def is_read_query(",
    "def build_ask_result(",
    "def ask_status_payload(",
    "def ask_read_payload(",
    "def ask_google_id_payload(",
    "def ask_find_payload(",
    "def ask_payload(",
    "def print_json(",
    "def print_compact_find(",
    "def print_compact_open(",
    "def print_compact_read(",
    "def build_compact_ask_output(",
    "def print_human_lines(",
    "def parse_json_flag(",
    "def handle_query_command(",
    "def cmd_find_doc_any(",
    "def cmd_open_doc_from_query(",
    "def cmd_read_doc_from_query(",
    "def cmd_ask(",
    "def usage(",
    "def main() -> int:",
]

for target in targets:
    idx = text.find(target)
    print("\n" + "=" * 120)
    print(target)
    print("index:", idx)
    if idx == -1:
        continue

    end = len(text)
    for marker in ["\ndef ", "\nclass ", '\nif __name__ == "__main__":']:
        j = text.find(marker, idx + 1)
        if j != -1 and j < end:
            end = j

    print(text[idx:end])
