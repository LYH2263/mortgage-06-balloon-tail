from fastapi import APIRouter
from app.routers import balloon_rules, dashboard, history, loans, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, balloon_rules): api.include_router(r.router)
