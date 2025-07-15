SELECT t1.steam_id, t1.name, t1.weapon, CAST(t1.kills as float) / (t1.kills + t2.deaths) as kd
FROM
(SELECT player.steam_id, player.name, kill.weapon, COUNT(kill.weapon) as kills FROM kill INNER JOIN player ON player.id = kill.attacker_id GROUP BY player.steam_id, player.name, kill.weapon) t1
	INNER JOIN 
(SELECT player.name, kill.victim_weapon, COUNT(kill.victim_weapon) as deaths FROM kill INNER JOIN player ON player.id = kill.victim_id GROUP BY player.name, kill.victim_weapon) t2 
ON t1.name = t2.name and t1.weapon = t2.victim_weapon
ORDER BY t1.name DESC, kd DESC;