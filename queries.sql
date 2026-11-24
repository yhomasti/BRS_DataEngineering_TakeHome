--row counts for every table
SELECT 'team', COUNT(*) FROM team
UNION ALL SELECT 'player', COUNT(*) FROM player
UNION ALL SELECT 'schedule', COUNT(*) FROM schedule
UNION ALL SELECT 'pitch', COUNT(*) FROM pitch
UNION ALL SELECT 'box_score', COUNT(*) FROM box_score
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions;

--looking for the hardest hit balls, with pitcher and batter names
SELECT b.full_name AS batter, p.full_name AS pitcher,
       pi.launch_speed, pi.launch_angle, pi.pa_event
FROM pitch pi
JOIN player b ON pi.batter_id = b.player_id
JOIN player p ON pi.pitcher_id = p.player_id
WHERE pi.launch_speed IS NOT NULL
ORDER BY pi.launch_speed DESC
LIMIT 10;

--most common transaction types
SELECT type_desc, COUNT(*) AS n
FROM transactions
GROUP BY type_desc
ORDER BY n DESC;

-- given one of my favorite pitchers now is Jake Bennett, whose extension rates
-- in this time frame gave the best "perceived velocity"?
SELECT p.full_name,
       ROUND(AVG(pi.extension), 1) AS avg_extension,
       ROUND(AVG(pi.release_speed), 1) AS avg_velo,
       ROUND(AVG(pi.effective_speed - pi.release_speed), 2) AS perceived_gain
FROM pitch pi
JOIN player p ON pi.pitcher_id = p.player_id
WHERE pi.is_pitch_thrown = 1
GROUP BY pi.pitcher_id
HAVING COUNT(*) >= 50
ORDER BY perceived_gain DESC
LIMIT 10;

--who had the most plate appearances in a single game
SELECT pl.full_name,
       t.abbreviation AS team,
       s.game_date,
       b.bat_pa,
       b.bat_h,
       b.bat_ab
FROM box_score b
JOIN player pl   ON b.player_id = pl.player_id
JOIN team t      ON b.team_id = t.team_id
JOIN schedule s  ON b.game_pk = s.game_pk
WHERE b.bat_pa IS NOT NULL
ORDER BY b.bat_pa DESC, b.bat_h DESC
LIMIT 10;

--most strikeouts by a pitcher in a single game
SELECT pl.full_name, s.game_date, b.pit_so, b.pit_outs, b.pit_pitches
FROM box_score b
JOIN player pl  ON b.player_id = pl.player_id
JOIN schedule s ON b.game_pk = s.game_pk
WHERE b.pit_so IS NOT NULL
ORDER BY b.pit_so DESC
LIMIT 10;

SELECT s.game_date, away.abbreviation AS away, s.away_score,
       home.abbreviation AS home, s.home_score,
       --highest scoring games, looking for TOTAL runs here.
       s.away_score + s.home_score AS total_runs
FROM schedule s
JOIN team away ON s.away_team_id = away.team_id
JOIN team home ON s.home_team_id = home.team_id
WHERE s.abstract_state = 'Final'
ORDER BY total_runs DESC
LIMIT 5;