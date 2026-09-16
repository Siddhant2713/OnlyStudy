from __future__ import annotations

import json
from pathlib import Path

from manim import *

from .equations import EquationRenderer
from .state import ObjectRegistry, RuntimeObject

def load_storyboard(path="storyboard.json"):
    path = Path(path)
    if not path.is_absolute():
        path = Path(config.input_file).parent / path
    return json.loads(path.read_text(encoding="utf-8"))

class CameraController:
    def __init__(self, scene): self.scene = scene
    def apply(self, intent, registry):
        kind = intent.get("type", "none")
        target_id = intent.get("target_object_id")
        if kind in {"none", "show_context", "pull_back"}:
            if kind == "pull_back" and hasattr(self.scene.camera, "frame"):
                self.scene.play(self.scene.camera.frame.animate.set_width(config.frame_width), run_time=.35)
            return
        if not target_id or not hasattr(self.scene.camera, "frame"): return
        target = registry.get(target_id).mobject
        zoom = intent.get("zoom") or (1.5 if kind in {"focus", "focus_on", "zoom", "zoom_to_relation"} else 1)
        self.scene.play(self.scene.camera.frame.animate.move_to(target).set_width(self.scene.camera.frame.width / zoom), run_time=.35)

class LessonScene(MovingCameraScene):
    """Deterministic semantic renderer. Storyboards name meaning; this class selects Manim."""
    def make_object(self, spec):
        state, kind = spec.get("initial_state", {}), spec["type"]
        if hasattr(state, "model_dump"): state = state.model_dump(exclude_none=True)
        position = RIGHT * state.get("position", {}).get("x", 0) + UP * state.get("position", {}).get("y", 0)
        if kind in {"wheel", "circle"}:
            result = Circle(radius=state.get("radius", .7), color=BLUE)
        elif kind == "bicycle":
            result = VGroup(Rectangle(width=2, height=.45, color=GREEN), Circle(radius=.42, color=BLUE).shift(LEFT*.7+DOWN*.55), Circle(radius=.42, color=BLUE).shift(RIGHT*.7+DOWN*.55))
        elif kind in {"body", "rectangle", "array", "memory_block"}:
            result = Rectangle(width=state.get("width", 2), height=state.get("height", .8), color=GREEN)
        elif kind in {"vector", "arrow"}:
            direction = state.get("direction", "right")
            vector = {"left": LEFT, "up": UP, "down": DOWN}.get(direction, RIGHT)
            result = Arrow(ORIGIN, vector * state.get("length", 1.2), color=YELLOW)
        elif kind in {"line", "trajectory"}:
            result = Line(LEFT * state.get("length", 3), RIGHT * state.get("length", 3), color=GRAY)
        elif kind in {"coordinate_system", "graph"}:
            result = Axes(x_length=state.get("width", 5), y_length=state.get("height", 3))
        else:
            result = Text(state.get("text") or spec["semantic_role"], font_size=28, color=WHITE)
        return result.move_to(position).scale(state.get("scale", 1))

    def _registry(self, board):
        registry = ObjectRegistry()
        for spec in board["objects"]:
            registry.add(RuntimeObject(spec["id"], self.make_object(spec), spec["type"], dict(spec.get("initial_state") or {}), spec.get("parent_id"), spec.get("relations", [])))
        # Parent-relative attachments preserve their visual relationship when the parent moves.
        for entry in registry.all().values():
            if entry.parent_id:
                parent = registry.get(entry.parent_id).mobject
                offset = entry.mobject.get_center() - parent.get_center()
                entry.mobject.add_updater(lambda child, parent=parent, offset=offset: child.move_to(parent.get_center() + offset))
        return registry

    def _show(self, entry, duration):
        if not entry.visible:
            self.play(Create(entry.mobject), run_time=duration); entry.visible = True

    def _action(self, action, registry, equations, duration):
        kind, object_id = action["type"], action.get("object_id")
        entry = registry.get(object_id) if object_id else None
        if kind in {"create", "show", "introduce_object", "show_vector", "show_force", "show_measurement"} and entry:
            self._show(entry, duration)
        elif kind in {"hide", "fade"} and entry and entry.visible:
            self.play(FadeOut(entry.mobject), run_time=duration); entry.visible = False
        elif kind in {"move", "transform_representation"} and entry:
            target = action.get("to") or {}; delta = RIGHT * target.get("x", 0) + UP * target.get("y", 0)
            self.play(entry.mobject.animate.shift(delta), run_time=duration)
        elif kind == "rotate" and entry:
            self.play(Rotate(entry.mobject, action.get("to", {}).get("angle", PI / 2)), run_time=duration)
        elif kind in {"highlight", "highlight_relation", "show_cause", "show_effect"} and entry:
            self.play(Indicate(entry.mobject), run_time=duration)
        elif kind in {"show_interaction", "connect_objects", "show_force_pair"}:
            source, target = action.get("source_object_id"), action.get("target_object_id")
            if source and target:
                arrow = Arrow(registry.get(source).mobject.get_center(), registry.get(target).mobject.get_center(), buff=.15, color=ORANGE)
                self.play(Create(arrow), run_time=duration)
        elif kind == "attach_quantity" and entry:
            # The registry attachment updater handles future parent motion; reveal it at the parent.
            target = action.get("target_object_id")
            if target:
                entry.mobject.next_to(registry.get(target).mobject, UP)
            self._show(entry, duration)
        elif kind in {"compare_states", "show_before_after", "split_vector", "compose_vectors"} and entry:
            self._show(entry, duration / 2)
            self.play(Indicate(entry.mobject), run_time=duration / 2)
        elif kind in {"show_motion_trace", "trace"} and entry:
            trace = TracedPath(entry.mobject.get_center, stroke_color=YELLOW)
            self.add(trace); self.play(entry.mobject.animate.shift(RIGHT*.6), run_time=duration)
        elif kind in {"show_equation", "derive_equation", "derive_equation_step", "substitute_value"}:
            spec = next((eq for eq in equations if eq["id"] == object_id), None)
            expression = action.get("expression") or (spec or {}).get("expression")
            if expression:
                equation = EquationRenderer().make(spec or {"expression": expression}, WHITE).to_edge(DOWN)
                self.play(Write(equation), run_time=duration)
        elif kind == "pause": self.wait(duration)

    def run_storyboard(self, board):
        registry = self._registry(board)
        equations = [equation for scene in board["scenes"] for equation in scene.get("equations", [])]
        for scene in board["scenes"]:
            CameraController(self).apply(scene.get("camera", {}), registry)
            spent = 0
            for action in scene["actions"]:
                duration = max(.1, action.get("duration", .4)); spent += duration
                self._action(action, registry, equations, duration)
            remaining = (scene.get("duration_seconds") or 0) - spent
            if remaining > 0: self.wait(remaining)
