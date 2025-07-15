from demoparser2 import DemoParser
from data import *

# SELECT player.name, CAST(SUM(kills) as float)/SUM(deaths) as kd, CAST(SUM(kills) as float)/SUM(rounds) as kr, CAST(SUM(damage) as float)/SUM(rounds) as adr
# FROM basic_player_stats
# INNER JOIN player on player.id = player_id
# GROUP BY player.name
# ORDER BY kd

def parse(demo_players: dict, demo_teams: dict, match_id: UUID, parser: DemoParser):
    num_rounds = len(parser.parse_event("round_freeze_end").index)

    player_stats = {}

    hurts = parser.parse_event("player_hurt", player=["team_clan_name"])

    # Handle damage
    for _, row in hurts.iterrows():
        if row["attacker_steamid"] is None: continue

        if row["attacker_steamid"] not in player_stats.keys():
            player_stats[row["attacker_steamid"]] = {
                "team_id": demo_teams[row["attacker_team_clan_name"]],
                "kills": 0,
                "deaths": 0, 
                "assists": 0,
                "damage": 0
            }

        player_stats[row["attacker_steamid"]]["damage"] += row["dmg_health"]

    deaths = parser.parse_event("player_death", player=["team_clan_name"])
    

    # Handle kills deaths and assists
    for _, row in deaths.iterrows():
        if row["attacker_steamid"] is not None and row["attacker_steamid"] not in player_stats.keys():
            player_stats[row["attacker_steamid"]] = {
                "team_id": demo_teams[row["attacker_team_clan_name"]],
                "kills": 0,
                "deaths": 0, 
                "assists": 0,
                "damage": 0
            }

        if row["attacker_steamid"] is not None:
            player_stats[row["attacker_steamid"]]["kills"] += 1

        if row["assister_steamid"] is not None and row["assister_steamid"] not in player_stats.keys():
            player_stats[row["assister_steamid"]] = {
                "team_id": demo_teams[row["assister_team_clan_name"]],
                "kills": 0,
                "deaths": 0, 
                "assists": 0,
                "damage": 0
            }

        if row["assister_steamid"] is not None:
            player_stats[row["assister_steamid"]]["assists"] += 1

        if row["user_steamid"] is not None and row["user_steamid"] not in player_stats.keys():
            player_stats[row["user_steamid"]] = {
                "team_id": demo_teams[row["user_team_clan_name"]],
                "kills": 0,
                "deaths": 0, 
                "assists": 0,
                "damage": 0
            }

        if row["user_steamid"] is not None:
            player_stats[row["user_steamid"]]["deaths"] += 1

    basic_player_stats = []
    
    for player in player_stats.keys():
        basic_player_stats.append(BasicPlayerStats(
            rounds=num_rounds,
            player_id=demo_players[player],
            team_id=player_stats[player]["team_id"],
            match_id=match_id,
            kills=player_stats[player]["kills"],
            deaths=player_stats[player]["deaths"],
            assists=player_stats[player]["assists"],
            damage=player_stats[player]["damage"]
        ))

    return basic_player_stats
