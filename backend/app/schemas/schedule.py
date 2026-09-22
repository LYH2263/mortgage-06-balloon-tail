from pydantic import BaseModel, Field
class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
    balloon_rule_id: int | None = Field(default=None, description="传入启用中的气球规则即按气球尾款试算；停用或不传则整表等额本息")
