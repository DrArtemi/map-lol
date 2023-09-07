from pydantic import BaseModel


class TeamResults(BaseModel):
    win: bool = False
    kda: float = 0
    first_turret: bool = False
    first_rift_herald: bool = False
    first_dragon: bool = False
    first_baron: bool = False
    first_inhib: bool = False
    rift_herald_kills: int = 0
    dragon_kills: int = 0
    baron_kills: int = 0
    tower_kills: int = 0
    inhib_kills: int = 0
    plates: int = 0
    first_blood: bool = False
    gold_diff_10: int = 0
    gold_diff_15: int = 0
    gold_diff_20: int = 0
    gold_diff_end: int = 0