from __future__ import annotations
import json
from pathlib import Path
from manim import *
def load_storyboard(path="storyboard.json"):
    path = Path(path)
    if not path.is_absolute(): path = Path(config.input_file).parent / path
    return json.loads(path.read_text(encoding="utf-8"))
class CameraController:
    def __init__(self, scene): self.scene = scene
    def apply(self, intent, objects):
        target = objects.get(intent.get("target_object_id")); zoom = intent.get("zoom")
        if target and zoom and hasattr(self.scene.camera, "frame"):
            self.scene.play(self.scene.camera.frame.animate.move_to(target).set_width(self.scene.camera.frame.width / zoom), run_time=.35)
class LessonScene(MovingCameraScene):
    def make_object(self, spec):
        state, kind = spec.get("initial_state", {}), spec["type"]
        if kind in {"wheel", "circle"}: return Circle(radius=state.get("radius", .7), color=BLUE)
        if kind in {"bicycle", "body", "rectangle"}: return Rectangle(width=state.get("width", 2), height=state.get("height", .8), color=GREEN)
        if kind in {"vector", "arrow"}: return Arrow(ORIGIN, RIGHT * state.get("length", 1.2), color=YELLOW)
        return Text(state.get("text", spec["semantic_role"]), font_size=28, color=WHITE)
    def run_storyboard(self, board):
        objects = {spec["id"]: self.make_object(spec) for spec in board["objects"]}
        for scene in board["scenes"]:
            CameraController(self).apply(scene.get("camera", {}), objects)
            for action in scene["actions"]:
                obj = objects.get(action.get("object_id")); duration = max(.1, action.get("duration", .4))
                if action["type"] in {"create", "show"} and obj: self.play(Create(obj), run_time=duration)
                elif action["type"] in {"hide", "fade"} and obj: self.play(FadeOut(obj), run_time=duration)
                elif action["type"] == "move" and obj: self.play(obj.animate.shift(RIGHT * action.get("to", {}).get("x", 0) + UP * action.get("to", {}).get("y", 0)), run_time=duration)
                elif action["type"] == "rotate" and obj: self.play(Rotate(obj, PI / 2), run_time=duration)
                elif action["type"] == "highlight" and obj: self.play(Indicate(obj), run_time=duration)
                elif action["type"] in {"show_force", "show_vector", "show_measurement", "show_equation"} and obj: self.play(Create(obj), run_time=duration)
                elif action["type"] == "pause": self.wait(duration)
            remaining = (scene.get("duration_seconds") or 0) - sum(a.get("duration", .4) for a in scene["actions"])
            if remaining > 0: self.wait(remaining)
