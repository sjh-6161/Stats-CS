from demoparser2 import DemoParser
from data import *

BOMB_ZONES = {
    1: "A",
    2: "B"
}

def parse(rounds: List[Round], match_id: UUID, parser: DemoParser):
    bomb_plant_events = parser.parse_event("bomb_planted", player=["X", "Y", "Z", "which_bomb_zone"])

    plants = []

    for _, row in bomb_plant_events.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        plants.append(Plant(
            match_id=match_id,
            round_id=round_id,
            tick=row['tick'],
            site=BOMB_ZONES[row['user_which_bomb_zone']],
            x=row['user_X'],
            y=row['user_Y'],
            z=row['user_Z'],
        ))

    return plants