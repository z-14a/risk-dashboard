-- Database: market_risk

DROP DATABASE IF EXISTS market_risk;

CREATE DATABASE market_risk
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

COMMENT ON DATABASE market_risk
    IS 'Personal Project. Will store data on stock data and treasury yields';

CREATE USER riskuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE market_risk TO riskuser;
