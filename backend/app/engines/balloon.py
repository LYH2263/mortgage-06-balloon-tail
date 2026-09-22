class BalloonLimitExceeded(ValueError):
    """末期本金超过规则上限：调用方必须拒绝且不得落库。"""
    def __init__(self, balloon_principal: float, cap: float):
        self.balloon_principal = round(balloon_principal, 2)
        self.cap = round(cap, 2)
        super().__init__(f"balloon principal {self.balloon_principal} exceeds cap {self.cap}")


def balloon_schedule(principal: float, annual_rate: float, months: int,
                     balloon_period: int, balloon_cap: float) -> dict:
    """前 balloon_period-1 期按整表等额本息月供，末期收齐剩余本金加利息。

    末期本金（收齐后的剩余本金）超过 balloon_cap 时抛 BalloonLimitExceeded。
    """
    P = float(principal)
    B = int(balloon_period)
    cap = float(balloon_cap)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if not (1 <= B <= n):
        raise ValueError("balloon_period")
    if cap < 0:
        raise ValueError("balloon_cap")

    if r == 0:
        regular_pay = P / n
    else:
        regular_pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)

    bal = P
    interest_sum = 0.0
    rows = []
    for i in range(1, B + 1):
        interest = bal * r
        if i < B:
            principal_part = regular_pay - interest
            pay_i = regular_pay
        else:
            principal_part = bal
            if principal_part > cap:
                raise BalloonLimitExceeded(principal_part, cap)
            pay_i = principal_part + interest
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    balloon_payment = rows[-1]["payment"]
    balloon_principal = rows[-1]["principal"]
    return {
        "monthly_payment": round(regular_pay, 2),
        "balloon_period": B,
        "balloon_payment": balloon_payment,
        "balloon_principal": balloon_principal,
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
