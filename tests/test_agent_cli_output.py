from __future__ import annotations

import json

from agent_cli_output import (
    build_compact_ask_output,
    build_compact_error_output,
    build_error_payload,
    print_compact_doctor_lite,
    print_compact_find,
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


def test_build_compact_ask_output_formats_find_result() -> None:
    lines = build_compact_ask_output(
        {
            "ok": True,
            "command": "ask",
            "query": "DOC-0001",
            "routed_to": "find-doc-any",
            "result": {
                "ok": True,
                "command": "find-doc-any",
                "summary": {
                    "document_id": "DOC-0001",
                    "document_name": "Operating Prompt",
                    "link": "https://example.test/doc",
                },
            },
        }
    )

    assert lines == [
        "ok: True",
        "route: find-doc-any",
        "query: DOC-0001",
        "document_id: DOC-0001",
        "document_name: Operating Prompt",
        "link: https://example.test/doc",
    ]


def test_print_compact_find_emits_summary(capsys) -> None:
    print_compact_find(
        {
            "ok": True,
            "query": "DOC-0001",
            "summary": {
                "document_id": "DOC-0001",
                "document_name": "Operating Prompt",
                "link": "https://example.test/doc",
            },
        }
    )

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "ok: True",
        "route: find-doc-any",
        "query: DOC-0001",
        "document_id: DOC-0001",
        "document_name: Operating Prompt",
        "link: https://example.test/doc",
    ]
    assert captured.err == ""


def test_print_compact_doctor_lite_includes_google_verification_flags(
    capsys,
) -> None:
    print_compact_doctor_lite(
        {
            "ok": True,
            "checks": {
                "environment": {"ok": True},
                "status": {"ok": True},
                "master_index_lookup": {"ok": True},
            },
            "cache_backed": True,
            "live_google_verified": False,
            "summary": "cache-backed",
            "next_step": "live not checked",
            "diagnosis": "healthy",
            "likely_cause": "none",
            "recommended_action": "continue",
        }
    )

    captured = capsys.readouterr()
    assert "cache_backed: True" in captured.out.splitlines()
    assert "live_google_verified: False" in captured.out.splitlines()
