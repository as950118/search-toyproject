CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_company_names_name_trgm ON company_names USING gin (name gin_trgm_ops);
