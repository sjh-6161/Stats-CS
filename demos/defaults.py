from demoparser2 import DemoParser
from data import *
from collections import Counter
import json
from pandas import DataFrame

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

def parse(rounds: List[Round], demo_teams: dict, match_id: UUID, map_name: str, default_df: DataFrame):
    with open('place_names.json', 'r') as file:
        place_names = json.load(file)

    positions_df = default_df[default_df['is_warmup_period'] == False]

    # Group by round and player to aggregate zones across all sampled ticks
    # Key: (round_id, player_steamid) -> list of zones
    player_round_zones: dict[tuple, list] = {}
    player_round_info: dict[tuple, dict] = {}  # Store team info for each player/round

    for _, row in positions_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id is None or row['team_name'] is None:
            continue

        zone = get_zone(place_names, map_name, row['last_place_name'])

        # Skip ticks where the player is not in a valid zone
        if zone is None:
            continue

        key = (round_id, str(row['steamid']))

        if key not in player_round_zones:
            player_round_zones[key] = []
            player_round_info[key] = {
                'team_id': demo_teams[row['team_clan_name']],
                'side': row['team_name'],
            }

        player_round_zones[key].append(zone)

    defaults = []

    for (round_id, player_id), zones in player_round_zones.items():
        if not zones:
            continue

        # Find the most common zone
        most_common_zone = Counter(zones).most_common(1)[0][0]
        info = player_round_info[(round_id, player_id)]

        defaults.append(PlayerDefault(
            match_id=match_id,
            round_id=round_id,
            player_id=player_id,
            team_id=info['team_id'],
            side=info['side'],
            zone=most_common_zone,
        ))

    return defaults
