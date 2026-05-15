from __future__ import annotations

import sys
from agent_cli_artifact import artifact_state_payload as build_artifact_state_payload
from agent_cli_cache import find_doc_any_payload_from_cache
from agent_cli_ask import ask_payload as build_ask_payload
from agent_cli_doc_body import (
    assemble_context_payload as build_assemble_context_payload,
    doc_body_only_payload as build_doc_body_only_payload,
)
from agent_cli_doctor import (
    diagnose_payload_failure,
    doctor_lite_payload as build_doctor_lite_payload,
    doctor_payload as build_doctor_payload,
)
from agent_cli_error_classification import is_network_error_text, is_network_error_type
from agent_cli_lookup import (
    find_doc_any_payload as lookup_find_doc_any_payload,
    find_doc_id_payload,
    find_doc_name_payload,
    find_link_payload,
    open_doc_from_query_payload as lookup_open_doc_from_query_payload,
    read_doc_from_query_payload as lookup_read_doc_from_query_payload,
)
from agent_cli_live_probe import (
    live_google_probe_payload as build_live_google_probe_payload,
)
from agent_cli_output import (
    build_compact_ask_output,
    print_compact_error,
    print_compact_doctor,
    print_compact_doctor_lite,
    print_compact_find,
    print_compact_open,
    print_compact_read,
    print_compact_repo_state,
    print_compact_status,
    print_human_lines,
    print_json,
)
from agent_cli_subprocess import (
    BASE,
    run_docs_agent,
)
from repo_state import branch_safety_snapshot, local_branch_safety_snapshot

EXIT_OK = 0
EXIT_USAGE_ERROR = 1
EXIT_NOT_FOUND = 2
EXIT_AUTH_ERROR = 3
EXIT_NETWORK_ERROR = 4
EXIT_INTERNAL_ERROR = 5
EXIT_INTERRUPTED = 130


def doctor_payload() -> dict:
    return build_doctor_payload(
        status_payload=cmd_status_payload,
        find_doc_any_payload=find_doc_any_payload,
    )


def doctor_lite_payload() -> dict:
    return build_doctor_lite_payload(
        status_payload=cmd_status_payload,
        find_doc_any_payload=find_doc_any_payload,
    )


def live_google_probe_payload() -> dict:
    return build_live_google_probe_payload(run_docs_agent_with_retry)


def is_retryable_network_error(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    if payload.get("network_related") is True and payload.get("retryable") is True:
        return True

    err = str(payload.get("error_type") or "")
    msg = str(payload.get("error_message") or "")

    if is_network_error_type(err):
        return True

    if is_network_error_text(msg):
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


def cmd_status_payload() -> dict:
    safety = run_docs_agent_with_retry(["show-safety-mode"])
    config = run_docs_agent_with_retry(["show-config-status"])
    return {
        "ok": bool(safety.get("ok")) and bool(config.get("ok")),
        "command": "status",
        "safety": safety,
        "config": config,
    }


def repo_state_payload() -> dict:
    payload = branch_safety_snapshot(BASE)

    if payload.get("ok"):
        return payload

    return {
        "ok": False,
        "command": "repo-state",
        "error_type": payload.get("error_type", "RepoStateError"),
        "error_message": payload.get(
            "error_message", "Failed to build repo state snapshot."
        ),
        "retryable": bool(payload.get("retryable")),
        "auth_related": False,
        "network_related": False,
        "details": payload,
    }


def repo_state_local_payload() -> dict:
    payload = local_branch_safety_snapshot(BASE)

    if payload.get("ok"):
        return payload

    return {
        "ok": False,
        "command": "repo-state-local",
        "error_type": payload.get("error_type", "RepoStateError"),
        "error_message": payload.get(
            "error_message", "Failed to build local repo state snapshot."
        ),
        "retryable": bool(payload.get("retryable")),
        "auth_related": False,
        "network_related": False,
        "details": payload,
    }


def cmd_repo_state(json_output: bool = False) -> int:
    payload = repo_state_payload()
    if json_output:
        print_json(payload)
    else:
        if payload.get("ok"):
            print_compact_repo_state(payload)
        else:
            print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_repo_state_local(json_output: bool = False) -> int:
    payload = repo_state_local_payload()
    if json_output:
        print_json(payload)
    else:
        if payload.get("ok"):
            print_compact_repo_state(payload)
        else:
            print_compact_error(payload)
    return resolve_command_exit_code(payload)


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


def cmd_live_google_probe(json_output: bool = False) -> int:
    payload = live_google_probe_payload()
    if json_output:
        print_json(payload)
    elif payload.get("ok"):
        print("ok: True")
        print("route: live-google-probe")
        print(f"target: {payload.get('target')}")
        print(f"cache_bypassed: {payload.get('cache_bypassed')}")
        print(f"live_google_verified: {payload.get('live_google_verified')}")
        print(f"summary: {payload.get('summary')}")
        print(f"next_step: {payload.get('next_step')}")
    else:
        print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_find_doc_id(value: str) -> None:
    payload = find_doc_id_payload(value, run_docs_agent_with_retry)
    print_json(payload)


def cmd_find_doc_name(value: str) -> None:
    payload = find_doc_name_payload(value, run_docs_agent_with_retry)
    print_json(payload)


def cmd_find_link(value: str) -> None:
    payload = find_link_payload(value, run_docs_agent_with_retry)
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


def find_doc_any_payload(query):
    return lookup_find_doc_any_payload(
        query, diagnose_payload_failure, run_docs_agent_with_retry
    )


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


def open_doc_from_query_payload(query: str) -> dict:
    return lookup_open_doc_from_query_payload(
        query, diagnose_payload_failure, run_docs_agent_with_retry
    )


def read_doc_from_query_payload(query: str) -> dict:
    return lookup_read_doc_from_query_payload(
        query, diagnose_payload_failure, run_docs_agent_with_retry
    )


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


def ask_payload(query: str) -> dict:
    return build_ask_payload(
        query,
        status_payload=cmd_status_payload,
        read_doc_from_query_payload=read_doc_from_query_payload,
        find_doc_any_payload=find_doc_any_payload,
        run_docs_agent_with_retry=run_docs_agent_with_retry,
    )


def capabilities_payload() -> dict:
    status_payload = cmd_status_payload()

    diagnostics = [
        "status",
        "doctor-lite",
        "doctor",
        "live-google-probe",
        "repo-state",
        "ask",
    ]
    assisted_bounded_baseline = [
        "status",
        "repo-state",
        "doctor",
        "live-google-probe",
        "find-doc-id",
        "find-doc-name",
        "find-link",
        "find-doc-any",
        "artifact-state",
        "open-doc-from-query",
        "doc-body-only",
    ]
    read_only = [
        "find-doc-any",
        "open-doc-from-query",
        "read-doc-from-query",
        "read-doc",
        "get-file",
    ]
    degraded = [
        "get-file",
        "read-doc",
        "read-doc-from-query",
    ]
    helper_surface = [
        "ask",
    ]
    bounded_write = [
        "create-temp-doc",
        "create-staging-copy",
        "create-doc-in-folder",
        "replace-doc-text-safe",
        "move-file-with-log",
    ]
    registry_and_sheet_helpers = [
        "read-sheet-values",
        "read-sheet-header",
        "get-sheet-rows",
        "find-row-by-column",
        "find-row-by-link-fragment",
        "append-log",
        "append-master-index-row",
        "update-master-index-row",
    ]
    config_and_safety = [
        "show-config-status",
        "show-safety-mode",
        "set-safety-mode",
    ]

    safety = {
        "mode": ((status_payload.get("safety") or {}).get("mode")),
        "default_dry_run": (
            (status_payload.get("safety") or {}).get("default_dry_run")
        ),
        "forbid_master_index_write": (
            (status_payload.get("safety") or {}).get("forbid_master_index_write")
        ),
        "forbid_delete": ((status_payload.get("safety") or {}).get("forbid_delete")),
        "default_test_folder": (
            (status_payload.get("safety") or {}).get("default_test_folder")
        ),
    }

    capabilities = {
        "can_find_docs": True,
        "can_read_docs": True,
        "can_read_sheets": True,
        "can_list_folders": True,
        "can_get_file_meta": True,
        "can_create_draft_doc": True,
        "can_create_staging_copy": True,
        "can_safe_replace": True,
        "can_move_with_log": True,
        "can_update_registry": True,
        "can_patch_doc": True,
        "patch_doc_autonomous_mode_allowed": False,
        "master_index_write_allowed": not bool(safety.get("forbid_master_index_write")),
        "delete_allowed": not bool(safety.get("forbid_delete")),
    }

    notes = [
        "Capability discovery is descriptive and reflects currently surfaced CLI/document operations.",
        "categories.read_only is descriptive and is not the assisted bounded baseline.",
        "Use categories.assisted_bounded_baseline for the current Path A baseline.",
        "Use categories.degraded for commands that remain available but non-baseline by default.",
        "Safe autonomous mode should prefer read-only, draft-first, create-staging-copy, and replace-doc-text-safe.",
        "patch-doc exists but should be treated as supervised-only for autonomous agent workflows.",
        "Master Index writes and delete operations remain constrained by current safety settings.",
    ]

    return {
        "ok": True,
        "command": "capabilities",
        "categories": {
            "diagnostics": diagnostics,
            "assisted_bounded_baseline": assisted_bounded_baseline,
            "read_only": read_only,
            "degraded": degraded,
            "helper_surface": helper_surface,
            "bounded_write": bounded_write,
            "registry_and_sheet_helpers": registry_and_sheet_helpers,
            "config_and_safety": config_and_safety,
        },
        "capabilities": capabilities,
        "safety": safety,
        "status_snapshot_ok": bool(status_payload.get("ok")),
        "notes": notes,
    }


def assemble_context_payload(profile: str) -> dict:
    return build_assemble_context_payload(
        profile,
        capabilities_payload=capabilities_payload,
        status_payload=cmd_status_payload,
        find_doc_any_payload_from_cache=find_doc_any_payload_from_cache,
    )


def doc_body_only_payload(profile: str, document_type: str, title: str) -> dict:
    return build_doc_body_only_payload(
        profile=profile,
        document_type=document_type,
        title=title,
        assemble_context_payload=assemble_context_payload,
    )


def artifact_state_payload(file_id: str) -> dict:
    return build_artifact_state_payload(
        file_id,
        run_docs_agent_with_retry=run_docs_agent_with_retry,
        status_payload=cmd_status_payload,
    )


def cmd_capabilities(json_output: bool = False) -> int:
    payload = capabilities_payload()
    if json_output:
        print_json(payload)
        return EXIT_OK

    print("CAPABILITIES OK")
    print(f"Safety mode: {payload['safety'].get('mode')}")
    print(f"Default dry run: {payload['safety'].get('default_dry_run')}")
    print("")
    for category, routes in payload["categories"].items():
        print(f"[{category}]")
        for route in routes:
            print(f"- {route}")
        print("")
    return EXIT_OK


def cmd_assemble_context(profile: str, json_output: bool = False) -> int:
    payload = assemble_context_payload(profile)
    if json_output:
        print_json(payload)
        return resolve_command_exit_code(payload)

    if payload.get("ok"):
        print("ASSEMBLE CONTEXT OK")
        print(f"Profile: {payload.get('profile')}")
        print(
            f"Resolved sources: {(payload.get('context_summary') or {}).get('resolved_count')}"
        )
        print(
            f"Unresolved sources: {(payload.get('context_summary') or {}).get('unresolved_count')}"
        )
        print(
            f"Recommended generation mode: {payload.get('recommended_generation_mode')}"
        )
        return EXIT_OK

    print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_doc_body_only(
    profile: str,
    document_type: str,
    title: str,
    json_output: bool = False,
) -> int:
    payload = doc_body_only_payload(profile, document_type, title)
    if json_output:
        print_json(payload)
        return resolve_command_exit_code(payload)

    if payload.get("ok"):
        print("DOC BODY ONLY OK")
        print(f"Profile: {payload.get('profile')}")
        print(f"Document type: {payload.get('document_type')}")
        print(f"Title: {payload.get('title')}")
        print("")
        print(payload.get("body", ""))
        return EXIT_OK

    print_compact_error(payload)
    return resolve_command_exit_code(payload)


def cmd_artifact_state(file_id: str, json_output: bool = False) -> int:
    payload = artifact_state_payload(file_id)
    if json_output:
        print_json(payload)
        return resolve_command_exit_code(payload)

    if payload.get("ok"):
        print("ARTIFACT STATE OK")
        print(f"File ID: {(payload.get('target_artifact') or {}).get('file_id')}")
        print(f"Name: {(payload.get('target_artifact') or {}).get('name')}")
        print(f"Artifact state: {payload.get('artifact_state')}")
        print(f"Review status: {payload.get('review_status')}")
        print(f"Next safe step: {payload.get('next_safe_step')}")
        return EXIT_OK

    print_compact_error(payload)
    return resolve_command_exit_code(payload)


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
        "  python agent_cli.py status [--json]\n  python agent_cli.py repo-state [--json]    | rs [--json]\n"
        "  python agent_cli.py repo-state-local [--json]\n"
        "  python agent_cli.py doctor [--json]        | diagnose [--json]\n"
        "  python agent_cli.py live-google-probe [--json]\n"
        "  python agent_cli.py assemble-context [--json] --profile <profile>\n"
        "  python agent_cli.py doc-body-only [--json] --profile <profile> --document-type <type> --title <title>\n"
        "  python agent_cli.py artifact-state [--json] --file-id <google_drive_file_id>\n"
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
        "  python agent_cli.py status --json\n  python agent_cli.py repo-state\n  python agent_cli.py repo-state --json\n"
        "  python agent_cli.py repo-state-local --json\n"
        "  python agent_cli.py f DOC-0001\n"
        "  python agent_cli.py o DOC-0002\n"
        "  python agent_cli.py r DOC-0002\n"
        '  python agent_cli.py r "00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"\n'
        '  python agent_cli.py q "прочитай DOC-0002"\n'
        '  python agent_cli.py q --json "прочитай 00_PROJECT_AI_OPERATING_PROMPT_АСТЦВ"\n'
        "  python agent_cli.py doctor\n"
        "  python agent_cli.py doctor --json\n"
        "  python agent_cli.py live-google-probe --json\n"
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
        if cmd in {"--help", "-h", "help"}:
            usage()
            return EXIT_OK

        if cmd == "status":
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("status does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_status(json_output=json_output)

        if cmd in {"repo-state", "rs"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("repo-state does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_repo_state(json_output=json_output)

        if cmd == "repo-state-local":
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error(
                    "repo-state-local does not accept positional arguments."
                )
                return EXIT_USAGE_ERROR
            return cmd_repo_state_local(json_output=json_output)

        if cmd in {"doctor-lite", "diagnose-lite"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("doctor-lite does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_doctor_lite(json_output=json_output)

        if cmd == "capabilities":
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("capabilities does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_capabilities(json_output=json_output)

        if cmd in {"doctor", "diagnose"}:
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error("doctor does not accept positional arguments.")
                return EXIT_USAGE_ERROR
            return cmd_doctor(json_output=json_output)

        if cmd == "live-google-probe":
            json_output, args = parse_json_flag(argv)
            if args:
                print_usage_error(
                    "live-google-probe does not accept positional arguments."
                )
                return EXIT_USAGE_ERROR
            return cmd_live_google_probe(json_output=json_output)

        if cmd == "assemble-context":
            json_output, args = parse_json_flag(argv)
            if len(args) != 2 or args[0] != "--profile":
                print_usage_error("assemble-context requires: --profile <profile>")
                return EXIT_USAGE_ERROR
            return cmd_assemble_context(args[1], json_output=json_output)

        if cmd == "doc-body-only":
            json_output, args = parse_json_flag(argv)
            if len(args) != 6:
                print_usage_error(
                    "doc-body-only requires: --profile <profile> --document-type <type> --title <title>"
                )
                return EXIT_USAGE_ERROR
            if (
                args[0] != "--profile"
                or args[2] != "--document-type"
                or args[4] != "--title"
            ):
                print_usage_error(
                    "doc-body-only requires: --profile <profile> --document-type <type> --title <title>"
                )
                return EXIT_USAGE_ERROR
            return cmd_doc_body_only(
                args[1],
                args[3],
                args[5],
                json_output=json_output,
            )

        if cmd == "artifact-state":
            json_output, args = parse_json_flag(argv)
            if len(args) != 2 or args[0] != "--file-id":
                print_usage_error(
                    "artifact-state requires: --file-id <google_drive_file_id>"
                )
                return EXIT_USAGE_ERROR
            return cmd_artifact_state(args[1], json_output=json_output)

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
