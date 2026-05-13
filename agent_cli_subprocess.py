from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from agent_cli_output import build_error_payload


BASE = Path.home() / "AI" / "docs-agent"
DOCS_AGENT = BASE / "docs_agent.py"
DOCS_AGENT_TIMEOUT_SEC = 60


def resolve_python_bin() -> tuple[Path, str]:
    env_python = os.environ.get("DOCS_AGENT_PYTHON")
    if env_python:
        return Path(env_python).expanduser(), "env:DOCS_AGENT_PYTHON"

    candidates = [
        (BASE / "venv312" / "bin" / "python", "project:venv312"),
        (BASE / ".venv" / "bin" / "python", "project:.venv"),
        (BASE / "venv" / "bin" / "python", "project:venv"),
    ]

    for candidate, source in candidates:
        if candidate.exists():
            return candidate, source

    return Path(sys.executable), "fallback:sys.executable"


PYTHON_BIN, PYTHON_BIN_SOURCE = resolve_python_bin()


def run_docs_agent(args: list[str]) -> dict:
    cmd = [str(PYTHON_BIN), str(DOCS_AGENT)] + args + ["--json-output"]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCS_AGENT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as exc:
        return build_error_payload(
            command="subprocess",
            error_type="TimeoutExpired",
            error_message=f"docs_agent.py timed out after {DOCS_AGENT_TIMEOUT_SEC} seconds.",
            retryable=True,
            auth_related=False,
            network_related=True,
            _debug={
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
                "stdout_preview": (exc.stdout or "")[:500] if exc.stdout else "",
                "stderr_preview": (exc.stderr or "")[:500] if exc.stderr else "",
            },
        )
    except Exception as exc:
        return build_error_payload(
            command="subprocess",
            error_type=exc.__class__.__name__,
            error_message=f"Failed to start docs_agent.py: {exc}",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "cmd": cmd,
            },
        )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if not stdout:
        return build_error_payload(
            command="subprocess",
            error_type="EmptyOutput",
            error_message="No stdout from docs_agent.py.",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "returncode": proc.returncode,
                "stderr": stderr,
                "stdout_preview": stdout[:500],
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            },
        )

    try:
        data = json.loads(stdout)
    except Exception as exc:
        return build_error_payload(
            command="subprocess",
            error_type=exc.__class__.__name__,
            error_message="Failed to parse JSON output from docs_agent.py.",
            retryable=False,
            auth_related=False,
            network_related=False,
            _debug={
                "returncode": proc.returncode,
                "stderr": stderr,
                "stdout_preview": stdout[:1000],
                "cmd": cmd,
                "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
            },
        )

    if "_debug" not in data:
        data["_debug"] = {
            "returncode": proc.returncode,
            "stderr": stderr,
            "cmd": cmd,
            "timeout_sec": DOCS_AGENT_TIMEOUT_SEC,
        }

    return data
