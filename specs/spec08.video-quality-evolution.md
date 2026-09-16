# OnlyStudy Spec 08 — Video Quality Evolution: From Generated Video to Real Concept Explanation

## 0. Purpose

The current `main` branch can now complete the end-to-end generation path and produce a playable MP4. The reliability work from Spec 07 materially improved job state, final-video validation, and delivery behavior.

The supplied Newton's Laws test video confirms an important milestone: **the system can generate a real lesson video**.

The next problem is not basic generation. It is **quality of explanation and quality of animation**.

The central objective of this spec is therefore:

> Turn OnlyStudy from a system that can successfully generate an educational-looking video into a system that can deliberately construct a strong visual explanation of a concept.

This is an evolution of Spec 04, not a replacement.

The architectural direction remains:

```text
Topic
  ↓
Lesson Plan
  ↓
Screenplay
  ↓
Storyboard
  ↓
Semantic Runtime
  ↓
Animation Timeline
  ↓
Render
  ↓
Voice + Mux
  ↓
Final Lesson
```

But the implementation must now enforce a much stronger contract:

```text
Gemini decides WHAT the learner should see and understand.

OnlyStudy runtime decides HOW that meaning is rendered.
```

Do not solve current quality problems by simply making Gemini produce more Manim code.

---

# 1. Current-state assessment

## 1.1 What is working now

The current implementation contains the major structural components introduced by the previous specs:

- durable jobs
- explicit generation stages
- lesson-plan artifact
- screenplay artifact
- storyboard artifact
- voice stage
- generated scene artifact
- render stage
- final MP4 validation
- React job polling and playback
- Gemini provider abstraction

The most recent commit also moved Gemini client creation to the provider lifetime, introduced richer job state, and validates the final video before reporting availability.

These are useful foundations and should remain.

## 1.2 What remains weak

The produced video demonstrates the core limitation of the current architecture:

### The intermediate representation is richer than the renderer.

The storyboard can express things such as:

- bicycle
- wheel
- force
- vector
- equation
- measurement
- camera focus
- transformation
- semantic relation

but the runtime still maps many of those concepts into generic Manim primitives.

For example, several semantic object types collapse into generic `Circle`, `Rectangle`, `Arrow`, or `Text`, and several semantic action types share the same low-level behavior.

This creates a dangerous mismatch:

```text
Storyboard says:
"show Newton's third-law interaction between two bodies"

Runtime produces:
"create two shapes and some arrows"
```

The code runs, but the visual explanation is not guaranteed to be meaningful.

## 1.3 The current runtime is too CRUD-like

The runtime mostly behaves like:

```text
create object
move object
rotate object
highlight object
fade object
```

That is animation control, not explanation control.

The next runtime must understand semantic educational operations such as:

```text
show interaction
show causality
compare two states
derive equation
attach quantity to object
show conservation
show before/after
trace motion
show force decomposition
follow moving object
transform one representation into another
```

The semantic runtime is therefore the main engineering priority of this spec.

---

# 2. Quality target

OnlyStudy should optimize for five dimensions.

## 2.1 Conceptual coherence

The lesson should feel like one continuous argument, not a collection of animated slides.

A learner should be able to answer:

```text
What was the question?
What changed?
Why did it change?
How did the previous scene cause the next scene?
```

## 2.2 Visual causality

Whenever possible, visuals should demonstrate relationships rather than merely label them.

Weak:

```text
Object A
Object B
F = ma
```

Strong:

```text
Object A pushes Object B
        ↓
interaction appears
        ↓
force vectors emerge from contact
        ↓
motion changes
        ↓
equation connects the observed change to the force
```

## 2.3 Persistent state

Objects should survive conceptually across scenes.

The learner should see the same object transform, move, interact, or become reinterpreted.

Avoid:

```text
scene 1: bicycle
scene 2: unrelated rectangle
scene 3: unrelated equation
```

Prefer:

```text
bicycle
  ↓ zoom
rear wheel
  ↓ rotation
contact patch
  ↓ force visualization
friction vector
  ↓ abstraction
F = μN
```

## 2.4 Mathematical faithfulness

Equations are explanatory objects, not decorations.

Every displayed equation must have:

- a semantic meaning
- defined variables
- a reason for being introduced
- a relation to the current visual state
- a clear transition from prior reasoning

## 2.5 Pacing

Animation should follow teaching rhythm.

Do not maximize animation density.

Prefer:

```text
show → pause → transform → explain → reinforce
```

over:

```text
create 8 things → move 8 things → zoom → flash → replace
```

---

# 3. New architecture: semantic runtime + timeline compiler

The next architecture should be:

```text
                 +------------------+
                 |   Lesson Plan    |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 |    Screenplay     |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Semantic Storyboard|
                 +--------+---------+
                          |
                          v
             +----------------------------+
             | Storyboard Normalizer       |
             | reference resolution        |
             | semantic validation         |
             | timeline planning           |
             +-------------+--------------+
                           |
                           v
             +----------------------------+
             | Semantic Animation Runtime  |
             | objects / relations / state |
             | visual primitives           |
             +-------------+--------------+
                           |
                           v
             +----------------------------+
             | Timeline Compiler            |
             | audio duration               |
             | beats / pauses / transitions |
             +-------------+--------------+
                           |
                           v
                       Manim
```

Gemini should never be responsible for deciding low-level implementation details such as:

- exact Mobject composition
- `play()` calls
- raw coordinate arithmetic
- repeated geometry boilerplate
- animation object construction
- low-level camera frame manipulation

Those responsibilities belong to deterministic OnlyStudy code.

---

# 4. Storyboard schema upgrade

The current storyboard schema should be retained but expanded from an action list into a semantic scene description.

## 4.1 Visual object state

Add explicit state fields where useful:

```python
class VisualState(BaseModel):
    position: dict[str, float] | None
    rotation: float | None
    scale: float | None
    visible: bool
    text: str | None
    value: float | None
    unit: str | None
```

A `VisualObject` should maintain:

```text
id
semantic_role
type
initial_state
current_state expectations
parent
relations
```

The runtime owns the actual current state.

## 4.2 Semantic relations

Extend relations to support educational meaning:

- `causes`
- `opposes`
- `acts_on`
- `depends_on`
- `equals`
- `proportional_to`
- `conserved_with`
- `derived_from`
- `measured_from`
- `represents`
- `is_part_of`
- `moves_with`
- `attached_to`

Relations are not just metadata. They should inform default renderer behavior.

Example:

```json
{
  "type": "acts_on",
  "source_id": "hand",
  "target_id": "box",
  "quantity": "force"
}
```

The runtime can therefore know that the force arrow belongs to the interaction between those objects.

## 4.3 Semantic action types

Add actions such as:

```text
introduce_object
show_interaction
show_cause
show_effect
compare_states
connect_objects
attach_quantity
show_vector_field
show_force_pair
show_motion_trace
show_coordinate_change
derive_equation
substitute_value
highlight_relation
transform_representation
split_vector
compose_vectors
show_before_after
```

These are higher-level than raw `move`/`rotate`.

Raw primitive actions can remain as implementation-level fallbacks, but Gemini should prefer semantic actions.

---

# 5. Build the semantic visual runtime

Create a proper package under:

```text
server/app/video/runtime/
```

Suggested modules:

```text
runtime/
    __init__.py
    engine.py
    object_registry.py
    state.py
    semantic_actions.py
    primitives.py
    camera.py
    equations.py
    labels.py
    relationships.py
    timeline.py
    style.py
```

## 5.1 Object registry

Maintain a registry:

```python
registry.get("box")
registry.get("force_on_box")
registry.get("velocity")
```

Each object should know:

- its semantic ID
- its Mobject
- semantic type
- current transform
- visibility
- parent
- relation metadata

## 5.2 Attachment system

An attached label/vector/measurement must follow its parent automatically.

Example:

```text
box
 ├── velocity_vector
 ├── force_vector
 └── mass_label
```

When the box moves, the attached objects should update automatically.

This is essential for physics explanations.

## 5.3 Domain-aware primitives

Create reusable primitives for common educational concepts.

Physics examples:

```text
PhysicsBody
Wheel
Bicycle
ForceArrow
VelocityArrow
AccelerationArrow
TorqueArrow
ContactPoint
Trajectory
CoordinateFrame
MeasurementBracket
VectorDecomposition
```

Mathematics examples:

```text
NumberLine
CoordinatePlane
FunctionGraph
Point
Vector
AreaRegion
Matrix
```

Computer science examples:

```text
Array
Node
Edge
Pointer
Stack
Queue
Tree
Graph
MemoryBlock
```

Do not implement every domain immediately. Build a clean extension mechanism and implement the primitives needed by the validation fixtures first.

---

# 6. Equations become first-class visual objects

The current runtime must stop treating `show_equation` as a generic create action.

Implement an `EquationRenderer`.

Each equation should support:

```text
equation ID
expression
meaning
symbol definitions
source concept
previous equation
next equation
```

Semantic operations:

```text
introduce equation
transform equation
replace one term
substitute value
highlight term
map term to visual object
```

For example:

```text
F = ma
```

should be able to highlight `F`, connect it to a force arrow, then highlight `a`, connect it to observed motion, and then substitute a numerical value.

Do not require a full symbolic algebra engine in this milestone.

But do require:

- deterministic equation rendering
- transition support
- symbol annotations
- visual references

Use the installed mathematical rendering capabilities rather than forcing the LLM to fake equation typography with plain text.

---

# 7. Camera becomes semantic

The camera system should understand the explanation graph.

Supported semantic commands:

```text
focus_on(object)
follow(object)
zoom_to_relation(source, target)
show_context()
pull_back()
move_with(object)
compare(left, right)
```

Example:

```text
bicycle
   ↓
zoom to rear wheel
   ↓
zoom to contact patch
   ↓
show friction
   ↓
pull back
   ↓
return to bicycle
```

This gives the learner spatial continuity.

Do not expose raw Manim camera coordinates to Gemini unless absolutely necessary.

---

# 8. Screenplay quality upgrade

The screenplay should become more than narration text.

Add a teaching-beat model.

Each narration block should define:

```text
concept_step_id
purpose
spoken_text
visual_requirement
learner_intent
emphasis_terms
estimated_duration
```

`learner_intent` examples:

```text
notice a relationship
predict an outcome
understand a causal mechanism
connect intuition to equation
correct a misconception
compare two cases
generalize from example
```

The storyboard planner should consume this intent directly.

This prevents the animation from merely illustrating the narration literally.

---

# 9. Add a deterministic teaching-quality validator

The current validator mainly verifies references and schema correctness.

Add a second layer that evaluates structural teaching quality without needing Gemini.

Checks should include:

## 9.1 Coverage

Every core concept has:

- narration
- at least one meaningful visual action

## 9.2 Visual density

Flag scenes with too many simultaneous objects/actions.

Use soft thresholds rather than absolute rejection initially.

## 9.3 Text density

Reject paragraph-sized text blocks on screen.

Prefer:

```text
short label
single equation
few symbols
```

## 9.4 Transformation continuity

Warn when a scene destroys all prior objects and introduces an unrelated visual state without a declared transition.

## 9.5 Camera intent

Flag lessons where:

- every scene uses the same camera state
- camera requests target nonexistent objects
- camera movement occurs without a conceptual reason

## 9.6 Equation linkage

Flag equations that do not connect to a visual object or prior equation.

## 9.7 Idle time

Flag scenes with long waits but no deliberate narration or visual purpose.

## 9.8 Action redundancy

Flag sequences such as:

```text
create → create → create
```

without transformation or conceptual progression.

The validator should produce warnings and a quality report rather than reject every stylistic issue.

---

# 10. Timeline compiler

The current duration normalization is too shallow.

Replace it with a timeline compiler.

Input:

```text
Screenplay
TTS durations
Storyboard
```

Output:

```text
CompiledTimeline
```

Each beat should have:

```text
start
end
duration
narration_block_id
visual actions
camera state
pause policy
```

Example:

```text
0.0–2.0   establish box
2.0–5.5   force appears
5.5–8.0   box accelerates
8.0–10.0  equation appears
10.0–12.0 pause / reinforce
```

The compiler must enforce:

```text
visual actions fit inside narration duration
```

When they do not:

1. compress nonessential animations
2. merge adjacent actions
3. extend only when the lesson design allows it
4. never silently create large mismatches

Actual TTS duration is authoritative.

---

# 11. Improve Gemini prompting without adding more model layers yet

Do not add another LLM solely because visual quality is weak.

First improve the existing stage prompts.

## Lesson planner

Require:

- one central question
- one causal chain
- 2–6 core concepts for a short lesson
- explicit misconception handling
- explicit learner intent

Avoid encyclopedic lesson plans.

## Screenplay writer

Require:

- spoken language
- concrete intuition
- a reason before an equation
- one conceptual beat at a time
- no filler
- no narration of obvious on-screen events

## Storyboard planner

Require:

- semantic actions over primitive actions
- persistent objects
- relation-first visualization
- transformation continuity
- camera intent
- no decorative animation
- equations connected to visuals

The prompt should include the actual runtime capability catalog so Gemini does not invent unsupported operations.

---

# 12. Renderer capability contract

The runtime must publish a machine-readable capability catalog.

Example:

```json
{
  "objects": [
    "physics_body",
    "wheel",
    "force_arrow",
    "velocity_arrow",
    "equation",
    "label"
  ],
  "actions": [
    "show_interaction",
    "show_force_pair",
    "show_motion_trace",
    "derive_equation",
    "attach_quantity",
    "focus_on",
    "follow"
  ]
}
```

The storyboard generator consumes this catalog.

This creates an explicit contract:

```text
Gemini cannot plan a visual the renderer cannot execute.
```

The system should reject unknown capabilities before code generation.

---

# 13. Add a benchmark suite instead of judging videos randomly

Create:

```text
server/tests/video_quality/
```

with benchmark fixtures.

At minimum:

### Newton's laws

Test:

- two interacting bodies
- force arrows
- direction
- equal/opposite relationship
- motion response
- equation connection

### Bicycle physics

Test:

- wheel rotation
- forward motion
- tire-road interaction
- velocity direction
- turning
- lean relationship

### Mathematical function

Test:

- coordinate plane
- graph
- parameter change
- point movement
- equation-to-graph connection

### Computer science

Test:

- array or linked list
- pointer/reference movement
- state transition
- persistent node identity

Each benchmark should verify the storyboard and runtime behavior, not just that Manim exits with code 0.

---

# 14. Visual regression testing

Add a small deterministic visual regression harness.

For each benchmark:

1. generate a fixed storyboard fixture
2. render at low quality
3. capture selected frames
4. compare to expected structural properties

Do not require pixel-perfect matching initially.

Prefer checks such as:

- expected number of semantic objects visible
- expected object movement
- expected camera focus
- expected equation present
- expected force/vector direction
- expected scene duration

Store representative frame snapshots for manual review.

---

# 15. Debugging interface for development

The React dashboard should eventually show a compact lesson inspector.

For each completed lesson:

```text
Lesson
 ├─ Plan
 ├─ Screenplay
 ├─ Storyboard
 ├─ Timeline
 ├─ Voice
 ├─ Render diagnostics
 └─ Final video
```

Do not turn this into a user-facing IDE yet.

The purpose is developer debugging:

```text
Why did the video look wrong?
```

should be answerable from persisted artifacts.

---

# 16. Feedback should target the semantic layer

Keep Spec 07's targeted feedback routing, but make it more precise.

Examples:

```text
"The video doesn't actually show why the box accelerates."
→ storyboard semantic action

"The force arrows are floating."
→ object attachment / runtime

"The equation appears suddenly."
→ screenplay + equation transition

"The explanation is too fast."
→ screenplay/timeline

"The graph should move when the parameter changes."
→ semantic graph action/runtime

"The camera loses the bicycle."
→ camera strategy
```

The system should avoid regenerating unaffected stages.

---

# 17. Performance constraints

Do not sacrifice generation reliability while improving quality.

For a ~2 minute lesson, aim for:

- minimal redundant Gemini calls
- compact structured contexts
- one bounded repair per stage
- deterministic normalization wherever possible
- one TTS request per block
- one Manim render

The new runtime must not cause exponential complexity.

Avoid creating thousands of individual Mobjects when one semantic primitive can represent the same idea.

---

# 18. Implementation order

Implement in this order.

## Phase 1 — runtime foundation

Build:

- object registry
- persistent semantic state
- attachments
- reusable domain primitives
- equation renderer
- semantic camera

Do not change every benchmark at once.

## Phase 2 — semantic actions

Implement:

- show_interaction
- show_force_pair
- show_motion_trace
- attach_quantity
- compare_states
- derive_equation
- transform_representation

## Phase 3 — timeline compiler

Integrate actual voice durations and compile storyboard actions into controlled beats.

## Phase 4 — storyboard upgrade

Teach Gemini to prefer semantic capabilities supported by the runtime.

## Phase 5 — quality validator

Add structural teaching-quality warnings.

## Phase 6 — benchmark suite

Create deterministic Newton / bicycle / math / CS fixtures.

## Phase 7 — visual regression

Render and inspect representative frames.

## Phase 8 — Gemini refinement

Only after runtime quality is measurable, tune lesson/screenplay/storyboard prompts using benchmark failures.

---

# 19. What NOT to do

Do not:

- revert to direct topic-to-Manim generation
- ask Gemini for 500+ lines of animation code
- add another LLM stage before measuring current failures
- build a general-purpose animation editor
- implement full physics simulation immediately
- hard-code only the Newton's-laws lesson
- make every object a generic rectangle/circle
- treat every storyboard action as `Create()`
- rely on guessed timings when TTS durations exist
- use raw camera coordinates as the primary semantic interface
- judge success only by HTTP 200 / Manim exit code

---

# 20. Definition of done

Spec08 is complete when all of the following are true:

1. A storyboard capability catalog exists and is consumed by Gemini.
2. Runtime object identity persists across scenes.
3. Attached labels/vectors/measurements follow their parent objects.
4. At least three domain-aware primitives are implemented for physics.
5. Equations are rendered by a dedicated equation system.
6. At least five semantic visual actions execute differently from raw `Create()`.
7. Camera follow/focus behavior is semantic rather than coordinate-driven.
8. A compiled timeline uses actual TTS durations.
9. Structural teaching-quality validation produces a report.
10. Newton's laws has a deterministic semantic storyboard fixture.
11. Bicycle physics has a deterministic semantic storyboard fixture.
12. At least one math and one CS fixture exist.
13. Low-quality benchmark renders complete successfully.
14. Representative frames can be inspected for each benchmark.
15. Feedback can target storyboard/runtime/timeline without rebuilding unrelated stages.
16. The final React dashboard still receives and plays the final MP4.
17. No core functionality depends on Gemini generating arbitrary Manim geometry.

---

# 21. Final engineering principle

The next major leap in OnlyStudy does **not** come from asking Gemini to write smarter Python.

It comes from making the system understand that an educational animation consists of:

```text
concepts
relationships
states
transformations
visual evidence
camera attention
mathematical representations
teaching beats
```

Gemini should plan those things.

OnlyStudy should execute those things deterministically.

That separation is the foundation for moving from:

```text
"AI-generated Manim video"
```

toward:

```text
"AI-generated visual explanation"
```
