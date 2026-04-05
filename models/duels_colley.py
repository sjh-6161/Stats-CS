import psycopg2
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from python_graphql_client import GraphqlClient
import matplotlib.pyplot as plt

load_dotenv()

if __name__ == "__main__":
    tier = "Challenger"

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    cur = conn.cursor()

    cur.execute(f"""
        SELECT kill.attacker_id, kill.victim_id, kill.assister_id
        FROM kill
        INNER JOIN (
            SELECT *
        FROM match
        WHERE match.tournament = 'CSC' AND match.stage = '{tier} Combines' AND match.season = 19
        ) mat ON kill.match_id = mat.id
        INNER JOIN (
        SELECT t_eqv.round_id, t_eqv.sum AS t_eqv, ct_eqv.sum AS ct_eqv  FROM (
            SELECT round_id, SUM(equipment_value)
            FROM buy
            WHERE buy.side = 'TERRORIST'
            GROUP BY round_id
        ) t_eqv
        INNER JOIN (
            SELECT round_id, SUM(equipment_value)
            FROM buy
            WHERE buy.side = 'CT'
            GROUP BY round_id
        ) ct_eqv
        ON t_eqv.round_id = ct_eqv.round_id
        ) buys ON buys.round_id = kill.round_id
        WHERE buys.t_eqv > 20000 AND buys.ct_eqv > 20000 AND NOT (kill.weapon = 'planted_c4' OR kill.weapon = 'world') 
        AND NOT kill.assistedflash AND NOT kill.attackerblind AND NOT kill.attackerinair AND NOT kill.noscope AND kill.penetrated = 0 AND NOT kill.thrusmoke
    """)
    rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=['winner', 'loser', 'assister']).dropna(subset=['winner', 'loser'])
    df = df[df['winner'] != df['loser']]
    # df['assister'] = None

    players = pd.unique(df.values.ravel())
    num_players = len(players)

    a_matrix = np.zeros((num_players, num_players))
    b_vec = np.zeros(num_players) + 1
    player_duels = np.zeros(num_players, dtype='int64')

    player_indexes = {}

    for i, player in enumerate(players):
        player_indexes[player] = i

        a_matrix[i][i] = 2

    for _, row in df.iterrows():
        if row['assister'] is None:
            # Increment the diagonals
            a_matrix[player_indexes[row['winner']]][player_indexes[row['winner']]] += 1
            a_matrix[player_indexes[row['loser']]][player_indexes[row['loser']]] += 1

            # Keep track of number of duels
            player_duels[player_indexes[row['winner']]] += 1
            player_duels[player_indexes[row['loser']]] += 1

            # Increment the winner-loser combo spots
            a_matrix[player_indexes[row['winner']]][player_indexes[row['loser']]] -= 1
            a_matrix[player_indexes[row['loser']]][player_indexes[row['winner']]] -= 1

            # Adjust the b vec for the winners and losers
            b_vec[player_indexes[row['winner']]] += 0.5
            b_vec[player_indexes[row['loser']]] -= 0.5

        else:
            # Increment the diagonals
            a_matrix[player_indexes[row['winner']]][player_indexes[row['winner']]] += 0.7
            a_matrix[player_indexes[row['assister']]][player_indexes[row['assister']]] += 0.3
            a_matrix[player_indexes[row['loser']]][player_indexes[row['loser']]] += 1

            # Keep track of number of duels
            player_duels[player_indexes[row['winner']]] += 0.7
            player_duels[player_indexes[row['assister']]] += 0.3
            player_duels[player_indexes[row['loser']]] += 1

            # Increment the winner-loser combo spots
            a_matrix[player_indexes[row['winner']]][player_indexes[row['loser']]] -= 0.7
            a_matrix[player_indexes[row['loser']]][player_indexes[row['winner']]] -= 0.7
            a_matrix[player_indexes[row['assister']]][player_indexes[row['loser']]] -= 0.3
            a_matrix[player_indexes[row['loser']]][player_indexes[row['assister']]] -= 0.3

            # Adjust the b vec for the winners and losers
            b_vec[player_indexes[row['winner']]] += 0.35
            b_vec[player_indexes[row['assister']]] += 0.15
            b_vec[player_indexes[row['loser']]] -= 0.5

    player_strengths = np.linalg.solve(a_matrix, b_vec)
    output_df = pd.DataFrame({'steam_id': players, 'strength': player_strengths, 'duels': player_duels}).sort_values('strength')

    cur.execute( """
        SELECT steam_id, name
        FROM player
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    player_names_df = pd.DataFrame(rows, columns=['steam_id', 'name'])
    output_df = pd.merge(output_df, player_names_df, on='steam_id')
    output_df.to_csv("models/combine_strengths.csv", index=False)

    client = GraphqlClient(endpoint="https://stats.csconfederation.com/graphql")

    query = f"""
        query MyQuery {{
            tierSeasonStats(season: 19, tier: "{tier}", matchType: "Combine") {{
                gameCount
                name
                rating
            }}
        }} """

    matches = client.execute(query=query)['data']['tierSeasonStats']

    csc_df = pd.DataFrame(matches)
    output_df = pd.merge(output_df, csc_df, on='name')

    min_duels = 50
    filtered_df = output_df[output_df['duels'] >= min_duels]

    plt.scatter(filtered_df['rating'], filtered_df['strength'])
    for _, row in filtered_df.iterrows():
        plt.annotate(row['name'], (row['rating'], row['strength']))
    plt.xlabel('rating')
    plt.ylabel('strength')
    plt.show()