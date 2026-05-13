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
