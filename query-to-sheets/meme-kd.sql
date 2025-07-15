SELECT player.steam_id, player.name, t1.d, COALESCE(t2.md, 0) as md, CAST(COALESCE(t2.md, 0) AS FLOAT) / t1.d AS mdr
FROM (
  SELECT victim_id, COUNT(victim_id) as d
  FROM kill
  GROUP BY victim_id
) t1 
LEFT JOIN (
  SELECT victim_id, COUNT(victim_id) as md
  FROM kill
  WHERE (victim_weapon = 'bizon') OR (victim_weapon = 'scar20') OR 
  			(victim_weapon = 'g3sg1') OR (victim_weapon = 'revolver') OR 
  			(victim_weapon = 'mag7') OR (victim_weapon = 'negev') OR 
  			(victim_weapon = 'sawedoff') OR (victim_weapon = 'nova') OR
  			(victim_weapon = 'm249') OR (victim_weapon = 'xm1014')
 	GROUP BY victim_id
) t2 ON t1.victim_id = t2.victim_id
INNER JOIN player ON player.id = t1.victim_id
ORDER BY mdr DESC;