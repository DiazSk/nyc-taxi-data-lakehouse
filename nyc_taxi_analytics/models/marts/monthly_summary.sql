{{
    config(
        materialized='table'
    )
}}

SELECT
    year,
    month,
    COUNT(*) as total_trips,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(trip_duration_minutes), 2) as avg_duration_minutes,
    ROUND(AVG(passenger_count), 2) as avg_passengers,
    ROUND(AVG(avg_speed_mph), 2) as avg_speed_mph,
    ROUND(SUM(trip_distance), 2) as total_miles_traveled,
    ROUND(SUM(trip_duration_minutes) / 60.0, 2) as total_hours
FROM {{ ref('stg_taxi_trips') }}
GROUP BY 1, 2
ORDER BY 1, 2
