from demoparser2 import DemoParser
from data import *
from pandas import DataFrame

def parse(rounds: List[Round], demo_teams: dict,  match_id: UUID, freeze_time_end_df: DataFrame):
    # ticks = parser.parse_event("round_freeze_end")["tick"].to_list()

    # df = parser.parse_ticks(["current_equip_value", "balance", 'team_clan_name', 'team_name'], ticks=ticks)

    buys = []

    for _, row in freeze_time_end_df.iterrows():
        round_id = ""

        for round in rounds:
            if round.freeze_time_end_tick == row["tick"]:
                round_id = round.id

                break

        if round_id == ""  or row['team_clan_name'] == None:
            continue

        buys.append(Buy(
            player_id=str(row['steamid']),
            round_id=round_id,
            match_id=match_id,
            team_id=demo_teams[row['team_clan_name']],
            side=row['team_name'],
            equipment_value=row['current_equip_value'],
            balance=row['balance']
        ))
    
    return buys