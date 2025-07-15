SELECT total_rounds.side, total_rounds.num_a, total_rounds.num_mid, total_rounds.num_b, ct_wins, rounds FROM (
  SELECT team_default.side, team_default.num_a, team_default.num_mid, team_default.num_b, COUNT(team_default.num_a) AS ct_wins
  FROM team_default
  INNER JOIN match
  ON team_default.match_id = match.id
  INNER JOIN (
    SELECT t_eqv.round_id, t_eqv.sum AS t_eqv, ct_eqv.sum AS ct_eqv  FROM (
      SELECT round_id, SUM(equipment_value)
      FROM buy
      WHERE buy.side = 'TERRORIST'
      GROUP BY round_id
    ) t_eqv
    INNER JOIN (
      SELECT round_id, SUM(equipment_value)
      FROM buy
      WHERE buy.side = 'CT'
      GROUP BY round_id
    ) ct_eqv
    ON t_eqv.round_id = ct_eqv.round_id
  ) buys 
  ON buys.round_id = team_default.round_id 
  INNER JOIN round
  ON round.id = team_default.round_id
  WHERE match.map = 'de_mirage' AND buys.t_eqv < 5100 AND buys.ct_eqv < 5100 AND round.winning_side = 'CT'  AND team_default.team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b')
  GROUP BY team_default.num_a, team_default.num_b, team_default.num_mid, team_default.side
) ct_wins
FULL OUTER JOIN (
  SELECT team_default.side, team_default.num_a, team_default.num_mid, team_default.num_b, COUNT(team_default.num_a) AS rounds
  FROM team_default
  INNER JOIN match
  ON team_default.match_id = match.id
  INNER JOIN (
    SELECT t_eqv.round_id, t_eqv.sum AS t_eqv, ct_eqv.sum AS ct_eqv  FROM (
      SELECT round_id, SUM(equipment_value)
      FROM buy
      WHERE buy.side = 'TERRORIST'
      GROUP BY round_id
    ) t_eqv
    INNER JOIN (
      SELECT round_id, SUM(equipment_value)
      FROM buy
      WHERE buy.side = 'CT'
      GROUP BY round_id
    ) ct_eqv
    ON t_eqv.round_id = ct_eqv.round_id
  ) buys 
  ON buys.round_id = team_default.round_id 
  INNER JOIN round
  ON round.id = team_default.round_id
  WHERE match.map = 'de_mirage' AND buys.t_eqv < 5100 AND buys.ct_eqv < 5100 AND team_default.team_id = UUID('8e414050-2084-49fc-a703-1cd32ceb071b')
  GROUP BY team_default.num_a, team_default.num_b, team_default.num_mid, team_default.side
) total_rounds 
ON ct_wins.side = total_rounds.side AND ct_wins.num_a = total_rounds.num_a AND ct_wins.num_b = total_rounds.num_b AND ct_wins.num_mid = total_rounds.num_mid
ORDER BY side, rounds DESC