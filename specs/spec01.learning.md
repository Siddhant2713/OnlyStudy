# Spec 01 learning plan

## Current milestone

The project currently has a Streamlit frontend coupled directly to Python video-generation code. Spec 01 calls for a clean React client and a separately deployable server.

## Next plan

1. Create `client/` as a React/Vite application that collects lesson options, submits jobs, polls their status, displays videos, downloads MP4s, and supports feedback regeneration.
2. Create `server/` as a FastAPI service with endpoints for health checks, lesson creation, job status, feedback regeneration, video download, and cleanup.
3. Move the AI-generation and Manim rendering responsibilities behind server services, keeping generated job artifacts outside source folders.
4. Update the root documentation, ignore generated videos and client build artifacts, and retain legacy files until the new path is verified.
5. Verify the API walking skeleton first, then run a low-quality silent lesson end-to-end before testing voiceover and deployment configuration.


## Implementation update

The React client and FastAPI server structure have now been created. The API exposes health, create lesson, job polling, feedback regeneration, and MP4 download endpoints. The client includes the corresponding form, polling state, player, download link, and feedback flow.

## Next actionable plan

1. Install `server/requirements.txt`, set `server/.env`, and verify `GET /api/health` with Uvicorn running.
2. Install the client dependencies and build the Vite app.
3. Run one low-quality silent lesson end-to-end, then verify voiceover and feedback regeneration.
4. Before deployment, add durable job storage plus a proper background worker so rendering survives process restarts.
