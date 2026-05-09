from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _build_error_payload(
    *,
    command: str,
    error_type: str,
    error_message: str,
    retryable: bool = False,
) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "error_type": error_type,
        "error_message": error_message,
        "retryable": retryable,
    }


def verify_repo_path(repo_path: Path) -> dict[str, Any]:
    path = Path(repo_path).expanduser().resolve()

    if not path.exists():
        return _build_error_payload(
            command="verify-repo-path",
            error_type="RepoPathNotFound",
            error_message=f"Repository path does not exist: {path}",
        ) | {
            "repo_path": str(path),
            "exists": False,
            "has_git_dir": False,
        }

    if not path.is_dir():
        return _build_error_payload(
            command="verify-repo-path",
            error_type="RepoPathNotDirectory",
            error_message=f"Repository path is not a directory: {path}",
        ) | {
            "repo_path": str(path),
            "exists": True,
            "has_git_dir": False,
        }

    git_dir = path / ".git"
    has_git_dir = git_dir.exists()

    if not has_git_dir:
        return _build_error_payload(
            command="verify-repo-path",
            error_type="NotGitRepository",
            error_message=f"Path is not a git repository: {path}",
        ) | {
            "repo_path": str(path),
            "exists": True,
            "has_git_dir": False,
        }

    return {
        "ok": True,
        "command": "verify-repo-path",
        "repo_path": str(path),
        "exists": True,
        "has_git_dir": True,
    }


def _run_git(
    repo_path: Path,
    args: list[str],
    *,
    timeout_sec: int = 20,
) -> dict[str, Any]:
    verify = verify_repo_path(repo_path)
    if not verify.get("ok"):
        return verify

    cmd = ["git", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(Path(repo_path).expanduser().resolve()),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return _build_error_payload(
            command="git " + " ".join(args),
            error_type="TimeoutExpired",
            error_message=f"Git command timed out after {timeout_sec} seconds.",
            retryable=True,
        )
    except Exception as exc:
        return _build_error_payload(
            command="git " + " ".join(args),
            error_type=exc.__class__.__name__,
            error_message=f"Failed to run git command: {exc}",
            retryable=False,
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    payload: dict[str, Any] = {
        "ok": proc.returncode == 0,
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "_debug": {
            "cwd": str(Path(repo_path).expanduser().resolve()),
            "cmd": cmd,
            "timeout_sec": timeout_sec,
        },
    }

    if proc.returncode != 0:
        payload.update(
            {
                "error_type": "GitCommandFailed",
                "error_message": stderr or stdout or "Git command failed.",
                "retryable": False,
            }
        )

    return payload


def git_status_snapshot(repo_path: Path) -> dict[str, Any]:
    branch_result = _run_git(repo_path, ["branch", "--show-current"])
    if not branch_result.get("ok"):
        return branch_result

    status_result = _run_git(repo_path, ["status", "--short"])
    if not status_result.get("ok"):
        return status_result

    raw_status = status_result.get("stdout", "")
    lines = [line for line in raw_status.splitlines() if line.strip()]

    return {
        "ok": True,
        "command": "git-status-snapshot",
        "branch": (branch_result.get("stdout") or "").strip(),
        "working_tree_clean": len(lines) == 0,
        "raw_status_short": raw_status,
        "changed_entries": lines,
    }


def git_head_sha(repo_path: Path) -> dict[str, Any]:
    result = _run_git(repo_path, ["rev-parse", "HEAD"])
    if not result.get("ok"):
        return result

    return {
        "ok": True,
        "command": "git-head-sha",
        "head_sha": (result.get("stdout") or "").strip(),
    }


def git_fetch_origin(repo_path: Path) -> dict[str, Any]:
    result = _run_git(repo_path, ["fetch", "origin"], timeout_sec=60)
    if not result.get("ok"):
        return result

    return {
        "ok": True,
        "command": "git-fetch-origin",
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
    }


def git_origin_main_sha(repo_path: Path) -> dict[str, Any]:
    result = _run_git(repo_path, ["rev-parse", "origin/main"])
    if not result.get("ok"):
        return result

    return {
        "ok": True,
        "command": "git-origin-main-sha",
        "origin_main_sha": (result.get("stdout") or "").strip(),
    }


def git_diff_stat_against_origin_main(repo_path: Path) -> dict[str, Any]:
    result = _run_git(repo_path, ["diff", "--stat", "origin/main...HEAD"])
    if not result.get("ok"):
        return result

    return {
        "ok": True,
        "command": "git-diff-stat-against-origin-main",
        "diff_stat": result.get("stdout", ""),
    }


def git_diff_name_status_against_origin_main(repo_path: Path) -> dict[str, Any]:
    result = _run_git(repo_path, ["diff", "--name-status", "origin/main...HEAD"])
    if not result.get("ok"):
        return result

    raw_output = result.get("stdout", "")
    entries = [line for line in raw_output.splitlines() if line.strip()]

    return {
        "ok": True,
        "command": "git-diff-name-status-against-origin-main",
        "raw_name_status": raw_output,
        "entries": entries,
    }


def local_vs_origin_reconciliation_snapshot(repo_path: Path) -> dict[str, Any]:
    verify = verify_repo_path(repo_path)
    if not verify.get("ok"):
        return verify

    status = git_status_snapshot(repo_path)
    if not status.get("ok"):
        return status

    head = git_head_sha(repo_path)
    if not head.get("ok"):
        return head

    fetch = git_fetch_origin(repo_path)
    if not fetch.get("ok"):
        return fetch

    origin_main = git_origin_main_sha(repo_path)
    if not origin_main.get("ok"):
        return origin_main

    diff_stat = git_diff_stat_against_origin_main(repo_path)
    if not diff_stat.get("ok"):
        return diff_stat

    diff_name_status = git_diff_name_status_against_origin_main(repo_path)
    if not diff_name_status.get("ok"):
        return diff_name_status

    head_sha = head.get("head_sha")
    origin_main_sha = origin_main.get("origin_main_sha")
    entries = diff_name_status.get("entries") or []

    return {
        "ok": True,
        "command": "local-vs-origin-reconciliation-snapshot",
        "repo_path": str(Path(repo_path).expanduser().resolve()),
        "branch": status.get("branch"),
        "working_tree_clean": status.get("working_tree_clean"),
        "head_sha": head_sha,
        "origin_main_sha": origin_main_sha,
        "local_equals_origin_main": head_sha == origin_main_sha,
        "ahead_or_diverged_entries_present": len(entries) > 0,
        "diff_stat": diff_stat.get("diff_stat", ""),
        "diff_name_status_entries": entries,
    }


def branch_safety_snapshot(repo_path: Path) -> dict[str, Any]:
    snapshot = local_vs_origin_reconciliation_snapshot(repo_path)
    if not snapshot.get("ok"):
        return snapshot

    branch = snapshot.get("branch") or ""
    working_tree_clean = bool(snapshot.get("working_tree_clean"))
    local_equals_origin_main = bool(snapshot.get("local_equals_origin_main"))

    is_main = branch == "main"
    safe_for_mutation = (not is_main) and working_tree_clean

    if is_main:
        recommended_next_step = "Create or switch to a non-main feature branch before mutations."
    elif not working_tree_clean:
        recommended_next_step = "Commit, stash, or inspect local changes before mutations."
    elif local_equals_origin_main:
        recommended_next_step = "Safe to begin controlled additive work in current feature branch."
    else:
        recommended_next_step = "Review divergence against origin/main before mutations."

    return {
        "ok": True,
        "command": "branch-safety-snapshot",
        "repo_path": snapshot.get("repo_path"),
        "branch": branch,
        "is_main": is_main,
        "working_tree_clean": working_tree_clean,
        "local_equals_origin_main": local_equals_origin_main,
        "safe_for_mutation": safe_for_mutation,
        "recommended_next_step": recommended_next_step,
        "head_sha": snapshot.get("head_sha"),
        "origin_main_sha": snapshot.get("origin_main_sha"),
        "diff_name_status_entries": snapshot.get("diff_name_status_entries", []),
    }
