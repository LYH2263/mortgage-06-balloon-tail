import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="mortgage-test-"))

import pytest
from app import seed
from app.engines.amortization import equal_payment_schedule
from app.engines.balloon import balloon_schedule
from app.modules.balloon import CapExceeded
from app.services.mortgage_service import MortgageService

seed.init_db()

P, RATE, N, B = 1_000_000, 3.5, 360, 36


def test_regular_payment_matches_equal_payment():
    b = balloon_schedule(P, RATE, N, B)
    e = equal_payment_schedule(P, RATE, N)
    assert b["monthly_payment"] == e["monthly_payment"]


def test_final_period_collects_remaining_balance():
    b = balloon_schedule(P, RATE, N, B)
    assert len(b["rows"]) == B
    last = b["rows"][-1]
    assert last["period"] == B
    assert last["balance"] == 0
    assert last["principal"] == b["final_principal"]
    assert last["payment"] == b["final_payment"]
    assert b["final_payment"] == round(b["final_principal"] + last["interest"], 2)
    assert b["final_principal"] > b["monthly_payment"]


def test_full_term_balloon_equals_equal_payment():
    b = balloon_schedule(P, RATE, N, N)
    e = equal_payment_schedule(P, RATE, N)
    assert b["total_interest"] == e["total_interest"]
    assert b["final_principal"] == e["rows"][-1]["principal"]


def test_zero_rate():
    b = balloon_schedule(120000, 0, 12, 6)
    assert b["monthly_payment"] == 10000.0
    assert b["final_principal"] == 70000.0
    assert b["total_interest"] == 0.0


def test_invalid_period():
    with pytest.raises(ValueError):
        balloon_schedule(P, RATE, N, N + 1)
    with pytest.raises(ValueError):
        balloon_schedule(P, RATE, N, 0)


def test_cap_exceeded_rejects_and_writes_nothing():
    with MortgageService() as s:
        before = len(s.history(1000))
        with pytest.raises(CapExceeded):
            s.balloon_schedule(P, RATE, N, balloon_period=B, cap=1000.0, enabled=True, persist=True)
        assert len(s.history(1000)) == before


def test_persist_false_writes_nothing():
    with MortgageService() as s:
        before = len(s.history(1000))
        out = s.balloon_schedule(P, RATE, N, balloon_period=B, cap=950_000, enabled=True, persist=False)
        assert out["run_id"] is None
        assert out["mode"] == "balloon"
        assert len(s.history(1000)) == before


def test_disabled_falls_back_to_equal_payment():
    with MortgageService() as s:
        out = s.balloon_schedule(P, RATE, N, balloon_period=B, cap=1.0, enabled=False, persist=False)
        e = equal_payment_schedule(P, RATE, N)
        assert out["mode"] == "equal_payment"
        assert out["monthly_payment"] == e["monthly_payment"]
        assert out["row_count"] == N
        assert out["final_principal"] is None


def test_rule_crud_and_disable():
    with MortgageService() as s:
        rule = s.create_balloon_rule("三年气球", B, 950_000, True)
        assert rule["id"] and rule["enabled"] is True
        rule = s.update_balloon_rule(rule["id"], {"cap": 850_000})
        assert rule["cap"] == 850_000
        rule = s.disable_balloon_rule(rule["id"])
        assert rule["enabled"] is False
        assert s.update_balloon_rule(999999, {"cap": 1}) is None


def test_disabled_rule_falls_back_when_referenced():
    with MortgageService() as s:
        rule = s.create_balloon_rule("停用规则", B, 950_000, False)
        out = s.balloon_schedule(P, RATE, N, rule_id=rule["id"], persist=False)
        assert out["mode"] == "equal_payment"


def test_snapshot_immutable_after_cap_tightened():
    with MortgageService() as s:
        rule = s.create_balloon_rule("快照规则", B, 950_000, True)
        out = s.balloon_schedule(P, RATE, N, rule_id=rule["id"], persist=True)
        written = out["final_principal"]
        assert out["run_id"]
        s.update_balloon_rule(rule["id"], {"cap": 1.0})  # 改严上限
        row = s.run(out["run_id"])
        assert row["kind"] == "balloon"
        assert row["result"]["final_principal"] == written
        # 新试算按新上限会被拒绝，但旧记录仍是写入值
        with pytest.raises(CapExceeded):
            s.balloon_schedule(P, RATE, N, rule_id=rule["id"], persist=True)
        assert s.run(out["run_id"])["result"]["final_principal"] == written
