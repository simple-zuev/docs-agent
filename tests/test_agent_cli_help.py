from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_CLI = ROOT / "agent_cli.py"


def run_agent_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AGENT_CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_help_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "python agent_cli.py repo-state [--json]" in result.stdout
    assert "python agent_cli.py live-google-probe [--json]" in result.stdout
    assert "UsageError" not in result.stdout
    assert result.stderr == ""


def test_agent_cli_dash_dash_help_returns_usage_successfully() -> None:
    assert_help_success(run_agent_cli("--help"))


def test_agent_cli_help_returns_usage_successfully() -> None:
    assert_help_success(run_agent_cli("help"))


def test_agent_cli_short_help_returns_usage_successfully() -> None:
    assert_help_success(run_agent_cli("-h"))
