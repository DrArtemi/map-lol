from typing import Literal
from pydantic import BaseModel, Field


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
    neutral_minions_killed: int = Field(alias="neutralMinionsKilled")
    neutral_minions_killed_your_jungle: int = Field(alias="neutralMinionsKilledYourJungle")
    neutral_minions_killed_enemy_jungle: int = Field(alias="neutralMinionsKilledEnemyJungle")
    champions_killed: int = Field(alias="championsKilled")
    num_deaths: int = Field(alias="numDeaths")
    assists: int
    perks: list[dict]  # TODO : SHOULD DETAIL FRAME PERKS INFO
    ward_placed: int = Field(alias="wardPlaced")
    ward_killed: int = Field(alias="wardKilled")
    vision_score: float = Field(alias="visionScore")
    total_damage_delt: float = Field(alias="totalDamageDelt")
    physical_damage_delt_player: float = Field(alias="physicalDamageDeltPlayer")
    magic_damage_delt_player: float = Field(alias="magicDamageDeltPlayer")
    true_damage_delt_player: float = Field(alias="truDamageDeltPlayer")
    total_damage_delt_champions: float = Field(alias="totalDamageDeltChampions")
    physical_damage_delt_champions: float = Field(alias="physicalDamageDeltChampions")
    magic_damage_delt_champions: float = Field(alias="magicDamageDeltChampions")
    true_damage_delt_champions: float = Field(alias="trueDamageDeltChampions")
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
    keystone_id: int = Field(alias="keystoneID")
    champion_id: int = Field(alias="championID")
    level: int
    experience: int
    attack_damage: int = Field(alias="attackDamage")
    attack_speed: int = Field(alias="attackSpeed")
    alive: bool
    respawn_timer: int = Field(alias="respawnTimer")
    health: int
    health_max: int = Field(alias="healthMax")
    health_regen: int = Field(alias="healthRegen")
    magic_resist: int = Field(alias="magicResist")
    magic_penetration: int = Field(alias="magicPenetration")
    magic_penetration_percent: int = Field(alias="magicPenetrationPercent")
    magic_penetration_percent_bonus: int = Field(alias="magicPenetrationPercentBonus")
    armor: int
    armor_penetration: int = Field(alias="armorPenetration")
    armor_penetration_percent: int = Field(alias="armorPenetrationPercent")
    armor_penetration_percent_bonus: int = Field(alias="armorPenetrationPercentBonus")
    ability_power: int = Field(alias="abilityPower")
    primary_ability_resource: int = Field(alias="primaryAbilityResource")
    primary_ability_resource_regen: int = Field(alias="primaryAbilityResourceRegen")
    primary_ability_resource_max: int = Field(alias="primaryAbilityResourceMax")
    current_gold: int = Field(alias="currentGold")
    total_gold: int = Field(alias="totalGold")
    gold_per_second: int = Field(alias="goldPerSecond")
    cc_reduction: int = Field(alias="ccReduction")
    cooldown_reduction: int = Field(alias="cooldownReduction")
    life_steal: int = Field(alias="lifeSteal")
    spell_vamp: int = Field(alias="spellVamp")
    items: list[ItemFrame]
    items_undo: list[dict] = Field(alias="itemsUndo")  # TODO : SHOULD DETAIL FRAME ITEM INFO
    items_sold: list[dict] = Field(alias="itemsSold")  # TODO : SHOULD DETAIL FRAME ITEM INFO
    stats: StatsFrame
    spell1: SpellFrame
    spell2: SpellFrame
    ultimate: SpellFrame


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
    
    players: list[PlayerFrame] | None = None
    teams: list[TeamFrame] | None = None    
    

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