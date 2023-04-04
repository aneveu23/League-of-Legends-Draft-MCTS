import requests
import sqlite3
import time

api = "RGAPI-642a3a40-ea80-4a19-9348-177de2e8484b"


def get_league(api, region, league, tier=False, page = 1):
    """
    Get all players satisfying certain parameters.
    :param page: If sub-master, Riot's "page" of the tier to access
    :param api: the user's API key
    :param region: the region for which to get player data
    :param league: the league for which to get player data
    :param tier: the tier for which to get player data, if applicable
    :return: IF TIER: Set of LeagueEntryDTO objects, which contain summonerId unique to region
             ELSE   : List of LeagueItemDTO objects, which contain summonerId unique to region
    """
    if tier:
        URL = f"https://{region}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{league}/{tier}?page={page}&api_key={api}"
        response = requests.get(URL)
        data = response.json()
        print(data)
        return data
    else:
        URL = f"https://{region}.api.riotgames.com/lol/league/v4/{league}leagues/by-queue/RANKED_SOLO_5x5?api_key={api}"
        response = requests.get(URL)
        data = response.json()
        return data['entries']


def create_table(region):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {region}_summoners (
                    summonerid TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()
def create_matches_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS matches (
                    matchId TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

regions = ["na1", "euw1", "kr"]
#create_matches_table()
#for i in regions:
    #create_table(i)


def insert_summoner(c, region, entry):
    summonerid = entry['summonerId']
    # Check if the summonerId already exists in the table
    c.execute(f'''SELECT summonerid FROM {region}_summoners WHERE summonerid = ?''', (summonerid,))
    existing_entry = c.fetchone()
    # If the entry doesn't exist, insert the new record
    if existing_entry is None:
        c.execute(f'''INSERT INTO {region}_summoners (summonerid) VALUES (?)''', (summonerid,))


leagues = ["challenger", "grandmaster", "master"]
tiers = ["I", "II"]

def insert_leagues(api):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for region in regions:
        for league in leagues:
            for entry in get_league(api, region, league):
                insert_summoner(c, region, entry)
        for tier in tiers:
            page_counter = 1
            while True:
                league_set = get_league(api, region, "DIAMOND", tier, page_counter)
                time.sleep(5/6)
                if len(league_set) == 0:
                    break
                for entry in league_set:
                    insert_summoner(c, region, entry)
                page_counter += 1
    conn.commit()
    conn.close()


#insert_leagues(api)


def add_column_to_table(column_name, column_type, region):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f"ALTER TABLE {region}_summoners ADD COLUMN {column_name} {column_type}")
    conn.commit()
    conn.close()


# Call the function to add a new columns
#for region in regions:
    #add_column_to_table("puuid", "TEXT", region)


def fetch_summoner_puuid(api, region, summoner_id):
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["puuid"]
    else:
        print(f"Error fetching puuid for summonerId {summoner_id}: {response.status_code}, {response.text}")
        return None


def update_puuids(api, region, n):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch the first 100 rows with a null value in the 'puuid' column
    c.execute(f"SELECT summonerId FROM {region}_summoners WHERE puuid IS NULL LIMIT {n}")
    summoner_ids = c.fetchall()

    for summoner_id in summoner_ids:
        print(time.perf_counter())
        puuid = fetch_summoner_puuid(api, region, summoner_id[0])
        time.sleep(5/6)

        if puuid is not None:
            c.execute(f"UPDATE {region}_summoners SET puuid = ? WHERE summonerId = ?", (puuid, summoner_id))
            conn.commit()
    conn.close()


#for region in regions:
    #update_puuids(api, region, 300)