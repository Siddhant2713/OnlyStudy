# Spec 03 learning notes

## Diagnosis

The Uvicorn log proves the API accepted and began the lesson job. The displayed Google SDK message was a warning, not a successful render: the application called `Models.generate_content` directly, which current `google-genai` releases warn against when automatic function calling is enabled. The configured default, `gemini-3.6-flash`, was also not a safe public model default, so generation could fail before Manim ran.

The original pipeline also made failures difficult to recover from: renderer output could be excessively large, renders could run indefinitely, and generated scene code was discarded if Manim failed. Consequently, feedback could not repair a failed generated scene.

## Changes made

1. Replaced direct model generation with `client.chats.create(...).send_message(...)`, eliminating the AFC warning path.
2. Changed the default and example model to `gemini-2.5-flash`, while retaining `GEMINI_MODEL` as an environment override.
3. Added response validation for empty responses, invalid Python, and a missing `SceneTopic.construct` before rendering.
4. Added a bounded Manim render timeout (`RENDER_TIMEOUT_SECONDS`, default 900 seconds) and preserved the useful final 6,000 characters of renderer output.
5. Persisted generated code before rendering so feedback regeneration can repair a failed scene, and rejected duplicate feedback requests while a job is active.

## Operating notes

Run the server from `server/` using its own virtual environment. A virtual environment must be recreated—not moved—if its location changes, because its scripts contain absolute interpreter paths. Let `npm install` finish before `npm run dev`; cancelling it leaves Vite unavailable.

For a first end-to-end check, submit a low-quality lesson with voiceover disabled. That isolates Gemini and Manim before adding gTTS/network dependency failures. If a render fails, copy the job error or submit focused feedback; the generated `scene.py` remains in `server/runtime/jobs/<job-id>/` for inspection.
## Connection-lifecycle follow-up

A `POST /api/lessons` returning 202 and a later `GET /api/lessons/<id>` returning 200 are issued by the React client in `client/src/App.tsx`; they prove the browser reached the current FastAPI endpoints. The browser was not the closed client.

The error occurred in the background job after the POST response. The backend used `genai.Client(...).chats.create(...)` as one temporary expression. A `Chat` retains the temporary client transport, so Python could collect that temporary `Client` and close the HTTP transport before `chat.send_message(...)`. The fix keeps a named Gemini client alive for the entire send operation and closes it only afterwards. The React client now also catches failed create, polling, and feedback requests and displays a concrete API/connection error instead of an unhandled browser exception.
