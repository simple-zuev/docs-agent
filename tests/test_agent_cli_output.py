from __future__ import annotations

import json

from agent_cli_output import (
    build_compact_error_output,
    build_error_payload,
    print_json,
)


def test_build_error_payload_preserves_standard_and_extra_fields() -> None:
    payload = build_error_payload(
        command="sample",
        query="DOC-0001",
        error_type="NotFound",
        error_message="No match",
        retryable=False,
        auth_related=False,
        network_related=False,
        details={"source": "test"},
    )

    assert payload == {
        "ok": False,
        "command": "sample",
        "query": "DOC-0001",
        "error_type": "NotFound",
        "error_message": "No match",
        "retryable": False,
        "auth_related": False,
        "network_related": False,
        "details": {"source": "test"},
    }


def test_build_compact_error_output_includes_guidance() -> None:
    lines = build_compact_error_output(
        {
            "ok": False,
            "command": "find-doc-any",
            "query": "missing",
            "error_type": "NotFound",
            "error_message": "No match",
            "retryable": False,
            "auth_related": False,
            "network_related": False,
        }
    )

    assert "ok: False" in lines
    assert "command: find-doc-any" in lines
    assert "query: missing" in lines
    assert "error_type: NotFound" in lines
    assert any(line.startswith("explanation: ") for line in lines)
    assert any(line.startswith("next_step: ") for line in lines)


def test_print_json_emits_pretty_json(capsys) -> None:
    print_json({"ok": True, "message": "Привет"})

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"ok": True, "message": "Привет"}
    assert captured.err == ""
