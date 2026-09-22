"""气球尾款模块。

启用规则后：前 B-1 期按整表等额本息月供还款，第 B 期一次性收齐剩余本金及当期利息；
末期本金受规则上限约束，超限由引擎抛错，上层拒绝且不得落库。规则停用后回到整表等额本息。
"""
from app.engines.balloon import BalloonLimitExceeded, balloon_schedule


def build_packet(principal, annual_rate, months, balloon_period, balloon_cap, preview_rows=12):
    """根据规则试算并组装对外回包（不含 run_id）。"""
    full = balloon_schedule(principal, annual_rate, months, balloon_period, balloon_cap)
    rows = full["rows"]
    if len(rows) <= preview_rows:
        preview = rows
    else:
        # 行数超出预览窗口时，保留前若干期并始终带上末期气球行
        preview = rows[: max(0, preview_rows - 1)] + [rows[-1]]
    return {
        "kind": "balloon",
        "monthly_payment": full["monthly_payment"],
        "balloon_period": full["balloon_period"],
        "balloon_payment": full["balloon_payment"],
        "balloon_principal": full["balloon_principal"],
        "total_interest": full["total_interest"],
        "total_payment": full["total_payment"],
        "preview": preview,
        "row_count": len(rows),
    }
