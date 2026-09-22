from fastapi import APIRouter, HTTPException
from app.schemas.balloon import BalloonRuleCreate, BalloonRuleUpdate
from app.services.mortgage_service import MortgageService

router = APIRouter()


@router.get("/balloon-rules")
def list_rules():
    with MortgageService() as s:
        return {"items": s.list_balloon_rules()}


@router.post("/balloon-rules")
def create_rule(body: BalloonRuleCreate):
    with MortgageService() as s:
        return s.create_balloon_rule(body.balloon_period, body.balloon_cap, body.enabled)


@router.patch("/balloon-rules/{rule_id}")
def update_rule(rule_id: int, body: BalloonRuleUpdate):
    with MortgageService() as s:
        row = s.update_balloon_rule(
            rule_id, body.balloon_period, body.balloon_cap, body.enabled)
        if not row:
            raise HTTPException(404, "balloon rule not found")
        return row
