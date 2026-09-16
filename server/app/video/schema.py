from __future__ import annotations
from typing import Any, Literal
from pydantic import AliasChoices, BaseModel, Field, field_validator

SCHEMA_VERSION = "1.1"

class ConceptStep(BaseModel):
    id: str
    concept: str
    what_learner_should_realize: str
    depends_on: list[str] = Field(default_factory=list)
    importance: Literal["core", "supporting"] = "core"
    requires_visualization: bool = True

class Misconception(BaseModel):
    statement: str
    correction: str

class LessonPlan(BaseModel):
    schema_version: str = SCHEMA_VERSION
    title: str
    topic: str
    subject: str
    learner_level: str = "beginner"
    learning_objectives: list[str]
    prerequisite_knowledge: list[str] = Field(default_factory=list)
    central_question: str
    conceptual_chain: list[ConceptStep]
    misconceptions: list[Misconception] = Field(default_factory=list)
    estimated_duration_seconds: float

class NarrationBlock(BaseModel):
    id: str
    concept_step_id: str
    text: str
    purpose: Literal["hook", "intuition", "derivation", "example", "transition", "recap"]
    estimated_duration_seconds: float = Field(validation_alias=AliasChoices("estimated_duration_seconds", "duration_seconds"))
    emphasis_terms: list[str] = Field(default_factory=list)
    visual_requirement: str
    learner_intent: Literal["notice_relationship", "predict_outcome", "understand_causality", "connect_intuition_to_equation", "correct_misconception", "compare_cases", "generalize"] = "understand_causality"

    @field_validator("purpose", mode="before")
    @classmethod
    def normalize_purpose(cls, value):
        aliases = {"explanation": "intuition", "concept": "intuition", "application": "example", "summary": "recap", "conclusion": "recap", "connection": "transition"}
        return aliases.get(str(value).strip().lower(), value)

class Screenplay(BaseModel):
    schema_version: str = SCHEMA_VERSION
    title: str
    hook: str
    narration_blocks: list[NarrationBlock]
    total_estimated_duration_seconds: float

class CanvasSpec(BaseModel):
    width: int = 1920
    height: int = 1080
    background: str = "#101523"

class VisualStyle(BaseModel):
    name: str = "dark_educational"
    primary: str = "#edf4ff"
    secondary: str = "#aab8d0"
    accent: str = "#79f2c0"
    force: str = "#ffb86b"

class VisualState(BaseModel):
    """Declarative expectations; the runtime remains the source of live state."""
    position: dict[str, float] | None = None
    rotation: float | None = None
    scale: float | None = None
    visible: bool = False
    text: str | None = None
    value: float | None = None
    unit: str | None = None

class VisualRelation(BaseModel):
    type: Literal["causes", "opposes", "acts_on", "depends_on", "equals", "proportional_to", "conserved_with", "derived_from", "measured_from", "represents", "is_part_of", "moves_with", "attached_to", "points_to", "contains", "follows", "corresponds_to"]
    target_id: str
    quantity: str | None = None

class VisualObject(BaseModel):
    id: str
    type: Literal["text", "equation", "point", "vector", "line", "circle", "rectangle", "coordinate_system", "graph", "particle", "body", "wheel", "bicycle", "arrow", "label", "highlight", "group"]
    semantic_role: str
    initial_state: dict[str, Any] | VisualState = Field(default_factory=dict)
    parent_id: str | None = None
    relations: list[VisualRelation] = Field(default_factory=list)

class CameraAction(BaseModel):
    type: Literal["focus", "focus_on", "zoom", "zoom_to_relation", "follow", "pull_back", "show_context", "move_with", "compare", "pan", "none"] = "none"
    target_object_id: str | None = None
    zoom: float | None = None
    amount: float | None = None
    direction: Literal["left", "right", "up", "down"] | None = None

class VisualAction(BaseModel):
    type: Literal["create", "show", "hide", "fade", "move", "rotate", "scale", "morph", "transform", "highlight", "trace", "show_vector", "show_force", "show_measurement", "show_equation", "derive_equation_step", "camera_focus", "camera_zoom", "camera_follow", "pause", "introduce_object", "show_interaction", "show_cause", "show_effect", "compare_states", "connect_objects", "attach_quantity", "show_vector_field", "show_force_pair", "show_motion_trace", "show_coordinate_change", "derive_equation", "substitute_value", "highlight_relation", "transform_representation", "split_vector", "compose_vectors", "show_before_after"]
    object_id: str | None = None
    source_object_id: str | None = None
    target_object_id: str | None = None
    duration: float = 0.5
    to: dict[str, float] | None = None
    expression: str | None = None
    direction: str | None = None

class EquationSpec(BaseModel):
    id: str
    expression: str
    motivated_by_object_id: str
    meaning: str
    symbol_definitions: dict[str, str] = Field(default_factory=dict)
    previous_equation_id: str | None = None
    next_equation_id: str | None = None

class StoryboardScene(BaseModel):
    id: str
    narration_block_ids: list[str]
    purpose: str
    duration_policy: Literal["audio_locked", "visual_locked", "hybrid"] = "audio_locked"
    active_objects: list[str]
    actions: list[VisualAction]
    camera: CameraAction = Field(default_factory=CameraAction)
    equations: list[EquationSpec] = Field(default_factory=list)
    transition_to_next: str = "fade"
    duration_seconds: float | None = None

class Storyboard(BaseModel):
    schema_version: str = SCHEMA_VERSION
    canvas: CanvasSpec = Field(default_factory=CanvasSpec)
    global_style: VisualStyle = Field(default_factory=VisualStyle)
    objects: list[VisualObject]
    scenes: list[StoryboardScene]
