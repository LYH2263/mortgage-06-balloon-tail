from pydantic import BaseModel, Field


class BalloonRuleCreate(BaseModel):
    balloon_period: int = Field(gt=0, le=600, description="气球期序号 B（第几期收尾）")
    balloon_cap: float = Field(ge=0, description="末期本金上限")
    enabled: bool = True


class BalloonRuleUpdate(BaseModel):
    balloon_period: int | None = Field(default=None, gt=0, le=600)
    balloon_cap: float | None = Field(default=None, ge=0)
    enabled: bool | None = None
