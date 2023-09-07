from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Position(BaseModel):
    x: int
    y: int


class ItemFrame(BaseModel):
    item_id: int = Field(alias="itemID")
    stack_size: int = Field(alias="stackSize")
    purchase_game_time: int = Field(alias="purchaseGameTime")
    cooldown_remaining: float = Field(alias="cooldownRemaining")
    

class StatsFrame(BaseModel):
    minions_killed: int = Field(alias="minionsKilled")
    neutral_minions_killed: float = Field(alias="neutralMinionsKilled")
    neutral_minions_killed_your_jungle: float = Field(alias="neutralMinionsKilledYourJungle")
    neutral_minions_killed_enemy_jungle: float = Field(alias="neutralMinionsKilledEnemyJungle")
    champions_killed: int = Field(alias="championsKilled")
    num_deaths: int = Field(alias="numDeaths")
    assists: int
    perks: list[dict]  # TODO : SHOULD DETAIL FRAME PERKS INFO
    ward_placed: int = Field(alias="wardPlaced")
    ward_killed: int = Field(alias="wardKilled")
    vision_score: float = Field(alias="visionScore")
    total_damage_dealt: float = Field(alias="totalDamageDealt")
    physical_damage_dealt_player: float = Field(alias="physicalDamageDealtPlayer")
    magic_damage_dealt_player: float = Field(alias="magicDamageDealtPlayer")
    true_damage_dealt_player: float = Field(alias="trueDamageDealtPlayer")
    total_damage_dealt_champions: float = Field(alias="totalDamageDealtChampions")
    physical_damage_dealt_champions: float = Field(alias="physicalDamageDealtChampions")
    magic_damage_dealt_champions: float = Field(alias="magicDamageDealtChampions")
    true_damage_dealt_champions: float = Field(alias="trueDamageDealtChampions")
    total_damage_taken: float = Field(alias="totalDamageTaken")
    physical_damage_taken: float = Field(alias="physicalDamageTaken")
    magic_damage_taken: float = Field(alias="magicDamageTaken")
    true_damage_taken: float = Field(alias="trueDamageTaken")
    total_damage_self_mitigated: float = Field(alias="totalDamageSelfMitigated")
    total_time_crowd_control_dealt: float = Field(alias="totalTimeCrowdControlDealt")
    total_heal_on_teammates: float = Field(alias="totalHealOnTeammates")
    total_time_cc_others: float = Field(alias="totalTimeCCOthers")
    total_damage_shielded_on_teammates: float = Field(alias="totalDamageShieldedOnTeammates")
    total_damage_dealt_to_buildings: float = Field(alias="totalDamageDealtToBuildings")
    total_damage_dealt_to_turrets: float = Field(alias="totalDamageDealtToTurrets")
    total_damage_dealt_to_objectives: float = Field(alias="totalDamageDealtToObjectives")


class SpellFrame(BaseModel):
    name: str
    cooldown_remaining: float = Field(alias="cooldownRemaining")


class PlayerFrame(BaseModel):
    urn: str = Field(alias="liveDataPlayerUrn")
    position: Position | None = None
    keystone_id: int | None = Field(default=None, alias="keystoneID")
    champion_id: int | None = Field(default=None, alias="championID")
    level: int | None = None
    experience: int | None = None
    attack_damage: int | None = Field(default=None, alias="attackDamage")
    attack_speed: int | None = Field(default=None, alias="attackSpeed")
    alive: bool | None = None
    respawn_timer: float | None = Field(default=None, alias="respawnTimer")
    health: int | None = None
    health_max: int | None = Field(default=None, alias="healthMax")
    health_regen: int | None = Field(default=None, alias="healthRegen")
    magic_resist: int | None = Field(default=None, alias="magicResist")
    magic_penetration: int | None = Field(default=None, alias="magicPenetration")
    magic_penetration_percent: int | None = Field(default=None, alias="magicPenetrationPercent")
    magic_penetration_percent_bonus: int | None = Field(default=None, alias="magicPenetrationPercentBonus")
    armor: int | None = None
    armor_penetration: int | None = Field(default=None, alias="armorPenetration")
    armor_penetration_percent: int | None = Field(default=None, alias="armorPenetrationPercent")
    armor_penetration_percent_bonus: int | None = Field(default=None, alias="armorPenetrationPercentBonus")
    ability_power: int | None = Field(default=None, alias="abilityPower")
    primary_ability_resource: int | None = Field(default=None, alias="primaryAbilityResource")
    primary_ability_resource_regen: int | None = Field(default=None, alias="primaryAbilityResourceRegen")
    primary_ability_resource_max: int | None = Field(default=None, alias="primaryAbilityResourceMax")
    current_gold: int | None = Field(default=None, alias="currentGold")
    total_gold: int | None = Field(default=None, alias="totalGold")
    gold_per_second: int | None = Field(default=None, alias="goldPerSecond")
    cc_reduction: int | None = Field(default=None, alias="ccReduction")
    cooldown_reduction: int | None = Field(default=None, alias="cooldownReduction")
    life_steal: int | None = Field(default=None, alias="lifeSteal")
    spell_vamp: int | None = Field(default=None, alias="spellVamp")
    items: list[ItemFrame] | None = None
    items_undo: list[dict] | None = Field(default=None, alias="itemsUndo")  # TODO : SHOULD DETAIL FRAME ITEM INFO
    items_sold: list[dict] | None = Field(default=None, alias="itemsSold")  # TODO : SHOULD DETAIL FRAME ITEM INFO
    stats: StatsFrame | None = None
    spell1: SpellFrame | None = None
    spell2: SpellFrame | None = None
    ultimate: SpellFrame | None = None

    # Allows population by classic name    
    model_config = ConfigDict(
        populate_by_name=True,
    )


class TeamFrame(BaseModel):
    urn: str = Field(alias="liveDataTeamUrn")
    assists: int
    baron_kills: int = Field(alias="baronKills")
    champions_kills: int = Field(alias="championsKills")
    deaths: int
    dragon_kills: int = Field(alias="dragonKills")
    inhib_kills: int = Field(alias="inhibKills")
    total_gold: int = Field(alias="totalGold")
    tower_kills: int = Field(alias="towerKills")
    killed_dragon_types: list[Literal["fire", "ocean", "earth", "air"]] = Field(alias="killedDragonTypes")  # TODO : Add other dragon types


class Frame(BaseModel):
    game_time: int
    players: list[PlayerFrame] = list()
    teams: list[TeamFrame] = list()
    

class Player(BaseModel):
    urn: str
    summoner_name: str | None = Field(default=None, alias="summonerName")
    champion_id: int = Field(default=None, alias="championId")


class Team(BaseModel):
    urn: str
    players: list[Player] | None = Field(default=None, alias="participants")


class Game(BaseModel):
    urn: str
    start_time: str | None = None
    teams: list[Team] | None = None

    frames: list[Frame] = Field(default=list())