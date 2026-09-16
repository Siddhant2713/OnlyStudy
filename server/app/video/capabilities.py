"""Machine-readable semantic renderer contract, available without importing Manim."""

CAPABILITIES = {
    "objects": ["physics_body", "wheel", "bicycle", "force_arrow", "velocity_arrow", "equation", "label", "coordinate_system", "graph", "array", "node"],
    "actions": ["introduce_object", "show_interaction", "show_force_pair", "show_motion_trace", "attach_quantity", "compare_states", "derive_equation", "substitute_value", "transform_representation", "connect_objects", "highlight_relation", "show_before_after", "split_vector", "compose_vectors"],
    "camera": ["focus_on", "follow", "zoom_to_relation", "show_context", "pull_back", "move_with", "compare"],
}

def capability_catalog() -> dict[str, list[str]]:
    return {name: list(values) for name, values in CAPABILITIES.items()}
