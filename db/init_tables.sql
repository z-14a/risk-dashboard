

CREATE SCHEMA IF NOT EXISTS bronze AUTHORIZATION riskuser;

-- Make sure the user has privileges
GRANT ALL ON SCHEMA bronze TO riskuser;

-- Make sure new tables default to that ownership
ALTER DEFAULT PRIVILEGES IN SCHEMA bronze
GRANT ALL ON TABLES TO riskuser;
SET ROLE riskuser;

DROP TABLE IF EXISTS bronze.twelve_price;

CREATE TABLE bronze.twelve_price (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    ticker TEXT NOT NULL,
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    volume DOUBLE PRECISION
);
CREATE INDEX idx_price_ticker_ts ON bronze.twelve_price(ticker, ts);

DROP TABLE IF EXISTS bronze.ts_yield;
CREATE TABLE bronze.ts_yield (
    id BIGSERIAL PRIMARY KEY,
    record_date TIMESTAMPTZ NOT NULL,
    avg_interest_rate_amt DOUBLE PRECISION NOT NULL
);


CREATE SCHEMA IF NOT EXISTS clean AUTHORIZATION riskuser;

GRANT ALL ON SCHEMA clean TO riskuser;

CREATE SCHEMA IF NOT EXISTS clean;

DROP TABLE IF EXISTS clean.twelve_price;
CREATE TABLE IF NOT EXISTS clean.twelve_price (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    ticker TEXT NOT NULL,
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    volume DOUBLE PRECISION
);

DROP TABLE IF EXISTS clean.ts_yield;

CREATE TABLE IF NOT EXISTS clean.ts_yield (
    id BIGSERIAL PRIMARY KEY,
    record_date DATE NOT NULL,
    avg_interest_rate_amt DOUBLE PRECISION
);
ALTER TABLE clean.ts_yield OWNER TO riskuser;


-- give your app user rights on everything in bronze and clean
GRANT USAGE ON SCHEMA bronze, clean TO riskuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bronze, clean TO riskuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA bronze, clean TO riskuser;

-- make sure future tables and sequences inherit these rights
ALTER DEFAULT PRIVILEGES IN SCHEMA bronze, clean
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO riskuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA bronze, clean
GRANT USAGE, SELECT ON SEQUENCES TO riskuser;