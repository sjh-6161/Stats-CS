SELECT t2.steam_id, t2.name, COALESCE(t1.count, 0) AS g_deaths, t2.count as deaths, CAST(COALESCE(t1.count, 0) AS FLOAT) / t2.count as gdr
FROM (
	SELECT player.name, COUNT(player.name)
  FROM kill
  INNER JOIN player ON kill.victim_id = player.id
  WHERE victim_weapon LIKE '%knife%' OR victim_weapon = 'incgrenade' OR victim_weapon = 'molotov' OR victim_weapon = 'hegrenade' OR victim_weapon = 'flashbang' OR victim_weapon = 'smokegrenade'
  GROUP BY player.name
) t1 RIGHT JOIN (
	SELECT player.steam_id, player.name, COUNT(player.name)
  FROM kill
  INNER JOIN player ON kill.victim_id = player.id
  GROUP BY player.steam_id, player.name
) t2 ON t1.name = t2.name
ORDER BY gdr