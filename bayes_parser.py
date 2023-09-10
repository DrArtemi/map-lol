from enum import Enum
import io
import json
import plotly.express as px
import pandas as pd
from PIL import Image
from pathlib import Path
from bayes_models import Frame, Game, PlayerFrame, Position, Team, TeamFrame
from results_models import TeamResults
from utils import get_first_frame_at_time, get_first_team_objective

"""
IDEAS :
- Gold curves
- Baron efficienty (+ gold, towers, inhibs, drakes, kills, ...)
"""


class Action(Enum):
    KILLED_WARD = 'KILLED_WARD'
    UPDATE = 'UPDATE'
    UNDO_ITEM = 'UNDO_ITEM'
    KILLED_ANCIENT = 'KILLED_ANCIENT'  # Ancient = all camps + krug + baron + rift + dragon
    CONSUMED_ITEM = 'CONSUMED_ITEM'
    PLACED_WARD = 'PLACED_WARD'
    EXPIRED_OBJECTIVE = 'EXPIRED_OBJECTIVE'  # TODO: Verify what this means (herald not used ? Baron buff finished ?)
    SOLD_ITEM = 'SOLD_ITEM'
    START_MAP = 'START_MAP'
    KILL = 'KILL'
    SPAWNED_ANCIENT = 'SPAWNED_ANCIENT'  # TODO: Verify what ancient means
    SELECTED_HERO = 'SELECTED_HERO'
    TOOK_OBJECTIVE = 'TOOK_OBJECTIVE'  # TODO: Verify what objective means (turret, inib, drake, baron, herald ?)
    SPECIAL_KILL = 'SPECIAL_KILL'  # TODO: Check what special stands for
    BANNED_HERO = 'BANNED_HERO'
    END_PAUSE = 'END_PAUSE'
    PURCHASED_ITEM = 'PURCHASED_ITEM'
    UPDATE_SCORE = 'UPDATE_SCORE'  # TODO: Verify what this is
    DIED = 'DIED'
    PICKED_UP_ITEM = 'PICKED_UP_ITEM'
    ANNOUNCE = 'ANNOUNCE'
    SPAWNED = 'SPAWNED'
    UPDATE_POSITIONS = 'UPDATE_POSITIONS'
    LEVEL_UP = 'LEVEL_UP'
    ANNOUNCED_ANCIENT = 'ANNOUNCED_ANCIENT'  # TODO: Verify what ancient means


class BayesParser:
    
    def __init__(self, directory: Path) -> None:
        files = {f.name: f for f in directory.iterdir() if f.is_file()}
        
        self.data = [json.load(open(files[f"{i}".zfill(6) + ".json"], "r")) for i in range(1, len(files) - 1)]
        self.game = self.init_game()

        # Init frames with the positions (every 1sec)
        self.parse_positions()
        # Parse stats and complete frames
        self.parse_stats()
    
    def init_game(self) -> Game:
        """ Initialize game model with basic information about game, teams and players.
        """
        # Retreive game announce
        game_announce = [d["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.ANNOUNCE.value]
        assert len(game_announce) > 0, "Could not find game announce in the loaded data."
        game_announce = game_announce[0]
        
        # Iniitalize game object
        game = Game(urn=game_announce["urn"])
        
        # Fill additional information
        game_information = game_announce["payload"]["payload"]["fixture"]
        game.start_time = game_information["startTime"]
        
        # Initialize teams objects
        teams_information = game_announce["payload"]["payload"]["teams"]
        teams = [Team(**t) for t in teams_information]
        game.teams = teams
        
        return game
    
    def parse_positions(self) -> None:
        """Parse players positions. Positions are logged every second.
        This method initialize our frames models. (That's dirty).
        """
        position_data = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.UPDATE_POSITIONS.value]
        
        for frame in position_data:
            frame_info = Frame(game_time=int(frame.get("gameTime", -1000) / 1000))
            for p in frame["positions"]:
                frame_info.players.append(PlayerFrame(
                    urn=p["playerUrn"],
                    position=Position(x=p["position"][0], y=p["position"][1])
                ))
            self.game.frames.append(frame_info)
    
    def parse_stats(self) -> None:
        """Parse statistics from teams and players. Note that this stats are only logged every 5 seconds.
        """
        score_updates = [
            d["payload"]["payload"]["payload"]
            for d in self.data
            if d["payload"]["payload"]["action"] == Action.UPDATE.value and
            "gameTime" in d["payload"]["payload"]["payload"]  # Could do this with other field, maybe gameState set to POST_CHAMP_SELECT
        ]
        for frame in score_updates:
            gt = int(frame["gameTime"] / 1000)
            frame_update = [f for f in self.game.frames if f.game_time == gt]
            
            # FIXME : HACKY AS FUCK BUT PLEASE WHY WOULD YOU NOT BE CONSTANT ON GAME TIME
            while len(frame_update) == 0 and gt < len(self.game.frames):
                # Big chance we skipped a second on position frames
                gt += 1
                frame_update = [f for f in self.game.frames if f.game_time == gt]
            frame_update = frame_update[0]
            
            for team in ["teamOne", "teamTwo"]:
                frame_update.teams.append(TeamFrame(**frame[team]))
                for player in frame[team]["players"]:
                    player_update_idx = [i for i, p in enumerate(frame_update.players) if p.urn == player["liveDataPlayerUrn"]]
                    assert len(player_update_idx) == 1, f"Could not find a player matching urn {player['liveDataPlayerUrn']}"
                    player_update_idx = player_update_idx[0]
                    del player["position"]  # Delete position as it is already set
                    frame_update.players[player_update_idx] = PlayerFrame(**player)

    def get_teams_stats(self) -> dict:
        """Gather some team statistics
        Can improved a lot but well it's a POC

        Returns:
            pd.DataFrame: Dataframe of team statistics
        """
        # Get only stats frames with relevent data logged
        frames = [f for f in self.game.frames if len(f.teams) > 0]
        stats = dict()
        
        # Get 10, 15 and 20 minutes frames
        frame_10 = get_first_frame_at_time(frames, 10 * 60)
        frame_15 = get_first_frame_at_time(frames, 15 * 60)
        frame_20 = get_first_frame_at_time(frames, 20 * 60)
        
        # First events
        ancient_frames = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.KILLED_ANCIENT.value]
        first_baron = get_first_team_objective(ancient_frames, "monsterType", "baron")
        first_dragon = get_first_team_objective(ancient_frames, "monsterType", "dragon")
        first_rift_herald = get_first_team_objective(ancient_frames, "monsterType", "riftHerald")
        objective_frames = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.TOOK_OBJECTIVE.value]
        first_turret = get_first_team_objective(objective_frames, "buildingType", "turret")
        first_inhibitor = get_first_team_objective(objective_frames, "buildingType", "turret")
        objective_frames = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.SPECIAL_KILL.value]
        first_blood = get_first_team_objective(objective_frames, "killType", "firstBlood")
                
        for i, team in enumerate(frames[-1].teams):
            final_gold_diff = team.total_gold - frames[-1].teams[0 if i == 1 else 1].total_gold
            stats[team.urn] = TeamResults(
                kda=round((team.champions_kills + team.assists) / max(1, team.deaths), 1),
                rift_herald_kills=len([f for f in ancient_frames if f.get("monsterType", "") == "riftHerald" and f.get("killerTeamUrn", "") == team.urn]),
                dragon_kills=team.dragon_kills,
                baron_kills=team.baron_kills,
                tower_kills=team.tower_kills,
                inhib_kills=team.inhib_kills,
                plates=len([f for f in objective_frames if f.get("buildingType", "") == "turretPlate" and f.get("killerTeamUrn", "") == team.urn]),
                first_blood=first_blood == team.urn,
                gold_diff_10=frame_10.teams[i].total_gold - frame_10.teams[0 if i == 1 else 1].total_gold if frame_10 is not None else final_gold_diff,
                gold_diff_15=frame_15.teams[i].total_gold - frame_15.teams[0 if i == 1 else 1].total_gold if frame_15 is not None else final_gold_diff,
                gold_diff_20=frame_20.teams[i].total_gold - frame_20.teams[0 if i == 1 else 1].total_gold if frame_20 is not None else final_gold_diff,
                gold_diff_end=final_gold_diff,
                first_rift_herald=first_rift_herald == team.urn,
                first_dragon=first_dragon == team.urn,
                first_baron=first_baron == team.urn,
                first_turret=first_turret == team.urn,
                first_inhibitor=first_inhibitor == team.urn,
            )
        # FIXME : How can I know who wins
        return stats

    def position_map(self, gif_path: Path = None) -> None:    
        """Generates an animation of players moving on a map during game.

        Args:
            gif_path (Path, optional): Path where a GIF of the animation should be saved.
            If None, no GIF is saved. Defaults to None.
        """
        player_info = {p.urn: {"team": t.urn, "name": p.summoner_name} for t in self.game.teams for p in t.players}
        d = {
            "game_time": [f.game_time for f in self.game.frames for p in f.players if p.position is not None],
            "x": [p.position.x for f in self.game.frames for p in f.players if p.position is not None],
            "y": [p.position.y for f in self.game.frames for p in f.players if p.position is not None],
            "player": [player_info[p.urn]["name"] for f in self.game.frames for p in f.players if p.position is not None],
            "team": [player_info[p.urn]["team"] for f in self.game.frames for p in f.players if p.position is not None],
        }
        
        df = pd.DataFrame(data=d)
            
        fig = px.scatter(
            df,
            x="x",
            y="y",
            animation_frame="game_time",
            animation_group="player",
            color="team",
            hover_name="player",
            range_x=[-1000, 16000],
            range_y=[-1000, 16000],
            width=900, height=900,
        )
        
        fig.update_traces(
            marker=dict(
                size=30,
                line=dict(
                    width=2,
                    color='DarkSlateGrey'
                )
            ),
            selector=dict(mode='markers')
        )
        fig.update_layout(showlegend=False)
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 30
        fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5

        im = Image.open("map_lol.png")
        fig.update_layout(
            images= [dict(
                source=im,
                xref="paper", yref="paper",
                x=0, y=1,
                sizex=1, sizey=1,
                xanchor="left",
                yanchor="top",
                sizing="stretch",
                opacity=0.7,
                layer="below")]
        )
        
        if gif_path:
            # generate images for each step in animation
            frames = []
            for s, fr in enumerate(fig.frames):
                # set main traces to appropriate traces within plotly frame
                fig.update(data=fr.data)
                # move slider to correct place
                fig.layout.sliders[0].update(active=s)
                # generate image of current state
                frames.append(Image.open(io.BytesIO(fig.to_image(format="png"))))
                
            # create animated GIF
            frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    optimize=True,
                    duration=50,
                    loop=0,
                )
        else:
            fig.show()