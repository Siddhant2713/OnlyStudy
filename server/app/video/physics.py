from pydantic import BaseModel
class PhysicalQuantity(BaseModel):
    id: str; symbol: str; value: float | None = None; unit: str | None = None
class ForceRelation(BaseModel):
    id: str; source: str; target: str; expression: str | None = None; direction: str
