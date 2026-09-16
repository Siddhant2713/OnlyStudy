"""Headless timeline compilation for semantic lessons."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class TimelineBeat:
    start: float
    end: float
    narration_block_id: str
    actions: list[dict[str, Any]]
    camera: dict[str, Any]
    pause_policy: str

@dataclass
class CompiledTimeline:
    beats: list[TimelineBeat]
    duration_seconds: float
    warnings: list[str]
    def model_dump(self, **_kwargs): return {"beats": [asdict(beat) for beat in self.beats], "duration_seconds": self.duration_seconds, "warnings": self.warnings}

def compile_timeline(board, screenplay, durations: dict[str, float]) -> CompiledTimeline:
    blocks = {block.id: block for block in screenplay.narration_blocks}
    cursor, beats, warnings = 0.0, [], []
    for scene in board.scenes:
        block_ids = scene.narration_block_ids or [f"scene:{scene.id}"]
        audio = sum(durations.get(block_id, blocks.get(block_id).estimated_duration_seconds if block_id in blocks else 0) for block_id in block_ids)
        target = audio if scene.duration_policy == "audio_locked" else max(audio, scene.duration_seconds or 0)
        actions = [action.model_dump(mode="json") for action in scene.actions]
        action_total = sum(max(0.0, action.get("duration", .5)) for action in actions)
        if target and action_total > target:
            for action in actions: action["duration"] = round(max(.1, action.get("duration", .5) * target / action_total), 3)
            warnings.append(f"{scene.id}: compressed visual actions to fit {target:.2f}s of audio")
        duration = max(target, sum(action.get("duration", .5) for action in actions), .1)
        for block_id in block_ids:
            end = cursor + duration / len(block_ids)
            beats.append(TimelineBeat(cursor, end, block_id, actions, scene.camera.model_dump(mode="json"), "reinforce" if duration > action_total else "none")); cursor = end
        scene.duration_seconds = duration
    return CompiledTimeline(beats, cursor, warnings)
