from __future__ import annotations

import json
from typing import Any


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def print_human_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def build_error_payload(
    *,
    command: str,
    query: str | None = None,
    error_type: str,
    error_message: str,
    retryable: bool = False,
    auth_related: bool = False,
    network_related: bool = False,
    **extra: Any,
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


def print_compact_repo_state(payload: dict):
    print(f"ok: {payload.get('ok')}")
    print("route: repo-state")

    if not payload.get("ok"):
        print(f"error_type: {payload.get('error_type')}")
        print(f"error_message: {payload.get('error_message')}")
        return

    print(f"repo_path: {payload.get('repo_path')}")
    print(f"branch: {payload.get('branch')}")
    print(f"is_main: {payload.get('is_main')}")
    print(f"working_tree_clean: {payload.get('working_tree_clean')}")
    print(f"local_equals_origin_main: {payload.get('local_equals_origin_main')}")
    print(f"safe_for_mutation: {payload.get('safe_for_mutation')}")
    print(f"head_sha: {payload.get('head_sha')}")
    print(f"origin_main_sha: {payload.get('origin_main_sha')}")

    entries = payload.get("diff_name_status_entries") or []
    if entries:
        print("diff_name_status_entries:")
        for entry in entries:
            print(f"  - {entry}")

    print(f"recommended_next_step: {payload.get('recommended_next_step')}")


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
