-- Migration: Split tournament column into tournament, stage, and season

-- Add new columns
ALTER TABLE match ADD COLUMN stage varchar(500);
ALTER TABLE match ADD COLUMN season int;

-- Populate from existing tournament values (format: "S{season} {stage}")
-- e.g. "S19 Recruit Combines" -> tournament="CSC", stage="Recruit Combines", season=19
UPDATE match
SET tournament = 'CSC',
    stage = SUBSTRING(tournament FROM '^S\d+\s+(.+)$'),
    season = CAST(SUBSTRING(tournament FROM '^S(\d+)\s+') AS int);

-- Add NOT NULL constraints after populating
ALTER TABLE match ALTER COLUMN stage SET NOT NULL;
ALTER TABLE match ALTER COLUMN season SET NOT NULL;
