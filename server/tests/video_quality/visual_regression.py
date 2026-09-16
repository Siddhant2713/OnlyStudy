"""Low-cost visual-regression contract; rendering is optional in developer/CI environments."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class StructuralSnapshot:
    scene_id: str
    visible_object_ids: list[str]
    action_types: list[str]
    camera_target_id: str | None
    equations: list[str]
    duration_seconds: float | None

def capture_structural_snapshots(board) -> list[StructuralSnapshot]:
    """Deterministic proxy until frame rendering is available; no pixel-perfect assertion."""
    return [StructuralSnapshot(scene.id, sorted(scene.active_objects), [action.type for action in scene.actions], scene.camera.target_object_id, [equation.expression for equation in scene.equations], scene.duration_seconds) for scene in board.scenes]

def write_snapshots(board, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "structural_snapshots.json"
    path.write_text(json.dumps([asdict(snapshot) for snapshot in capture_structural_snapshots(board)], indent=2))
    return path
