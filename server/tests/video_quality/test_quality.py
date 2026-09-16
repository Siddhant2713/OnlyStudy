import json
import unittest
from pathlib import Path

from app.video.capabilities import capability_catalog
from app.video.timeline import compile_timeline
from app.video.schema import LessonPlan, Screenplay, Storyboard
from app.video.validate import teaching_quality_report, validate_screenplay, validate_storyboard
from visual_regression import capture_structural_snapshots

FIXTURES = Path(__file__).parent / "fixtures"

class VideoQualityBenchmarks(unittest.TestCase):
    def load(self, name):
        data = json.loads((FIXTURES / f"{name}.json").read_text())
        return LessonPlan.model_validate(data["lesson_plan"]), Screenplay.model_validate(data["screenplay"]), Storyboard.model_validate(data["storyboard"])

    def test_benchmarks_are_semantic_and_valid(self):
        for name in ("newton", "bicycle", "function", "linked_list"):
            plan, screenplay, board = self.load(name)
            validate_screenplay(screenplay, plan); validate_storyboard(board, screenplay)
            self.assertTrue(any(action.type in capability_catalog()["actions"] for scene in board.scenes for action in scene.actions), name)

    def test_newton_fixture_links_force_and_equation(self):
        plan, screenplay, board = self.load("newton")
        report = teaching_quality_report(plan, screenplay, board)
        self.assertEqual(report["status"], "ok")
        self.assertTrue(any(action.type == "show_force_pair" for scene in board.scenes for action in scene.actions))
        self.assertTrue(board.scenes[-1].equations[0].motivated_by_object_id)

    def test_timeline_uses_actual_voice_duration(self):
        plan, screenplay, board = self.load("bicycle")
        timeline = compile_timeline(board, screenplay, {"n1": 3.0, "n2": 5.0})
        self.assertEqual(timeline.duration_seconds, 8.0)
        self.assertEqual(board.scenes[0].duration_seconds, 3.0)

    def test_structural_regression_snapshot_keeps_newton_force_pair_visible(self):
        _plan, _screenplay, board = self.load("newton")
        snapshot = capture_structural_snapshots(board)[1]
        self.assertIn("force_pair", snapshot.visible_object_ids)
        self.assertIn("show_force_pair", snapshot.action_types)
        self.assertTrue(snapshot.equations)

if __name__ == "__main__": unittest.main()
