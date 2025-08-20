from demoparser2 import DemoParser
from data import *
from pandas import DataFrame

def parse(rounds: List[Round], team_uuids: dict, match_id: UUID, parser: DemoParser, grenades_df: DataFrame):
    # grenades_df = parser.parse_grenades(grenades=False, extra=["team_name", "team_clan_name"])
    # grenades_df = grenades_df.drop_duplicates(subset=["grenade_entity_id"])

    # {0: {"steamid": 0000, "variant": "flashbang", "start": {"tick": 0, "x": 0.0, "y": 0.0, "z": 0.0}, "end": {"tick": 0, "x": 0.0, "y": 0.0, "z": 0.0}}
    active_grenades = {}
    grenades = []

    # for _, row in grenades_df.iterrows():
    #     if row['grenade_entity_id'] 

    grenades_df = grenades_df.sort_values(["grenade_entity_id", "tick"])

    grenades_df['tick_diff'] = grenades_df['tick'].diff()

    sequence_starts = grenades_df[(grenades_df['tick_diff'] != 1) | (grenades_df['tick_diff'].isna())].index
    sequence_ends = grenades_df[grenades_df['tick'].diff(-1) != -1].index
    
    start_rows = grenades_df.loc[sequence_starts].reset_index()
    end_rows = grenades_df.loc[sequence_ends].reset_index()

    # print(start_rows)
    # print(end_rows)

    for i in start_rows.index:
        round_id = None
        for round in rounds:
            if start_rows.loc[i]["tick"] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        grenades.append(Grenade(
            player_id=str(start_rows.loc[i]["steamid"]),
            team_id=None,
            round_id=round_id,
            match_id=match_id,
            team=None,
            grenade_type=start_rows.loc[i]["grenade_type"].replace("C", "").replace("Projectile", ""),
            start_tick=int(start_rows.loc[i]["tick"]),
            start_x=float(start_rows.loc[i]["x"]),
            start_y=float(start_rows.loc[i]["y"]),
            start_z=float(start_rows.loc[i]["z"]),
            end_tick=int(end_rows.loc[i]["tick"]),
            end_x=float(end_rows.loc[i]["x"]),
            end_y=float(end_rows.loc[i]["y"]),
            end_z=float(end_rows.loc[i]["z"]),
        ))

    # exit(0)

    # for row in grenades_df.itertuples():
    #     if row.grenade_entity_id not in active_grenades.keys():

    #         active_grenades[row.grenade_entity_id] = {
    #             "steamid": row.steamid, 
    #             "variant": row.grenade_type.replace("C", "").replace("Projectile", ""), 
    #             "start": {"tick": row.tick, "x": row.x, "y": row.y, "z": row.z}, 
    #             "end": {"tick": row.tick, "x": row.x, "y": row.y, "z": row.z}
    #         }
        
    #     else:
    #         # if this grenade entity ID is being reused by a new grenade
    #         if row.tick > active_grenades[row.grenade_entity_id]['end']['tick'] + 1:
    #             # Get the round ID and add the old grenade to the grenades list
    #             round_id = None
    #             for round in rounds:
    #                 if active_grenades[row.grenade_entity_id]['end']['tick'] > round.freeze_time_end_tick:
    #                     round_id = round.id

    #             if round_id == None: continue

    #             grenades.append(Grenade(
    #                 player_id=active_grenades[row.grenade_entity_id]["steamid"],
    #                 team_id=None,
    #                 round_id=round_id,
    #                 match_id=match_id,
    #                 team=None,
    #                 grenade_type=active_grenades[row.grenade_entity_id]["variant"],
    #                 start_tick=active_grenades[row.grenade_entity_id]["start"]["tick"],
    #                 start_x=active_grenades[row.grenade_entity_id]["start"]["x"],
    #                 start_y=active_grenades[row.grenade_entity_id]["start"]["y"],
    #                 start_z=active_grenades[row.grenade_entity_id]["start"]["z"],
    #                 end_tick=active_grenades[row.grenade_entity_id]["end"]["tick"],
    #                 end_x=active_grenades[row.grenade_entity_id]["end"]["x"],
    #                 end_y=active_grenades[row.grenade_entity_id]["end"]["y"],
    #                 end_z=active_grenades[row.grenade_entity_id]["end"]["z"],
    #             ))

    #             # Update the grenade in the active grenades list to be the new grenade
    #             active_grenades[row.grenade_entity_id] = {
    #                 "steamid": row.steamid, 
    #                 "variant": row.grenade_type.replace("C", "").replace("Projectile", ""), 
    #                 "start": {"tick": row.tick, "x": row.x, "y": row.y, "z": row.z}, 
    #                 "end": {"tick": row.tick, "x": row.x, "y": row.y, "z": row.z}
    #             }
    #         # if this grenade entity id is still being used by the old grenade
    #         else:
    #             # Update the end position and tick
    #             active_grenades[row.grenade_entity_id]["end"] = {"tick": row.tick, "x": row.x, "y": row.y, "z": row.z}

    # # Add all of the grenades from the active grenades list to the grenades list
    # for gid in active_grenades.keys():
    #     # Get the round ID and add the old grenade to the grenades list
    #     round_id = None
    #     for round in rounds:
    #         if active_grenades[gid]['end']['tick'] > round.freeze_time_end_tick:
    #             round_id = round.id

    #     if round_id == None: continue

    #     grenades.append(Grenade(
    #         player_id=active_grenades[gid]["steamid"],
    #         team_id=None,
    #         round_id=round_id,
    #         match_id=match_id,
    #         team=None,
    #         grenade_type=active_grenades[gid]["variant"],
    #         start_tick=active_grenades[gid]["start"]["tick"],
    #         start_x=active_grenades[gid]["start"]["x"],
    #         start_y=active_grenades[gid]["start"]["y"],
    #         start_z=active_grenades[gid]["start"]["z"],
    #         end_tick=active_grenades[gid]["end"]["tick"],
    #         end_x=active_grenades[gid]["end"]["x"],
    #         end_y=active_grenades[gid]["end"]["y"],
    #         end_z=active_grenades[gid]["end"]["z"],
    #     ))

    # Go back and get the team and team clan names for the players who threw the grenades
    ticks = []

    for g in grenades:
        ticks.append(g.start_tick)

    ticks_df = parser.parse_ticks(wanted_props=["team_name", "team_clan_name"], ticks=ticks)

    for _, row in ticks_df.iterrows():
        for g in grenades:
            if str(row['steamid']) == g.player_id and row['tick'] == g.start_tick:
                g.team_id = team_uuids[row['team_clan_name']]
                g.team = row['team_name']

                break
            
    return grenades