from demoparser2 import DemoParser
import os

def get_demo_bomb_plant_times(demo_file: str, teams: dict):
    parser = DemoParser(demo_file)

    freeze_end_ticks = parser.parse_event("round_freeze_end")['tick'].to_list()

    bomb_plant_events = parser.parse_event("bomb_planted", player=["team_clan_name"])

    for _, row in bomb_plant_events.iterrows():

        bomb_plant_tick = row['tick']

        freeze_end_tick = 0

        for i in range(len(freeze_end_ticks)):
            if bomb_plant_tick > freeze_end_ticks[i]:
                freeze_end_tick = freeze_end_ticks[i]

        if freeze_end_tick == 0: 
            continue

        if row['t_team_clan_name'] not in teams.keys():
            teams[row['t_team_clan_name']] = {'plants': 0, 'ticks': 0}

        teams[row['t_team_clan_name']]['plants'] += 1
        teams[row['t_team_clan_name']]['ticks'] += bomb_plant_tick - freeze_end_tick

    return teams


def get_many_demo_bomb_plant_times(folder_path: str):
    teams = {}

    files = os.listdir(folder_path)

    for file in files:
        teams = get_demo_bomb_plant_times(folder_path + "/" + file, teams)

    return teams


