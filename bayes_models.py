from pydantic import BaseModel, Field


class Position(BaseModel):
    x: int
    y: int


class Frame(BaseModel):
    game_time: int
    position: Position | None = None


class Player(BaseModel):
    urn: str
    summoner_name: str | None = Field(default=None, alias="summonerName")
    champion_id: int = Field(default=None, alias="championId")
    
    frames: list[Frame] = Field(default=list())


class Team(BaseModel):
    urn: str
    players: list[Player] | None = Field(default=None, alias="participants")


class Game(BaseModel):
    urn: str
    start_time: str | None = None
    teams: list[Team] | None = None
