"""气球尾款模块：前 B-1 期等额本息，第 B 期收齐剩余本金与利息，末期本金受尾款上限约束。"""
from app.engines.balloon import balloon_schedule


class CapExceeded(Exception):
    """末期本金超过尾款上限；调用方须拒绝请求且不写任何记录。"""

    def __init__(self, final_principal: float, cap: float):
        self.final_principal = final_principal
        self.cap = cap
        super().__init__(f"末期本金 {final_principal} 超过尾款上限 {cap}")


__all__ = ["balloon_schedule", "CapExceeded"]
