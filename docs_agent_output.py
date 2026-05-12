import json

import typer
from googleapiclient.errors import HttpError


def normalize_jsonable(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)


def emit_json(payload: dict):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


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
