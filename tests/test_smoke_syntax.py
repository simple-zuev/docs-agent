from __future__ import annotations

from pathlib import Path


ROOT = Path("/Users/zuevvladimir/AI/docs-agent")


def test_python_files_compile() -> None:
    py_files = sorted(
        path for path in ROOT.iterdir() if path.is_file() and path.suffix == ".py"
    )
    assert py_files, "No Python files found in repository root"

    for path in py_files:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
