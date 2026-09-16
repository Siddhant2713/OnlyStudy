import ast
from .schema import LessonPlan, Screenplay, Storyboard
from .capabilities import capability_catalog
ALLOWED_IMPORTS = {"manim", "app.video.runtime"}
DANGEROUS = {"eval", "exec", "compile", "__import__", "open", "input", "getattr", "setattr", "delattr"}

def _unique(values, label):
    if len(values) != len(set(values)): raise ValueError(f"duplicate {label} IDs")
def validate_plan(plan: LessonPlan):
    if not plan.central_question.strip(): raise ValueError("lesson plan central question is empty")
    if len(plan.learning_objectives) < 2: raise ValueError("lesson plan needs at least two learning objectives")
    ids = [s.id for s in plan.conceptual_chain]; _unique(ids, "concept step")
    if len(ids) < 2: raise ValueError("lesson plan needs at least two concept steps")
    known = set(ids)
    for step in plan.conceptual_chain:
        if any(dep not in known for dep in step.depends_on): raise ValueError(f"unknown dependency in {step.id}")
        if step.id in step.depends_on: raise ValueError(f"self dependency in {step.id}")
    return plan
def validate_screenplay(screenplay: Screenplay, plan: LessonPlan):
    ids = {s.id for s in plan.conceptual_chain}; canonical = {step_id.casefold(): step_id for step_id in ids}
    blocks = screenplay.narration_blocks
    _unique([b.id for b in blocks], "narration block")
    if not blocks: raise ValueError("screenplay has no narration blocks")
    for block in blocks:
        # IDs are semantic references; canonicalize harmless casing differences,
        # but never invent a missing concept reference.
        block.concept_step_id = canonical.get(block.concept_step_id.strip().casefold(), block.concept_step_id)
        if not block.text.strip(): raise ValueError(f"narration block {block.id} has no spoken text")
        if block.estimated_duration_seconds <= 0: raise ValueError(f"narration block {block.id} has a non-positive duration")
        if block.concept_step_id not in ids: raise ValueError(f"narration block {block.id} references unknown concept step {block.concept_step_id}")
        if not block.visual_requirement.strip(): raise ValueError(f"narration block {block.id} has no visual requirement")
    covered = {b.concept_step_id for b in blocks}
    missing = [s.id for s in plan.conceptual_chain if s.importance == "core" and s.id not in covered]
    if missing: raise ValueError(f"core concepts have no narration: {', '.join(missing)}")
    if screenplay.total_estimated_duration_seconds <= 0: raise ValueError("screenplay total duration must be positive")
    return screenplay
def validate_storyboard(board: Storyboard, screenplay: Screenplay):
    object_ids = {o.id for o in board.objects}; _unique([o.id for o in board.objects], "visual object")
    block_ids = {b.id for b in screenplay.narration_blocks}; _unique([s.id for s in board.scenes], "scene")
    if not board.scenes: raise ValueError("storyboard needs scenes")
    for obj in board.objects:
        if obj.parent_id and obj.parent_id not in object_ids: raise ValueError(f"unknown parent {obj.parent_id}")
        if any(r.target_id not in object_ids for r in obj.relations): raise ValueError(f"dangling relation on {obj.id}")
    capabilities = set(capability_catalog()["actions"])
    primitive_actions = {"create", "show", "hide", "fade", "move", "rotate", "scale", "morph", "transform", "highlight", "trace", "show_vector", "show_force", "show_measurement", "show_equation", "derive_equation_step", "camera_focus", "camera_zoom", "camera_follow", "pause"}
    for scene in board.scenes:
        if not set(scene.narration_block_ids) <= block_ids: raise ValueError(f"unknown narration in {scene.id}")
        if not set(scene.active_objects) <= object_ids: raise ValueError(f"unknown active object in {scene.id}")
        if scene.camera.target_object_id and scene.camera.target_object_id not in object_ids: raise ValueError(f"unknown camera target in {scene.id}")
        for action in scene.actions:
            if action.duration < 0: raise ValueError("negative action duration")
            for target in (action.object_id, action.source_object_id, action.target_object_id):
                if target and target not in object_ids: raise ValueError(f"unknown action object {target}")
            if action.type not in capabilities | primitive_actions: raise ValueError(f"unsupported semantic action {action.type}")
        for equation in scene.equations:
            if equation.motivated_by_object_id not in object_ids: raise ValueError(f"equation {equation.id} has no visual reference")
    return board

def teaching_quality_report(plan: LessonPlan, screenplay: Screenplay, board: Storyboard) -> dict:
    """Non-blocking structural checks that make lesson quality debuggable."""
    warnings: list[str] = []
    blocks = {block.id: block for block in screenplay.narration_blocks}
    meaningful = {"show_interaction", "show_force_pair", "show_motion_trace", "attach_quantity", "compare_states", "derive_equation", "transform_representation", "connect_objects", "show_before_after", "show_force", "show_equation"}
    covered = {blocks[block_id].concept_step_id for scene in board.scenes for block_id in scene.narration_block_ids if block_id in blocks and any(action.type in meaningful for action in scene.actions)}
    missing = [step.id for step in plan.conceptual_chain if step.importance == "core" and step.id not in covered]
    if missing: warnings.append(f"core concepts without a meaningful visual action: {', '.join(missing)}")
    prior_active: set[str] = set()
    camera_types = set()
    for scene in board.scenes:
        camera_types.add(scene.camera.type)
        if len(scene.active_objects) > 8 or len(scene.actions) > 10: warnings.append(f"{scene.id}: high visual density")
        if scene.duration_seconds and scene.duration_seconds > 0 and not scene.actions: warnings.append(f"{scene.id}: idle scene has no visual purpose")
        if prior_active and scene.active_objects and not prior_active & set(scene.active_objects) and scene.transition_to_next == "fade": warnings.append(f"{scene.id}: no persistent object bridges the scene transition")
        creates = [action.type for action in scene.actions]
        if len(creates) >= 3 and creates[:3] == ["create", "create", "create"]: warnings.append(f"{scene.id}: repeated create actions have no semantic progression")
        for equation in scene.equations:
            if not equation.motivated_by_object_id and not equation.previous_equation_id: warnings.append(f"{scene.id}: equation {equation.id} is not linked")
        prior_active = set(scene.active_objects)
    if len(board.scenes) > 1 and camera_types == {"none"}: warnings.append("lesson has no camera intent")
    return {"status": "ok" if not warnings else "warnings", "warnings": warnings, "metrics": {"scenes": len(board.scenes), "objects": len(board.objects), "semantic_actions": sum(action.type in meaningful for scene in board.scenes for action in scene.actions)}}
def validate_scene_code(code: str) -> str:
    tree = ast.parse(code, filename="scene.py")
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SceneTopic"]
    if len(classes) != 1 or not any(isinstance(n, ast.FunctionDef) and n.name == "construct" for n in classes[0].body): raise ValueError("code needs exactly one SceneTopic.construct")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if any(not any(name == allowed or name.startswith(allowed + ".") for allowed in ALLOWED_IMPORTS) for name in names): raise ValueError("generated code has a disallowed import")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in DANGEROUS: raise ValueError(f"generated code uses forbidden {node.func.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"): raise ValueError("generated code uses dunder attribute access")
    compile(tree, "scene.py", "exec")
    return code
