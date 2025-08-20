from demoparser2 import DemoParser
from data import *
from pandas import DataFrame

round_end_reasons = {
    0: "StillInProgress",
    1: "TargetBombed",
    2: "VIPEscaped",
    3: "VIPKilled",
    4: "TerroristsEscaped",
    5: "CTStoppedEscape",
    6: "TerroristsStopped",
    7: "BombDefused",
    8: "CTWin",
    9: "TerroristsWin",
    10: "Draw",
    11: "HostagesRescued",
    12: "TargetSaved",
    13: "HostagesNotRescued",
    14: "TerroristsNotEscaped",
    15: "VIPNotEscaped",
    16: "GameStart",
    17: "TerroristsSurrender",
    18: "CTSurrender",
    19: "TerroristsPlanted",
    20: "CTsReachedHostage",
}

def parse(demo_teams: dict, match_id: UUID, round_freeze_end_df: DataFrame, round_officially_ended_df: DataFrame, cs_win_panel_match_df: DataFrame):
    # freeze_time_end_df = parser.parse_event("round_freeze_end", other=["team_clan_name", "team_rounds_total", "round_win_reason", "round_in_progress", "is_warmup_period"])
    # round_end_df = parser.parse_event("round_officially_ended", other=["team_clan_name", "team_rounds_total", "round_win_reason", "round_in_progress"])
    # match_end_df = parser.parse_event("cs_win_panel_match", other=["team_clan_name", "team_rounds_total", "round_win_reason", "round_in_progress"])

    rounds: List[Round] = []

    parsed_ticks = []
    
    for _, row in round_freeze_end_df.iterrows():
        if row['tick'] in parsed_ticks or row['is_warmup_period']:
            continue

        parsed_ticks.append(row['tick'])

        rounds.append(Round(
            match_id=match_id,
            freeze_time_end_tick=row['tick'],
            end_official_tick=0,
            round_end_reason="",
            t_rounds=row['t_team_rounds_total'],
            ct_rounds=row['ct_team_rounds_total'],
            t_team_id=demo_teams[row['t_team_clan_name']],
            ct_team_id=demo_teams[row['ct_team_clan_name']],
            winning_side="",
            winning_team_id=UUID,
            losing_side="",
            losing_team_id=UUID,
        ))

    for _, row in round_officially_ended_df.iterrows():
        for i in range(len(rounds)):
            if row['tick'] > rounds[i].freeze_time_end_tick and rounds[i].end_official_tick == 0:
                rounds[i].end_official_tick = row['tick']
                rounds[i].round_end_reason = round_end_reasons[row['round_win_reason']]

                # If CTs won the round
                if row['ct_team_rounds_total'] > rounds[i].ct_rounds:
                    rounds[i].winning_side = "CT"
                    rounds[i].losing_side = "C"

                    rounds[i].winning_team_id = rounds[i].ct_team_id
                    rounds[i].losing_team_id = rounds[i].t_team_id
                # If Ts won the round
                else:
                    rounds[i].winning_side = "T"
                    rounds[i].losing_side = "CT"

                    rounds[i].winning_team_id = rounds[i].t_team_id
                    rounds[i].losing_team_id = rounds[i].ct_team_id

                break

              
    if len(cs_win_panel_match_df) > 0:
        for _, row in cs_win_panel_match_df.iterrows():
            for i in range(len(rounds)):
                if row['tick'] > rounds[i].freeze_time_end_tick and rounds[i].end_official_tick == 0:
                    rounds[i].end_official_tick = row['tick']
                    rounds[i].round_end_reason = round_end_reasons[row['round_win_reason']]

                    # If CTs won the round
                    if row['ct_team_rounds_total'] > rounds[i].ct_rounds:
                        rounds[i].winning_side = "CT"
                        rounds[i].losing_side = "T"

                        rounds[i].winning_team_id = rounds[i].ct_team_id
                        rounds[i].losing_team_id = rounds[i].t_team_id
                    # If Ts won the round
                    else:
                        rounds[i].winning_side = "T"
                        rounds[i].losing_side = "CT"

                        rounds[i].winning_team_id = rounds[i].t_team_id
                        rounds[i].losing_team_id = rounds[i].ct_team_id

    return rounds

    