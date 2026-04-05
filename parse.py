import os
import traceback
from demoparser2 import DemoParser
from data import DbConnection, Team, Player, Match, UUID, FailedDemo
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


def create_match(parser: DemoParser, tournament: str, stage: str, season: int, file_name: str, team_uuids: list[UUID]):
    map_name = parser.parse_header()["map_name"]

    temp_match = Match(
        team_one_id=team_uuids[0],
        team_two_id=team_uuids[1],
        map=map_name,
        file=file_name,
        tournament=tournament,
        stage=stage,
        season=season
    )

    return temp_match, temp_match.id


def parse_one_demo(file_path: str, tournament: str, stage: str, season: int, connection: DbConnection, s3_key: str = None):
    """Parse a single .dem file and insert all data into the database.
    Returns True on success, False on failure (with FailedDemo inserted)."""
    file = os.path.basename(file_path)
    parser = DemoParser(file_path)

    try:
        required_events = ["round_freeze_end", "player_hurt", "player_death", "chat_message", "bomb_planted", "round_officially_ended", "cs_win_panel_match", "weapon_fire"]
        player_event_props = ["team_name", "team_clan_name", "X", "Y", "Z", "active_weapon_name", "which_bomb_zone", "pitch", "yaw", "last_place_name"]
        other_event_props = ["team_rounds_total", "round_win_reason", "round_in_progress", "is_warmup_period"]

        player_grenade_props = ["team_name", "team_clan_name", "last_place_name"]

        player_tick_props = ["current_equip_value", "balance", "team_clan_name", "team_name", "last_place_name", "is_warmup_period", "is_alive", "X", "Y", "Z"]

        all_events = parser.parse_events(event_name=required_events, player=player_event_props, other=other_event_props)

        freeze_time_end_ticks = next((df for event_name, df in all_events if event_name == "round_freeze_end"), None)["tick"].to_list()
        # Sample every second from 10s to 40s into each round (31 samples per round)
        # At 64 ticks/second: offsets are 640, 704, 768, ... 2560
        default_ticks = [x + (seconds * 64) for x in freeze_time_end_ticks for seconds in range(10, 41)]
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
        teams, team_uuids = get_teams(parser, connection)
        players = get_players(parser, connection, team_uuids)

        # Create match database entry, and save match UUID
        match, match_id = create_match(parser, tournament, stage, season, file, list(team_uuids.values()))

        # Parse rounds
        round_objects = rounds.parse(team_uuids, match_id, round_freeze_end_df, round_officially_ended_df, cs_win_panel_match_df)
        plant_objects = plants.parse(round_objects, match_id, bomb_planted_df)
        default_objects = defaults.parse(round_objects, team_uuids, match_id, match.map, default_df)
        kill_objects = kills.parse(round_objects, team_uuids, match_id, match.map, player_death_event_df, player_death_tick_df)
        buy_objects = buys.parse(round_objects, team_uuids, match_id, freeze_time_end_df)
        damage_objects = damages.parse(round_objects, match_id, match.map, player_hurt_df)
        weapon_fire_objects = weapon_fires.parse(round_objects, match_id, match.map, weapon_fire_df)
        grenade_objects = grenades.parse(round_objects, team_uuids, match_id, match.map, parser, grenades_df)
        message_objects = messages.parse(round_objects, match_id, chat_message_df)

        connection.insert_many(teams)
        connection.insert_many(players)
        connection.insert(match)
        connection.insert_many(round_objects)
        connection.insert_many(plant_objects)
        connection.insert_many(default_objects)
        connection.insert_many(kill_objects)
        connection.insert_many(buy_objects)
        connection.insert_many(grenade_objects)
        connection.insert_many(message_objects)

        return True
    except Exception as e:
        error_str = f"{e}\n{traceback.format_exc()}"
        if s3_key:
            connection.insert(FailedDemo(
                file=file,
                s3_key=s3_key,
                error=error_str,
                parser_version=parser_version,
            ))
        return False


def parse_many_demos(tournament: str, stage: str, season: int, folder_path: str, connection: DbConnection):
    files = os.listdir(folder_path)

    # Get existing matches / demos parsed
    matches = connection.list_demos()
    existing_matches = {(x[0], x[1]) for x in matches}

    for file in files:
        if ".dem" not in file or (file, tournament) in existing_matches:
            continue

        parse_one_demo(f"{folder_path}/{file}", tournament, stage, season, connection)



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

    