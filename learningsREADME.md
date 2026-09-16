# Spec 06 learning notes

## What failed

The lesson ID in the browser was valid, and its generated files were still present in `server/runtime/jobs/dbafac4cc03a462e8dd7e8c586c1cfdb/`, including `final.mp4`. The API had restarted, however, so the in-memory `JOBS` dictionary was empty. Every status request therefore returned `404 Lesson not found`.

The React polling effect treated every request error as retryable. It kept polling the same missing ID every 1.5 seconds, which produced the long sequence of 404 log entries.

## Fix implemented

- Each job now writes a small `job_state.json` next to its existing request and generation artifacts whenever its stage or terminal result changes.
- On startup, the API rebuilds its in-memory job registry from job directories. A directory with `final.mp4` is restored as completed, so its status, artifacts, and video endpoint work after a restart.
- A job interrupted before completion is restored as failed with an explicit restart message. Background tasks cannot safely continue after their host process has exited; the persisted artifacts remain available for diagnosis and the lesson can be regenerated.
- The client polls immediately and then at the normal interval, clears a stale error after a successful response, and converts a `Lesson not found` response into a terminal failed state. This prevents infinite 404 polling even if a job directory was genuinely deleted.

## Verification to retain

The regression check should create a job, persist a completed job directory with `final.mp4`, restart or reload the API module, and confirm that `GET /api/lessons/{id}` returns `completed` and `GET /api/lessons/{id}/video` serves the file. Also verify a non-existent ID causes only one client-visible failure rather than repeated polling.
