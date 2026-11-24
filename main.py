import argparse
import sqlite3
from datetime import date

from extract import fetch_teams, fetch_schedule, fetch_statcast, fetch_boxscore, fetch_people, fetch_transactions
from transform import transform_teams, transform_schedule, transform_pitch, transform_boxscore, transform_people, transform_transactions
from load import create_tables, load_teams, load_schedule, load_pitch, load_boxscore,update_boxscore_statcast, load_people, load_transactions


def parse_args():
    parser = argparse.ArgumentParser(description="Red Sox take-home: baseball data pipeline")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD")
    parser.add_argument("--db", default="baseball.db", help="SQLite database file")
    args = parser.parse_args()

    try:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
    except ValueError:
        parser.error("Dates must be in YYYY-MM-DD format")
    if start > end:
        parser.error("--start must be on or before --end")

    return args


def main():
    args = parse_args()
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)

    #adding team table first, as schedule's foreign keys reference it
    teams = transform_teams(fetch_teams())
    load_teams(conn, teams)
    print(f"TEAM TABLE: loaded {len(teams)} rows")

    games = transform_schedule(fetch_schedule(args.start, args.end))
    load_schedule(conn, games)
    print(f"SCHEDULE TBALE: loaded {len(games)} rows")

    #fetch and transform first, then load in dependency order:
    #player must exist before pitch and box_score can reference it
    final_games = [g[0] for g in games if g[6] == "Final"]
    all_pitches = []
    all_box = []
    for game_pk in final_games:
        all_pitches.extend(transform_pitch(fetch_statcast(game_pk)))
        all_box.extend(transform_boxscore(fetch_boxscore(game_pk), game_pk))

    #every player who appears in the data: box score players, pitchers, and batters
    player_ids = {r[1] for r in all_box} | {r[3] for r in all_pitches} | {r[4] for r in all_pitches}
    player_ids.discard(None)
    players = transform_people(fetch_people(player_ids))
    load_people(conn, players)
    print(f"PLAYER TABLE: loaded {len(players)} rows")

    load_pitch(conn, all_pitches)
    print(f"PITCH TABLE: loaded {len(all_pitches)} rows from {len(final_games)} games")
    load_boxscore(conn, all_box)
    print(f"BOX_SCORE TABLE: loaded {len(all_box)} rows")

    update_boxscore_statcast(conn)
    print("BOX_SCORE TABLE: filled Statcast pitch metrics")

    #no foreign keys, as transactions often involve minor league teams or players outside the games loaded
    txns = transform_transactions(fetch_transactions(args.start, args.end))
    load_transactions(conn, txns)
    print(f"TRANSACTIONS TABLE: loaded {len(txns)} rows")

    conn.close()


if __name__ == "__main__":
    main()