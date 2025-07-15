SELECT t1.steam_id, t1.name, CAST(t1.kills as float) / t2.deaths as kd
FROM
	(SELECT player.steam_id, player.name, COUNT(player.name) AS kills FROM kill INNER JOIN player on player.id = kill.attacker_id GROUP BY player.steam_id, player.name) t1
INNER JOIN
	(SELECT player.name, COUNT(player.name) AS deaths FROM kill INNER JOIN player on player.id = kill.victim_id GROUP BY player.name) t2 ON t1.name = t2.name
ORDER BY kd DESC;