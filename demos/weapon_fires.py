from demoparser2 import DemoParser
from data import *

def parse(rounds: List[Round], match_id: UUID, parser: DemoParser):
    fires_df = parser.parse_event(event_name='weapon_fire', player=['team_name'])

    weapon_fires = []

    for _, row in fires_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        weapon_fires.append(WeaponFire(
            match_id=match_id,
            round_id=round_id,
            attacker_id=row['user_steamid'],
            attacker_team=row['user_team_name'],
            tick=row['tick'],
            weapon=row['weapon'],
            silenced=row['silenced'],
        ))

    return weapon_fires
