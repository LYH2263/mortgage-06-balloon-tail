import os
import tempfile

# 必须在导入 app.* 之前指向临时数据库
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="balloon-svc-test-")

import pytest
from fastapi import HTTPException

from app import seed
from app.services.mortgage_service import MortgageService

seed.init_db()


@pytest.fixture()
def svc():
    with MortgageService() as s:
        yield s


def _count_runs(svc, kind=None):
    q = "SELECT COUNT(*) c FROM calc_runs" + (" WHERE kind=?" if kind else "")
    args = (kind,) if kind else ()
    return svc._c.execute(q, args).fetchone()["c"]


def test_enabled_rule_persists_balloon_run(svc):
    rule = svc.create_balloon_rule(60, 10_000_000, True)
    before = _count_runs(svc, "balloon")
    out = svc.schedule(1_000_000, 3.5, 360, None, True, 12, rule["id"])
    assert out["run_id"] is not None
    assert out["kind"] == "balloon"
    assert out["balloon_period"] == 60
    assert out["balloon_payment"] > out["monthly_payment"]
    assert _count_runs(svc, "balloon") == before + 1
    stored = svc.run(out["run_id"])
    assert stored["kind"] == "balloon"
    # 旧条保存写入时的规则快照
    assert stored["input"]["balloon_period"] == 60
    assert stored["input"]["balloon_cap"] == 10_000_000


def test_cap_exceeded_rejected_and_no_record_written(svc):
    rule = svc.create_balloon_rule(60, 500_000, True)
    before = _count_runs(svc)
    with pytest.raises(HTTPException) as ei:
        svc.schedule(1_000_000, 3.5, 360, None, True, 12, rule["id"])
    assert ei.value.status_code == 400
    assert ei.value.detail["error"] == "balloon_cap_exceeded"
    assert ei.value.detail["balloon_principal"] > 500_000
    assert ei.value.detail["balloon_cap"] == 500_000
    assert _count_runs(svc) == before  # 拒绝且不写记录


def test_persist_false_returns_packet_without_writing(svc):
    rule = svc.create_balloon_rule(36, 10_000_000, True)
    before = _count_runs(svc, "balloon")
    out = svc.schedule(800_000, 4.2, 240, None, False, 12, rule["id"])
    assert out["run_id"] is None
    assert out["balloon_payment"] > 0
    assert _count_runs(svc, "balloon") == before


def test_disabled_rule_falls_back_to_full_equal_payment(svc):
    rule = svc.create_balloon_rule(60, 10_000_000, True)
    svc.update_balloon_rule(rule["id"], None, None, False)
    out = svc.schedule(1_000_000, 3.5, 360, None, False, 12, rule["id"])
    assert "balloon_payment" not in out
    assert out["monthly_payment"] == 4490.45
    assert out["row_count"] == 360


def test_tightening_cap_keeps_old_run_value_and_rejects_new(svc):
    rule = svc.create_balloon_rule(60, 10_000_000, True)
    out = svc.schedule(1_000_000, 3.5, 360, None, True, 12, rule["id"])
    written_principal = out["balloon_principal"]
    run_id = out["run_id"]

    # 落库后把上限改严（低于已写入的末期本金）
    svc.update_balloon_rule(rule["id"], None, 100_000, True)

    # 打开旧条：末期本金仍是写入值，不随后续规则变化
    old = svc.run(run_id)
    assert old["result"]["balloon_principal"] == written_principal
    assert old["result"]["balloon_payment"] == out["balloon_payment"]

    # 同一条规则现在重新试算应被拒绝，且不影响旧条
    with pytest.raises(HTTPException) as ei:
        svc.schedule(1_000_000, 3.5, 360, None, True, 12, rule["id"])
    assert ei.value.status_code == 400
    assert svc.run(run_id)["result"]["balloon_principal"] == written_principal


def test_update_rule_fields(svc):
    rule = svc.create_balloon_rule(60, 1_000_000, True)
    updated = svc.update_balloon_rule(rule["id"], 120, 2_000_000, None)
    assert updated["balloon_period"] == 120
    assert updated["balloon_cap"] == 2_000_000
    assert updated["enabled"] is True
    assert svc.update_balloon_rule(999999, 12, 1, True) is None
