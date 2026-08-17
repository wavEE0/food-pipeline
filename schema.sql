-- run this once to set up the database tables
-- psql -U postgres -d food_pipeline -f schema.sql

CREATE TABLE IF NOT EXISTS foods (
    id          SERIAL PRIMARY KEY,
    barcode     VARCHAR(50)  UNIQUE NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    calories    NUMERIC(8, 2),
    protein     NUMERIC(8, 2),
    carbs       NUMERIC(8, 2),
    fat         NUMERIC(8, 2),
    fibre       NUMERIC(8, 2),
    sodium      NUMERIC(8, 2),
    category    VARCHAR(200),
    loaded_at   TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- track every pipeline run so we know what happened
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id               SERIAL PRIMARY KEY,
    started_at       TIMESTAMP NOT NULL,
    completed_at     TIMESTAMP,
    records_fetched  INTEGER DEFAULT 0,
    records_loaded   INTEGER DEFAULT 0,
    records_rejected INTEGER DEFAULT 0,
    status           VARCHAR(20) DEFAULT 'running',
    error_message    TEXT
);

-- barcode is how we look things up, so index it
CREATE INDEX IF NOT EXISTS idx_foods_barcode ON foods(barcode);
