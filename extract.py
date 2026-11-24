import requests
import csv
import io
import time

#MLB Stats API URL
BASE_URL = "https://statsapi.mlb.com/api/v1"

#baseballSavant URL
SAVANT_URL = "https://baseballsavant.mlb.com/statcast_search/csv"

def fetch_teams():
    #adding a timeout to the API request
    #sportId=1 limits results to major league teams
    resp = requests.get(f"{BASE_URL}/teams", params={"sportId": 1}, timeout=30)
    #raise an error on a failure code 
    resp.raise_for_status()   
    return resp.json()["teams"]


def fetch_schedule(start_date, end_date):
    params = {
        "sportId": 1,
        "startDate": start_date,
        "endDate": end_date,
    }
    resp = requests.get(f"{BASE_URL}/schedule", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    #it appears the API groups games by date; flatten them into one list
    games = []
    #empty-list default means a date range with no games returns [] instead of crashing
    for day in data.get("dates", []):
        #extend adds each game individually; append would nest each day's list
        games.extend(day.get("games", []))
    return games

def fetch_statcast(game_pk):
    #type=details returns one row per pitch instead of a summary
    params = {"all": "true", "type": "details", "game_pk": game_pk}
    #longer timeout since savant's csv responses are much larger than the stats api's
    resp = requests.get(SAVANT_URL, params=params, timeout=60)
    resp.raise_for_status()

    #Claude Assisted: Decode with utf-8-sig to strip a hidden byte-order mark from the first column name
    text = resp.content.decode("utf-8-sig")
    #StringIO wraps the text so DictReader can read it like a file, and each row becomes a dict keyed by column name
    rows = list(csv.DictReader(io.StringIO(text)))

    return rows

def fetch_boxscore(game_pk):
    #the game id is part of the url path here, not a query parameter
    resp = requests.get(f"{BASE_URL}/game/{game_pk}/boxscore", timeout=30)
    resp.raise_for_status()
    return resp.json()

#creating the people table
#stepping through the ids 100 at a time,
def fetch_people(player_ids, batch_size=100):
    people = []
    ids = list(player_ids)
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        #the api accepts a comma-separated list of ids, so one request covers a whole batch
        params = {"personIds": ",".join(str(pid) for pid in batch)}
        resp = requests.get(f"{BASE_URL}/people", params=params, timeout=30)
        resp.raise_for_status()
        people.extend(resp.json().get("people", []))
    return people

def fetch_transactions(start_date, end_date):
    params = {
        "sportId": 1,
        "startDate": start_date,
        "endDate": end_date,
    }
    resp = requests.get(f"{BASE_URL}/transactions", params=params, timeout=30)
    resp.raise_for_status()
    #empty-list default means a range with no transactions
    return resp.json().get("transactions", [])