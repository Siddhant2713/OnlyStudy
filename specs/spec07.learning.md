# Spec 07 learning notes

## Reliability work implemented

- Added a durable Pydantic job-state model with explicit queued, running, completed, failed, and interrupted states; active-stage timestamps, attempts, details, and heartbeats are persisted in `job_state.json`.
- Added `GET /api/lessons/{job_id}/diagnostics` to expose stage telemetry and available artifacts.
- The lesson response now includes backend messages, heartbeat/update timestamps, stage records, and verified video metadata.
- Before a job is completed, `ffprobe` verifies that the MP4 exists, is non-empty, includes a video stream, and has positive duration.
- Gemini now reuses one SDK client for the provider/job lifetime rather than opening a new client for every call.
- React’s job type and polling policy recognize only `queued` and `running` as active states, so failed and interrupted jobs stop polling.

## Recovery fix

Old state files can name a stage without containing a matching stage record. Startup recovery now handles that legacy/incomplete state safely instead of crashing Uvicorn during import.

## Gemini availability handling

`503 UNAVAILABLE` means temporary model/service capacity, whereas `429` indicates quota or rate limiting. Gemini calls now use a bounded, configurable retry budget (`GEMINI_MAX_ATTEMPTS`, default 3) with longer exponential backoff (`GEMINI_RETRY_BASE_SECONDS`, default 5). Rate-limit retries wait longer than temporary-capacity retries. A final failure reports the exact retry count and remains a recoverable failed job rather than waiting forever.

## Scope remaining

The semantic-runtime v2 work in Spec 07 (world registry, relation tracking, full action compiler, equation renderer, and timeline compiler) remains a separate implementation slice. The pipeline remains safely storyboard-driven rather than reverting to arbitrary model-generated Manim code.
