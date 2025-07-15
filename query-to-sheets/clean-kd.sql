SELECT player.steam_id, player.name, CAST(t1.k AS FLOAT) / t2.d as kd, CAST(t3.k AS FLOAT) / t4.d as cdk, CAST(t1.k AS FLOAT) / t2.d - CAST(t3.k AS FLOAT) / t4.d AS diff
FROM (
	SELECT attacker_id as id, COUNT(attacker_id) as k
  FROM kill
  GROUP BY attacker_id
) t1 
INNER JOIN (
  SELECT victim_id as id, COUNT(victim_id) as d
  FROM kill
  GROUP BY victim_id
) t2 ON t1.id = t2.id
INNER JOIN (
  SELECT attacker_id as id, COUNT(attacker_id) as k
  FROM kill
  WHERE (NOT assistedflash) AND (NOT attackerblind) AND (NOT attackerinair) AND (NOT noscope) AND (penetrated = 0) AND (NOT thrusmoke)
  GROUP BY attacker_id
) t3 ON t1.id = t3.id
INNER JOIN (
  SELECT victim_id as id, COUNT(victim_id) as d
  FROM kill
  WHERE (NOT assistedflash) AND (NOT attackerblind) AND (NOT attackerinair) AND (NOT noscope) AND (penetrated = 0) AND (NOT thrusmoke)
  GROUP BY victim_id
) t4 ON t1.id = t4.id
INNER JOIN player
ON player.id = t1.id
ORDER BY diff;