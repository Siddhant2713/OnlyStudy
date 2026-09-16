# Spec 04 learning notes

## Architecture implemented

The old path treated Gemini output as a complete executable scene. The new path persists and validates a lesson plan, screenplay, storyboard, deterministic critique result, voice timing, and thin scene orchestration before rendering. Each artifact remains in `server/runtime/jobs/<job-id>/`, so a late rendering problem no longer destroys the teaching and visual planning evidence needed to diagnose it.

## Important implementation decisions

- Gemini is isolated behind `LLMProvider` and `GeminiProvider`; no other LLM provider was added.
- Structured stages use strict JSON followed by Pydantic validation and one bounded JSON-repair call. Invalid JSON is never accepted silently.
- Storyboards hold stable semantic object IDs and relations. The bicycle fixture demonstrates the same `rear_wheel` across scenes and attaches friction to it through a semantic relation.
- The code-generation stage is constrained to a small `LessonScene` runtime API. The AST validator permits only Manim and the trusted runtime import and rejects dangerous calls and dunder access.
- TTS happens after screenplay creation. Block-level audio durations normalize `audio_locked` scene timing before Manim code is rendered. Generated code no longer imports gTTS or manim-voiceover.
- Feedback uses deterministic routing: voice/timing feedback begins at voicing; visual, equation, and physics feedback begins at storyboarding; wording/speed feedback begins at screenwriting; other feedback starts at planning.

## Limitations remaining

The reusable runtime is deliberately an MVP: it implements a small set of primitives and qualitative camera/action translations rather than a numerical physics simulator or word-level lip sync. Audio muxing requires the system `ffmpeg` executable. A production deployment should replace the in-memory job registry with durable job metadata and move long render jobs to a worker queue.

## Verification

Six deterministic backend tests pass: bicycle schema/reference validation, dangling-reference rejection, generated-code security validation, feedback routing, mocked Gemini JSON repair, and audio-locked timing normalization. A short Manim smoke render completed with the trusted runtime. Finally, a mocked-Gemini `POST /api/lessons` bicycle job completed through the actual FastAPI endpoint with voice disabled; it persisted `request.json`, `lesson_plan.json`, `screenplay.json`, `storyboard.json`, `validation.json`, `scene.py`, render media, and `final.mp4`, and all plan/storyboard/video endpoints returned successfully. The React production build also passes.
