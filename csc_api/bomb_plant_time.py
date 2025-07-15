from python_graphql_client import GraphqlClient

def get_bomb_start_times(season: int):
    client = GraphqlClient(endpoint="https://stats.csconfederation.com/graphql")

    query = """
        query MyQuery {
            findManyMatch(where: {season: {equals: %s}, matchType: {equals: Regulation}}) {
                rounds {
                    bombStartTick
                    startingTick
                    winnerClanName
                    roundEndReason
                }
                teamStats {
                    name
                }
            }
        } """ % (season)
    
    matches = client.execute(query=query)['data']['findManyMatch']

    teams = {}

    for m in matches:
        match_teams = [m['teamStats'][0]['name'], m['teamStats'][1]['name']]

        for r in m['rounds']:
            if r['bombStartTick'] == "0": 
                continue

            plant_team = ""

            if r['roundEndReason'] in ["TargetBombed", "TerroristsWin"]:
                plant_team = r['winnerClanName']
            else:
                if r['winnerClanName'] == match_teams[0]:
                    plant_team = match_teams[1]
                else:
                    plant_team = match_teams[0]

            if plant_team not in teams.keys():
                teams[plant_team] = {'plants': 0, 'ticks': 0}

            teams[plant_team]['plants'] += 1
            teams[plant_team]['ticks'] += int(r['bombStartTick']) - int(r['startingTick'])
            
    return teams

