Stage: screenwriting
✓ Planning lesson
● Writing explanation
○ Designing visuals
○ Generating voice
○ Building animation
○ Rendering
○ Finalizing
invalid narration block
View lesson plan
lesson_plan
{
  "schema_version": "1.0",
  "title": "Introduction to Newton's Laws of Motion",
  "topic": "laws of motion",
  "subject": "General",
  "learner_level": "beginner",
  "learning_objectives": [
    "Define force as a push or a pull and describe its basic effect on an object's motion.",
    "Explain the concept of inertia and provide an example of an object resisting a change in its state of motion.",
    "Qualitatively describe how the strength of a force and an object's mass influence its acceleration."
  ],
  "prerequisite_knowledge": [
    "Basic understanding of 'motion' (e.g., moving, still, speed, direction)."
  ],
  "central_question": "How do pushes and pulls affect how things move, and why do objects resist changes to their motion?",
  "conceptual_chain": [
    {
      "id": "C1",
      "concept": "Force is a push or a pull.",
      "what_learner_should_realize": "Learners will realize that forces are interactions that can start, stop, or change an object's speed or direction of motion.",
      "depends_on": [],
      "importance": "core",
      "requires_visualization": true
    },
    {
      "id": "C2",
      "concept": "Inertia: Objects resist changes in their state of motion (Newton's First Law).",
      "what_learner_should_realize": "Learners will understand that an object at rest tends to stay at rest, and an object in motion tends to stay in motion at a constant speed and direction, unless acted upon by an unbalanced force.",
      "depends_on": [
        "C1"
      ],
      "importance": "core",
      "requires_visualization": true
    },
    {
      "id": "C3",
      "concept": "Force causes acceleration (Newton's Second Law - Qualitative).",
      "what_learner_should_realize": "Learners will grasp that a stronger net force causes a greater change in an object's speed or direction (acceleration), and that heavier objects require more force to achieve the same acceleration.",
      "depends_on": [
        "C1",
        "C2"
      ],
      "importance": "core",
      "requires_visualization": true
    },
    {
      "id": "C4",
      "concept": "Forces always come in pairs (Newton's Third Law).",
      "what_learner_should_realize": "Learners will understand that whenever one object exerts a force on a second object, the second object simultaneously exerts an equal and opposite force back on the first object.",
      "depends_on": [
        "C1"
      ],
      "importance": "supporting",
      "requires_visualization": true
    }
  ],
  "misconceptions": [
    {
      "statement": "An object needs a continuous force to keep moving at a constant speed.",
      "correction": "According to Newton's First Law (Inertia), an object in motion will stay in motion at a constant velocity unless an unbalanced force acts upon it. Forces are needed to *change* motion (speed up, slow down, or change direction), not necessarily to *maintain* it."
    }
  ],
  "estimated_duration_seconds": 120
}