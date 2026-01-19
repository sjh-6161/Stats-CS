from demoparser2 import DemoParser
from data import *
from pandas import DataFrame
import json

def get_zone(place_names: dict, map_name: str, last_place_name: str) -> str:
    """Get the zone for a place name, returning None if not found or if zone is 'None'."""
    if not last_place_name or last_place_name == '':
        return None

    if map_name not in place_names:
        return None

    if last_place_name not in place_names[map_name]:
        return None

    zone = place_names[map_name][last_place_name]

    if zone == "None":
        return None

    return zone

def parse(rounds: List[Round], match_id: UUID, map_name: str, weapon_fire_df: DataFrame):
    # fires_df = parser.parse_event(event_name='weapon_fire', player=['team_name', 'X', 'Y', 'Z', 'pitch', 'yaw'])

    with open('place_names.json', 'r') as file:
        place_names = json.load(file)

    weapon_fires = []

    for _, row in weapon_fire_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        attacker_zone = get_zone(place_names, map_name, row['user_last_place_name'])

        weapon_fires.append(WeaponFire(
            match_id=match_id,
            round_id=round_id,
            attacker_id=row['user_steamid'],
            attacker_x=row['user_X'],
            attacker_y=row['user_Y'],
            attacker_z=row['user_Z'],
            attacker_zone=attacker_zone,
            attacker_pitch=row['user_pitch'],
            attacker_yaw=row['user_yaw'],
            attacker_team=row['user_team_name'],
            tick=row['tick'],
            weapon=row['weapon'],
            silenced=row['silenced'],
        ))

    return weapon_fires
