from demoparser2 import DemoParser
from data import *

def parse(rounds: List[Round], match_id: UUID, parser: DemoParser):
    hurts_df = parser.parse_event(event_name='player_hurt', player=['team_name'])

    damages = []
    
    for _, row in hurts_df.iterrows():
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