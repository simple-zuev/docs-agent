from __future__ import annotations

from pathlib import Path

import agent_cli
import repo_state


def test_local_branch_safety_snapshot_does_not_fetch_remote(
    monkeypatch, tmp_path: Path
) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    monkeypatch.setattr(
        repo_state,
        "git_status_snapshot",
        lambda _repo_path: {
            "ok": True,
            "command": "git-status-snapshot",
            "branch": "codex/local",
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
        repo_state,
        "git_fetch_origin",
        lambda _repo_path: (_ for _ in ()).throw(
            AssertionError("local snapshot must not fetch origin")
        ),
    )

    payload = repo_state.local_branch_safety_snapshot(tmp_path)

    assert payload["ok"] is True
    assert payload["command"] == "local-branch-safety-snapshot"
    assert payload["branch"] == "codex/local"
    assert payload["is_main"] is False
    assert payload["working_tree_clean"] is True
    assert payload["local_equals_origin_main"] is None
    assert payload["safe_for_mutation"] is True
    assert payload["head_sha"] == "local-sha"
    assert payload["origin_main_sha"] is None
    assert payload["remote_checked"] is False


def test_repo_state_local_payload_wraps_local_failure(monkeypatch) -> None:
    failure = {
        "ok": False,
        "command": "git status --short",
        "error_type": "GitCommandFailed",
        "error_message": "fatal: local git failure",
        "retryable": False,
    }

    monkeypatch.setattr(
        agent_cli, "local_branch_safety_snapshot", lambda _base: failure
    )

    payload = agent_cli.repo_state_local_payload()

    assert payload["ok"] is False
    assert payload["command"] == "repo-state-local"
    assert payload["error_type"] == "GitCommandFailed"
    assert payload["error_message"] == "fatal: local git failure"
    assert payload["retryable"] is False
    assert payload["auth_related"] is False
    assert payload["network_related"] is False
    assert payload["details"] == failure
