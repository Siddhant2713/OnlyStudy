import json
from pathlib import Path
from pydantic import BaseModel
SAFE_ARTIFACTS = {"request", "lesson_plan", "screenplay", "storyboard", "storyboard_draft", "validation", "quality_report", "timeline", "voice_timing", "scene", "screenplay_draft"}
class ArtifactStore:
    def __init__(self, directory: Path): self.directory = directory; directory.mkdir(parents=True, exist_ok=True)
    def write_json(self, name: str, value):
        path = self.directory / f"{name}.json"; data = value.model_dump(mode="json") if hasattr(value, "model_dump") else value; path.write_text(json.dumps(data, indent=2), encoding="utf-8"); return path
    def read_json(self, name: str): return json.loads((self.directory / f"{name}.json").read_text(encoding="utf-8"))
    def write_text(self, name: str, text: str):
        path = self.directory / name; path.write_text(text, encoding="utf-8"); return path
    def path(self, name: str):
        if name not in SAFE_ARTIFACTS: raise ValueError("unknown artifact")
        return self.directory / ("scene.py" if name == "scene" else f"{name}.json")
