import sqlite3
from datetime import datetime, timezone


def _to_dict(r):
    return {
        "id": r["id"],
        "balloon_period": r["balloon_period"],
        "balloon_cap": r["balloon_cap"],
        "enabled": bool(r["enabled"]),
        "created_at": r["created_at"],
        "updated_at": r["updated_at"],
    }


def list_all(conn):
    return [_to_dict(r) for r in conn.execute(
        "SELECT * FROM balloon_rules ORDER BY id").fetchall()]


def get(conn, rule_id):
    r = conn.execute("SELECT * FROM balloon_rules WHERE id=?", (rule_id,)).fetchone()
    return _to_dict(r) if r else None


def create(conn, balloon_period, balloon_cap, enabled=True):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO balloon_rules(balloon_period,balloon_cap,enabled,created_at,updated_at)"
        " VALUES (?,?,?,?,?)",
        (balloon_period, balloon_cap, 1 if enabled else 0, now, now))
    conn.commit()
    return get(conn, cur.lastrowid)


def update(conn, rule_id, balloon_period=None, balloon_cap=None, enabled=None):
    sets, vals = [], []
    if balloon_period is not None:
        sets.append("balloon_period=?"); vals.append(balloon_period)
    if balloon_cap is not None:
        sets.append("balloon_cap=?"); vals.append(balloon_cap)
    if enabled is not None:
        sets.append("enabled=?"); vals.append(1 if enabled else 0)
    if not sets:
        return get(conn, rule_id)
    sets.append("updated_at=?"); vals.append(datetime.now(timezone.utc).isoformat())
    vals.append(rule_id)
    cur = conn.execute(f"UPDATE balloon_rules SET {', '.join(sets)} WHERE id=?", vals)
    conn.commit()
    if cur.rowcount == 0:
        return None
    return get(conn, rule_id)
