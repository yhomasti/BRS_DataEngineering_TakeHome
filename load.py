def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team (
            team_id            INTEGER PRIMARY KEY,
            name               TEXT NOT NULL,
            abbreviation       TEXT,
            team_name          TEXT,
            location_name      TEXT,
            league_id          INTEGER,
            league_name        TEXT,
            division_id        INTEGER,
            division_name      TEXT,
            venue_id           INTEGER,
            venue_name         TEXT,
            first_year_of_play INTEGER,
            active             BOOLEAN,
            season             INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            game_pk            INTEGER PRIMARY KEY,
            game_date          TEXT NOT NULL,
            game_datetime_utc  TEXT,
            season             INTEGER,
            game_type          TEXT,
            status             TEXT,
            abstract_state     TEXT,
            away_team_id       INTEGER,
            home_team_id       INTEGER,
            away_score         INTEGER,
            home_score         INTEGER,
            venue_id           INTEGER,
            double_header      TEXT,
            game_number        INTEGER,
            day_night          TEXT,
            scheduled_innings  INTEGER,
            FOREIGN KEY (away_team_id) REFERENCES team(team_id),
            FOREIGN KEY (home_team_id) REFERENCES team(team_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS pitch (
            game_pk          INTEGER NOT NULL,
            at_bat_number    INTEGER NOT NULL,
            pitch_number     INTEGER NOT NULL,
            pitcher_id       INTEGER,
            batter_id        INTEGER,
            inning           INTEGER,
            inning_half      TEXT,
            balls            INTEGER,
            strikes          INTEGER,
            outs             INTEGER,
            batter_side      TEXT,
            pitcher_hand     TEXT,
            pitch_type       TEXT,
            pitch_name       TEXT,
            release_speed    REAL,
            effective_speed  REAL,
            spin_rate        INTEGER,
            spin_axis        INTEGER,
            extension        REAL,
            release_pos_x    REAL,
            release_pos_z    REAL,
            arm_angle        REAL,
            pfx_x            REAL,
            pfx_z            REAL,
            plate_x          REAL,
            plate_z          REAL,
            zone             INTEGER,
            result_type      TEXT,
            description      TEXT,
            pa_event         TEXT,
            launch_speed     REAL,
            launch_angle     INTEGER,
            hit_distance     INTEGER,
            bb_type          TEXT,
            is_pitch_thrown  INTEGER NOT NULL,
            PRIMARY KEY (game_pk, at_bat_number, pitch_number),
            FOREIGN KEY (game_pk) REFERENCES schedule(game_pk),
            FOREIGN KEY (pitcher_id) REFERENCES player(player_id),
            FOREIGN KEY (batter_id) REFERENCES player(player_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS box_score (
            game_pk            INTEGER NOT NULL,
            player_id          INTEGER NOT NULL,
            team_id            INTEGER,
            position           TEXT,
            batting_order      INTEGER,
            bat_pa             INTEGER,
            bat_ab             INTEGER,
            bat_r              INTEGER,
            bat_h              INTEGER,
            bat_2b             INTEGER,
            bat_3b             INTEGER,
            bat_hr             INTEGER,
            bat_rbi            INTEGER,
            bat_bb             INTEGER,
            bat_so             INTEGER,
            bat_hbp            INTEGER,
            bat_sb             INTEGER,
            pit_games_started  INTEGER,
            pit_outs           INTEGER,
            pit_h              INTEGER,
            pit_r              INTEGER,
            pit_er             INTEGER,
            pit_bb             INTEGER,
            pit_so             INTEGER,
            pit_hr             INTEGER,
            pit_batters_faced  INTEGER,
            pit_pitches        INTEGER,
            pit_strikes        INTEGER,
            sc_pitches_thrown  INTEGER,
            sc_avg_velo        REAL,
            sc_max_velo        REAL,
            sc_avg_spin        REAL,
            PRIMARY KEY (game_pk, player_id),
            FOREIGN KEY (game_pk) REFERENCES schedule(game_pk),
            FOREIGN KEY (team_id) REFERENCES team(team_id),
            FOREIGN KEY (player_id) REFERENCES player(player_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS player (
            player_id         INTEGER PRIMARY KEY,
            full_name         TEXT NOT NULL,
            first_name        TEXT,
            last_name         TEXT,
            birth_date        TEXT,
            birth_country     TEXT,
            primary_position  TEXT,
            bat_side          TEXT,
            pitch_hand        TEXT,
            height_inches     INTEGER,
            weight            INTEGER,
            primary_number    TEXT,
            mlb_debut_date    TEXT,
            active            BOOLEAN
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id   INTEGER PRIMARY KEY,
            transaction_date TEXT,
            effective_date   TEXT,
            resolution_date  TEXT,
            type_code        TEXT,
            type_desc        TEXT,
            description      TEXT,
            player_id        INTEGER,
            player_name      TEXT,
            from_team_id     INTEGER,
            from_team_name   TEXT,
            to_team_id       INTEGER,
            to_team_name     TEXT
        )
    """)


def load_teams(conn, rows):
    conn.executemany("""
        INSERT INTO team (
            team_id, name, abbreviation, team_name, location_name,
            league_id, league_name, division_id, division_name, venue_id, venue_name,
            first_year_of_play, active, season
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
        ON CONFLICT(team_id) DO UPDATE SET
            name = excluded.name,
            abbreviation = excluded.abbreviation,
            team_name = excluded.team_name,
            location_name = excluded.location_name,
            league_id = excluded.league_id,
            league_name = excluded.league_name,
            division_id = excluded.division_id,
            division_name = excluded.division_name,
            venue_id = excluded.venue_id,
            venue_name = excluded.venue_name,
            first_year_of_play = excluded.first_year_of_play,
            active = excluded.active,
            season = excluded.season
    """, rows)
    conn.commit()

def load_schedule(conn, rows):
    conn.executemany("""
        INSERT INTO schedule (
            game_pk, game_date, game_datetime_utc, season, game_type,
            status, abstract_state, away_team_id, home_team_id,
            away_score, home_score, venue_id, double_header,
            game_number, day_night, scheduled_innings
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_pk) DO UPDATE SET
            game_date = excluded.game_date,
            game_datetime_utc = excluded.game_datetime_utc,
            season = excluded.season,
            game_type = excluded.game_type,
            status = excluded.status,
            abstract_state = excluded.abstract_state,
            away_team_id = excluded.away_team_id,
            home_team_id = excluded.home_team_id,
            away_score = excluded.away_score,
            home_score = excluded.home_score,
            venue_id = excluded.venue_id,
            double_header = excluded.double_header,
            game_number = excluded.game_number,
            day_night = excluded.day_night,
            scheduled_innings = excluded.scheduled_innings
    """, rows)
    conn.commit()

def load_pitch(conn, rows):
    columns = [
        "game_pk", "at_bat_number", "pitch_number", "pitcher_id", "batter_id",
        "inning", "inning_half", "balls", "strikes", "outs", "batter_side", "pitcher_hand",
        "pitch_type", "pitch_name", "release_speed", "effective_speed", "spin_rate",
        "spin_axis", "extension", "release_pos_x", "release_pos_z", "arm_angle",
        "pfx_x", "pfx_z", "plate_x", "plate_z", "zone",
        "result_type", "description", "pa_event",
        "launch_speed", "launch_angle", "hit_distance", "bb_type", "is_pitch_thrown",
    ]
    keys = {"game_pk", "at_bat_number", "pitch_number"}
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(f"{c} = excluded.{c}" for c in columns if c not in keys)

    conn.executemany(f"""
        INSERT INTO pitch ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(game_pk, at_bat_number, pitch_number) DO UPDATE SET {updates}
    """, rows)
    conn.commit()


def load_boxscore(conn, rows):
    columns = [
        "game_pk", "player_id", "team_id", "position", "batting_order",
        "bat_pa", "bat_ab", "bat_r", "bat_h", "bat_2b", "bat_3b", "bat_hr",
        "bat_rbi", "bat_bb", "bat_so", "bat_hbp", "bat_sb",
        "pit_games_started", "pit_outs", "pit_h", "pit_r", "pit_er", "pit_bb",
        "pit_so", "pit_hr", "pit_batters_faced", "pit_pitches", "pit_strikes",
    ]
    keys = {"game_pk", "player_id"}
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(f"{c} = excluded.{c}" for c in columns if c not in keys)

    conn.executemany(f"""
        INSERT INTO box_score ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(game_pk, player_id) DO UPDATE SET {updates}
    """, rows)
    conn.commit()

#fills box_score's statcast columns by aggregating pitch data per pitcher per game
def update_boxscore_statcast(conn):
    conn.execute("""
        UPDATE box_score
        SET sc_pitches_thrown = agg.pitches_thrown,
            sc_avg_velo       = agg.avg_velo,
            sc_max_velo       = agg.max_velo,
            sc_avg_spin       = agg.avg_spin
        FROM (
            SELECT game_pk,
                   pitcher_id,
                   SUM(is_pitch_thrown)          AS pitches_thrown,
                   ROUND(AVG(release_speed), 1)  AS avg_velo,
                   MAX(release_speed)            AS max_velo,
                   ROUND(AVG(spin_rate))         AS avg_spin
            FROM pitch
            GROUP BY game_pk, pitcher_id
        ) AS agg
        WHERE box_score.game_pk = agg.game_pk
          AND box_score.player_id = agg.pitcher_id
    """)
    conn.commit()

def load_people(conn, rows):
    columns = [
        "player_id", "full_name", "first_name", "last_name", "birth_date",
        "birth_country", "primary_position", "bat_side", "pitch_hand",
        "height_inches", "weight", "primary_number", "mlb_debut_date", "active",
    ]
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(f"{c} = excluded.{c}" for c in columns if c != "player_id")

    conn.executemany(f"""
        INSERT INTO player ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(player_id) DO UPDATE SET {updates}
    """, rows)
    conn.commit()

def load_transactions(conn, rows):
    columns = [
        "transaction_id", "transaction_date", "effective_date", "resolution_date",
        "type_code", "type_desc", "description", "player_id", "player_name",
        "from_team_id", "from_team_name", "to_team_id", "to_team_name",
    ]
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(f"{c} = excluded.{c}" for c in columns if c != "transaction_id")

    conn.executemany(f"""
        INSERT INTO transactions ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(transaction_id) DO UPDATE SET {updates}
    """, rows)
    conn.commit()