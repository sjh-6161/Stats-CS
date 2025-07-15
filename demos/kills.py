from demoparser2 import DemoParser
from data import *

WEAPON_NAME_MAPPING = {
    "Smoke Grenade": "smokegrenade",
    "Molotov": "molotov",
    "Flashbang": "flashbang",
    "High Explosive Grenade": "hegrenade",
    "Incendiary Grenade": "incgrenade",
    "Decoy": "decoy",
    "MAC-10": "mac10",
    "MP5-SD": "mp5sd",
    "UMP-45": "ump45",
    "MP7": "mp7",
    "MP9": "mp9",
    "PP-Bizon": "bizon",
    "P90": "p90",
    "AK-47": "ak47",
    "AUG": "aug",
    "FAMAS": "famas",
    "Galil AR": "galilar",
    "M4A1-S": "m4a1_silencer",
    "M4A4": "m4a1",
    "SG 553": "sg556",
    "MAG-7": "mag7",
    "Negev": "negev",
    "Sawed-Off": "sawedoff",
    "Nova": "nova",
    "M249": "m249",
    "XM1014": "xm1014",
    "CZ75-Auto": "cz75a",
    "Desert Eagle": "deagle",
    "Dual Berettas": "elite",
    "Five-SeveN": "fiveseven",
    "Glock-18": "glock",
    "P2000": "hkp2000",
    "P250": "p250",
    "R8 Revolver": "revolver",
    "Tec-9": "tec9",
    "USP-S": "usp_silencer",
    "AWP": "awp",
    "G3SG1": "g3sg1",
    "SCAR-20": "scar20",
    "SSG 08": "ssg08"
}

def parse(rounds: List[Round], match_id: UUID, parser: DemoParser):
    deaths_df = parser.parse_event("player_death", player=["active_weapon_name", "team_name"])
    ticks_df = parser.parse_ticks(wanted_props=["is_alive", "team_name"], ticks=deaths_df["tick"].to_list())

    alive_dict = {}

    for _, row in ticks_df.iterrows():
        if row['tick'] not in alive_dict:
            alive_dict[row['tick']] = {"CT": 0, "TERRORIST": 0}

        if row['team_name'] is not None:
            alive_dict[row['tick']][row['team_name']] += row['is_alive']

    kills = []

    for _, row in deaths_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        assister_id = None
        if row['assister_steamid'] is not None:
            assister_id = row['assister_steamid']

        attacker_id = None
        if row['attacker_steamid'] is not None:
            attacker_id = row['attacker_steamid']

        victim_weapon = row['user_active_weapon_name']

        if row['user_active_weapon_name'] in WEAPON_NAME_MAPPING.keys():
            victim_weapon = WEAPON_NAME_MAPPING[row['user_active_weapon_name']]

        trade = False
        traded = False

        for _, row_2 in deaths_df.iterrows():
            if row['user_steamid'] == row_2['attacker_steamid'] and row['tick'] - row_2['tick'] > 0 and row['tick'] - row_2['tick'] < (5 * 64):
                trade = True

            if row['attacker_steamid'] == row_2['user_steamid'] and row_2['tick'] - row['tick'] > 0 and row_2['tick'] - row['tick'] < (5 * 64):
                traded = True

        kills.append(Kill(
            match_id=match_id,
            round_id=round_id,
            assister_id=assister_id,
            attacker_id=attacker_id,
            victim_id=row['user_steamid'],
            assistedflash=row['assistedflash'],
            attackerblind=row['attackerblind'],
            attackerinair=row['attackerinair'],
            headshot=row['headshot'],
            noscope=row['noscope'],
            penetrated=row['penetrated'],
            thrusmoke=row['thrusmoke'],
            distance=row['distance'],
            dmg_armor=row['dmg_armor'],
            dmg_health=row['dmg_health'],
            hitgroup=row['hitgroup'],
            weapon=row['weapon'],
            victim_weapon=victim_weapon,
            attacker_team=row['attacker_team_name'],
            assister_team=row['assister_team_name'],
            victim_team=row['user_team_name'],
            t_alive=alive_dict[row['tick']]["TERRORIST"],
            ct_alive=alive_dict[row['tick']]["CT"],
            trade=trade,
            traded=traded
        ))

    return kills
