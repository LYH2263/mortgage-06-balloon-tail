from pydantic import BaseModel, Field


class BalloonRuleIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    balloon_period: int = Field(gt=0, le=600)
    cap: float = Field(gt=0)
    enabled: bool = True


class BalloonRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    balloon_period: int | None = Field(default=None, gt=0, le=600)
    cap: float | None = Field(default=None, gt=0)
    enabled: bool | None = None


class BalloonScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    rule_id: int | None = None
    balloon_period: int | None = Field(default=None, gt=0, le=600)
    cap: float | None = Field(default=None, gt=0)
    enabled: bool = False
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
