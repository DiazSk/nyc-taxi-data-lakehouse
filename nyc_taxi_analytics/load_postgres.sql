-- Create NYC Taxi schema and tables in PostgreSQL

-- Create schema
CREATE SCHEMA IF NOT EXISTS nyc_taxi;

-- Daily trip summary table
DROP TABLE IF EXISTS nyc_taxi.daily_trip_summary CASCADE;
CREATE TABLE nyc_taxi.daily_trip_summary (
    trip_date DATE PRIMARY KEY,
    total_trips BIGINT,
    avg_distance NUMERIC(10, 2),
    avg_duration_minutes NUMERIC(10, 2),
    avg_passengers NUMERIC(10, 2),
    avg_speed NUMERIC(10, 2),
    high_speed_trips BIGINT,
    long_distance_trips BIGINT,
    min_distance NUMERIC(10, 2),
    max_distance NUMERIC(10, 2),
    min_duration NUMERIC(10, 2),
    max_duration NUMERIC(10, 2)
);

-- Load data from CSV
COPY nyc_taxi.daily_trip_summary FROM '/tmp/daily_trip_summary.csv' CSV HEADER;

-- Hourly trip patterns table
DROP TABLE IF EXISTS nyc_taxi.hourly_trip_patterns CASCADE;
CREATE TABLE nyc_taxi.hourly_trip_patterns (
    pickup_hour INTEGER,
    day_of_week INTEGER,
    day_type VARCHAR(20),
    trip_count BIGINT,
    avg_distance NUMERIC(10, 2),
    avg_duration_minutes NUMERIC(10, 2),
    avg_passengers NUMERIC(10, 2),
    PRIMARY KEY (pickup_hour, day_of_week)
);

-- Load data from CSV
COPY nyc_taxi.hourly_trip_patterns FROM '/tmp/hourly_trip_patterns.csv' CSV HEADER;

-- Monthly summary table
DROP TABLE IF EXISTS nyc_taxi.monthly_summary CASCADE;
CREATE TABLE nyc_taxi.monthly_summary (
    year INTEGER,
    month INTEGER,
    total_trips BIGINT,
    avg_distance NUMERIC(10, 2),
    avg_duration_minutes NUMERIC(10, 2),
    avg_passengers NUMERIC(10, 2),
    avg_speed_mph NUMERIC(10, 2),
    total_miles_traveled NUMERIC(12, 2),
    total_hours NUMERIC(12, 2),
    PRIMARY KEY (year, month)
);

-- Load data from CSV
COPY nyc_taxi.monthly_summary FROM '/tmp/monthly_summary.csv' CSV HEADER;

-- Verify data loaded
SELECT 'daily_trip_summary' as table_name, COUNT(*) as row_count FROM nyc_taxi.daily_trip_summary
UNION ALL
SELECT 'hourly_trip_patterns', COUNT(*) FROM nyc_taxi.hourly_trip_patterns
UNION ALL
SELECT 'monthly_summary', COUNT(*) FROM nyc_taxi.monthly_summary;
