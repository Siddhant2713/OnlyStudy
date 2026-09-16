import json
import tempfile
import unittest
from pathlib import Path
from app.video.pipeline import route_feedback
from app.llm.gemini import GeminiProvider
from app.video.schema import LessonPlan, Screenplay, Storyboard
from app.video.validate import validate_plan, validate_screenplay, validate_storyboard, validate_scene_code
from app.voice.timing import normalize_storyboard_timing

FIXTURE = Path(__file__).parents[1] / "fixtures" / "bicycle_pipeline.json"
class PipelineTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(FIXTURE.read_text()); self.plan = LessonPlan.model_validate(data["lesson_plan"]); self.screenplay = Screenplay.model_validate(data["screenplay"]); self.board = Storyboard.model_validate(data["storyboard"])
    def test_bicycle_fixture_has_persistent_semantic_objects(self):
        validate_plan(self.plan); validate_screenplay(self.screenplay, self.plan); validate_storyboard(self.board, self.screenplay)
        self.assertIn("rear_wheel", self.board.scenes[0].active_objects); self.assertIn("rear_wheel", self.board.scenes[1].active_objects)
    def test_rejects_dangling_storyboard_reference(self):
        self.board.scenes[0].actions[0].object_id = "missing"
        with self.assertRaises(ValueError): validate_storyboard(self.board, self.screenplay)
    def test_storyboard_semantic_reference_gets_one_targeted_repair(self):
        class Provider:
            def __init__(self, replies): self.replies = iter(replies)
            def generate_structured(self, **_kwargs): return next(self.replies)
        from app.video.artifacts import ArtifactStore
        from app.video.pipeline import VideoPipeline
        bad = self.board.model_copy(deep=True); bad.scenes[0].actions[0].object_id = "missing"
        with tempfile.TemporaryDirectory() as directory:
            pipeline = VideoPipeline(Provider([bad, self.board]), ArtifactStore(Path(directory)), type("Request", (), {})(), lambda _stage: None)
            repaired = pipeline.storyboard(self.plan, self.screenplay)
            self.assertEqual(repaired.scenes[0].actions[0].object_id, "bike")
            self.assertTrue((Path(directory) / "storyboard_draft.json").exists())
    def test_code_security(self):
        safe = "from app.video.runtime import LessonScene, load_storyboard\nclass SceneTopic(LessonScene):\n    def construct(self): self.run_storyboard(load_storyboard())"
        self.assertEqual(validate_scene_code(safe), safe)
        with self.assertRaises(ValueError): validate_scene_code("import os\nclass SceneTopic: \n def construct(self): os.system('x')")
    def test_feedback_routing(self):
        self.assertEqual(route_feedback("Use a calmer voice"), "voicing"); self.assertEqual(route_feedback("the equation is wrong"), "storyboarding"); self.assertEqual(route_feedback("too fast"), "screenwriting")
    def test_gemini_json_repair_is_bounded_and_validated(self):
        provider = GeminiProvider("test", "test")
        replies = iter(["not json", json.dumps(self.plan.model_dump())])
        provider._send = lambda *args: next(replies)  # type: ignore[method-assign]
        repaired = provider.generate_structured(system_prompt="x", user_prompt="x", schema=LessonPlan)
        self.assertEqual(repaired.title, self.plan.title)
    def test_screenplay_normalizes_common_gemini_aliases(self):
        data = self.screenplay.model_dump()
        data["narration_blocks"][0]["purpose"] = "explanation"
        data["narration_blocks"][0]["concept_step_id"] = "ROLLING"
        data["narration_blocks"][0]["duration_seconds"] = data["narration_blocks"][0].pop("estimated_duration_seconds")
        screenplay = Screenplay.model_validate(data)
        validate_screenplay(screenplay, self.plan)
        self.assertEqual(screenplay.narration_blocks[0].purpose, "intuition")
        self.assertEqual(screenplay.narration_blocks[0].concept_step_id, "rolling")
    def test_screenplay_adds_missing_core_concept_after_bounded_repair(self):
        class Provider:
            def __init__(self, replies): self.replies = iter(replies)
            def generate_structured(self, **_kwargs): return next(self.replies)
        from app.video.artifacts import ArtifactStore
        from app.video.pipeline import VideoPipeline
        incomplete = self.screenplay.model_copy(deep=True)
        incomplete.narration_blocks = [block for block in incomplete.narration_blocks if block.concept_step_id != "rolling"]
        with tempfile.TemporaryDirectory() as directory:
            pipeline = VideoPipeline(Provider([incomplete, incomplete]), ArtifactStore(Path(directory)), type("Request", (), {})(), lambda _stage: None)
            completed = pipeline.screenplay(self.plan)
            validate_screenplay(completed, self.plan)
            self.assertIn("rolling", [block.concept_step_id for block in completed.narration_blocks])
            self.assertTrue((Path(directory) / "screenplay_draft.json").exists())
    def test_actual_voice_duration_locks_scene(self):
        board = normalize_storyboard_timing(self.board, self.screenplay, {"n1": 3.5, "n2": 4.5})
        self.assertEqual(board.scenes[0].duration_seconds, 3.5); self.assertEqual(board.scenes[1].duration_seconds, 4.5)
if __name__ == "__main__": unittest.main()
