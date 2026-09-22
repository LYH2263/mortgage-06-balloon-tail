from fastapi import HTTPException
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.engines.balloon import BalloonLimitExceeded
from app.modules import balloon as balloon_mod
from app.repositories import balloon_rules, loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, run_id): return runs.get(self._c, run_id)
    def list_balloon_rules(self): return balloon_rules.list_all(self._c)
    def create_balloon_rule(self, balloon_period, balloon_cap, enabled=True):
        return balloon_rules.create(self._c, balloon_period, balloon_cap, enabled)
    def update_balloon_rule(self, rid, balloon_period, balloon_cap, enabled):
        return balloon_rules.update(self._c, rid, balloon_period, balloon_cap, enabled)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, balloon_rule_id=None):
        # 传入启用中的气球规则才走气球尾款；规则不存在或已停用均回到整表等额本息。
        rule = None
        if balloon_rule_id is not None:
            rule = balloon_rules.get(self._c, balloon_rule_id)
            if rule is None:
                raise HTTPException(404, "balloon rule not found")
            if not rule["enabled"]:
                rule = None
        if rule is not None:
            try:
                out = balloon_mod.build_packet(
                    principal, annual_rate, months,
                    rule["balloon_period"], rule["balloon_cap"], preview_rows)
            except BalloonLimitExceeded as e:
                # 上限校验失败：拒绝请求，且不写任何 calc_runs 记录。
                raise HTTPException(400, {
                    "error": "balloon_cap_exceeded",
                    "balloon_principal": e.balloon_principal,
                    "balloon_cap": e.cap,
                })
            except ValueError as e:
                raise HTTPException(400, str(e))
            if persist:
                rid = runs.insert(self._c, "balloon", {
                    "principal": principal, "annual_rate": annual_rate, "months": months,
                    # 快照规则参数：旧条此后不再随规则当前值变化
                    "balloon_rule_id": rule["id"],
                    "balloon_period": rule["balloon_period"],
                    "balloon_cap": rule["balloon_cap"],
                }, out, loan_id)
            else:
                rid = None
            return {"run_id": rid, **out}

        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months}, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
