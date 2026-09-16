# Spec 08 learning notes — semantic video quality

## What changed

- The storyboard is now an explanation contract, not a list of low-level drawing commands. Gemini selects supported meanings; the runtime selects Manim primitives and animation calls.
- A semantic object registry keeps object identity, visibility, parentage, relations, and attachments alive across scenes. This is what lets a wheel, force arrow, or pointer remain the *same* teaching object.
- Actual voice durations feed a timeline compiler. Visual work is compressed in order when it exceeds narration time, rather than quietly drifting out of sync.
- Teaching quality has a deterministic warning report for visual coverage, density, continuity, idle scenes, redundant creation, camera intent, and equation linkage.

## Durable design lessons

1. A richer JSON schema does not improve an animation unless the renderer has distinct behavior for its semantics. The critical boundary is semantic action → deterministic rendering.
2. Persistence is an educational property: retaining object IDs across scenes helps a learner track cause, effect, and transformation.
3. Equations need a visual motivation and a source object. Showing `F = ma` is weaker than connecting `F` to a force arrow and `a` to changing motion.
4. TTS duration is authoritative timing data. Estimated narration duration is useful only before speech exists.
5. Reliability tests must go beyond “the render exited 0.” Fixed subject fixtures give us a way to test concepts such as force direction, graph transformation, and pointer identity.

## Validation still to extend

- The visual-regression harness currently verifies structural semantic properties. Adding low-quality Manim frame capture and image/geometry assertions is the next phase once CI provides Manim.
- The dashboard persists timeline and quality-report artifacts for inspection; a compact visual inspector is still a future UI task.
