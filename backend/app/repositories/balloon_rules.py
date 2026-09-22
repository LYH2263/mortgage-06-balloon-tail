import sqlite3
from datetime import datetime, timezone

_COLUMNS = ("name", "balloon_period", "cap", "enabled")


def _row(r):
    d = dict(r)
    d["enabled"] = bool(d["enabled"])
    return d


def list_all(conn):
    return [_row(r) for r in conn.execute("SELECT * FROM balloon_rules ORDER BY id").fetchall()]


def get(conn, rid):
    row = conn.execute("SELECT * FROM balloon_rules WHERE id=?", (rid,)).fetchone()
    return _row(row) if row else None


def insert(conn, name, balloon_period, cap, enabled):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO balloon_rules(name,balloon_period,cap,enabled,created_at) VALUES (?,?,?,?,?)",
        (name, int(balloon_period), float(cap), 1 if enabled else 0, now))
    conn.commit()
    return int(cur.lastrowid)


def update(conn, rid, fields):
    sets, vals = [], []
    for k in _COLUMNS:
        if k in fields and fields[k] is not None:
            sets.append(f"{k}=?")
            vals.append((1 if fields[k] else 0) if k == "enabled" else fields[k])
    if not sets:
        return False
    cur = conn.execute(f"UPDATE balloon_rules SET {','.join(sets)} WHERE id=?", (*vals, rid))
    conn.commit()
    return cur.rowcount > 0


def set_enabled(conn, rid, enabled):
    cur = conn.execute("UPDATE balloon_rules SET enabled=? WHERE id=?", (1 if enabled else 0, rid))
    conn.commit()
    return cur.rowcount > 0
