SELECT t1.steam_id, t1.name, t1.k, t2.d, t1.k - t2.d as diff, CAST(t3.rounds AS FLOAT), (CAST(t1.k as float) - t2.d) / t3.rounds as diffr
FROM (
	SELECT player.steam_id, player.name, COUNT(player.name) as k
	FROM kill 
  INNER JOIN player ON kill.attacker_id = player.id
  INNER JOIN round ON kill.round_id = round.id
  WHERE (kill.attacker_team = 'CT' AND kill.ct_alive - kill.t_alive < 2 AND round.winning_side = 'CT') OR (kill.attacker_team = 'TERRORIST' AND kill.t_alive - kill.ct_alive < 2 AND round.winning_side = 'TERRORIST') AND (kill.trade = false)
  GROUP BY player.steam_id, player.name
) t1 
INNER JOIN (
	SELECT player.name, COUNT(player.name) as d
	FROM kill 
  INNER JOIN player ON kill.victim_id = player.id
  INNER JOIN round ON kill.round_id = round.id
  WHERE (kill.victim_team = 'CT' AND kill.t_alive - kill.ct_alive < 2 AND round.winning_side = 'TERRORIST') OR (kill.victim_team = 'TERRORIST' AND kill.ct_alive - kill.t_alive < 2 AND round.winning_side = 'CT') AND (kill.traded = false)
  GROUP BY player.name
) t2 ON t1.name = t2.name 
INNER JOIN (
  SELECT t31.name, SUM(t32.rounds) as rounds
  FROM (
    SELECT kill.match_id, player.name
    FROM kill
    INNER JOIN player on kill.victim_id = player.id
    GROUP BY kill.match_id, player.name
  ) t31 
  INNER JOIN (
    SELECT match_id, COUNT(match_id) as rounds
    FROM round
    GROUP BY match_id
  ) t32 on t31.match_id = t32.match_id
  GROUP BY t31.name
) t3 ON t1.name = t3.name
ORDER BY diff DESC;