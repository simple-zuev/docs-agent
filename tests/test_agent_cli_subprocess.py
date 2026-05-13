from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import agent_cli_subprocess


def test_run_docs_agent_appends_json_output_and_debug(monkeypatch) -> None:
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"ok": True, "command": "sample"}),
            stderr="",
        )

    monkeypatch.setattr(agent_cli_subprocess.subprocess, "run", fake_run)

    payload = agent_cli_subprocess.run_docs_agent(["show-safety-mode"])

    assert payload["ok"] is True
    assert payload["command"] == "sample"
    assert calls[0][0][-2:] == ["show-safety-mode", "--json-output"]
    assert calls[0][1]["capture_output"] is True
    assert calls[0][1]["text"] is True
    assert calls[0][1]["timeout"] == agent_cli_subprocess.DOCS_AGENT_TIMEOUT_SEC
    assert payload["_debug"]["returncode"] == 0


def test_run_docs_agent_reports_empty_stdout(monkeypatch) -> None:
    def fake_run(_cmd, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="", stderr="warning")

    monkeypatch.setattr(agent_cli_subprocess.subprocess, "run", fake_run)

    payload = agent_cli_subprocess.run_docs_agent(["show-safety-mode"])

    assert payload["ok"] is False
    assert payload["command"] == "subprocess"
    assert payload["error_type"] == "EmptyOutput"
    assert payload["error_message"] == "No stdout from docs_agent.py."
    assert payload["_debug"]["stderr"] == "warning"


def test_run_docs_agent_reports_json_decode_error(monkeypatch) -> None:
    def fake_run(_cmd, **_kwargs):
        return SimpleNamespace(returncode=0, stdout="not json", stderr="")

    monkeypatch.setattr(agent_cli_subprocess.subprocess, "run", fake_run)

    payload = agent_cli_subprocess.run_docs_agent(["show-safety-mode"])

    assert payload["ok"] is False
    assert payload["command"] == "subprocess"
    assert payload["error_type"] == "JSONDecodeError"
    assert payload["error_message"] == "Failed to parse JSON output from docs_agent.py."


def test_run_docs_agent_reports_timeout(monkeypatch) -> None:
    def fake_run(_cmd, **_kwargs):
        raise subprocess.TimeoutExpired(
            cmd=["python", "docs_agent.py"],
            timeout=agent_cli_subprocess.DOCS_AGENT_TIMEOUT_SEC,
            output="partial",
            stderr="slow",
        )

    monkeypatch.setattr(agent_cli_subprocess.subprocess, "run", fake_run)

    payload = agent_cli_subprocess.run_docs_agent(["show-safety-mode"])

    assert payload["ok"] is False
    assert payload["command"] == "subprocess"
    assert payload["error_type"] == "TimeoutExpired"
    assert payload["retryable"] is True
    assert payload["network_related"] is True
