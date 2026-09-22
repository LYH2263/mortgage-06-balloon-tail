import pytest
from app.engines.amortization import equal_payment_schedule
from app.engines.balloon import BalloonLimitExceeded, balloon_schedule


def test_regular_payment_matches_equal_payment():
    # 前若干期的常规月供必须与整表等额本息一致
    ref = equal_payment_schedule(1_000_000, 3.5, 360)
    s = balloon_schedule(1_000_000, 3.5, 360, 60, 10_000_000)
    assert s["monthly_payment"] == ref["monthly_payment"] == 4490.45
    assert all(r["payment"] == 4490.45 for r in s["rows"][:-1])


def test_rows_end_at_balloon_period_and_balance_zero():
    s = balloon_schedule(1_000_000, 3.5, 360, 60, 10_000_000)
    assert len(s["rows"]) == 60
    last = s["rows"][-1]
    assert last["period"] == 60
    assert last["balance"] == 0.0
    assert last["payment"] == pytest.approx(last["principal"] + last["interest"], abs=0.02)


def test_balloon_principal_matches_closed_form_balance():
    # 用独立的余额闭式公式核对末期本金：bal_k = P(1+r)^k - pay*((1+r)^k-1)/r
    P, annual, n, B = 1_000_000, 3.5, 360, 60
    r = annual / 12 / 100
    pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    expected = P * (1 + r) ** (B - 1) - pay * ((1 + r) ** (B - 1) - 1) / r
    s = balloon_schedule(P, annual, n, B, P)
    assert s["balloon_principal"] == round(expected, 2)
    assert s["balloon_payment"] == round(expected * (1 + r), 2)
    # 只还到第 B 期，利息合计应小于整表利息
    assert s["total_interest"] < equal_payment_schedule(P, annual, n)["total_interest"]


def test_first_period_is_balloon():
    s = balloon_schedule(120_000, 6.0, 12, 1, 120_000)
    assert len(s["rows"]) == 1
    assert s["rows"][0]["principal"] == 120_000.0
    assert s["rows"][0]["interest"] == 600.0
    assert s["balloon_payment"] == 120_600.0
    assert s["total_interest"] == 600.0


def test_zero_rate():
    s = balloon_schedule(120_000, 0, 12, 12, 10_000)
    assert s["monthly_payment"] == 10_000.0
    assert s["balloon_principal"] == 10_000.0
    assert s["balloon_payment"] == 10_000.0
    assert s["total_interest"] == 0.0


def test_cap_exceeded_raises_without_partial_rows_leak():
    with pytest.raises(BalloonLimitExceeded) as ei:
        balloon_schedule(1_000_000, 3.5, 360, 60, 100_000)
    assert ei.value.balloon_principal > 100_000
    assert ei.value.cap == 100_000


@pytest.mark.parametrize("B,n", [(0, 12), (13, 12), (-1, 12)])
def test_bad_balloon_period(B, n):
    with pytest.raises(ValueError):
        balloon_schedule(100, 3, n, B, 100)


def test_cap_boundary_accepted():
    s = balloon_schedule(120_000, 0, 12, 12, 10_000)
    assert s["balloon_principal"] == 10_000.0
