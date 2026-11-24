#helper that converts a value into an integer.
#returns none if missing or not a number.
def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

#helper that converts a value into a float.
#returns None if missing or not a number.
def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

#helper that turns empty strings into None, so they load as NULL.
def blank_to_none(value):
    return value if value not in ("", None) else None

#converts height like 6' 0" into total inches
#returns None if the format is unexpected
def height_to_inches(value):
    try:
        feet, inches = value.replace('"', "").split("'")
        return int(feet) * 12 + int(inches)
    except (AttributeError, ValueError):
        return None

#transforming the teams table
def transform_teams(raw_teams):
    rows = []
    for t in raw_teams:
        league = t.get("league", {})
        division = t.get("division", {})
        venue = t.get("venue", {})

        rows.append((
            t["id"],                 
            t.get("name"),            
            t.get("abbreviation"),
            t.get("teamName"),
            t.get("locationName"),
            league.get("id"),         
            league.get("name"),      
            division.get("id"),
            division.get("name"),
            venue.get("id"),
            venue.get("name"),
            to_int(t.get("firstYearOfPlay")), 
            t.get("active"),
            t.get("season")
        ))
    return rows

#transforming schedule table
def transform_schedule(raw_games):
    rows = []
    for g in raw_games:
        status = g.get("status", {})
        away = g.get("teams", {}).get("away", {})
        home = g.get("teams", {}).get("home", {})
        venue = g.get("venue", {})

        rows.append((
            g["gamePk"],                        
            g.get("officialDate"),               
            g.get("gameDate"),                   
            to_int(g.get("season")),            
            g.get("gameType"),                   
            status.get("detailedState"),         
            status.get("abstractGameState"),
            away.get("team", {}).get("id"),     
            home.get("team", {}).get("id"),
            away.get("score"),                   
            home.get("score"),
            venue.get("id"),
            g.get("doubleHeader"),
            g.get("gameNumber"),
            g.get("dayNight"),
            g.get("scheduledInnings")
        ))
    return rows


#transforming pitch data
def transform_pitch(raw_pitches):
    rows = []
    for p in raw_pitches:
        rows.append((
            # keys
            to_int(p.get("game_pk")),             
            to_int(p.get("at_bat_number")),       
            to_int(p.get("pitch_number")),        
            to_int(p.get("pitcher")), #pitcher_id
            to_int(p.get("batter")), #batter_id
            #game context
            to_int(p.get("inning")),              
            blank_to_none(p.get("inning_topbot")),
            to_int(p.get("balls")),               
            to_int(p.get("strikes")),             
            to_int(p.get("outs_when_up")),        
            blank_to_none(p.get("stand")),        
            blank_to_none(p.get("p_throws")), #the pitcher's throwing hand
            #the pitch itself
            blank_to_none(p.get("pitch_type")),   
            blank_to_none(p.get("pitch_name")),   
            to_float(p.get("release_speed")),     
            to_float(p.get("effective_speed")),   
            to_int(p.get("release_spin_rate")),   
            to_int(p.get("spin_axis")),           
            to_float(p.get("release_extension")), 
            to_float(p.get("release_pos_x")),     
            to_float(p.get("release_pos_z")),     
            to_float(p.get("arm_angle")),         
            to_float(p.get("pfx_x")),             
            to_float(p.get("pfx_z")),             
            to_float(p.get("plate_x")),           
            to_float(p.get("plate_z")),           
            to_int(p.get("zone")),                
            #result
            blank_to_none(p.get("type")),         
            blank_to_none(p.get("description")),  
            blank_to_none(p.get("events")),       
            #batted ball
            to_float(p.get("launch_speed")),      
            to_int(p.get("launch_angle")),        
            to_int(p.get("hit_distance_sc")),     
            blank_to_none(p.get("bb_type")), 
            #something that came up were automatic balls/strikes where no pitch is thrown
            #intentional walks, pitch clock violations
            0 if p.get("description") in ("automatic_ball", "automatic_strike") else 1,     
        ))
    return rows

#transforming box score: one row per player who appeared in the game
def transform_boxscore(raw_box, game_pk):
    rows = []
    for side in ("away", "home"):
        team_data = raw_box.get("teams", {}).get(side, {})
        team_id = team_data.get("team", {}).get("id")
        players = team_data.get("players", {})

        #batters + pitchers = players who appeared; fromkeys removes two-way duplicates
        appeared = dict.fromkeys(team_data.get("batters", []) + team_data.get("pitchers", []))

        for player_id in appeared:
            player = players.get(f"ID{player_id}", {})
            stats = player.get("stats", {})
            bat = stats.get("batting", {})
            pit = stats.get("pitching", {})

            rows.append((
                game_pk,
                player_id,
                team_id,
                player.get("position", {}).get("abbreviation"),
                to_int(player.get("battingOrder")),
                #batting
                bat.get("plateAppearances"),
                bat.get("atBats"),
                bat.get("runs"),
                bat.get("hits"),
                bat.get("doubles"),
                bat.get("triples"),
                bat.get("homeRuns"),
                bat.get("rbi"),
                bat.get("baseOnBalls"),
                bat.get("strikeOuts"),
                bat.get("hitByPitch"),
                bat.get("stolenBases"),
                #pitching
                pit.get("gamesStarted"),
                pit.get("outs"), #used instead of inningsPitched, where "4.2" means 4 2/3 innings pitched, would get kind of confusing I imagine.
                pit.get("hits"),
                pit.get("runs"),
                pit.get("earnedRuns"),
                pit.get("baseOnBalls"),
                pit.get("strikeOuts"),
                pit.get("homeRuns"),
                pit.get("battersFaced"),
                pit.get("numberOfPitches"),
                pit.get("strikes"),
            ))
    return rows

#transforming player info: one row per player
def transform_people(raw_people):
    rows = []
    for p in raw_people:
        rows.append((
            p["id"],
            p.get("fullName"),
            p.get("firstName"),
            p.get("lastName"),
            p.get("birthDate"),
            p.get("birthCountry"),
            p.get("primaryPosition", {}).get("abbreviation"),
            p.get("batSide", {}).get("code"),
            p.get("pitchHand", {}).get("code"),
            height_to_inches(p.get("height")),
            p.get("weight"),
            p.get("primaryNumber"), #this one is kept as text since "0" and "00" are different jersey numbers
            p.get("mlbDebutDate"),
            p.get("active"),
        ))
    return rows

#transforming transactions: one row per transaction
#ids and names are both kept since there are no foreign keys on this table
def transform_transactions(raw_txns):
    rows = []
    for t in raw_txns:
        person = t.get("person", {})
        from_team = t.get("fromTeam", {})
        to_team = t.get("toTeam", {})

        rows.append((
            t["id"],
            t.get("date"),
            t.get("effectiveDate"),
            t.get("resolutionDate"),
            t.get("typeCode"),
            t.get("typeDesc"),
            t.get("description"),
            person.get("id"),
            person.get("fullName"),
            from_team.get("id"),
            from_team.get("name"),
            to_team.get("id"),
            to_team.get("name"),
        ))
    return rows