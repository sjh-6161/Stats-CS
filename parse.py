import os
import traceback
from demoparser2 import DemoParser
from data import DbConnection, Team, Player, Match, UUID, TournamentTeam
from demos import kills, rounds, buys, messages, damages, weapon_fires, defaults, grenades, plants
import datetime


parser_version = 1

def get_teams(parser: DemoParser, connection: DbConnection):
    existing_teams = connection.list_teams()

    team_uuids = {}

    for team in existing_teams:
        team_uuids[team[0]] = team[1]

    demo_team_uuids = {}

    ticks_df = parser.parse_event("round_freeze_end", other=["is_warmup_period"])
    tick = ticks_df[ticks_df['is_warmup_period'] == False]["tick"].tolist()[0]

    df = parser.parse_ticks(["team_clan_name", "is_warmup_period"], ticks=[tick])
    df = df[df['is_warmup_period'] == False]

    unique_teams = list(set(df['team_clan_name'].to_list()))

    temp_teams = []

    for team in unique_teams:
        if team not in team_uuids.keys():
            temp_team = Team(name=team)

            demo_team_uuids[team] = temp_team.id

            temp_teams.append(temp_team)
        else:
            demo_team_uuids[team] = team_uuids[team]

    return temp_teams, demo_team_uuids


def get_players(parser: DemoParser, connection: DbConnection, team_uuids: dict):
    # existing_players = connection.list_players()

    # Use steamids as keys
    # player_uuids = {}
    player_names = {}
    player_teams = {}

    # for player in existing_players:
    #     # player_uuids[player[1]] = player[2]
    #     player_names[player[1]] = player[0]

    df = parser.parse_event("player_death", player=["team_clan_name"])

    temp_players = []

    for _, row in df.iterrows():
        if row['assister_steamid'] not in player_names.keys() and row['assister_steamid'] is not None: 
            player_names[row['assister_steamid']] = row['assister_name']
            player_teams[row['assister_steamid']] = row['assister_team_clan_name']

            temp_player = Player(row['assister_steamid'], row['assister_name'], team_uuids[row['assister_team_clan_name']])
            # player_uuids[row['assister_steamid']] = temp_player.id
            temp_players.append(temp_player)

        if row['attacker_steamid'] not in player_names.keys() and row['attacker_steamid'] is not None: 
            player_names[row['attacker_steamid']] = row['attacker_name']
            player_teams[row['attacker_steamid']] = row['attacker_team_clan_name']

            temp_player = Player(row['attacker_steamid'], row['attacker_name'], team_uuids[row['attacker_team_clan_name']])
            # player_uuids[row['attacker_steamid']] = temp_player.id
            temp_players.append(temp_player)

        if row['user_steamid'] not in player_names.keys() and row['user_steamid'] is not None: 
            player_names[row['user_steamid']] = row['user_name']
            player_teams[row['user_steamid']] = row['user_team_clan_name']

            temp_player = Player(row['user_steamid'], row['user_name'], team_uuids[row['user_team_clan_name']])
            # player_uuids[row['user_steamid']] = temp_player.id
            temp_players.append(temp_player)

    return temp_players


def create_match(parser: DemoParser, tournament: str, file_name: str, team_uuids: list[UUID]):
    map_name = parser.parse_header()["map_name"]

    temp_match = Match(
        team_one_id=team_uuids[0],
        team_two_id=team_uuids[1],
        map=map_name,
        file=file_name,
        tournament=tournament
    )

    return temp_match, temp_match.id


def parse_many_demos(tournament: str, folder_path: str, connection: DbConnection):
    files = os.listdir(folder_path)

    # Get existing matches / demos parsed
    matches = connection.list_demos()

    existing_matches = [(x[0], x[1]) for x in matches]

    tournament_players = {}

    for file in files:
        # Filter out already parsed demos
        if ".dem" not in file or (file, tournament) in existing_matches: 
            continue

        parser = DemoParser(f"{folder_path}/{file}")

        try:
            required_events = ["round_freeze_end", "player_hurt", "player_death", "chat_message", "bomb_planted", "round_officially_ended", "cs_win_panel_match", "weapon_fire"]
            player_event_props = ["team_name", "team_clan_name", "X", "Y", "Z", "active_weapon_name", "which_bomb_zone", "pitch", "yaw"]
            other_event_props = ["team_rounds_total", "round_win_reason", "round_in_progress", "is_warmup_period"]

            player_grenade_props = ["team_name", "team_clan_name"]

            player_tick_props = ["current_equip_value", "balance", "team_clan_name", "team_name", "last_place_name", "is_warmup_period", "is_alive"]


            all_events = parser.parse_events(event_name=required_events, player=player_event_props, other=other_event_props)


            freeze_time_end_ticks = next((df for event_name, df in all_events if event_name == "round_freeze_end"), None)["tick"].to_list()
            default_ticks = [x + (12 * 64) for x in freeze_time_end_ticks]
            player_death_ticks = next((df for event_name, df in all_events if event_name == "player_death"), None)["tick"].to_list()

            all_ticks = freeze_time_end_ticks + default_ticks + player_death_ticks

            ticks_df = parser.parse_ticks(ticks=all_ticks, wanted_props=player_tick_props)

            # The relevant event dfs
            round_freeze_end_df = next((df for event_name, df in all_events if event_name == "round_freeze_end"), None)
            player_hurt_df = next((df for event_name, df in all_events if event_name == "player_hurt"), None)
            player_death_event_df = next((df for event_name, df in all_events if event_name == "player_death"), None)
            chat_message_df = next((df for event_name, df in all_events if event_name == "chat_message"), None)
            bomb_planted_df = next((df for event_name, df in all_events if event_name == "bomb_planted"), None)
            round_officially_ended_df = next((df for event_name, df in all_events if event_name == "round_officially_ended"), None)
            cs_win_panel_match_df = next((df for event_name, df in all_events if event_name == "cs_win_panel_match"), None)
            weapon_fire_df = next((df for event_name, df in all_events if event_name == "weapon_fire"), None)

            # The grenades df
            grenades_df = parser.parse_grenades(grenades=False, extra=player_grenade_props)

            # The relevant necesary tick dataframes for the various functions
            freeze_time_end_df = ticks_df[ticks_df['tick'].isin(freeze_time_end_ticks)]
            default_df = ticks_df[ticks_df['tick'].isin(default_ticks)]
            player_death_tick_df = ticks_df[ticks_df['tick'].isin(player_death_ticks)]

            # Get the teams / players in the match and their corresponding UUIDs, and create database entries if needed
            # {"team_name_1": UUID, "team_name_2": UUID}
            # {"player_steamid_1": UUID}
            teams, team_uuids = get_teams(parser, connection)
            players = get_players(parser, connection, team_uuids)

            for player in players:
                if player.steam_id not in tournament_players.keys():
                    tournament_players[player.steam_id] = player.team_id

            # Create match database entry, and save match UUID
            match, match_id = create_match(parser, tournament, file, list(team_uuids.values()))

            # Parse basic team stats and create database entries
            # basic_team_stats_objects = basic_team_stats.parse(team_uuids, match_id, parser)

            # # Parse basic player stats and create database entries
            # basic_player_stats_objects = basic_player_stats.parse(player_uuids, team_uuids, match_id, parser)

            
            # Parse rounds
            # time = datetime.datetime.now()
            round_objects = rounds.parse(team_uuids, match_id, round_freeze_end_df, round_officially_ended_df, cs_win_panel_match_df)
            # current_time =  datetime.datetime.now(); print(f"Rounds: {current_time - time}"); time = current_time

            plant_objects = plants.parse(round_objects, match_id, bomb_planted_df)
            # current_time =  datetime.datetime.now(); print(f"Plants: {current_time - time}"); time = current_time

            default_objects  = defaults.parse(round_objects, team_uuids, match_id, match.map, default_df)
            # current_time =  datetime.datetime.now(); print(f"Defaults: {current_time - time}"); time = current_time

            # Parse kills
            kill_objects = kills.parse(round_objects, team_uuids, match_id, player_death_event_df, player_death_tick_df)
            # current_time =  datetime.datetime.now(); print(f"Kills: {current_time - time}"); time = current_time

            # Parse round eq vals and balances
            buy_objects = buys.parse(round_objects, team_uuids, match_id, freeze_time_end_df)
            # current_time =  datetime.datetime.now(); print(f"Buys: {current_time - time}"); time = current_time

            damage_objects = damages.parse(round_objects, match_id, player_hurt_df)
            # current_time =  datetime.datetime.now(); print(f"Damages: {current_time - time}"); time = current_time

            weapon_fire_objects = weapon_fires.parse(round_objects, match_id, weapon_fire_df)
            # current_time =  datetime.datetime.now(); print(f"Weapon Fires: {current_time - time}"); time = current_time

            grenade_objects = grenades.parse(round_objects, team_uuids, match_id, parser, grenades_df)
            # current_time =  datetime.datetime.now(); print(f"Grenades: {current_time - time}"); time = current_time

            # Parse chat messages
            message_objects = messages.parse(round_objects, match_id, chat_message_df)
            # current_time =  datetime.datetime.now(); print(f"Messages: {current_time - time}"); time = current_time

            connection.insert_many(teams)
            connection.insert_many(players)
            connection.insert(match)
            connection.insert_many(round_objects)
            connection.insert_many(plant_objects)
            connection.insert_many(default_objects)
            connection.insert_many(kill_objects)
            connection.insert_many(buy_objects)
            connection.insert_many(weapon_fire_objects)
            connection.insert_many(grenade_objects)
            connection.insert_many(damage_objects)
            connection.insert_many(message_objects)

            print(f"Succesfully parsed {file}")
        except Exception as e:
            print(f"Something went wrong when parsing {file}\n{e}\n{traceback.format_exc()}")

    tournament_team_objects = []

    # Go throught the players in the tournament and update TournamentTeams with their team
    for steam_id in tournament_players.keys():
        tournament_team_objects.append(TournamentTeam(
            player_id=steam_id,
            team_id=tournament_players[steam_id],
            tournament_name=tournament
        ))

    connection.insert_many(tournament_team_objects)


def reparse_many_demos(tournament: str, folder_path: str, connection: DbConnection):
    files = os.listdir(folder_path)

    # Get existing matches / demos parsed
    matches = connection.list_demos()

    for match in matches:
        if match[0] not in files or match[1] != tournament: continue

        parser = DemoParser(f"{folder_path}/{match[0]}")

        try:
            # teams, team_uuids = get_teams(parser, connection)
            # players, player_uuids = get_players(parser, connection)

            match_id = match[2]

            players, player_uuids = get_players(parser, connection)

            round_objects = connection.list_rounds(match_id)

            buy_objects = buys.parse(round_objects, player_uuids, match_id, parser)

            message_objects = messages.parse(round_objects, player_uuids, match_id, parser)

            connection.insert_many(message_objects)

            print(f"Succesfully reparsed {match[0]}")
        except Exception as e:
            print(f"Something went wrong when reparsing {match[0]}\n{e}\n{traceback.format_exc()}")

    