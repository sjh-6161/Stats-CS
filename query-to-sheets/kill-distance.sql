SELECT player.steam_id, player.name, AVG(distance) AS avg_distance
FROM kill
INNER JOIN player ON player.id = kill.attacker_id
GROUP BY player.steam_id, player.name
ORDER BY avg_distance;