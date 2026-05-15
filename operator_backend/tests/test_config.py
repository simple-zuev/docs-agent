from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import (  # noqa: E402
    DEFAULT_OPERATOR_DB_RELATIVE_PATH,
    OPERATOR_DB_PATH_ENV,
    resolve_operator_db_path,
)


def test_resolve_operator_db_path_uses_default_repo_local_runtime_path(
    tmp_path: Path,
) -> None:
    resolved = resolve_operator_db_path(env={}, repository_root=tmp_path)

    assert resolved == (tmp_path / DEFAULT_OPERATOR_DB_RELATIVE_PATH).resolve()
    assert resolved.name == "operator_backend.sqlite3"
    assert "var" in resolved.parts
    assert "operator_backend" in resolved.parts


def test_resolve_operator_db_path_uses_explicit_env_path(tmp_path: Path) -> None:
    explicit_path = tmp_path / "custom" / "operator.sqlite3"

    resolved = resolve_operator_db_path(
        env={OPERATOR_DB_PATH_ENV: str(explicit_path)},
        repository_root=tmp_path / "ignored-root",
    )

    assert resolved == explicit_path.resolve()


def test_resolve_operator_db_path_strips_whitespace_and_expands_home() -> None:
    resolved = resolve_operator_db_path(env={OPERATOR_DB_PATH_ENV: "  ~/operator.sqlite3  "})

    assert resolved == Path("~/operator.sqlite3").expanduser().resolve()


def test_resolve_operator_db_path_does_not_create_database_or_parent_dirs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    resolved = resolve_operator_db_path(env={}, repository_root=root)

    assert resolved == (root / DEFAULT_OPERATOR_DB_RELATIVE_PATH).resolve()
    assert not resolved.exists()
    assert not resolved.parent.exists()
