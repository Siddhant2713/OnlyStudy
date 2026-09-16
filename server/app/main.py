import json
import os
import shutil
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from app.llm.gemini import GeminiProvider
from app.video.artifacts import ArtifactStore, SAFE_ARTIFACTS
from app.video.pipeline import VideoPipeline, route_feedback
from app.video.job_state import JobState
from app.video.media import validate_video

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
JOBS_DIR = ROOT / "runtime" / "jobs"; JOBS_DIR.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
RENDER_TIMEOUT_SECONDS = int(os.getenv("RENDER_TIMEOUT_SECONDS", "900"))
JOBS: dict[str, dict] = {}; LOCK = threading.Lock()
STAGES = ["planning", "screenwriting", "storyboarding", "criticizing", "voicing", "codegen", "validating", "rendering", "muxing"]

def state_path(directory: Path) -> Path:
    return directory / "job_state.json"

def persist_job(job: dict) -> None:
    """Persist only the data needed to recover a job after an API restart."""
    path = state_path(job["directory"])
    temporary = path.with_suffix(".tmp")
    temporary.write_text(job["state"].model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(path)

def recover_jobs() -> None:
    """Rebuild the in-memory index from persisted artifacts on application startup."""
    for directory in JOBS_DIR.iterdir():
        if not directory.is_dir():
            continue
        request_path = directory / "request.json"
        if not request_path.exists():
            continue
        try:
            request = LessonRequest.model_validate_json(request_path.read_text(encoding="utf-8"))
            saved = JobState.model_validate_json(state_path(directory).read_text(encoding="utf-8")) if state_path(directory).exists() else JobState()
        except (ValueError, OSError, json.JSONDecodeError):
            continue
        final = directory / "final.mp4"
        status = saved.status
        if final.exists():
            status, stage, error = "completed", None, None; saved.finish()
        elif status in STAGES or status == "queued" or not status:
            status, stage = "interrupted", saved.stage
            error = "Generation was interrupted by an API restart. Regenerate the lesson to resume."
            saved.status, saved.message = "interrupted", error
        else:
            stage_state = saved.stages.get(saved.stage) if saved.stage else None
            stage, error = saved.stage, stage_state.error if stage_state else None
        job = {"request": request, "directory": directory, "status": status, "stage": stage, "error": error, "state": saved}
        if final.exists():
            job["video"] = final
        JOBS[directory.name] = job
        persist_job(job)
app = FastAPI(title="OnlyStudies API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class LessonRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=160)
    subject: Literal["General", "Mathematics", "Computer Science", "Physics", "Chemistry", "Biology", "Economics", "History"] = "General"
    quality: Literal["Low", "Medium", "High"] = "Medium"
    voice_preset: Literal["teaching_assistant", "professor", "enthusiastic", "calm", "neutral"] = "teaching_assistant"
    use_voiceover: bool = True
    learner_level: str = Field(default="beginner", max_length=60)
    duration_minutes: float = Field(default=2, ge=.25, le=10)
    style: str = Field(default="dark_educational", max_length=60)
class FeedbackRequest(BaseModel): feedback: str = Field(min_length=3, max_length=1000)

def response(job_id):
    job = JOBS.get(job_id)
    if not job: raise HTTPException(404, "Lesson not found")
    state = job["state"]; stage = state.stage
    artifact_paths = {"lesson_plan": "plan", "screenplay": "screenplay", "storyboard": "storyboard", "storyboard_draft": "artifacts/storyboard_draft"}
    video = job.get("video"); metadata = validate_video(video) if job["status"] == "completed" and video else None
    return {"id": job_id, "status": state.status, "stage": stage, "message": state.message, "progress": state.progress, "heartbeat_at": state.heartbeat_at, "updated_at": state.updated_at, "topic": job["request"].topic, "error": job.get("error"), "stages": {key: value.model_dump() for key, value in state.stages.items()}, "artifacts": {name: f"/api/lessons/{job_id}/{endpoint}" for name, endpoint in artifact_paths.items() if (job["directory"] / f"{name}.json").exists()}, "video": {"available": bool(metadata), "url": f"/api/lessons/{job_id}/video" if metadata else None, "size_bytes": metadata.size_bytes if metadata else None}, "video_url": f"/api/lessons/{job_id}/video" if metadata else None}
def set_stage(job_id, stage):
    with LOCK:
        job = JOBS[job_id]
        job["state"].begin(stage, f"Running {stage}"); job.update(status="running", stage=stage, error=None)
        persist_job(job)
def mux(video, voice_dir, output):
    tracks = sorted(voice_dir.glob("*.mp3"))
    if not tracks: shutil.copy2(video, output); return
    concat = voice_dir / "concat.txt"; concat.write_text("".join(f"file '{p.name}'\n" for p in tracks))
    audio = voice_dir / "narration.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(audio)], cwd=voice_dir, check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-shortest", str(output)], check=True, capture_output=True)
def run_job(job_id, feedback=None, start_stage="planning"):
    with LOCK: job = JOBS[job_id]; request = job["request"]; directory = job["directory"]
    store = ArtifactStore(directory)
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "replace_me": raise RuntimeError("GOOGLE_API_KEY is not configured. Add a real key to server/.env.")
        pipeline = VideoPipeline(GeminiProvider(api_key, MODEL), store, request, lambda stage: set_stage(job_id, stage))
        code, _ = pipeline.run(feedback, start_stage)
        set_stage(job_id, "rendering")
        media = directory / "render"
        result = subprocess.run([sys.executable, "-m", "manim", {"Low":"-ql", "Medium":"-qm", "High":"-qh"}[request.quality], "--media_dir", str(media), "-o", "visual.mp4", str(directory / "scene.py"), "SceneTopic"], cwd=directory, env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, text=True, timeout=RENDER_TIMEOUT_SECONDS)
        if result.returncode: raise RuntimeError(f"Manim render failed:\n{(result.stdout + result.stderr)[-6000:]}")
        visual = max(media.rglob("visual.mp4"), key=lambda p:p.stat().st_mtime, default=None)
        if not visual: raise RuntimeError("Manim completed without visual.mp4")
        set_stage(job_id, "muxing"); final = directory / "final.mp4"; mux(visual, directory / "voice", final)
        metadata = validate_video(final)
        with LOCK:
            job["state"].finish(); job.update(status="completed", stage=None, video=final, error=None)
            persist_job(job)
    except subprocess.TimeoutExpired:
        with LOCK:
            job["state"].finish(f"Manim render exceeded {RENDER_TIMEOUT_SECONDS} seconds"); job.update(status="failed", error=f"Manim render exceeded {RENDER_TIMEOUT_SECONDS} seconds")
            persist_job(job)
    except Exception as error:
        with LOCK:
            stage = job.get("stage", "generation")
            job["state"].finish(f"{stage} failed: {error}"); job.update(status="failed", error=f"{stage} failed: {error}")
            persist_job(job)

@app.get("/api/health")
def health(): return {"status":"ok", "model":MODEL, "pipeline":"structured"}
@app.post("/api/lessons", status_code=202)
def create_lesson(request: LessonRequest, tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex; directory = JOBS_DIR / job_id; directory.mkdir(); store = ArtifactStore(directory); store.write_json("request", request.model_dump())
    with LOCK:
        JOBS[job_id] = {"request":request, "directory":directory, "status":"queued", "stage":"planning", "state": JobState()}
        persist_job(JOBS[job_id])
    tasks.add_task(run_job, job_id); return response(job_id)
@app.get("/api/lessons/{job_id}")
def get_lesson(job_id: str):
    with LOCK: return response(job_id)
def artifact(job_id, name):
    with LOCK: job = JOBS.get(job_id)
    if not job: raise HTTPException(404, "Lesson not found")
    path = ArtifactStore(job["directory"]).path(name)
    if not path.exists(): raise HTTPException(404, "Artifact is not available yet")
    return JSONResponse(json.loads(path.read_text())) if path.suffix == ".json" else FileResponse(path)
@app.get("/api/lessons/{job_id}/plan")
def get_plan(job_id: str): return artifact(job_id, "lesson_plan")
@app.get("/api/lessons/{job_id}/screenplay")
def get_screenplay(job_id: str): return artifact(job_id, "screenplay")
@app.get("/api/lessons/{job_id}/storyboard")
def get_storyboard(job_id: str): return artifact(job_id, "storyboard")
@app.get("/api/lessons/{job_id}/artifacts/{name}")
def get_artifact(job_id: str, name: str):
    if name not in SAFE_ARTIFACTS: raise HTTPException(404, "Unknown artifact")
    return artifact(job_id, name)
@app.post("/api/lessons/{job_id}/feedback", status_code=202)
def regenerate(job_id: str, payload: FeedbackRequest, tasks: BackgroundTasks):
    with LOCK:
        job = JOBS.get(job_id)
        if not job: raise HTTPException(404, "Lesson not found")
        if job["status"] in STAGES: raise HTTPException(409, "This lesson is already being generated")
        if not (job["directory"] / "lesson_plan.json").exists(): raise HTTPException(409, "No lesson plan is available yet")
        start = route_feedback(payload.feedback); job["state"] = JobState(message="Queued for regeneration"); job.update(status="queued", stage=start, error=None)
        persist_job(job)
    tasks.add_task(run_job, job_id, payload.feedback, start); return response(job_id)
@app.get("/api/lessons/{job_id}/video")
def video(job_id: str):
    with LOCK: job = JOBS.get(job_id); path = job.get("video") if job else None
    if not path or not path.exists(): raise HTTPException(404, "Video not found")
    return FileResponse(path, media_type="video/mp4", filename=f"{job['request'].topic.replace(' ', '_')}_lesson.mp4")
@app.get("/api/lessons/{job_id}/diagnostics")
def diagnostics(job_id: str):
    with LOCK: job = JOBS.get(job_id)
    if not job: raise HTTPException(404, "Lesson not found")
    return {"job_id": job_id, "status": job["state"].status, "stage": job["state"].stage, "message": job["state"].message, "stages": {key: value.model_dump() for key, value in job["state"].stages.items()}, "artifacts": sorted(path.name for path in job["directory"].iterdir())}

recover_jobs()
