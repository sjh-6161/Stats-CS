from demoparser2 import DemoParser
from data import *
from pandas import DataFrame

def parse(rounds: List[Round], match_id: UUID, player_hurt_df: DataFrame):
    # hurts_df = parser.parse_event(event_name='player_hurt', player=['team_name', "X", "Y", "Z"])

    damages = []
    
    for _, row in player_hurt_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        attacker_id = None
        if row['attacker_steamid'] is not None:
            attacker_id = row['attacker_steamid']

        damages.append(Damage(
            match_id=match_id,
            round_id=round_id,
            attacker_id=attacker_id,
            victim_id=row['user_steamid'],
            attacker_x=row['attacker_X'],
            attacker_y=row['attacker_Y'],
            attacker_z=row['attacker_Z'],
            victim_x=row['user_X'],
            victim_y=row['user_Y'],
            victim_z=row['user_Z'],
            armor=row['armor'],
            health=row['health'],
            dmg_armor=row['dmg_armor'],
            dmg_health=row['dmg_health'],
            hitgroup=row['hitgroup'],
            tick=row['tick'],
            weapon=row['weapon'],
            attacker_team=row['attacker_team_name'],
            victim_team=row['user_team_name'],
        ))

    return damages