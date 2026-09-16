import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class VideoMetadata:
    size_bytes: int
    duration_seconds: float

def validate_video(path: Path) -> VideoMetadata:
    if path.suffix.lower() != ".mp4" or not path.is_file() or path.stat().st_size <= 0: raise ValueError("final video is missing or empty")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True, timeout=30)
    if probe.returncode: raise ValueError(f"ffprobe failed: {probe.stderr[-500:]}")
    data = json.loads(probe.stdout); duration = float(data.get("format", {}).get("duration", 0))
    if duration <= 0 or not any(stream.get("codec_type") == "video" for stream in data.get("streams", [])): raise ValueError("final MP4 has no playable video stream")
    return VideoMetadata(path.stat().st_size, duration)
