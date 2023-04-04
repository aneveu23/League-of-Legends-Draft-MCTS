import requests
import sqlite3
import time

api = api = "RGAPI-642a3a40-ea80-4a19-9348-177de2e8484b"
start_time = "1679468400"
puuid = "2J-I1Sj_XVRL94Jfy1qqOAAlkUm0vuIWzedqZWrPPSGwU6QpnNggX6-ejmUqfDWlrjOgp2rCsMwqKA"


def fetch_matches_from_puuid(api, region, puuid, starttime):
    URL = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={starttime}&queue=420&type=ranked&start=0&count=100&api_key={api}"
    print(URL)
    response = requests.get(URL)
    data = response.json()
    return data


def insert_matchid(c, matchid):
    c.execute("SELECT COUNT(*) FROM matches WHERE matchId=?", (matchid,))
    result_count = c.fetchone()[0]
    # If the value does not exist, insert it into the table
    if result_count == 0:
        c.execute("INSERT INTO matches (matchId) VALUES (?)", (matchid,))


def parse_regiontable_puuids(region1, region2):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Select the puuid column from the na1_summoners table
    c.execute(f"SELECT puuid FROM {region1}_summoners")
    for value in c.fetchall():
        for matchid in fetch_matches_from_puuid(api, region2, value[0], start_time):
            insert_matchid(c, matchid)
            conn.commit()
        time.sleep(5 / 6)
    conn.close()


parse_regiontable_puuids("na1", "americas")
