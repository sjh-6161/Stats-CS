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

    # Reverse lookup: team_id -> clan_name
    team_id_to_clan = {v: k for k, v in demo_teams.items()}

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

                # Check if sides swapped by comparing clan names
                round_start_ct_clan = team_id_to_clan[rounds[i].ct_team_id]
                sides_swapped = row['ct_team_clan_name'] != round_start_ct_clan

                if not sides_swapped:
                    # No swap: use end event values directly
                    if row['ct_team_rounds_total'] > rounds[i].ct_rounds:
                        rounds[i].winning_side = "CT"
                        rounds[i].losing_side = "T"
                        rounds[i].winning_team_id = rounds[i].ct_team_id
                        rounds[i].losing_team_id = rounds[i].t_team_id
                    else:
                        rounds[i].winning_side = "T"
                        rounds[i].losing_side = "CT"
                        rounds[i].winning_team_id = rounds[i].t_team_id
                        rounds[i].losing_team_id = rounds[i].ct_team_id
                else:
                    # Sides swapped: end event CT was our T, end event T was our CT
                    if row['t_team_rounds_total'] > rounds[i].ct_rounds:
                        rounds[i].winning_side = "CT"
                        rounds[i].losing_side = "T"
                        rounds[i].winning_team_id = rounds[i].ct_team_id
                        rounds[i].losing_team_id = rounds[i].t_team_id
                    else:
                        rounds[i].winning_side = "T"
                        rounds[i].losing_side = "CT"
                        rounds[i].winning_team_id = rounds[i].t_team_id
                        rounds[i].losing_team_id = rounds[i].ct_team_id

                break

              
    if cs_win_panel_match_df is not None and len(cs_win_panel_match_df) > 0:
        for _, row in cs_win_panel_match_df.iterrows():
            for i in range(len(rounds)):
                if row['tick'] > rounds[i].freeze_time_end_tick and rounds[i].end_official_tick == 0:
                    rounds[i].end_official_tick = row['tick']
                    rounds[i].round_end_reason = round_end_reasons[row['round_win_reason']]

                    # Check if sides swapped by comparing clan names
                    round_start_ct_clan = team_id_to_clan[rounds[i].ct_team_id]
                    sides_swapped = row['ct_team_clan_name'] != round_start_ct_clan

                    if not sides_swapped:
                        # No swap: use end event values directly
                        if row['ct_team_rounds_total'] > rounds[i].ct_rounds:
                            rounds[i].winning_side = "CT"
                            rounds[i].losing_side = "T"
                            rounds[i].winning_team_id = rounds[i].ct_team_id
                            rounds[i].losing_team_id = rounds[i].t_team_id
                        else:
                            rounds[i].winning_side = "T"
                            rounds[i].losing_side = "CT"
                            rounds[i].winning_team_id = rounds[i].t_team_id
                            rounds[i].losing_team_id = rounds[i].ct_team_id
                    else:
                        # Sides swapped: end event CT was our T, end event T was our CT
                        if row['t_team_rounds_total'] > rounds[i].ct_rounds:
                            rounds[i].winning_side = "CT"
                            rounds[i].losing_side = "T"
                            rounds[i].winning_team_id = rounds[i].ct_team_id
                            rounds[i].losing_team_id = rounds[i].t_team_id
                        else:
                            rounds[i].winning_side = "T"
                            rounds[i].losing_side = "CT"
                            rounds[i].winning_team_id = rounds[i].t_team_id
                            rounds[i].losing_team_id = rounds[i].ct_team_id

    # Post-process: verify winners using next round's starting scores
    # The freeze_end event scores are reliable, while round_end event scores may be stale
    for i in range(len(rounds) - 1):
        curr = rounds[i]
        next_round = rounds[i + 1]

        # Get each team's round count at start of current and next round
        # Account for potential side swap between rounds
        if curr.ct_team_id == next_round.ct_team_id:
            # No swap: same team is CT in both rounds
            curr_ct_team_next_rounds = next_round.ct_rounds
            curr_t_team_next_rounds = next_round.t_rounds
        else:
            # Sides swapped: curr CT is now T, curr T is now CT
            curr_ct_team_next_rounds = next_round.t_rounds
            curr_t_team_next_rounds = next_round.ct_rounds

        # Determine winner by who gained a round
        ct_gained = curr_ct_team_next_rounds - curr.ct_rounds
        t_gained = curr_t_team_next_rounds - curr.t_rounds

        if ct_gained == 1 and t_gained == 0:
            curr.winning_side = "CT"
            curr.losing_side = "T"
            curr.winning_team_id = curr.ct_team_id
            curr.losing_team_id = curr.t_team_id
        elif t_gained == 1 and ct_gained == 0:
            curr.winning_side = "T"
            curr.losing_side = "CT"
            curr.winning_team_id = curr.t_team_id
            curr.losing_team_id = curr.ct_team_id

    return rounds

    