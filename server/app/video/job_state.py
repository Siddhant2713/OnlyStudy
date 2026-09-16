from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

def now() -> str: return datetime.now(timezone.utc).isoformat()

class StageState(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    attempt: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    last_heartbeat_at: str | None = None
    detail: str | None = None
    error: str | None = None

class JobState(BaseModel):
    status: Literal["queued", "running", "completed", "failed", "interrupted"] = "queued"
    stage: str | None = None
    progress: float = 0
    message: str = "Queued"
    stages: dict[str, StageState] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now)
    updated_at: str = Field(default_factory=now)
    heartbeat_at: str = Field(default_factory=now)

    def begin(self, name: str, message: str, attempt: int = 1):
        stamp = now(); self.status = "running"; self.stage = name; self.message = message; self.updated_at = self.heartbeat_at = stamp
        self.stages[name] = StageState(name=name, status="running", attempt=attempt, started_at=stamp, last_heartbeat_at=stamp, detail=message)

    def heartbeat(self, message: str | None = None):
        stamp = now(); self.updated_at = self.heartbeat_at = stamp
        if message: self.message = message
        if self.stage and self.stage in self.stages:
            stage = self.stages[self.stage]; stage.last_heartbeat_at = stamp; stage.detail = message or stage.detail

    def finish(self, error: str | None = None):
        stamp = now(); self.updated_at = self.heartbeat_at = stamp
        if self.stage in self.stages:
            stage = self.stages[self.stage]; stage.status = "failed" if error else "completed"; stage.completed_at = stamp; stage.error = error
        self.status = "failed" if error else "completed"; self.message = error or "Lesson ready"; self.stage = None
