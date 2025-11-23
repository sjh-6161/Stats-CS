WITH pistol_stats AS (
  WITH pms AS (
    SELECT victim_id, match.tournament, COUNT(victim_id) FROM (
      SELECT DISTINCT kill.victim_id, kill.match_id
      FROM kill
      INNER JOIN match ON match.id = kill.match_id
    ) t1
    INNER JOIN match ON match.id = t1.match_id
    GROUP BY victim_id, match.tournament
  )
  SELECT player.steam_id, player.name, pms.tournament, COALESCE(t1.pk, 0), COALESCE(t2.pd, 0), pms.count * 2 AS r, (CAST(COALESCE(t1.pk, 0) AS FLOAT) -  COALESCE(t2.pd, 0)) / (pms.count * 2) AS pkd
  FROM (
    SELECT kill.attacker_id, match.tournament, COUNT(kill.attacker_id) AS pk
    FROM kill
    INNER JOIN round ON round.id = kill.round_id
    INNER JOIN match ON match.id = kill.match_id
    WHERE (round.t_rounds + round.ct_rounds = 0 OR round.t_rounds + round.ct_rounds = 12)
    GROUP BY kill.attacker_id, match.tournament
  ) t1 FULL OUTER JOIN (
    SELECT kill.victim_id, match.tournament, COUNT(kill.victim_id) AS pd
    FROM kill
    INNER JOIN round ON round.id = kill.round_id
    INNER JOIN match ON match.id = kill.match_id
    WHERE (round.t_rounds + round.ct_rounds = 0 OR round.t_rounds + round.ct_rounds = 12)
    GROUP BY kill.victim_id, match.tournament
  ) t2 ON t1.attacker_id = t2.victim_id AND t1.tournament = t2.tournament
  INNER JOIN player ON player.steam_id = t1.attacker_id OR player.steam_id = t2.victim_id
  INNER JOIN pms ON player.steam_id = pms.victim_id AND (pms.tournament = t1.tournament OR pms.tournament = t2.tournament)
  ORDER BY t1.tournament, pkd DESC
), 
team_diff_stats AS (
  SELECT team_kd.steam_id, team_kd.name, team_kd.tournament,
    ((CAST(team_kd.kills AS FLOAT) - player_kd.kills) - (team_kd.deaths - player_kd.deaths)) / (team_kd.r * 4) AS tkd, 
    (CAST(player_kd.kills AS FLOAT) - player_kd.deaths) / team_kd.r AS pkd, 
    ((CAST(player_kd.kills AS FLOAT) - player_kd.deaths) / team_kd.r) - (((CAST(team_kd.kills AS FLOAT) - player_kd.kills) - (team_kd.deaths - player_kd.deaths)) / (team_kd.r * 4)) AS diff 
  FROM (
    SELECT player.steam_id, player.name, match.tournament, SUM(kills) AS kills, SUM(deaths) AS deaths, SUM(rounds.count) AS r
    FROM (
      SELECT kill.match_id, kill.attacker_team_id AS team_id, COUNT(kill.match_id) AS kills
      FROM kill
      WHERE kill.attacker_team_id IS NOT NULL
      GROUP BY kill.match_id, kill.attacker_team_id
    ) t1 INNER JOIN (
      SELECT kill.match_id, kill.victim_team_id AS team_id, COUNT(kill.match_id) AS deaths
      FROM kill
      GROUP BY kill.match_id, kill.victim_team_id
    ) t2 ON t1.match_id = t2.match_id AND t1.team_id = t2.team_id
    INNER JOIN (
      SELECT DISTINCT kill.match_id, kill.attacker_team_id AS team_id, kill.attacker_id AS player_id
      FROM kill
      INNER JOIN match ON match.id = kill.match_id
      WHERE attacker_team_id IS NOT NULL
    ) matches ON matches.match_id = t1.match_id AND matches.team_id = t1.team_id
    INNER JOIN player ON player.steam_id = player_id
    INNER JOIN match ON match.id = t1.match_id
    INNER JOIN (
      SELECT match_id, COUNT(match_id)
      FROM round
      GROUP BY match_id
    ) rounds ON t1.match_id = rounds.match_id
    GROUP BY player.name, player.steam_id, match.tournament
  ) team_kd INNER JOIN (
    SELECT t1.name, t1.tournament, kills, deaths
    FROM (
      SELECT player.name, match.tournament, COUNT(player.name) AS kills
      FROM kill
      INNER JOIN player ON player.steam_id = kill.attacker_id
      INNER JOIN match ON match.id = kill.match_id
      GROUP BY player.name, match.tournament
    ) t1 INNER JOIN (
      SELECT player.name, match.tournament, COUNT(player.name) AS deaths
      FROM kill
      INNER JOIN player ON player.steam_id = kill.victim_id
      INNER JOIN match ON match.id = kill.match_id
      GROUP BY player.name, match.tournament
    ) t2 ON t1.name = t2.name AND t1.tournament = t2.tournament
  ) player_kd ON team_kd.name = player_kd.name AND team_kd.tournament = player_kd.tournament
  ORDER BY team_kd.tournament, diff DESC
),
pistol_hs AS (
  SELECT t1.attacker_id, t1.tournament, hits, COALESCE(hs, 0) AS hs, CAST(COALESCE(hs, 0) AS FLOAT) / hits AS hsbs
  FROM (
    SELECT damage.attacker_id, match.tournament, COUNT(damage.attacker_id) AS hits
    FROM damage
    INNER JOIN round ON round.id = damage.round_id
    INNER JOIN match ON match.id = damage.match_id
    WHERE (round.t_rounds + round.ct_rounds = 0 OR round.t_rounds + round.ct_rounds = 12) AND damage.attacker_id IS NOT NULL
    GROUP BY damage.attacker_id, match.tournament
  ) t1 FULL OUTER JOIN (
    SELECT damage.attacker_id, match.tournament, COUNT(damage.attacker_id) as hs
    FROM damage
    INNER JOIN round ON round.id = damage.round_id
    INNER JOIN match ON match.id = damage.match_id
    WHERE (round.t_rounds + round.ct_rounds = 0 OR round.t_rounds + round.ct_rounds = 12) AND damage.hitgroup = 'head' AND damage.attacker_id IS NOT NULL
    GROUP BY damage.attacker_id, match.tournament
  ) t2 ON t1.attacker_id = t2.attacker_id AND t1.tournament = t2.tournament
)
SELECT team_diff_stats.tournament, team_diff_stats.steam_id, team_diff_stats.name, team_diff_stats.diff, pistol_stats.pkd, pistol_hs.hsbs
FROM pistol_stats
FULL OUTER JOIN team_diff_stats
ON pistol_stats.steam_id = team_diff_stats.steam_id AND pistol_stats.tournament = team_diff_stats.tournament
FULL OUTER JOIN pistol_hs
ON pistol_stats.steam_id = pistol_hs.attacker_id AND pistol_stats.tournament = pistol_hs.tournament
ORDER BY name