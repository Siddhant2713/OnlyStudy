import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
JOBS_DIR = ROOT / "runtime" / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
JOBS: dict[str, dict] = {}
LOCK = threading.Lock()

app = FastAPI(title="OnlyStudies API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class LessonRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=160)
    subject: Literal["General", "Mathematics", "Computer Science", "Physics", "Chemistry", "Biology", "Economics", "History"] = "General"
    quality: Literal["Low", "Medium", "High"] = "Medium"
    voice_preset: Literal["teaching_assistant", "professor", "enthusiastic", "calm", "neutral"] = "teaching_assistant"
    use_voiceover: bool = True

class FeedbackRequest(BaseModel):
    feedback: str = Field(min_length=3, max_length=1000)

def job_response(job_id: str) -> dict:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Lesson not found")
    return {"id": job_id, "status": job["status"], "topic": job["request"].topic, "error": job.get("error"), "video_url": f"/api/lessons/{job_id}/video" if job["status"] == "completed" else None}

def generate_code(request: LessonRequest, feedback: str | None, previous: str | None) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured on the server.")
    voice_imports = "from manim_voiceover import VoiceoverScene\nfrom manim_voiceover.services.gtts import GTTSService" if request.use_voiceover else ""
    base = "VoiceoverScene" if request.use_voiceover else "Scene"
    narration = "Set GTTSService(lang='en', tld='com') and use self.voiceover blocks." if request.use_voiceover else "Use concise on-screen Text."
    revision = f"Address this feedback using the prior code: {feedback}\n{previous}" if feedback else ""
    prompt = f"""Return only runnable Python code for a Manim animation. Topic: {request.topic!r}; subject: {request.subject}. Use a clear dark 2D vector style and explain only the topic in definition, analogy, and worked-example phases. Prevent label overlap, fade out each phase before the next, do not use MathTex or LaTex, and make the total duration at least 60 seconds. Use class SceneTopic({base}). Imports: from manim import *\n{voice_imports}. {narration} {revision}"""
    for attempt in range(3):
        try:
            code = genai.Client(api_key=api_key).models.generate_content(model=MODEL, contents=prompt).text
            code = code.replace("```python", "").replace("```", "").strip()
            return code if "from manim import" in code else "from manim import *\n" + code
        except Exception as error:
            if (getattr(error, "status", None) or getattr(error, "code", None)) == 429 and attempt < 2:
                time.sleep(2)
                continue
            raise RuntimeError(f"Could not generate animation: {error}") from error
    raise RuntimeError("Could not generate animation after retries.")

def run_job(job_id: str, feedback: str | None = None) -> None:
    with LOCK:
        job = JOBS[job_id]
        job.update(status="generating", error=None)
        request: LessonRequest = job["request"]
        previous = job.get("code")
    try:
        code = generate_code(request, feedback, previous)
        compile(code, "scene.py", "exec")
        directory = JOBS_DIR / job_id
        script = directory / "scene.py"
        script.write_text(code, encoding="utf-8")
        with LOCK:
            job["status"] = "rendering"
        quality = {"Low": "-ql", "Medium": "-qm", "High": "-qh"}[request.quality]
        output = subprocess.run([sys.executable, "-m", "manim", quality, "--media_dir", str(directory / "media"), "-o", "lesson.mp4", str(script), "SceneTopic"], cwd=directory, capture_output=True, text=True)
        if output.returncode:
            raise RuntimeError((output.stdout + "\n" + output.stderr).strip() or "Manim failed.")
        rendered = max((directory / "media").rglob("lesson.mp4"), key=lambda path: path.stat().st_mtime, default=None)
        if not rendered:
            raise RuntimeError("Manim completed but no video was produced.")
        video = directory / "lesson.mp4"
        shutil.copy2(rendered, video)
        with LOCK:
            job.update(status="completed", code=code, video=video)
    except Exception as error:
        with LOCK:
            job.update(status="failed", error=str(error))

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/lessons", status_code=202)
def create_lesson(request: LessonRequest, tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex
    (JOBS_DIR / job_id).mkdir()
    with LOCK: JOBS[job_id] = {"request": request, "status": "queued"}
    tasks.add_task(run_job, job_id)
    return job_response(job_id)

@app.get("/api/lessons/{job_id}")
def get_lesson(job_id: str):
    with LOCK: return job_response(job_id)

@app.post("/api/lessons/{job_id}/feedback", status_code=202)
def regenerate_lesson(job_id: str, payload: FeedbackRequest, tasks: BackgroundTasks):
    with LOCK:
        if job_id not in JOBS: raise HTTPException(404, "Lesson not found")
        if not JOBS[job_id].get("code"): raise HTTPException(409, "A completed lesson is required.")
        JOBS[job_id]["status"] = "queued"
    tasks.add_task(run_job, job_id, payload.feedback)
    return job_response(job_id)

@app.get("/api/lessons/{job_id}/video")
def download_video(job_id: str):
    with LOCK:
        job = JOBS.get(job_id)
        video = job.get("video") if job else None
    if not video or not video.exists(): raise HTTPException(404, "Video not found")
    return FileResponse(video, media_type="video/mp4", filename=f"{job['request'].topic.replace(' ', '_')}_lesson.mp4")
