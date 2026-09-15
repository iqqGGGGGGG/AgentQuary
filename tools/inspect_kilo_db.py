"""Inspect Kilo's local SQLite schema without modifying the database."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_kilo_db.py PATH_TO_KILO_DB", file=sys.stderr)
        return 2

    database = Path(sys.argv[1]).resolve()
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    try:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
        result = []
        for (table,) in tables:
            quoted = table.replace("'", "''")
            columns = connection.execute(f"PRAGMA table_info('{quoted}')").fetchall()
            result.append(
                {
                    "table": table,
                    "columns": [column[1] for column in columns],
                }
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
