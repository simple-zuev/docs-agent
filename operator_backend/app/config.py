from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPERATOR_DB_RELATIVE_PATH = Path("var/operator_backend/operator_backend.sqlite3")
OPERATOR_DB_PATH_ENV = "DOCS_AGENT_OPERATOR_DB_PATH"


def resolve_operator_db_path(
    env: Mapping[str, str] | None = None,
    repository_root: Path | None = None,
) -> Path:
    """Resolve the local operator backend SQLite path without creating files.

    SQLite persistence remains opt-in. This helper only centralizes path
    resolution so future repository implementations do not hard-code runtime
    artifact locations.
    """
    source_env = env if env is not None else os.environ
    raw_path = (source_env.get(OPERATOR_DB_PATH_ENV) or "").strip()

    if raw_path:
        return Path(raw_path).expanduser().resolve()

    root = repository_root if repository_root is not None else REPOSITORY_ROOT
    return (root / DEFAULT_OPERATOR_DB_RELATIVE_PATH).resolve()
