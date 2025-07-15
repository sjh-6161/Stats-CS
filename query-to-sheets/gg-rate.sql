SELECT player.steam_id, t2.name, COALESCE(t1.ggs, 0) as ggs, t2.games, CAST(COALESCE(t1.ggs, 0) AS FLOAT) / games as ggr
FROM (
  SELECT player.id, player.name, COUNT(player.name) AS ggs
  FROM message
  INNER JOIN player 
  ON message.player_id = player.id
  WHERE LOWER(message.message) LIKE '%gg%'
  GROUP BY player.name, player.id
) t1 RIGHT JOIN (
  SELECT player.name, COUNT(player.name) as games FROM (
    SELECT buy.match_id, buy.player_id
    FROM buy
    GROUP BY buy.match_id, buy.player_id
  ) t3 
  INNER JOIN player
  ON t3.player_id = player.id
  GROUP BY player.name
) t2 ON t1.name = t2.name
INNER JOIN player ON player.name = t2.name
WHERE player.name != 'Stach'
ORDER BY ggr DESC