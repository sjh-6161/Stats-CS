from demoparser2 import DemoParser
from data import *

def parse(demo_teams: dict, match_id: UUID, parser: DemoParser):
    df = parser.parse_ticks(["team_clan_name", "team_rounds_total"])
    team_rounds_total = df["team_rounds_total"].to_list()
    team_clan_name = df["team_clan_name"].to_list()

    team_names = list(demo_teams.keys())
    team_rounds = {}

    team_rounds[team_names[0]] = 0
    team_rounds[team_names[1]] = 0

    for i in range(len(team_rounds_total)):
        if team_clan_name[i] is None or team_rounds_total[i] is None: continue
        
        if team_rounds_total[i] > team_rounds[team_clan_name[i]]:
            team_rounds[team_clan_name[i]] = team_rounds_total[i]

    basic_team_stats = []

    basic_team_stats.append(BasicTeamStats(
        team_id=demo_teams[team_names[0]],
        match_id=match_id,
        round_wins=team_rounds[team_names[0]],
        round_losses=team_rounds[team_names[1]],
    ))

    basic_team_stats.append(BasicTeamStats(
        team_id=demo_teams[team_names[1]],
        match_id=match_id,
        round_wins=team_rounds[team_names[1]],
        round_losses=team_rounds[team_names[0]],
    ))

    return basic_team_stats
