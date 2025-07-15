from demoparser2 import DemoParser
from data import *
import json

def parse(rounds: List[Round], demo_teams: dict, match_id: UUID, map_name: str, parser: DemoParser):
    with open('place_names.json', 'r') as file:
        place_names = json.load(file)

    wanted_ticks = []

    for r in rounds:
        wanted_ticks.append(r.freeze_time_end_tick + 12 * 64)

    positions_df = parser.parse_ticks(ticks=wanted_ticks, wanted_props=['last_place_name', 'team_name', 'team_clan_name', 'is_warmup_period']).sort_values(by='tick')
    positions_df = positions_df[positions_df['is_warmup_period'] == False]

    current_defaults = {"CT": {"A": 0, "Mid": 0, "B": 0, "Team": ""}, "TERRORIST": {"A": 0, "Mid": 0, "B": 0, "Team": ""}}

    current_tick = -1

    defaults = []

    round_id = None

    for _, row in positions_df.iterrows():
        if current_tick == -1: current_tick = row['tick']

        if row['tick'] != current_tick:
            current_tick = row['tick']

            for side in ["CT", "TERRORIST"]:
                defaults.append(TeamDefault(
                    match_id=match_id,
                    round_id=round_id,
                    team_id=demo_teams[current_defaults[side]["Team"]],
                    side=side,
                    num_a=current_defaults[side]["A"],
                    num_b=current_defaults[side]["B"],
                    num_mid=current_defaults[side]["Mid"],
                ))
            
            current_defaults = {"CT": {"A": 0, "Mid": 0, "B": 0, "Team": ""}, "TERRORIST": {"A": 0, "Mid": 0, "B": 0, "Team": ""}}

        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None or row['team_name'] == None: continue

        if current_tick == -1: current_tick = row['tick']

        if current_defaults[row['team_name']]["Team"] == "":
            current_defaults[row['team_name']]["Team"] = row['team_clan_name']

        side = place_names[map_name][row['last_place_name']]

        if side == "None": continue

        current_defaults[row['team_name']][side] += 1

    for side in ["CT", "TERRORIST"]:
        defaults.append(TeamDefault(
            match_id=match_id,
            round_id=round_id,
            team_id=demo_teams[current_defaults[side]["Team"]],
            side=side,
            num_a=current_defaults[side]["A"],
            num_b=current_defaults[side]["B"],
            num_mid=current_defaults[side]["Mid"],
        ))

    return defaults
