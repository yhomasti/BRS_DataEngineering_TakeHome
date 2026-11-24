## Setting up the Virtual Environment 

To set up the virtual environment, I ran the following commands in the root folder:

python -m venv .venv
.venv\Scripts\activate           
pip install requests pandas
pip freeze > requirements.txt


## Looking through the raw information

Before actually setting up the database, I went through each table with the following script

import requests, json
teams = requests.get("https://statsapi.mlb.com/api/v1/teams?sportId=1").json()[*TABLENAME*]

After looking throguh all the information, I chose out the most important fields in my mind and used them to create my database. 

## Design Decisions

Here are the fields I took out of each table:

    TEAM: kept identifiers, league/division (ID + name), venue, and basic info; skipped API links and duplicate name fields. League and division stored on TEAM rather than separate tables, since there are only 30 teams and the values rarely change.

    SCHEDULE: officialDate was used as the game date, since the gameDate field was a UTC timestamp. Only team IDs are stored, since TEAM has the names. Scores are NULL for games that haven't been played.

    PLAYER: built from every player ID that shows up in PITCH and BOX_SCORE instead of active rosters, so traded or injured players aren't missed. Players are fetched 100 at a time.

    PITCH: one row per pitch from Statcast, keyed on (game_pk, at_bat_number, pitch_number). Intentional walks and pitch clock violations show up as automatic balls/strikes with no pitch data, so I kept them but flagged them with is_pitch_thrown = 0.

    BOX_SCORE: one row per player per game, with batting and pitching columns side by side. I used outs instead of inningsPitched, since "4.2" means 4 2/3 innings. Statcast pitch totals and velocity are filled in afterwards from PITCH.

    TRANSACTIONS: keeps player and team IDs along with names, but no foreign keys, since many transactions involve minor league teams or players who weren't in any game in the date range. Trades have both a from and to team, while moves like injured list changes only have one, so either can be NULL.


## Running the program

python main.py --start **YYYY-MM-DD** --end **YYYY-MM-DD**
python main.py --start 2026-09-01 --end 2026-09-03