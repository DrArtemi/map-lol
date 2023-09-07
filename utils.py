from bayes_models import Frame


def get_first_frame_at_time(frames: list[Frame], frame_time: int) -> Frame | None:    
    frame = [f for f in frames if f.game_time >= frame_time]
    if len(frame) == 0:
        return None
    return frame[0]


def get_first_team_objective(frames: list[dict], objective_type: str, objective_name: str) -> str | None:
    frame = [f for f in frames if f.get(objective_type, "") == objective_name]
    if len(frame) == 0:
        return None
    return frame[0].get("killerTeamUrn")