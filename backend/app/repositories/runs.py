import json, sqlite3
from datetime import datetime, timezone
def insert(conn, kind, payload, result, loan_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,loan_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, loan_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)
def list_recent(conn, limit=50):
    return [_hydrate(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
def get(conn, run_id):
    r = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return _hydrate(r) if r else None
def _hydrate(r):
    d = dict(r)
    d["input"] = json.loads(d.pop("input_json") or "{}")
    d["result"] = json.loads(d.pop("result_json") or "{}")
    return d
