# Spec 06 learning notes

## Reported symptoms

Two separate behaviours appeared in the logs:

1. After an API restart, a previously valid lesson ID returned repeated 404 responses because the old process kept job state only in memory.
2. A new request returned 200 status responses while it was being generated, then failed at the `storyboarding` stage with `unknown action object satellite_velocity`.

## Root causes and fixes

### Restart recovery and polling

Job state is now saved as `job_state.json` beside the persisted request and generation artifacts. On application startup, the API rebuilds its in-memory registry from those directories. A job containing `final.mp4` is restored as completed and can serve its video again.

The client now treats `Lesson not found` as terminal and stops polling that job. It still polls normally while a job is queued or at an active generation stage, which is why repeated 200 responses are expected while Gemini or rendering is working.

### Invalid storyboard references

The storyboard schema verifies JSON shape, but a valid-shaped response can still reference an undeclared visual object. The affected Gemini response used `satellite_velocity` in an action without declaring it in `objects`; the semantic validator correctly rejected it.

`VideoPipeline.storyboard` now uses the same bounded semantic-repair strategy as screenplay generation:

- It validates object, action, camera, relation, and equation references after the structured response is parsed.
- On the first semantic failure, it saves `storyboard_draft.json` and sends the exact validation error back to Gemini with a narrowly scoped repair instruction.
- It accepts only a repaired storyboard that passes the deterministic validator. A second invalid result becomes a clear terminal error rather than entering an endless retry loop.
- The API exposes the rejected draft as a viewable artifact for diagnosis.

## Verification

The pipeline test suite includes a regression test where the first storyboard response contains a missing action object and the second response is valid. The test confirms the repair succeeds and the invalid draft is retained. Backend tests and the client production build pass after the change.

### Missing screenplay coverage

Gemini can also return narration blocks that have valid JSON and valid individual fields but omit a core concept from the lesson plan. The reported `C1` failure was exactly this case: the response began with `C2` and never supplied a narration block for the prerequisite concept `C1`.

The first invalid screenplay still receives one targeted Gemini repair. If that retry again omits only core-concept coverage, the pipeline now adds a small deterministic narration block using the plan's concept and learner-realization text, places it in conceptual order, recalculates the screenplay duration, and reruns the validator. Other screenplay failures still fail clearly rather than being silently modified.
