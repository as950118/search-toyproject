CREATE INDEX IF NOT EXISTS company_name_fts_idx
  ON company_names
  USING GIN (to_tsvector('simple', name));