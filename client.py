import sqlite3

DB_PATH = "database.sqlite"

READ_ONLY_FORBIDDEN = {
    "insert", "update", "delete",
    "drop", "alter", "truncate", "create", "replace"
}

def _enforce_read_only(sql: str):
    s = sql.lower()
    for kw in READ_ONLY_FORBIDDEN:
        if kw in s:
            raise ValueError(f"Forbidden SQL operation: {kw}")

def execute_sql(sql: str, max_rows: int = 100):
    _enforce_read_only(sql)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(sql)
    rows = cur.fetchmany(max_rows)

    conn.close()

    return [dict(r) for r in rows]
