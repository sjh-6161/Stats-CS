import psycopg2
import os

import gspread
from google.oauth2.service_account import Credentials
from python_graphql_client import GraphqlClient
from dotenv import load_dotenv

seasons = [
    14,
    15,
    16,
    17,
    18,
    19
]

types = [
    "Combine",
    "Regulation",
    "Playoff"
]

tiers = [
    "Recruit",
    "Prospect",
    "Contender",
    "Challenger",
    "Elite",
    "Premier"
]

# queries = {
#     "clean-kd.sql": "Clean KD",
#     "good-kill-bad-death.sql": "GKBD",
#     "grenade-deaths.sql": "Grenade Deaths",
#     "kill-distance.sql": "Kill Distance",
#     "meme-kd.sql": "Meme KD",
#     "weapon-kds.sql": "Weapon KDs",
#     "no-buy-pistols.sql": "No Buy Pistols",
#     "gg-rate.sql": "GGR"
# }

def get_combined_stats():
    stats_client = GraphqlClient(endpoint="https://stats.csconfederation.com/graphql")

    stats_array = []

    for season in seasons:
        for type in types:
            for tier in tiers:
                query = """
                    query MyQuery($season: Int!, $tier: String!, $type: String!) {
                        tierSeasonStats(season: $season, tier: $tier, matchType: $type) {
                            gameCount
                            rating
                            name
                            ef
                            fAssists
                            util
                            awpR
                            odr
                            odaR
                            consistency
                        }
                    }
                """

                variables = {"season": season, "tier": tier, "type": type}

                data = stats_client.execute(query=query, variables=variables)

                for entry in data["data"]["tierSeasonStats"]:
                    stats_array.append([
                        season,
                        type,
                        tier,
                        entry["name"],
                        entry["rating"],
                        entry["gameCount"],
                        entry["ef"],
                        entry["fAssists"],
                        entry["util"],
                        entry["awpR"],
                        entry["odr"],
                        entry["odaR"],
                        entry["consistency"]
                    ])

    worksheet_names_dict["Combined"].update(stats_array, "B2")

if __name__ == "__main__":
    # Postgres connection
    load_dotenv()

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    # Sheets api things
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file("./query-to-sheets/sheets-api.json", scopes=scopes)
    client = gspread.authorize(credentials)

    sheet_id = "1Am4y8OPgT2dQoufX-weXGsSUVVDvIWBIwDACjnO9Afc"

    sheet = client.open_by_key(sheet_id)

    worksheet_list = sheet.worksheets()
    worksheet_names = [x.title for x in worksheet_list]

    worksheet_names_dict = dict(map(lambda i,j : (i,j), worksheet_names, worksheet_list))

    get_combined_stats()

    print("Succesfully Updated Combined Stats")
    
    file = "aggregate.sql"

    with open(f"./query-to-sheets/{file}", 'r') as q:
        query = q.read()

    with connection.cursor() as cur:
        cur.execute(query)

        colnames = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    worksheet_names_dict["Custom Stats"].clear()
    worksheet_names_dict["Custom Stats"].update([colnames], "A1")
    worksheet_names_dict["Custom Stats"].update(data, "A2")

    print(f"Succesfully Updated Custom Stats")

    