import ast
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
from google.genai import types
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
JOBS_DIR = ROOT / "runtime" / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
RENDER_TIMEOUT_SECONDS = int(os.getenv("RENDER_TIMEOUT_SECONDS", "900"))
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

def clean_generated_code(text: str) -> str:
    """Extract a valid, renderable scene from the model response."""
    code = text.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[1] if "\n" in code else ""
        if code.rstrip().endswith("```"):
            code = code.rstrip()[:-3]
    code = code.strip()
    if "from manim import" not in code:
        code = "from manim import *\n" + code
    try:
        tree = ast.parse(code, filename="scene.py")
    except SyntaxError as error:
        raise RuntimeError(f"Gemini returned invalid Python: {error.msg} (line {error.lineno}).") from error
    scene = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SceneTopic"), None)
    if scene is None:
        raise RuntimeError("Gemini did not return the required SceneTopic class.")
    if not any(isinstance(node, ast.FunctionDef) and node.name == "construct" for node in scene.body):
        raise RuntimeError("SceneTopic is missing its construct method.")
    return code

def generate_code(request: LessonRequest, feedback: str | None, previous: str | None) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured on the server.")
    voice_imports = "from manim_voiceover import VoiceoverScene\nfrom manim_voiceover.services.gtts import GTTSService" if request.use_voiceover else ""
    base = "VoiceoverScene" if request.use_voiceover else "Scene"
    narration = f"In construct(), call self.set_speech_service(GTTSService(lang='en', tld='com')), then use self.voiceover blocks and tracker.duration for matching animations. Speak in a {request.voice_preset.replace('_', ' ')} style." if request.use_voiceover else "Do not import or use a voiceover service. Use concise on-screen Text."
    revision = f"Address this feedback using the prior code: {feedback}\n{previous}" if feedback else ""
    prompt = f"""Return only runnable Python code, without Markdown fences or explanation, for a Manim animation. Topic: {request.topic!r}; subject: {request.subject}. Required imports: from manim import *\n{voice_imports}. Define exactly one renderable class SceneTopic({base}) with a construct method. Use a clear dark 2D vector style and explain only the topic in definition, analogy, and worked-example phases. Prevent label overlap, fade out each phase before the next, and do not use MathTex, Tex, or LaTex. {narration} {revision}"""
    for attempt in range(3):
        client = None
        try:
            # Keep the SDK client alive while its Chat object sends the request.
            # Calling chats.create() on a temporary Client lets that client be
            # collected and its underlying HTTP transport closed too early.
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(
                model=MODEL,
                config=types.GenerateContentConfig(temperature=0.2, response_mime_type="text/plain"),
            )
            response = chat.send_message(prompt)
            if not response.text:
                raise RuntimeError("Gemini returned no text (the response may have been safety blocked).")
            return clean_generated_code(response.text)
        except Exception as error:
            if (getattr(error, "status", None) or getattr(error, "code", None)) == 429 and attempt < 2:
                time.sleep(2)
                continue
            raise RuntimeError(f"Could not generate animation: {error}") from error
        finally:
            if client is not None:
                client.close()
    raise RuntimeError("Could not generate animation after retries.")

def run_job(job_id: str, feedback: str | None = None) -> None:
    with LOCK:
        job = JOBS[job_id]
        job.update(status="generating", error=None)
        request: LessonRequest = job["request"]
        previous = job.get("code")
    try:
        code = generate_code(request, feedback, previous)
        directory = JOBS_DIR / job_id
        script = directory / "scene.py"
        script.write_text(code, encoding="utf-8")
        with LOCK:
            job.update(status="rendering", code=code)
        quality = {"Low": "-ql", "Medium": "-qm", "High": "-qh"}[request.quality]
        try:
            output = subprocess.run([sys.executable, "-m", "manim", quality, "--media_dir", str(directory / "media"), "-o", "lesson.mp4", str(script), "SceneTopic"], cwd=directory, capture_output=True, text=True, timeout=RENDER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"Manim exceeded the {RENDER_TIMEOUT_SECONDS}-second render limit.") from error
        if output.returncode:
            details = (output.stdout + "\n" + output.stderr).strip()
            raise RuntimeError(f"Manim failed:\n{details[-6000:] or 'No renderer output was captured.'}")
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
        if not JOBS[job_id].get("code"): raise HTTPException(409, "Wait for Gemini to generate the first scene before requesting changes.")
        if JOBS[job_id]["status"] in {"queued", "generating", "rendering"}: raise HTTPException(409, "This lesson is already being generated.")
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
