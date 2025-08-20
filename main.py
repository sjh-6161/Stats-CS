from csc_api import bomb_plant_time
# from demos import round_times
from data import DbConnection
from parse import parse_many_demos, reparse_many_demos
from sequential_uuids.generators import uuid_time_nextval as uuid
import pandas as pd


if __name__ == "__main__":
    # pd.DataFrame.from_dict(bomb_plant_time.get_bomb_start_times(15), orient="index").to_csv('data.csv')
    # a = round_times.get_many_demo_bomb_plant_times("C:/Users/Sjh47/DEMOS/HLTV/IEM Cologne 2024")
    # pd.DataFrame.from_dict(a, orient="index").to_csv('demo_data.csv')

    # drop table buy;
    # drop table damage;
    # drop table team_default;
    # drop table weapon_fire;
    # drop table grenade;
    # drop table kill;
    # drop table message;
    # drop table plant;
    # drop table tournament_team;
    # drop table player;
    # drop table round;
    # drop table match;
    # drop table team;
    

    # Connect to postgres database. Initializes tables in database if needed
    connection = DbConnection()

    # parse_many_demos("Season 17", "D:\CSC\Season 17", connection)

    # parse_many_demos("S17 Recruit Combines", "D:\CSC\Season 17 Combines\Recruit", connection)
    # parse_many_demos("S17 Prospect Combines", "D:\CSC\Season 17 Combines\Prospect", connection)
    # parse_many_demos("S17 Contender Combines", "D:\CSC\Season 17 Combines\Contender", connection)
    # parse_many_demos("S17 Challenger Combines", "D:\CSC\Season 17 Combines\Challenger", connection)
    # parse_many_demos("S17 Elite Combines", "D:\CSC\Season 17 Combines\Elite", connection)
    # parse_many_demos("S17 Premier Combines", "D:\CSC\Season 17 Combines\Premier", connection)

    parse_many_demos("Austin Major Stage 1", "D:\HLTV\Austin Major Stage 1 2025", connection)
    parse_many_demos("Austin Major Stage 2", "D:\HLTV\Austin Major Stage 2 2025", connection)
    parse_many_demos("Austin Major Stage 3", "D:\HLTV\Austin Major Stage 3 2025", connection)
    parse_many_demos("Austin Major Playoffs", "D:\HLTV\Austin Major Playoffs 2025", connection)