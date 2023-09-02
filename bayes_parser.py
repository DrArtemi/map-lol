from enum import Enum
import io
import json
import plotly.express as px
import pandas as pd
from PIL import Image
from pathlib import Path
from bayes_models import Frame, Game, Position, Team


class Action(Enum):
    KILLED_WARD = 'KILLED_WARD'
    UPDATE = 'UPDATE'
    UNDO_ITEM = 'UNDO_ITEM'
    KILLED_ANCIENT = 'KILLED_ANCIENT'  # TODO: Verify what ancient means
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
        
        self.data = [json.load(open(files[f"{i}.json"], "r")) for i in range(1, len(files) - 1)]
        self.game = self.init_game()
        self.parse_positions()
    
    def init_game(self) -> Game:
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
        position_data = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.UPDATE_POSITIONS.value]
        
        for frame in position_data:
            for p in frame["positions"]:
                player = [player for t in self.game.teams if t.urn == p["teamUrn"] for player in t.players if player.urn == p["playerUrn"]][0]
                player.frames.append(
                    Frame(
                        game_time=int(frame["gameTime"] / 1000),
                        position=Position(x=p["position"][0], y=p["position"][1])
                    )
                )
    
    def get_teams_stats(self) -> None:
        a = [d["payload"]["payload"]["payload"] for d in self.data if d["payload"]["payload"]["action"] == Action.UPDATE.value]
        breakpoint()

    def position_map(self, gif_path: Path = None) -> None:    
        d = {
            "game_time": [f.game_time for t in self.game.teams for p in t.players for f in p.frames],
            "x": [f.position.x for t in self.game.teams for p in t.players for f in p.frames],
            "y": [f.position.y for t in self.game.teams for p in t.players for f in p.frames],
            "player": [p.summoner_name for t in self.game.teams for p in t.players for _ in p.frames],
            "team": [t.urn for t in self.game.teams for p in t.players for _ in p.frames],
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