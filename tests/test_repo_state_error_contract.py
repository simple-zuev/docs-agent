from __future__ import annotations

from pathlib import Path

import agent_cli
import repo_state


def test_repo_state_payload_wraps_git_fetch_failure(monkeypatch) -> None:
    failure = {
        "ok": False,
        "command": "git fetch origin",
        "returncode": 128,
        "stdout": "",
        "stderr": "fatal: unable to access remote",
        "error_type": "GitCommandFailed",
        "error_message": "fatal: unable to access remote",
        "retryable": False,
        "_debug": {
            "cwd": str(Path("/tmp/docs-agent")),
            "cmd": ["git", "fetch", "origin"],
            "timeout_sec": 60,
        },
    }

    monkeypatch.setattr(agent_cli, "branch_safety_snapshot", lambda _base: failure)

    payload = agent_cli.repo_state_payload()

    assert payload["ok"] is False
    assert payload["command"] == "repo-state"
    assert payload["error_type"] == "GitCommandFailed"
    assert payload["error_message"] == "fatal: unable to access remote"
    assert payload["retryable"] is False
    assert payload["auth_related"] is False
    assert payload["network_related"] is False
    assert payload["details"] == failure


def test_local_vs_origin_snapshot_stops_on_fetch_failure(
    monkeypatch, tmp_path: Path
) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    fetch_failure = {
        "ok": False,
        "command": "git fetch origin",
        "returncode": 128,
        "stdout": "",
        "stderr": "fatal: unable to access remote",
        "error_type": "GitCommandFailed",
        "error_message": "fatal: unable to access remote",
        "retryable": False,
    }

    monkeypatch.setattr(
        repo_state,
        "git_status_snapshot",
        lambda _repo_path: {
            "ok": True,
            "command": "git-status-snapshot",
            "branch": "codex/test",
            "working_tree_clean": True,
            "raw_status_short": "",
            "changed_entries": [],
        },
    )
    monkeypatch.setattr(
        repo_state,
        "git_head_sha",
        lambda _repo_path: {
            "ok": True,
            "command": "git-head-sha",
            "head_sha": "local-sha",
        },
    )
    monkeypatch.setattr(
        repo_state, "git_fetch_origin", lambda _repo_path: fetch_failure
    )

    payload = repo_state.local_vs_origin_reconciliation_snapshot(tmp_path)

    assert payload == fetch_failure
