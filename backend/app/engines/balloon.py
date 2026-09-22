def balloon_schedule(principal: float, annual_rate: float, months: int, balloon_period: int) -> dict:
    """气球尾款：前 balloon_period-1 期按整贷期限等额本息，第 balloon_period 期收齐剩余本金加当期利息。"""
    P = float(principal)
    n = int(months)
    B = int(balloon_period)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if not 1 <= B <= n:
        raise ValueError("balloon_period")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, B + 1):
        interest = bal * r
        principal_part = bal if i == B else pay - interest
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
    return {
        "monthly_payment": round(pay, 2),
        "final_payment": rows[-1]["payment"],
        "final_principal": rows[-1]["principal"],
        "final_period": B,
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
