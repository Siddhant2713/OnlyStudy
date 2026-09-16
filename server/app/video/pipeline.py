from __future__ import annotations
import json
from pathlib import Path
from app.llm.provider import LLMProvider
from app.video.artifacts import ArtifactStore
from app.video.schema import LessonPlan, NarrationBlock, Screenplay, Storyboard
from app.video.validate import validate_plan, validate_screenplay, validate_storyboard, validate_scene_code
from app.voice.gtts_provider import GTTSProvider
from app.voice.timing import normalize_storyboard_timing

TEACHING = "You create precise educational explainers. Teach one causal idea at a time, preserve physical and mathematical truth, and return only the requested data."

def route_feedback(feedback: str) -> str:
    text = feedback.lower()
    if any(word in text for word in ("voice", "speak", "audio", "calmer", "faster", "slower")): return "voicing"
    if any(word in text for word in ("equation", "wrong", "formula", "physics", "math")): return "storyboarding"
    if any(word in text for word in ("visual", "animate", "camera", "turn", "arrow", "object")): return "storyboarding"
    if any(word in text for word in ("fast", "explanation", "narration", "confusing", "wording")): return "screenwriting"
    return "planning"

class VideoPipeline:
    def __init__(self, provider: LLMProvider, store: ArtifactStore, request, set_stage):
        self.provider, self.store, self.request, self.set_stage = provider, store, request, set_stage
    def structured(self, schema, task, context):
        return self.provider.generate_structured(system_prompt=TEACHING, user_prompt=f"{task}\nReturn strict JSON for this schema: {json.dumps(schema.model_json_schema())}\nContext: {json.dumps(context)}", schema=schema)
    def plan(self, feedback=None):
        self.set_stage("planning")
        plan = self.structured(LessonPlan, "Create a scoped lesson plan with a connected conceptual chain and at least two objectives.", {"topic": self.request.topic, "subject": self.request.subject, "learner_level": self.request.learner_level, "duration_minutes": self.request.duration_minutes, "feedback": feedback})
        validate_plan(plan); self.store.write_json("lesson_plan", plan); return plan
    def screenplay(self, plan, feedback=None):
        self.set_stage("screenwriting")
        context = {"lesson_plan": plan.model_dump(), "feedback": feedback}
        task = "Write spoken-teaching narration that covers every core concept. Every block needs nonempty text, a positive duration, a visual requirement, and a concept_step_id copied exactly from the lesson plan. Use only purpose values: hook, intuition, derivation, example, transition, recap. Motivate equations."
        for attempt in range(2):
            screenplay = self.structured(Screenplay, task, context)
            try:
                validate_screenplay(screenplay, plan)
                self.store.write_json("screenplay", screenplay)
                return screenplay
            except ValueError as error:
                self.store.write_json("screenplay_draft", screenplay)
                if attempt:
                    if str(error).startswith("core concepts have no narration:"):
                        completed = self.add_missing_core_narration(screenplay, plan)
                        validate_screenplay(completed, plan)
                        self.store.write_json("screenplay", completed)
                        return completed
                    raise RuntimeError(f"screenwriting failed after one targeted repair: {error}") from error
                context = {**context, "validation_error": str(error), "repair_instruction": "Repair only the invalid narration blocks; preserve valid concept coverage."}
        raise AssertionError("unreachable")

    def add_missing_core_narration(self, screenplay, plan):
        """Guarantee plan coverage when a valid-shaped LLM retry still omits a core step."""
        covered = {block.concept_step_id for block in screenplay.narration_blocks}
        missing = [step for step in plan.conceptual_chain if step.importance == "core" and step.id not in covered]
        for step in missing:
            block_id = f"coverage_{step.id}"
            screenplay.narration_blocks.append(NarrationBlock(
                id=block_id,
                concept_step_id=step.id,
                text=f"Start with {step.concept}: {step.what_learner_should_realize}",
                purpose="intuition",
                estimated_duration_seconds=12,
                emphasis_terms=[step.concept],
                visual_requirement=f"Show a simple visual example of {step.concept} before connecting it to the next idea.",
            ))
        order = {step.id: index for index, step in enumerate(plan.conceptual_chain)}
        screenplay.narration_blocks.sort(key=lambda block: order.get(block.concept_step_id, len(order)))
        screenplay.total_estimated_duration_seconds = sum(block.estimated_duration_seconds for block in screenplay.narration_blocks)
        return screenplay
    def storyboard(self, plan, screenplay, feedback=None):
        self.set_stage("storyboarding")
        context = {"lesson_plan": plan.model_dump(), "screenplay": screenplay.model_dump(), "primitive_catalog": ["circle", "rectangle", "wheel", "bicycle", "arrow", "text", "equation", "vector"], "feedback": feedback}
        task = "Create a declarative visual storyboard. Reuse stable object IDs across scenes, map every narration block, attach forces/measurements, and use camera intent. Every action, camera, relation, and equation reference must name an ID declared in objects. Do not use raw Manim calls or arbitrary Python."
        for attempt in range(2):
            board = self.structured(Storyboard, task, context)
            try:
                validate_storyboard(board, screenplay)
                self.store.write_json("storyboard", board)
                return board
            except ValueError as error:
                self.store.write_json("storyboard_draft", board)
                if attempt:
                    raise RuntimeError(f"storyboarding failed after one targeted repair: {error}") from error
                context = {**context, "validation_error": str(error), "repair_instruction": "Repair the storyboard references. Declare every referenced object in objects, or replace the reference with an existing declared object. Preserve valid scenes and narration mappings."}
        raise AssertionError("unreachable")
    def criticize(self, plan, screenplay, board):
        self.set_stage("criticizing")
        # Deterministic critic catches all reference and coverage failures before codegen.
        validate_plan(plan); validate_screenplay(screenplay, plan); validate_storyboard(board, screenplay)
        result = {"status": "ok", "checks": ["plan", "screenplay", "storyboard", "references"]}; self.store.write_json("validation", result); return result
    def voice(self, screenplay, board):
        if not self.request.use_voiceover: return board, {}
        self.set_stage("voicing")
        provider, durations = GTTSProvider(), {}
        for block in screenplay.narration_blocks:
            result = provider.synthesize(block.text, preset=self.request.voice_preset, output_path=self.store.directory / "voice" / f"{block.id}.mp3")
            durations[block.id] = result.duration_seconds
        board = normalize_storyboard_timing(board, screenplay, durations)
        self.store.write_json("voice_timing", durations); self.store.write_json("storyboard", board); return board, durations
    def code(self, board):
        self.set_stage("codegen")
        prompt = "Return only this thin approved orchestration pattern, adapted only if necessary: from app.video.runtime import LessonScene, load_storyboard; class SceneTopic(LessonScene): construct calls self.run_storyboard(load_storyboard('storyboard.json')). Never add imports, helpers, file/network/subprocess calls, or arbitrary geometry."
        request = f"{prompt}\nValidated storyboard: {json.dumps(board.model_dump())}"
        for attempt in range(2):
            code = self.provider.generate_text(system_prompt="Generate only secure thin Manim orchestration code using app.video.runtime.", user_prompt=request)
            code = code.removeprefix("```python").removeprefix("```").removesuffix("```").strip()
            self.set_stage("validating")
            try:
                validate_scene_code(code); self.store.write_text("scene.py", code); return code
            except ValueError as error:
                if attempt: raise RuntimeError(f"scene validation failed after one repair: {error}") from error
                request = f"{prompt}\nYour last code failed static validation: {error}. Return a repaired thin SceneTopic only."
        raise AssertionError("unreachable")
    def run(self, feedback=None, start_stage="planning"):
        # Reuse upstream persisted artifacts for targeted feedback, falling back to the earliest safe stage.
        if start_stage == "planning": plan = self.plan(feedback)
        else: plan = LessonPlan.model_validate(self.store.read_json("lesson_plan"))
        if start_stage in {"planning", "screenwriting"}: screenplay = self.screenplay(plan, feedback)
        else: screenplay = Screenplay.model_validate(self.store.read_json("screenplay"))
        if start_stage in {"planning", "screenwriting", "storyboarding"}: board = self.storyboard(plan, screenplay, feedback)
        else: board = Storyboard.model_validate(self.store.read_json("storyboard"))
        self.criticize(plan, screenplay, board)
        board, durations = self.voice(screenplay, board)
        return self.code(board), durations
