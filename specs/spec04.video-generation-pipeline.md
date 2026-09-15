# OnlyStudy Video Generation Pipeline — Gemini-Only Architecture

## Goal

Replace the current direct `topic -> Gemini -> one Manim Python file -> render` pipeline with a structured, multi-stage explanation pipeline that produces coherent concept-explainer videos.

For this implementation, **use Gemini only as the LLM provider**. Do not introduce Grok, Claude, OpenAI, or another model yet. The architecture must nevertheless isolate the LLM layer behind a provider interface so another model can be added later without changing the video engine.

The target is not to imitate a specific creator's branding. The target is the underlying quality bar of high-quality visual explainers: one coherent visual argument, persistent objects, meaningful transformations, camera movement that follows the reasoning, mathematically faithful equations, and narration synchronized to the visuals.

## Current repository / baseline

Repository: `Siddhant2713/OnlyStudy`

Current backend is a compact FastAPI app in `server/app/main.py`. It currently:

1. Receives `topic`, `subject`, `quality`, `voice_preset`, and `use_voiceover`.
2. Builds one large Gemini prompt.
3. Asks Gemini to return a single runnable `SceneTopic` Python class.
4. Validates that Python with `ast`.
5. Writes `scene.py`.
6. Runs Manim.
7. Returns the resulting MP4.
8. For feedback, sends the previous code and feedback back to Gemini and asks for another single scene.

The current generator explicitly tells Gemini to explain the topic in `definition, analogy, and worked-example phases`, to avoid LaTeX, and to use `manim_voiceover`/GTTS inside the generated scene when voiceover is enabled. This coupling must be removed from the planning architecture.

The frontend in `client/src/App.tsx` is also currently a single-topic submission flow followed by job polling and final-video playback. It has no representation of a lesson plan, screenplay, storyboard, scene list, approvals, or intermediate artifacts.

Current dependencies include FastAPI, `google-genai`, Manim 0.21.x, and `manim-voiceover[gtts]`.

## Core architectural decision

**Do not ask Gemini to directly write the complete Manim program.**

The new flow must be:

```text
User topic
   |
   v
Lesson Planner (Gemini)
   |
   |--> Lesson Plan / Concept Graph
   v
Screenplay Writer (Gemini)
   |
   |--> Narration + pedagogical progression
   v
Visual Storyboard / Scene Planner (Gemini)
   |
   |--> semantic objects
   |--> relationships
   |--> visual actions
   |--> equations
   |--> camera actions
   |--> timing intents
   v
Deterministic validation / normalization
   |
   v
Manim Code Generator (Gemini)
   |
   v
Static validation + render smoke test
   |
   v
Manim Renderer
   |
   +------------------+
   |                  |
   v                  v
visual video       TTS / voice track
   |                  |
   +---------> timing compositor <---------+
                       |
                       v
                   final MP4
```

Gemini may be called multiple times. Each call should have one narrow responsibility. Do not create one giant prompt containing the complete application requirements.

## Design principles

### 1. The explanation is the product

The pipeline must optimize for conceptual understanding, not for generating a large amount of code.

### 2. Persistent semantic objects

Objects need stable IDs across scenes. If scene 2 introduces `rear_wheel`, scene 5 must be able to refer to the same logical object. The renderer can reconstruct visuals from the semantic state, but the storyboard must preserve identity.

### 3. Visual-first planning

Every narration paragraph must have a visual purpose. Avoid narration that is not represented visually, and avoid visuals that are decorative but do not help the explanation.

### 4. Continuous transformations over disconnected slides

Prefer:

```text
existing object -> highlight -> transform -> zoom -> annotate
```

over:

```text
old diagram disappears -> unrelated new diagram appears
```

### 5. Deterministic rendering

Gemini produces declarative scene specifications. Python/Manim generation should be constrained by a known runtime API instead of allowing arbitrary architecture every run.

### 6. Narration drives timing, but narration does not directly manipulate Manim

TTS should be a separate stage. Generate narration text first, synthesize it, obtain audio duration, then provide those durations to the animation timing layer. Do not make Gemini guess exact audio durations.

### 7. Fail early

Validate every intermediate artifact before proceeding.

## Target intermediate representation

Create a versioned Pydantic schema in a dedicated module, preferably:

`server/app/video/schema.py`

with at least the following models.

### LessonPlan

```python
class LessonPlan(BaseModel):
    schema_version: str
    title: str
    topic: str
    subject: str
    learner_level: str
    learning_objectives: list[str]
    prerequisite_knowledge: list[str]
    central_question: str
    conceptual_chain: list[ConceptStep]
    misconceptions: list[Misconception]
    estimated_duration_seconds: float
```

`ConceptStep` should have:

- `id`
- `concept`
- `what_learner_should_realize`
- `depends_on`
- `importance`
- `requires_visualization: bool`

### Screenplay

```python
class Screenplay(BaseModel):
    schema_version: str
    title: str
    hook: str
    narration_blocks: list[NarrationBlock]
    total_estimated_duration_seconds: float
```

Each `NarrationBlock` needs:

- `id`
- `concept_step_id`
- `text`
- `purpose` (`hook`, `intuition`, `derivation`, `example`, `transition`, `recap`, etc.)
- `estimated_duration_seconds`
- `emphasis_terms`
- `visual_requirement`

Narration must sound like spoken teaching, not documentation. Avoid repeated headings and textbook-style prose.

### Storyboard

Create a declarative visual schema, for example:

```python
class Storyboard(BaseModel):
    schema_version: str
    canvas: CanvasSpec
    global_style: VisualStyle
    objects: list[VisualObject]
    scenes: list[StoryboardScene]
```

`VisualObject` must contain a stable `id`, `type`, initial state, semantic role, and optional parent/attachment information.

Example object types:

- `text`
- `equation`
- `point`
- `vector`
- `line`
- `circle`
- `rectangle`
- `coordinate_system`
- `graph`
- `particle`
- `body`
- `wheel`
- `bicycle`
- `arrow`
- `label`
- `highlight`
- `group`

The system should be extensible; do not hard-code the bicycle as the only domain object.

`VisualRelation` should support relationships such as:

- `attached_to`
- `points_to`
- `acts_on`
- `measured_from`
- `derived_from`
- `contains`
- `follows`
- `corresponds_to`

### StoryboardScene

Each scene must include:

- `id`
- `narration_block_ids`
- `purpose`
- `duration_policy`
- `active_objects`
- `actions`
- `camera`
- `equations`
- `transition_to_next`

Actions should be semantic, not raw Manim calls. Examples:

```json
{
  "type": "move",
  "object_id": "bike",
  "to": {"x": 3.0, "y": 0.0},
  "duration": 2.0
}
```

```json
{
  "type": "show_force",
  "object_id": "road_friction",
  "source_object_id": "road",
  "target_object_id": "rear_tire",
  "magnitude_expression": "mu_s * N",
  "direction": "forward"
}
```

```json
{
  "type": "focus",
  "target_object_id": "rear_wheel",
  "zoom": 2.2
}
```

Supported action families should include at least:

- create/show
- hide/fade
- move
- rotate
- scale
- morph/transform
- highlight
- trace
- show_vector
- show_force
- show_measurement
- show_equation
- derive_equation_step
- camera_focus
- camera_zoom
- camera_follow
- pause

Do not allow arbitrary Python expressions inside the storyboard.

## Camera system

Implement a reusable camera abstraction in the renderer. Gemini should specify intent rather than direct frame coordinates whenever possible.

Example camera intents:

```python
CameraAction(type="focus", target="wheel", zoom=2.0)
CameraAction(type="follow", target="bike", padding=1.0)
CameraAction(type="pull_back", amount=1.5)
CameraAction(type="pan", direction="right", amount=2.0)
```

The engine maps these to Manim camera operations.

The camera must be treated as part of the explanation, not as an afterthought.

## Physics/domain model

For physics subjects, add an optional domain model layer:

`server/app/video/physics.py`

It does not need to be a full physics simulator in the first implementation. It must at least support semantic quantities and relationships that are reused consistently in the storyboard and renderer.

Example:

```python
class PhysicalQuantity(BaseModel):
    id: str
    symbol: str
    value: float | None
    unit: str | None

class ForceRelation(BaseModel):
    id: str
    source: str
    target: str
    expression: str | None
    direction: str
```

For formulas, the system should preserve mathematical meaning. Never invent an equation merely because it sounds plausible.

For the bicycle example, the storyboard should be capable of representing:

- wheel rotation
- torque from the pedal
- rolling condition `v = omega R`
- tire-road friction
- velocity direction
- centripetal acceleration/force
- lean angle
- steering geometry
- angular momentum / gyroscopic contribution
- dynamic balance

It is acceptable for an early implementation to use deterministic equations and qualitative animation. Do not claim that a full numerical bicycle simulator exists unless it actually does.

## Gemini adapter

Refactor Gemini calls into a provider module:

`server/app/llm/gemini.py`

and expose a small interface, e.g.:

```python
class LLMProvider(Protocol):
    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel: ...
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> str: ...
```

Use the existing `google-genai` SDK.

The model name remains configurable through `GEMINI_MODEL`.

Prefer Gemini structured output / JSON schema support where reliably supported by the installed SDK. If SDK details make direct schema binding brittle, request strict JSON and validate through Pydantic, followed by one bounded repair attempt.

Never silently accept malformed JSON.

### Gemini call decomposition

Implement these stages:

#### Stage A — lesson planner

Input:

- topic
- subject
- optional learner level / desired duration

Output:

`LessonPlan`

Prompt responsibilities:

- identify the single central question
- break the concept into a causal chain
- choose prerequisites
- identify common misconceptions
- decide what truly needs a visual
- keep scope realistic
- avoid overloading one lesson with every related fact

The output must be suitable for teaching, not merely a topical outline.

#### Stage B — screenplay writer

Input:

- lesson plan

Output:

`Screenplay`

Rules:

- narration must follow the conceptual chain
- introduce intuition before formalism where appropriate
- equations should be motivated
- define symbols immediately when introduced
- include transitions that connect ideas
- avoid narrating what is already obvious visually
- use spoken, natural language

#### Stage C — visual storyboard planner

Input:

- lesson plan
- screenplay
- reusable visual primitive catalog

Output:

`Storyboard`

Rules:

- every narration block maps to one or more visual actions
- every visual action must have a semantic object target
- preserve object identity across scenes
- prefer transformations of existing objects
- use one coherent coordinate/world system when possible
- specify camera intent
- avoid overcrowding
- avoid paragraph-sized on-screen text
- equations must be introduced/derived rather than simply dumped on screen

#### Stage D — storyboard critic / repair

Before code generation, run a deterministic validation pass, then optionally a Gemini critic call when needed.

Critic should inspect:

- missing mappings
- object references to nonexistent IDs
- visual overload
- unexplained equations
- narration with no visual support
- visuals with no conceptual purpose
- awkward scene transitions
- unrealistic duration assumptions
- misleading physics

Return either:

```json
{"status":"ok"}
```

or a structured repair list. Apply at most one repair cycle in the MVP to control cost and complexity.

#### Stage E — Manim code generation

Input:

- validated storyboard
- renderer API documentation/schema
- narration block IDs + actual audio durations if voice is enabled

Output:

Python code using a **small stable runtime API** rather than arbitrary design.

The generated file must contain exactly one renderable class named `SceneTopic` for compatibility with the existing renderer initially.

The renderer API should expose helper methods such as:

```python
self.world.add_object(...)
self.world.animate(...)
self.camera_controller.focus(...)
self.show_equation(...)
self.show_force(...)
self.sync_to_audio(...)
```

The exact implementation can differ, but the idea is essential: Gemini should compose known primitives instead of recreating all low-level Manim geometry from scratch every time.

## Renderer runtime

Create a reusable runtime package under:

`server/app/video/runtime/`

Suggested components:

```text
runtime/
    __init__.py
    world.py
    objects.py
    actions.py
    camera.py
    equations.py
    timing.py
    style.py
```

The runtime should handle:

- semantic object registration
- stable object lookup
- style defaults
- object attachment
- action execution
- camera intent translation
- timing
- equation rendering
- safe text rendering
- validation

The generated Gemini code should be thin orchestration over this runtime.

## Voiceover architecture

The existing implementation directly imports `manim_voiceover` and GTTS inside Gemini-generated code. Remove that as the primary architecture.

Create:

`server/app/voice/`

with:

```text
voice/
    __init__.py
    provider.py
    gtts_provider.py
    timing.py
```

Define a provider interface, e.g.:

```python
class VoiceProvider(Protocol):
    def synthesize(self, text: str, *, preset: str, output_path: Path) -> VoiceResult: ...
```

`VoiceResult` should include:

- output path
- duration seconds
- optional word/segment timing when available

For this iteration, retain GTTS so the existing dependency remains useful.

Important: voice generation must happen **after the screenplay exists and before final animation timing is locked**.

The flow should be:

```text
Screenplay
   ↓
TTS per narration block
   ↓
actual duration per block
   ↓
Storyboard timing normalization
   ↓
Manim render
   ↓
combine / mux voice
```

Do not use guessed narration duration as the final source of truth if actual TTS duration is available.

## Timing model

Each storyboard scene must have a duration policy:

- `audio_locked`: animation follows actual narration duration
- `visual_locked`: animation has a fixed duration and narration must fit
- `hybrid`: key visual beats have minimum durations but can stretch/compress within limits

For educational videos, default to `audio_locked` with bounded minimum scene durations.

Do not try to synchronize every animation frame to word timestamps in the MVP unless those timestamps are available. Block-level synchronization is sufficient initially.

## New job state machine

Expand the current job states.

Suggested states:

```text
queued
planning
screenwriting
storyboarding
criticizing
voicing
codegen
validating
rendering
muxing
completed
failed
```

The API must expose the current stage so the frontend can show meaningful progress rather than only `generating` and `rendering`.

Each job should persist intermediate artifacts on disk under:

`server/runtime/jobs/<job_id>/`

Suggested files:

```text
request.json
lesson_plan.json
screenplay.json
voice/
storyboard.json
validation.json
scene.py
render/
final.mp4
```

Do not store these only in an in-memory `JOBS` dictionary. The current dictionary can remain for active process state, but artifacts must be persisted so they can be inspected and future APIs can read them.

## Feedback / regeneration architecture

The current feedback endpoint resends the whole previous Python program to Gemini. Replace that.

Feedback must target the earliest relevant artifact.

Examples:

> “The explanation is too fast.”

→ revise screenplay/timing, then regenerate voice + storyboard + code.

> “The bicycle should actually turn instead of just showing arrows.”

→ revise storyboard, then code.

> “The equation is wrong.”

→ revise storyboard/math representation, then code.

> “Use a calmer voice.”

→ regenerate voice only and remux where possible.

The backend should classify feedback into a target stage using deterministic keyword/rule logic first, with an optional Gemini classifier later. Keep the MVP deterministic.

## API changes

Preserve backward compatibility where reasonable, but add:

### `POST /api/lessons`

Same basic request, optionally extend with:

- `learner_level`
- `duration_minutes`
- `style`

Response includes:

```json
{
  "id": "...",
  "status": "queued",
  "stage": "planning"
}
```

### `GET /api/lessons/{job_id}`

Return:

- job ID
- topic
- status
- current stage
- progress estimate if available
- error
- URLs for available artifacts
- final video URL when completed

Do not expose internal absolute filesystem paths.

### `GET /api/lessons/{job_id}/plan`

Return validated lesson plan JSON.

### `GET /api/lessons/{job_id}/screenplay`

Return screenplay JSON.

### `GET /api/lessons/{job_id}/storyboard`

Return storyboard JSON.

### `GET /api/lessons/{job_id}/artifacts/{name}`

Allow a safe whitelist of persisted JSON/text artifacts to be downloaded for debugging.

### `POST /api/lessons/{job_id}/feedback`

Accept existing feedback schema, but re-run only the necessary stages when feasible.

## Frontend changes

Refactor `client/src/App.tsx` only as much as necessary for the first usable UI.

The user should see generation stages such as:

```text
✓ Planning lesson
✓ Writing explanation
● Designing visuals
○ Generating voice
○ Rendering
○ Finalizing
```

Once the plan/storyboard exist, show a compact “View plan” / “View storyboard” debug panel. This is important for development because the intermediate representations are the easiest way to diagnose quality failures.

Do not build a huge editor yet.

The final video player and feedback box should remain.

## Quality constraints for Gemini prompts

The system prompts should repeatedly enforce these principles:

### Teaching

- Explain one causal idea at a time.
- Start from the learner's likely intuition/misconception.
- Build from concrete to abstract when appropriate.
- Introduce mathematical notation only when it does explanatory work.
- Never assert a physical mechanism simply because it is a common textbook shortcut.

### Visuals

- The visual representation must carry information.
- Prefer persistent objects and transformations.
- A force arrow must be attached to the thing experiencing the force.
- A measurement must attach to the objects it measures.
- An equation must be connected to the visual phenomenon that motivates it.
- Do not fill the screen with headings, paragraph text, arrows, and equations simultaneously unless the storyboard explicitly justifies it.
- Avoid decorative animation.
- Prefer camera movement and object transformations over repeated scene resets.

### Code

- Use only approved runtime primitives.
- Keep generated code relatively small.
- Do not create arbitrary helper architecture per generation.
- Never use shell commands, network calls, file deletion, subprocesses, `eval`, `exec`, or dynamic imports in generated scene code.
- No base64/file dumping/network exfiltration.

## Security / sandboxing

The generated code executes on the server. Treat it as untrusted even though it comes from Gemini.

At minimum:

- AST-validate imports against an allowlist.
- Reject dangerous modules such as `os`, `subprocess`, `socket`, `pathlib`, `shutil`, `requests`, etc. in generated scene code unless explicitly required by trusted runtime internals.
- Reject `eval`, `exec`, `compile`, `__import__`, and attribute-based import tricks.
- Only allow imports from `manim` and the trusted OnlyStudy runtime package.
- Generated code should not be able to write arbitrary files; runtime owns output paths.

Do not rely on prompt instructions as the security boundary.

## Validation

Create:

`server/app/video/validate.py`

Validate at least:

### Lesson plan

- nonempty central question
- at least 2 learning objectives
- concept steps form a connected dependency graph
- no duplicate IDs

### Screenplay

- all concept step IDs exist
- narration blocks have text
- durations are positive
- total duration is sensible
- every core concept has narration coverage

### Storyboard

- all object/action IDs resolve
- all narration block IDs exist
- no dangling relations
- no duplicate object IDs
- scene order is valid
- no action duration is negative
- camera targets exist
- equations have valid references

### Code

- valid Python AST
- exactly one `SceneTopic`
- `construct` exists
- imports are allowed
- no dangerous calls
- compile succeeds

## Testing strategy

Add tests under `server/tests/`.

At minimum:

1. Schema validation tests.
2. Gemini JSON parsing/repair tests using mocked responses.
3. Storyboard reference validation tests.
4. Feedback routing tests.
5. Generated-code security validation tests.
6. A deterministic fixture for the bicycle example.
7. A minimal render smoke test that runs a short scene.
8. Voice-duration handling test with a mocked TTS provider.

The bicycle fixture should be the reference integration test because it exercises persistent objects, forces, equations, camera focus, and narration synchronization.

## Error handling

Never mark a lesson as completed merely because Gemini returned text.

Every stage should report actionable errors:

```text
planning failed
screenwriting failed
storyboard validation failed
voice generation failed
code generation failed
scene validation failed
Manim render failed
mux failed
```

Persist the last useful artifact even when a later stage fails so debugging is possible.

Implement bounded retries:

- Gemini transient API error: up to 2 retries with backoff.
- Structured output validation failure: at most 1 targeted repair call.
- Manim code failure: at most 1 code repair call, passing the compiler/render error and validated storyboard, not the entire unrelated job context.

Do not create unbounded regeneration loops.

## Output style defaults

Keep the existing dark educational visual language initially, but move it into a renderer style configuration rather than embedding colors/styles in every generated file.

Provide defaults for:

- background
- primary text
- secondary text
- semantic accent colors
- equation style
- vector style
- object stroke widths
- default animation easing
- camera behavior

Generated code should reference style tokens rather than inventing a new palette for every lesson.

## Important implementation constraint

Do **not** rewrite the whole application unnecessarily.

Reuse:

- FastAPI
- existing job creation/polling concept
- existing Gemini SDK dependency
- Manim
- existing final video endpoint
- existing GTTS dependency initially

Refactor the generation internals into clear modules and expand the API around them.

## Suggested implementation order

### Phase 1 — schemas and artifacts

Implement all Pydantic intermediate schemas and persistent artifact storage. Add fixture JSON for the bicycle example.

### Phase 2 — Gemini pipeline

Implement the five Gemini stages with strict structured outputs and validation.

### Phase 3 — runtime primitives

Build the semantic Manim runtime and refactor code generation around it.

### Phase 4 — voice/timing

Separate TTS from Manim and use actual duration to normalize storyboard timing.

### Phase 5 — API/frontend

Expose intermediate artifacts and meaningful stage progress.

### Phase 6 — feedback

Route feedback to the correct stage and regenerate only the necessary downstream artifacts.

### Phase 7 — integration test

Run the bicycle topic end-to-end and verify that the resulting video exhibits actual object continuity and explanation-driven animation.

## Acceptance criteria

The implementation is successful only if all of the following are true:

1. Entering “Physics of a bicycle” no longer causes Gemini to write one giant free-form Manim program as the first step.
2. A persisted lesson plan is produced first.
3. A persisted screenplay is produced from that plan.
4. A persisted storyboard is produced from plan + screenplay.
5. Storyboard references are semantic and stable.
6. The same bicycle/wheel objects can persist across multiple scenes.
7. Camera actions are generated as intents and executed by a reusable camera controller.
8. Equations are represented separately from arbitrary text.
9. Voice generation is independent from generated Manim code.
10. Actual TTS duration can affect animation timing.
11. The generated Manim program is substantially thinner than the current free-form programs and primarily orchestrates trusted runtime primitives.
12. Generated code passes AST/security validation before execution.
13. The frontend reports meaningful generation stages.
14. Plan/screenplay/storyboard artifacts are visible for debugging.
15. Feedback can regenerate a relevant downstream subset rather than always regenerating everything.
16. A bicycle end-to-end fixture completes successfully.

## Do not do these things

- Do not add Grok/Claude/OpenAI yet.
- Do not build an elaborate no-code editor.
- Do not attempt full 3D rendering in this milestone.
- Do not replace Manim unless a concrete blocker is demonstrated.
- Do not make Gemini output arbitrary 500–1000 line scene files.
- Do not use raw coordinates as the primary representation of semantic relationships.
- Do not couple TTS directly to generated scene code.
- Do not assume gyroscopic effect alone explains bicycle stability.

## Definition of done for Codex

After implementation, run the existing test suite plus the new tests, run the FastAPI server, submit a bicycle lesson request, and inspect the persisted artifacts. Fix any stage/reference/timing failures before considering the task complete.

The final response from Codex should summarize:

- files added/changed
- new pipeline stages
- API changes
- model calls made per job
- voice integration behavior
- test results
- any limitations that remain

Do not claim “3Blue1Brown quality” as a guaranteed outcome. The architecture should make that quality possible by making the explanation, visual semantics, object continuity, camera, and timing first-class data rather than leaving all of them to one unconstrained code-generation call.
