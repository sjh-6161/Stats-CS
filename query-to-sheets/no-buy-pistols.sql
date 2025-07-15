SELECT t1.steam_id, t1.name, t1.pistols, COALESCE(t2.no_buy_pistols, 0) as no_buys, CAST(COALESCE(t2.no_buy_pistols, 0) AS FLOAT) / t1.pistols as rate
FROM (
  SELECT player.steam_id, player.name, COUNT(player.name) as pistols
  FROM round
  INNER JOIN buy ON round.id = buy.round_id
  INNER JOIN player ON player.id = buy.player_id
  WHERE round.ct_rounds + round.t_rounds = 0 OR round.ct_rounds + round.t_rounds = 12
  GROUP BY player.steam_id, player.name
) t1
LEFT JOIN (
  SELECT player.name, COUNT(player.name) no_buy_pistols
  FROM round
  INNER JOIN buy ON round.id = buy.round_id
  INNER JOIN player ON player.id = buy.player_id
  WHERE (round.ct_rounds + round.t_rounds = 0 OR round.ct_rounds + round.t_rounds = 12) AND (buy.balance > 500)
  GROUP BY player.name
) t2 ON t1.name = t2.name
ORDER BY rate DESC, pistols DESC;