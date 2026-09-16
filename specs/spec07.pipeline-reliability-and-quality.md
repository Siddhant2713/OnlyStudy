# OnlyStudy Spec 07 — Pipeline Reliability, Stage Observability, and Generation Quality

## 0. Why this spec exists

The Gemini structured-video pipeline described in `spec04.video-generation-pipeline.md` is now partially implemented in `main`, but the current behavior exposes two different classes of problems:

1. **Pipeline reliability:** the React UI can remain on `Writing explanation` for a long time, while the actual cause is hidden inside a synchronous multi-call backend stage, a failed background task, a network/TTS delay, or a stale client state.
2. **Generation quality:** the implementation has the right high-level objects (lesson plan, screenplay, storyboard), but the renderer is currently too primitive to realize what those intermediate representations describe. The result can therefore be technically generated but visually much weaker than the storyboard promises.

This spec is deliberately a correction to spec04 rather than a request to add another layer blindly.

The implementation goal is:

```text
User request
    |
    v
Durable Job
    |
    +--> observable stage execution
    |
    +--> bounded model calls
    |
    +--> persisted intermediate artifacts
    |
    +--> deterministic validation
    |
    +--> real runtime execution
    |
    v
Final MP4 + diagnostics
```

The immediate milestone is **make the pipeline observable, resumable, bounded, and correctly delivered to React**. Only after that should visual sophistication be increased.

---

# 1. Repository audit — current implementation

The current `main` branch does implement a substantial portion of spec04.

Observed files:

- `server/app/main.py`
- `server/app/video/pipeline.py`
- `server/app/video/schema.py`
- `server/app/video/validate.py`
- `server/app/video/runtime/__init__.py`
- `server/app/video/artifacts.py`
- `server/app/voice/provider.py`
- `server/app/voice/gtts_provider.py`
- `server/app/voice/timing.py`
- `server/app/llm/gemini.py`
- `client/src/App.tsx`

The current backend exposes explicit stages and persists a `job_state.json`. The frontend polls the job and has a final video element. This is materially closer to the intended architecture than the old direct topic-to-Manim flow.

However, the implementation should **not be considered a completed realization of spec04**.

## 1.1 What spec04 got right

These architectural decisions should remain:

- separate lesson planning from screenplay generation
- separate screenplay from visual storyboard
- use stable semantic object IDs
- validate intermediate JSON using Pydantic
- persist intermediate artifacts
- keep voice generation outside generated Manim code
- make generated Manim code a thin orchestration layer
- expose pipeline stage information to the frontend
- keep Gemini behind a provider abstraction

Those are the correct foundations.

## 1.2 What the current implementation gets wrong or leaves incomplete

### A. `screenwriting` is a single opaque operation

`VideoPipeline.screenplay()` performs a structured Gemini request and may perform another repair request. The frontend receives only the current stage name. There is no per-stage progress, heartbeat, elapsed time, attempt count, token/input size, or last successful operation.

Therefore:

```text
Stage = screenwriting
```

currently means everything from:

- waiting to enter the Gemini SDK
- waiting for network response
- Gemini generation
- JSON parsing
- Pydantic validation
- second Gemini request
- repair

The UI cannot distinguish these.

### B. Gemini calls recreate a client and a chat for every request

`GeminiProvider._send()` creates `genai.Client(...)`, creates a chat, sends one message, and closes the client on each call.

This is unnecessarily expensive and makes the pipeline harder to instrument. The provider should hold one client for the lifetime of the pipeline/job process and use a single request function with explicit timeout/error classification.

### C. The structured prompt includes the entire JSON schema and serialized context every time

`VideoPipeline.structured()` builds a large prompt containing:

- the full Pydantic JSON schema
- the complete lesson plan
- or the complete lesson plan + screenplay
- or all of those plus the primitive catalog

This can be expensive and increases latency. More importantly, it means the storyboard stage can become large as lesson length increases.

Use compact stage-specific prompts and pass only the information required by that stage.

### D. No hard deadline around an individual Gemini stage

The pipeline has a 900-second render timeout but no comparable stage timeout for model calls or TTS. A model call can therefore keep the job in one stage longer than the user expects.

Add bounded timeouts at every external boundary.

### E. `BackgroundTasks` is not a real job worker

FastAPI `BackgroundTasks` is enough for a basic local prototype, but it is not a durable job queue. If the API process dies, the job stops. The repository already recognizes this in recovery behavior, but the UX still treats it like a durable generation service.

For this milestone, do not add Redis/Celery immediately. Instead:

- make jobs durable on disk
- record stage start/end times
- write heartbeats
- make every stage individually resumable
- expose a clear `interrupted`/`failed` state

A real queue can be introduced later when concurrent users matter.

### F. Stage state is encoded redundantly in `status` and `stage`

`main.py` currently updates both to the same stage string during execution. Terminal jobs then use `status="completed"`, `stage="completed"`.

Replace this with an explicit model:

```text
status: queued | running | completed | failed | interrupted
stage: planning | screenwriting | ... | muxing | none
```

Do not overload two fields with the same semantic value.

### G. Progress is mathematically misleading

The frontend derives progress from stage index alone. This tells the user that being anywhere in `screenwriting` means roughly one stage of work is complete, but it says nothing about work inside the stage.

Use stage-weighted progress plus heartbeat and attempt information.

### H. `criticize()` does not actually implement the Gemini critic described in spec04

The current method only calls deterministic validators and records:

```json
{"status":"ok","checks":["plan","screenplay","storyboard","references"]}
```

That is useful, but it is not the model-assisted pedagogical critic specified by spec04.

Do not add the Gemini critic until the reliability work below is complete. Once stable, introduce a separate critic that focuses on conceptual quality, not merely references.

### I. Voice generation remains sequential per narration block

`voice()` calls GTTS one block at a time in a loop. For longer screenplays this can make `voicing` feel stalled. It is also an external network dependency.

Keep the architecture, but make the stage observable and bounded. Consider parallel synthesis later, but preserve block ordering in the final concatenation.

### J. The runtime does not actually honor most storyboard semantics

This is the largest quality gap.

`server/app/video/runtime/__init__.py` declares a runtime, but its implementation currently only meaningfully handles a small subset:

- create/show
- hide/fade
- move
- rotate
- highlight
- pause
- a few action aliases that simply `Create()` the existing object

The current `make_object()` maps many semantic types to generic shapes:

- `wheel` / `circle` -> `Circle`
- `bicycle` / `body` / `rectangle` -> `Rectangle`
- `vector` / `arrow` -> `Arrow`
- everything else -> `Text`

This means a storyboard containing a bicycle, force, graph, equation, measurement, or transformation can collapse into visually generic primitives.

**Spec04 was correct to require a semantic runtime, but the first implementation is too shallow.**

### K. Equation semantics are declared but are not rendered as equations

The storyboard has `EquationSpec`, and actions can have `show_equation` / `derive_equation_step`, but the runtime does not implement an equation renderer. Such actions can therefore degrade into `Create(obj)` on whatever generic object happens to be referenced.

This violates an important part of the intended explanatory quality.

### L. Camera semantics are only partially implemented

`CameraController.apply()` only handles a focus/zoom-like path. `follow`, `pan`, `pull_back`, and camera actions represented inside `actions` are not actually interpreted.

### M. Animation state is not truly persistent

The storyboard preserves object IDs, but runtime objects are created once with initial states and then are blindly manipulated. There is no semantic state registry that tracks:

- current position
- current rotation
- visibility
- parent attachment
- semantic geometry
- which scene currently owns the object

This makes transformations brittle.

### N. Scene duration is calculated but not strongly tied to actual audio timing

`normalize_storyboard_timing()` sets scene duration based on summed TTS durations, but action durations themselves are not normalized against that target. If action durations already consume more time than the audio duration, the scene becomes longer than intended; if they consume far less, the runtime waits for the remainder but the animation pacing is not intentionally designed.

We need a timeline compiler, not just a duration field.

### O. Final video delivery should be treated as a separate verified stage

`main.py` does correctly create `/api/lessons/{job_id}/video` and returns a `video_url` on completion. However, the frontend currently discovers the video only through the terminal polling response.

The delivery contract should be hardened so:

1. the server verifies the final file exists and is non-empty before returning `completed`
2. the response contains artifact metadata including byte size
3. React explicitly transitions into a `ready` state when the video endpoint responds successfully
4. the browser gets cache-busting on regenerated videos
5. playback errors are surfaced separately from generation errors

---

# 2. Primary diagnosis of the reported "Writing explanation" stall

The repository itself does not prove one single root cause from source code alone, because runtime logs from the exact failed job are not stored in GitHub. However, the code identifies several concrete mechanisms that can produce the observed symptom.

## Most likely mechanism

The frontend stage is a projection of backend state. While `VideoPipeline.screenplay()` is executing, the API can legitimately remain on:

```text
screenwriting
```

for the entire duration of one or two Gemini calls.

The UI has no heartbeat or sub-stage, so a slow or blocked external call is visually indistinguishable from a hung pipeline.

The frontend is therefore not necessarily the place where generation is stuck; it is the place where **lack of observability becomes a perceived stall**.

## Secondary mechanism

A screenplay validation failure causes another Gemini repair request. Because repair is hidden inside the same stage, the user sees no transition and no indication that a second model call is occurring.

## Secondary mechanism: external voice/TTS

This is not the reported stage, but once screenwriting is fixed the same pattern can happen in `voicing`: each narration block invokes a network TTS call serially and there is no per-block progress.

## Secondary mechanism: UI state only updates at polling boundaries

React polling is reasonable, but the API response only contains coarse stage information. The UI cannot report:

```text
Writing explanation — Gemini call 1/2 — 31s
```

or:

```text
Writing explanation — repairing validation issue — 4s
```

That should be fixed regardless of the exact root cause.

---

# 3. Immediate reliability redesign

## 3.1 Introduce explicit stage execution records

Create:

`server/app/video/job_state.py`

with Pydantic models similar to:

```python
class StageState(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed"]
    attempt: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    last_heartbeat_at: str | None = None
    detail: str | None = None
    error: str | None = None
```

And:

```python
class JobState(BaseModel):
    status: Literal["queued", "running", "completed", "failed", "interrupted"]
    stage: str | None
    progress: float
    message: str
    stages: dict[str, StageState]
    created_at: str
    updated_at: str
    heartbeat_at: str
```

Persist this to:

`job_state.json`

after every meaningful change.

## 3.2 Add a heartbeat while an external call is running

A stage should not appear dead while a Gemini or TTS call is in flight.

At minimum update `heartbeat_at` before and after every external call.

Better: execute external calls in a helper that records:

- `attempt`
- `started_at`
- elapsed seconds
- completion/error

Example conceptual API:

```python
with stage_call("screenwriting", detail="Generating screenplay", attempt=1):
    screenplay = provider.generate_structured(...)
```

Do not create a background thread solely to fake a heartbeat. A stage heartbeat can be updated before and after each external call; for truly long calls, use a bounded worker abstraction.

## 3.3 Add explicit sub-stage messages

For screenwriting, expose:

- `Preparing screenplay prompt`
- `Generating explanation`
- `Validating screenplay`
- `Repairing screenplay`
- `Screenplay ready`

The backend should set these messages, not the frontend guess them.

## 3.4 Add per-stage timeouts

Use environment variables:

```text
GEMINI_TIMEOUT_SECONDS=120
SCREENWRITING_TIMEOUT_SECONDS=180
STORYBOARDING_TIMEOUT_SECONDS=180
TTS_TIMEOUT_SECONDS=60
```

Render timeout remains separately configurable.

On timeout:

- persist the error
- mark stage failed
- do not silently retry forever
- permit a bounded retry when safe

## 3.5 Make retries explicit

Each stage gets a maximum retry budget:

- transient Gemini/network errors: 2 retries
- schema repair: 1 repair request
- TTS block: 1 retry
- code validation repair: 1 repair
- render: 0 automatic retries by default

Never recursively call the pipeline.

---

# 4. Fix screenwriting specifically

Replace the current compact `screenplay()` method with an observable two-step process.

## Step A — generate

Gemini receives:

- lesson plan
- target duration
- learner level
- explicit style rules

It must return a screenplay with:

- 4–12 narration blocks for a ~2 minute lesson, unless the concept genuinely needs otherwise
- one primary idea per block
- actual spoken-language prose
- visual requirement
- concept ID
- purpose

Do not force a fixed number of blocks for longer or shorter requested lessons. Use duration as the primary constraint.

## Step B — deterministic validation

Validate:

- known concept IDs
- nonempty narration
- duration > 0
- coverage of core concepts
- total duration consistency
- no duplicated narration block IDs
- no giant single block
- no suspiciously tiny blocks

Add basic text heuristics:

```text
characters / estimated duration
```

If the model claims 5 seconds for 600 characters, reject that estimate and normalize it rather than asking Gemini to repair something deterministic.

Use a reasonable spoken-word estimate, but actual TTS duration remains authoritative later.

## Step C — repair only when needed

If validation fails for semantic/reference reasons, make one targeted repair request.

If validation fails for deterministic timing consistency, normalize locally.

Do not use Gemini for arithmetic the server can do.

## Step D — artifact persistence

Write after each step:

```text
screenplay_draft.json
screenplay.json
stage event log
```

The UI should be able to open the draft if the stage fails.

---

# 5. Shrink model context and make prompts stage-specific

## Current anti-pattern

The current generic `structured()` helper injects the complete Pydantic JSON schema and a JSON dump of the entire context for every stage.

## Required design

Create explicit prompt builders:

```text
server/app/llm/prompts/
    lesson_plan.py
    screenplay.py
    storyboard.py
    critic.py
    codegen.py
```

Each prompt builder should:

1. state one job
2. give only relevant schema instructions
3. include compact examples for difficult fields
4. include the minimum context needed
5. specify failure constraints
6. specify desired duration/learner level

Keep schemas machine-facing, but do not repeatedly dump massive schemas into prompts if the Gemini SDK can accept structured response schema directly.

## Gemini provider

Refactor `GeminiProvider` to:

- create one `genai.Client` in `__init__`
- close it through an explicit `close()` method or context manager
- use the installed SDK's structured output support when stable
- expose timeout/error information
- record model name and latency in stage telemetry

Avoid opening and closing a client for every stage call.

---

# 6. Fix the frontend contract

React should not infer readiness from a string field alone.

## Job response contract

`GET /api/lessons/{job_id}` should return approximately:

```json
{
  "id": "...",
  "status": "running",
  "stage": "screenwriting",
  "message": "Generating explanation",
  "progress": 0.21,
  "stage_progress": null,
  "heartbeat_at": "...",
  "elapsed_seconds": 31.4,
  "video": {
    "available": false,
    "url": null,
    "size_bytes": null
  },
  "artifacts": {},
  "error": null
}
```

When completed:

```json
"status": "completed",
"stage": null,
"video": {
  "available": true,
  "url": "/api/lessons/<id>/video",
  "size_bytes": 12345678
}
```

## Do not expose `stage="completed"`

A completed job has no active stage.

## React rendering behavior

When `status === "completed"`:

1. stop polling
2. set `videoReady` only after the video URL is known
3. render the video player
4. attach `onLoadedMetadata` to confirm browser playback initialization
5. attach `onError` to distinguish playback/network errors
6. add a cache-busting query parameter when a lesson is regenerated, e.g. `?v=<job-updated-at>`

The download link should use the same URL.

## Polling behavior

Poll while:

```text
queued OR running
```

Stop polling after:

```text
completed OR failed OR interrupted
```

If polling itself fails temporarily, show a connectivity warning but do not immediately overwrite valid job state with `failed`.

Only `404 Lesson not found` should terminally detach an unknown job ID.

---

# 7. Add a verified media-delivery stage

Create:

`server/app/video/media.py`

with helpers:

```python
validate_video(path: Path) -> VideoMetadata
```

At minimum verify:

- file exists
- file size > 0
- extension is `.mp4`
- ffprobe/ffmpeg can inspect the container
- a video stream exists
- duration > 0

Do not report `completed` until this validation passes.

After completion, perform one server-side internal check that the exact URL handler can read the file.

This directly addresses the case where generation succeeds but the React dashboard does not receive a playable artifact.

---

# 8. Correct the muxing implementation

Current `mux()` writes a concat file and then calls ffmpeg. Keep this approach for now, but make it robust:

- use absolute file paths or correctly escaped paths in concat input
- use `-safe 0` consistently
- handle the case where there is no audio
- handle missing/corrupt track files
- inspect ffmpeg stderr on failure
- validate final MP4 after muxing
- do not use `-shortest` blindly if the visual track is intentionally longer than the narration

The final composition policy should be explicit:

```text
video_duration = max(visual_timeline_duration, audio_duration)
```

or another consciously chosen policy. Do not let `-shortest` become an accidental timing policy.

---

# 9. Replace the current shallow runtime with a semantic runtime v2

This is the main quality correction to spec04.

## 9.1 Runtime goals

The storyboard must describe *what should happen* and the runtime must produce the visual behavior consistently.

Create modules:

```text
server/app/video/runtime/
    __init__.py
    world.py
    objects.py
    actions.py
    equations.py
    camera.py
    timing.py
    style.py
```

## 9.2 World state

Create a `WorldState` registry:

```python
class WorldObjectState:
    id: str
    kind: str
    mobject: Mobject
    visible: bool
    position: tuple[float, float, float]
    rotation: float
    scale: float
    parent_id: str | None
```

The registry must survive across storyboard scenes during one render.

## 9.3 Primitive implementations

Implement actual renderers for at least:

### text / label

- `Text`
- controlled font size
- max-width wrapping policy

### equation

- dedicated math renderer through a safe abstraction
- do not expose arbitrary TeX strings without validation
- permit plain-text fallback for environments where LaTeX is unavailable

### point

- `Dot`

### vector / arrow

- `Arrow`
- direction derived from semantic relation where available

### line

- `Line`

### circle / wheel

- `Circle`
- optional spoke marks for wheel

### body / object

- `Rectangle` or domain-specific shape

### bicycle

Create a reusable simple bicycle primitive consisting of:

- rear wheel
- front wheel
- frame
- handlebar
- seat
- pedal/crank
- rider/body placeholder when needed

All subparts must have stable IDs.

The objective is not photorealism. The objective is coherent motion and attachment.

### graph / coordinate system

Implement axes and plotted geometry through a reusable component rather than asking Gemini to rebuild them each time.

---

# 10. Semantic action compiler

Create `actions.py` that maps every supported storyboard action to a deterministic implementation.

At minimum implement:

```text
create
show
hide
fade
move
rotate
scale
morph
transform
highlight
trace
show_vector
show_force
show_measurement
show_equation
derive_equation_step
camera_focus
camera_zoom
camera_follow
pause
```

Each action must:

- resolve its object IDs
- validate required parameters
- update world state
- produce a Manim animation

Unknown actions must fail before rendering, not silently do nothing.

Current runtime behavior that simply treats `show_force`, `show_vector`, and `show_equation` as `Create(obj)` is explicitly prohibited in the new version.

---

# 11. Relations must affect rendering

The current schema contains relations but runtime ignores them.

Implement basic relation semantics:

- `attached_to`: child follows parent transform
- `points_to`: arrow endpoint follows target
- `acts_on`: force originates from source and targets the target
- `measured_from`: measurement line tracks two objects
- `derived_from`: equation/highlight can visually connect to source
- `contains`: group membership
- `follows`: trace path/trajectory relation
- `corresponds_to`: visual correspondence between object and label/equation

This is where stable semantic identity becomes an actual visual advantage.

---

# 12. Equation system

Create `equations.py`.

It should support:

- equation introduction
- term highlighting
- replacing one equation with the next derivation step
- linking an equation to a motivated object
- optional symbol labels

A derivation should look like:

```text
phenomenon
  -> relevant quantities appear
  -> equation appears
  -> one term is highlighted
  -> transformation
  -> resulting equation
```

rather than:

```text
show giant formula
```

Equation content must come from validated storyboard data. Do not invent formulas inside the renderer.

---

# 13. Camera system v2

The current camera implementation only partially supports the declared semantics.

Implement:

- focus
- zoom
- follow
- pull_back
- pan

`follow` should use a tracked object or bounding box.

`focus` should center a target while respecting padding.

The camera should never jump because a new object happened to be created elsewhere.

---

# 14. Timeline compiler

Replace simple scene-duration arithmetic with a timeline compiler.

Create:

`server/app/video/runtime/timing.py`

Input:

- storyboard scenes
- actual TTS block durations

Output:

```text
Timeline
    scene 1: [0.0, 11.4]
      audio blocks: [b1]
      visual beats: [...]
    scene 2: [11.4, 25.8]
      audio blocks: [b2, b3]
      visual beats: [...]
```

Each visual beat should have:

- start offset
- target duration
- action list
- easing policy

The compiler should:

- preserve audio-locked scene boundaries
- ensure action durations fit scene duration
- stretch waits instead of silently truncating
- reject a scene whose required animations exceed the allowed maximum without a recovery policy

Do not make every animation duration random or model-guessed.

---

# 15. Add deterministic content-quality checks before rendering

Create `server/app/video/quality.py`.

Checks should include:

## Structural

- every narration block appears in at least one scene
- every core concept appears in screenplay
- every core visual requirement appears in storyboard
- every referenced object exists
- every camera target exists

## Density

Reject or warn on:

- too many simultaneous objects
- excessively long text on screen
- more than a configured number of distinct new objects in one beat
- too many equation changes in a single scene

## Continuity

Check:

- an object is not faded out and then used as if visible without a show/create
- a child object is not moved independently when attached to a parent unless explicitly detached
- an equation references an actual motivated object

## Timing

Check:

- total timeline is close to actual audio length for audio-locked lessons
- no negative durations
- no zero-length required action
- no scene with many actions competing for too little time

Warnings can be auto-repaired deterministically. Hard failures should stop before code generation/rendering.

---

# 16. Reconsider what Gemini should generate

The current codegen stage asks Gemini to essentially output:

```python
from app.video.runtime import LessonScene, load_storyboard

class SceneTopic(LessonScene):
    def construct(self):
        self.run_storyboard(load_storyboard('storyboard.json'))
```

This is actually a good safety decision, but it means Gemini is no longer doing useful low-level animation design at codegen time.

That is acceptable.

The quality bottleneck has therefore moved to the semantic storyboard and runtime, exactly where it should be.

Do **not** solve visual quality by allowing Gemini to write arbitrary Manim again.

Instead:

```text
Gemini = planner / teacher / storyboard designer
Runtime = visual execution engine
```

This division should be treated as a core product decision.

---

# 17. Improve the storyboard contract

Extend `StoryboardScene` with explicit visual beats.

Suggested schema:

```python
class VisualBeat(BaseModel):
    id: str
    narration_block_id: str
    intent: str
    start_offset_seconds: float
    duration_seconds: float
    action_ids: list[str]
```

And keep actions independently addressable.

This prevents a flat list of actions from becoming ambiguous when one narration block contains multiple concepts.

Also add optional:

```python
teaching_intent: Literal[
    "establish",
    "contrast",
    "transform",
    "derive",
    "measure",
    "demonstrate",
    "emphasize",
    "recap",
]
```

This is more useful than trying to infer pedagogical intent from raw Manim actions.

---

# 18. Domain system for physics should be explicit but bounded

The earlier spec04 bicycle idea remains valid, but do not build a full simulator yet.

For a physics lesson, a domain layer should provide:

- semantic quantities
- direction
- source/target relations
- deterministic formulas where known
- qualitative behavior descriptors

For example, a bicycle lesson can represent:

```text
wheel rotation
rear-wheel contact point
forward velocity
friction force
steering angle
lean angle
turn radius
centripetal acceleration
```

The domain layer should never silently turn a qualitative claim into a numeric simulation.

For the bicycle, explicitly avoid treating gyroscopic effects as the sole explanation of stability.

---

# 19. Artifact visibility should be treated as a product feature

The intermediate artifacts are valuable debugging evidence.

Expose these states in the dashboard:

```text
Lesson Plan
Screenplay
Storyboard
Validation
Voice timing
Scene code
Render metadata
```

For each artifact, show:

- available/not available
- generated timestamp
- version
- stage that produced it

Do not require users to inspect raw JSON for normal use. A compact human-readable preview is sufficient.

---

# 20. Add a real diagnostic endpoint

Implement:

`GET /api/lessons/{job_id}/diagnostics`

Response:

```json
{
  "job_id": "...",
  "status": "running",
  "stage": "screenwriting",
  "stages": {
    "screenwriting": {
      "attempt": 1,
      "elapsed_seconds": 42.1,
      "message": "Generating explanation",
      "heartbeat_at": "..."
    }
  },
  "artifacts": [
    "request.json",
    "lesson_plan.json"
  ],
  "external_calls": [
    {
      "provider": "gemini",
      "purpose": "screenplay",
      "latency_seconds": 40.2,
      "success": true
    }
  ]
}
```

This endpoint is especially useful during development and can remain behind a debug flag later.

---

# 21. Add stage-level tests before visual polish

Create tests for:

### Reliability

- Gemini timeout -> stage fails cleanly
- transient Gemini failure -> bounded retry
- schema repair -> exactly one repair request
- TTS failure -> correct stage failure
- API restart -> interrupted job restored correctly
- completed artifact survives restart

### Screenwriting

- missing concept coverage -> targeted repair
- invalid duration -> deterministic normalization/rejection
- duplicate IDs -> rejection
- giant narration block -> warning/rejection

### Frontend/API contract

- completed job returns video metadata
- failed job stops polling
- temporary polling failure does not falsely fail a valid job
- video endpoint returns correct media type
- missing video cannot coexist with `status=completed`

### Runtime

- every supported action has an implementation
- unknown action fails validation
- relation tracking works for attached objects
- bicycle subparts move coherently
- equation replacement works
- camera follow works

---

# 22. Add an end-to-end smoke fixture

Create a deterministic fixture:

`server/tests/fixtures/bicycle_smoke.json`

The fixture should not depend on Gemini.

It should contain a tiny storyboard demonstrating:

1. show bicycle
2. rotate both wheels
3. move bicycle forward
4. show forward velocity vector
5. focus rear wheel
6. show contact/friction vector
7. show a simple rolling equation
8. pull camera back

Render this fixture in CI or local tests.

This is essential because it separates:

```text
Gemini quality
```

from:

```text
runtime quality
```

A broken runtime should be diagnosable without any model call.

---

# 23. Development order — do not implement everything at once

## Phase 1 — fix the apparent stall

Implement only:

- stage state model
- messages + heartbeats
- Gemini timeout
- provider reuse
- bounded retries
- improved API response
- React handling for running/failed/completed
- verified video metadata

Acceptance test:

A lesson either progresses visibly through stages or fails with a concrete reason. It must never sit on `Writing explanation` without an observable heartbeat/message.

## Phase 2 — make screenwriting dependable

Implement:

- stage-specific prompt
- deterministic duration sanity checks
- one repair max
- screenplay draft persistence
- diagnostics

Acceptance test:

A normal 2-minute topic reliably produces a valid screenplay artifact.

## Phase 3 — fix storyboard execution

Implement:

- world state
- semantic action compiler
- relations
- actual equations
- actual camera behaviors
- object continuity

Acceptance test:

The same storyboard fixture produces visually meaningful motion without custom model-generated Manim code.

## Phase 4 — timeline and voice

Implement:

- block-level timeline
- actual audio durations
- action fitting
- robust muxing
- final MP4 validation

Acceptance test:

Audio and video lengths are intentional and stable.

## Phase 5 — pedagogical critic

Only after the deterministic pipeline works, add the Gemini critic for:

- conceptual omissions
- weak visual mappings
- poor transitions
- misleading explanations

Do not use the critic as a generic “make it better” pass.

---

# 24. What to remove / avoid from spec04's first implementation

Do not repeat these patterns:

- one opaque stage that contains several external calls
- model-generated timing treated as authoritative
- generic `Create(obj)` fallback for semantic actions
- silently ignored unsupported actions
- closing and reopening Gemini clients for each request
- full context dumps for every model call
- treating API background tasks as durable queues
- reporting `completed` before validating the final media file
- using UI labels as a substitute for backend telemetry
- adding another LLM provider before the Gemini pipeline is stable
- reverting to giant arbitrary Manim scripts to chase visual quality

---

# 25. Definition of done for Spec07

Spec07 is complete only when all of the following are true:

1. A generation job has a durable state model.
2. Every stage has start/end/heartbeat/message information.
3. Gemini calls have explicit timeouts and bounded retries.
4. Screenwriting no longer looks like an unexplained frozen stage.
5. The provider reuses its client and records latency/errors.
6. React receives a completed job with verified video metadata.
7. The video endpoint serves a verified non-empty MP4.
8. Regenerated videos do not get hidden by browser caching.
9. Intermediate artifacts remain inspectable after failure.
10. Screenplay timing is sanity-checked deterministically.
11. The runtime has a real semantic object registry.
12. Supported semantic actions have actual implementations.
13. Relations affect object behavior.
14. Equations are rendered as equations, not generic text shapes.
15. Camera focus/zoom/follow/pan/pull_back work.
16. A deterministic bicycle storyboard fixture renders successfully without Gemini.
17. Audio timing is compiled from actual TTS durations.
18. Final mux output is validated before completion.
19. Unit/integration tests cover reliability and runtime behavior.
20. Only after these are true should visual-generation model sophistication be revisited.

---

# 26. Final architectural position

The central lesson from the first spec04 implementation is:

> **The abstraction boundary was correct; the runtime and observability beneath it were underbuilt.**

The product should not move back toward:

```text
Topic -> Gemini -> arbitrary Manim code
```

The durable architecture remains:

```text
Topic
  -> LessonPlan
  -> Screenplay
  -> Storyboard
  -> Timeline
  -> Trusted Runtime
  -> Voice / Audio
  -> Render
  -> Verified MP4
```

But every arrow must now be:

```text
bounded
observable
validated
persisted
recoverable
```

And the storyboard must correspond to a runtime that can actually execute the semantics it declares.

The next implementation task for Codex is therefore **not to add more conceptual stages**. It is to make the existing stages truthful, observable, testable, and executable.
