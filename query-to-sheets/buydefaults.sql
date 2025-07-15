SELECT total_rounds.side, total_rounds.num_a, total_rounds.num_mid, total_rounds.num_b, ct_wins.ct_win, rounds FROM (
  SELECT team_default.side, team_default.num_a, team_default.num_mid, team_default.num_b, COUNT(team_default.num_a) AS ct_win
  FROM team_default
  INNER JOIN match
  ON team_default.match_id = match.id
  INNER JOIN (
    SELECT round_id, team_id, SUM(equipment_value)
    FROM buy
    WHERE team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b')
    GROUP BY round_id, team_id
  ) buys 
  ON buys.round_id = team_default.round_id 
  INNER JOIN round
  ON round.id = team_default.round_id
  WHERE match.map = 'de_mirage' AND buys.sum < 10000 AND team_default.team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b') AND round.winning_side = 'CT' AND round.t_rounds + round.ct_rounds != 0 AND round.t_rounds + round.ct_rounds != 12
  GROUP BY team_default.num_a, team_default.num_b, team_default.num_mid, team_default.side
) ct_wins
FULL OUTER JOIN (
  SELECT team_default.side, team_default.num_a, team_default.num_mid, team_default.num_b, COUNT(team_default.num_a) AS rounds
  FROM team_default
  INNER JOIN match
  ON team_default.match_id = match.id
  INNER JOIN (
    SELECT round_id, team_id, SUM(equipment_value)
    FROM buy
    WHERE team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b')
    GROUP BY round_id, team_id
  ) buys 
  ON buys.round_id = team_default.round_id 
  INNER JOIN round
  ON round.id = team_default.round_id
  WHERE match.map = 'de_mirage' AND buys.sum < 10000 AND team_default.team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b') AND round.t_rounds + round.ct_rounds != 0 AND round.t_rounds + round.ct_rounds != 12
  GROUP BY team_default.num_a, team_default.num_b, team_default.num_mid, team_default.side
) total_rounds 
ON ct_wins.side = total_rounds.side AND ct_wins.num_a = total_rounds.num_a AND ct_wins.num_b = total_rounds.num_b AND ct_wins.num_mid = total_rounds.num_mid
ORDER BY side, rounds DESC