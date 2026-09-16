from pathlib import Path
from typing import Protocol
from pydantic import BaseModel
class VoiceResult(BaseModel): output_path: Path; duration_seconds: float; segments: list[dict] = []
class VoiceProvider(Protocol):
    def synthesize(self, text: str, *, preset: str, output_path: Path) -> VoiceResult: ...
