import json
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules import balloon
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
    def run(self, rid):
        row = runs.get(self._c, rid)
        if not row: return None
        row["input"] = json.loads(row.pop("input_json"))
        row["result"] = json.loads(row.pop("result_json"))
        return row
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12):
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months}, out, loan_id)
        return {"run_id": rid, **out}
    def list_balloon_rules(self): return balloon_rules.list_all(self._c)
    def create_balloon_rule(self, name, balloon_period, cap, enabled):
        rid = balloon_rules.insert(self._c, name, balloon_period, cap, enabled)
        return balloon_rules.get(self._c, rid)
    def update_balloon_rule(self, rid, fields):
        if fields and not balloon_rules.update(self._c, rid, fields):
            return None
        return balloon_rules.get(self._c, rid)
    def disable_balloon_rule(self, rid):
        if not balloon_rules.set_enabled(self._c, rid, False): return None
        return balloon_rules.get(self._c, rid)
    def balloon_schedule(self, principal, annual_rate, months, rule_id=None, balloon_period=None,
                         cap=None, enabled=False, loan_id=None, persist=True, preview_rows=12):
        if rule_id is not None:
            rule = balloon_rules.get(self._c, rule_id)
            if not rule: raise LookupError("balloon_rule")
            balloon_period, cap, enabled = rule["balloon_period"], rule["cap"], rule["enabled"]
        payload = {"principal": principal, "annual_rate": annual_rate, "months": months,
                   "rule_id": rule_id, "balloon_period": balloon_period, "cap": cap, "enabled": enabled}
        if enabled:
            if balloon_period is None: raise ValueError("balloon_period")
            full = balloon.balloon_schedule(principal, annual_rate, months, balloon_period)
            if cap is not None and full["final_principal"] > cap:
                raise balloon.CapExceeded(full["final_principal"], cap)
            out = {k: full[k] for k in ("monthly_payment", "final_payment", "final_principal", "final_period", "total_interest", "total_payment")}
            out["mode"] = "balloon"
            rows = full["rows"]
        else:
            full = equal_payment_schedule(principal, annual_rate, months)
            out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
            out.update(mode="equal_payment", final_payment=None, final_principal=None, final_period=None)
            rows = full["rows"]
        out["preview"] = rows[:preview_rows]
        out["row_count"] = len(rows)
        rid = None
        if persist:
            rid = runs.insert(self._c, "balloon", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
