from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BACKEND_ROOT / "migrations"


def migration_files(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    return sorted(migrations_dir.glob("*.sql"))


def apply_migrations(
    database_path: str | Path = ":memory:",
    migrations_dir: Path = MIGRATIONS_DIR,
) -> None:
    """Apply reviewed SQLite migrations to a target database.

    This helper is validation tooling only. The backend runtime does not call it,
    and it should be used with temporary databases until SQLite persistence is
    explicitly enabled in a later phase.
    """
    files = migration_files(migrations_dir)
    if not files:
        raise RuntimeError(f"No migration files found in {migrations_dir}")

    with sqlite3.connect(str(database_path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for migration_file in files:
            connection.executescript(migration_file.read_text(encoding="utf-8"))
        connection.commit()


def sqlite_tables(database_path: str | Path) -> set[str]:
    with sqlite3.connect(str(database_path)) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    return {row[0] for row in rows}


def sqlite_indexes(database_path: str | Path) -> set[str]:
    with sqlite3.connect(str(database_path)) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
    return {row[0] for row in rows if row[0] is not None}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate operator backend SQLite migrations against a temporary database."
    )
    parser.add_argument(
        "database_path",
        nargs="?",
        default=":memory:",
        help="SQLite database path to validate against. Defaults to in-memory.",
    )
    args = parser.parse_args()

    apply_migrations(args.database_path)
    print("MIGRATIONS OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
