from app.video.schema import Storyboard, Screenplay
def normalize_storyboard_timing(board: Storyboard, screenplay: Screenplay, durations: dict[str, float]) -> Storyboard:
    for scene in board.scenes:
        audio = sum(durations.get(block_id, 0) for block_id in scene.narration_block_ids)
        if scene.duration_policy == "audio_locked": scene.duration_seconds = max(1.0, audio)
        elif scene.duration_policy == "hybrid": scene.duration_seconds = max(scene.duration_seconds or 1.0, audio)
    return board
