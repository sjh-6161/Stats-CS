import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np
import matplotlib.pyplot as plt
import math

WEAPON_CLASSES = {
    # "smokegrenade": "grenade",
    # "molotov": "grenade",
    # "flashbang": "grenade",
    # "hegrenade": "grenade",
    # "incgrenade": "grenade",
    # "decoy": "grenade",
    "mac10": "smg",
    "mp5sd": "smg",
    "ump45": "smg",
    "mp7": "smg",
    "mp9": "smg",
    "bizon": "smg",
    "p90": "smg",
    "ak47": "ak",
    "aug": "rifle",
    "famas": "rifle",
    "galilar": "rifle",
    "m4a1_silencer": "m4",
    "m4a1": "m4",
    "sg556": "rifle",
    # "mag7": "shotgun",
    # "negev": "shotgun",
    # "sawedoff": "shotgun",
    # "nova": "shotgun",
    "m249": "rifle",
    # "xm1014": "shotgun",
    "cz75a": "pistol",
    "deagle": "pistol",
    "elite": "pistol",
    "fiveseven": "pistol",
    "glock": "glock",
    "hkp2000": "usp2k",
    "p250": "pistol",
    "revolver": "pistol",
    "tec9": "pistol",
    "usp_silencer": "usp2k",
    "awp": "sniper",
    "g3sg1": "sniper",
    "scar20": "sniper",
    # "ssg08": "scout",
    # "inferno": "grenade",
    # "C4 Explosive": "env"
}

def _calc_logistic(x: float, coef: float, intercept: float):
    return 1 / (1 + math.exp(-1 * (intercept + coef * x)))

if __name__ == "__main__":
    duels_df = pd.read_csv("./models/duels_distances.csv")

    categories = ['glock', 'usp2k', 'pistol', 'smg', 'ak', 'm4', 'rifle', 'sniper']

    coef_df = pd.DataFrame(columns=categories, index=categories)
    intercept_df = pd.DataFrame(columns=categories, index=categories)

    # Create X and Y lists, where X is the distance for each kill and Y is whether an AK was the winner or loser
    for winner in categories:
        for loser in categories:
            if winner == loser: continue

            dists = []
            results = []

            for _, row in duels_df.iterrows():
                if row['weapon'] not in WEAPON_CLASSES.keys() or row['victim_weapon'] not in WEAPON_CLASSES.keys():
                    continue

                if WEAPON_CLASSES[row['weapon']] == winner and WEAPON_CLASSES[row['victim_weapon']] == loser:
                    dists.append(row['dist'])
                    results.append(1)

                if WEAPON_CLASSES[row['weapon']] == loser and WEAPON_CLASSES[row['victim_weapon']] == winner:
                    dists.append(row['dist'])
                    results.append(0)

            clf = LogisticRegression().fit(np.array(dists).reshape(-1, 1), results)

            intercept_df.loc[loser, winner] = clf.intercept_[0]
            coef_df.loc[loser, winner] = clf.coef_[0][0]

            # plt.scatter(dists, results, alpha=0.1)
            # plt.scatter(dists, clf.predict_proba(np.array(dists).reshape(-1, 1))[:, 1])
            # plt.xlabel("Distance (In game units)")
            # plt.ylabel("AWP vs SMG Win %")
            # plt.show()

            # exit(0)

    print(coef_df)
    print(intercept_df)

    duels_df = pd.read_csv("./models/duels_distances_rec_c17.csv")


    # {"player": [kills, deaths, expected kills]}
    player_stats = {}

    player_names = duels_df['attacker'].unique()

    for player in player_names:
        player_stats[player] = [0, 0, 0]

    for _, row in duels_df.iterrows():
        if row['weapon'] not in WEAPON_CLASSES.keys() or row['victim_weapon'] not in WEAPON_CLASSES.keys(): 
            continue

        player_stats[row['attacker']][0] += 1
        player_stats[row['victim']][1] += 1

        if WEAPON_CLASSES[row['weapon']] == WEAPON_CLASSES[row['victim_weapon']]:
            player_stats[row['attacker']][2] += 0.5
            player_stats[row['victim']][2] += 0.5
        else:
            winner_expected = _calc_logistic(
                row['dist'], 
                coef_df.loc[WEAPON_CLASSES[row['victim_weapon']], WEAPON_CLASSES[row['weapon']]],
                intercept_df.loc[WEAPON_CLASSES[row['victim_weapon']], WEAPON_CLASSES[row['weapon']]]
            )

            player_stats[row['attacker']][2] += winner_expected
            player_stats[row['victim']][2] += 1 - winner_expected
    
    print(player_stats)

    

    