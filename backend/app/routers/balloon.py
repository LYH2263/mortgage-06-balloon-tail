from fastapi import APIRouter, HTTPException
from app.modules.balloon import CapExceeded
from app.schemas.balloon import BalloonRuleIn, BalloonRuleUpdate, BalloonScheduleRequest
from app.services.mortgage_service import MortgageService

router = APIRouter()


@router.get("/balloon/rules")
def list_rules():
    with MortgageService() as s: return {"items": s.list_balloon_rules()}


@router.post("/balloon/rules", status_code=201)
def create_rule(body: BalloonRuleIn):
    with MortgageService() as s:
        return s.create_balloon_rule(body.name, body.balloon_period, body.cap, body.enabled)


@router.put("/balloon/rules/{rule_id}")
def update_rule(rule_id: int, body: BalloonRuleUpdate):
    with MortgageService() as s:
        row = s.update_balloon_rule(rule_id, body.model_dump(exclude_none=True))
        if not row: raise HTTPException(404)
        return row


@router.post("/balloon/rules/{rule_id}/disable")
def disable_rule(rule_id: int):
    with MortgageService() as s:
        row = s.disable_balloon_rule(rule_id)
        if not row: raise HTTPException(404)
        return row


@router.post("/balloon/schedule")
def balloon_schedule(body: BalloonScheduleRequest):
    with MortgageService() as s:
        try:
            return s.balloon_schedule(body.principal, body.annual_rate, body.months,
                                      rule_id=body.rule_id, balloon_period=body.balloon_period,
                                      cap=body.cap, enabled=body.enabled, loan_id=body.loan_id,
                                      persist=body.persist, preview_rows=body.preview_rows)
        except CapExceeded as e:
            raise HTTPException(422, detail=str(e))
        except LookupError:
            raise HTTPException(404, detail="balloon_rule not found")
        except ValueError as e:
            raise HTTPException(422, detail=f"invalid {e}")
