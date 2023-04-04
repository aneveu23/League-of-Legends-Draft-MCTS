import requests
import sqlite3
import time

api = "RGAPI-3abcd13d-08e7-4a0f-921d-dcb7d7399088"


def get_league(api, region, league, tier=False):
    """
    Get all players satisfying certain parameters.
    :param api: the user's API key
    :param region: the region for which to get player data
    :param league: the league for which to get player data
    :param tier: the tier for which to get player data, if applicable
    :return: IF TIER: Set of LeagueEntryDTO objects, which contain summonerId unique to region
             ELSE   : List of LeagueItemDTO objects, which contain summonerId unique to region
    """
    if tier:
        URL = f"https://{region}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{league}/{tier}?api_key={api}"
        response = requests.get(URL)
        data = response.json()y
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


regions = ["na1", "euw1", "kr"]
for i in regions:
    create_table(i)


def insert_summoner(c, region, entry):
    summonerid = entry['summonerId']
    # Check if the summonerId already exists in the table
    c.execute(f'''SELECT summonerid FROM {region}_summoners WHERE summonerid = ?''', (summonerid,))
    existing_entry = c.fetchone()
    # If the entry doesn't exist, insert the new record
    if existing_entry is None:
        c.execute(f'''INSERT INTO {region}_summoners (summonerid) VALUES (?)''', (summonerid,))


leagues = ["challenger", "grandmaster", "master"]


def insert_leagues(api):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for region in regions:
        for league in leagues:
            for entry in get_league(api, region, league):
                insert_summoner(c, region, entry)
    conn.commit()
    conn.close()


insert_leagues(api)


def add_column_to_table(column_name, column_type):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f"ALTER TABLE league_entries ADD COLUMN {column_name} {column_type}")
    conn.commit()
    conn.close()


# Call the function to add a new column
# add_column_to_table("puuid", "TEXT")


def fetch_summoner_puuid(api, summoner_id):
    url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["puuid"]
    else:
        print(f"Error fetching puuid for summonerId {summoner_id}: {response.status_code}, {response.text}")
        return None


def update_puuids(api, n):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch the first 100 rows with a null value in the 'puuid' column
    c.execute(f"SELECT summonerId FROM league_entries WHERE puuid IS NULL LIMIT {n}")
    summoner_ids = c.fetchall()

    for summoner_id in summoner_ids:
        print(time.perf_counter())
        summoner_id = summoner_id[0]  # Unpack the tuple
        puuid = fetch_summoner_puuid(api, summoner_id)
        time.sleep(1)

        if puuid is not None:
            c.execute("UPDATE league_entries SET puuid = ? WHERE summonerId = ?", (puuid, summoner_id))
            conn.commit()
    conn.close()

# update_puuids(api, 100)
