-- FOR LOCAL DEVELOPMENT ONLY, DO NOT USE THESE PASSWORDS OTHERWISE
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables for hcs database
CREATE TABLE IF NOT EXISTS provider (
    provider_id VARCHAR(20) PRIMARY KEY,
    provider_name VARCHAR(255) NOT NULL,
    provider_city VARCHAR(255) NOT NULL,
    provider_state VARCHAR(2) NOT NULL,
    provider_zip_code VARCHAR(20) NOT NULL,
    provider_status VARCHAR(20) DEFAULT 'UNKNOWN'
);

CREATE INDEX IF NOT EXISTS idx_provider_zip_code ON provider(provider_zip_code);

CREATE TABLE IF NOT EXISTS provider_pricing (
    provider_pricing_id SERIAL PRIMARY KEY,
    provider_id VARCHAR(20) NOT NULL,
    ms_drg_definition VARCHAR(1000) NOT NULL,
    total_discharges INT DEFAULT 0,
    averaged_covered_charges INT DEFAULT 0,
    average_total_payments INT DEFAULT 0,
    average_medicare_payments INT DEFAULT 0,
    provider_pricing_year INT,
    FOREIGN KEY (provider_id) REFERENCES provider(provider_id)
);

CREATE INDEX IF NOT EXISTS idx_provider_pricing_ms_drg ON provider_pricing(ms_drg_definition);

CREATE TABLE IF NOT EXISTS provider_rating (
    provider_rating_id SERIAL PRIMARY KEY,
    provider_id VARCHAR(20) NOT NULL,
    provider_overall_rating INT DEFAULT 0,
    provider_star_rating INT DEFAULT 0,
    provider_rating_year INT,
    FOREIGN KEY (provider_id) REFERENCES provider(provider_id)
);

-- Function to calculate distance between zip codes using PostGIS
CREATE OR REPLACE FUNCTION calculate_zip_distance(zip1 TEXT, zip2 TEXT)
RETURNS FLOAT AS $$
DECLARE
    distance FLOAT;
BEGIN
    -- This is a simplified example - in production you'd need a zip code geocoding table
    -- For now, we'll return a mock distance
    SELECT RANDOM() * 100 INTO distance;
    RETURN distance;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to execute parameterized queries safely
CREATE OR REPLACE FUNCTION execute_safe_query(query_text TEXT, params TEXT[] DEFAULT '{}')
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    -- This is a placeholder - actual implementation would use dynamic SQL with proper parameterization
    -- For security, this should use prepared statements with parameter binding
    RETURN '{"status": "placeholder"}';
EXCEPTION
    WHEN OTHERS THEN
        RETURN '{"error": "Query execution failed"}';
END;
$$ LANGUAGE plpgsql;