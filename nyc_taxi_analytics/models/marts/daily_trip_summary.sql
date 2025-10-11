{{
    config(
        materialized='table'
    )
}}

SELECT
    DATE_TRUNC('day', tpep_pickup_datetime) as trip_date,
    COUNT(*) as total_trips,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(trip_duration_minutes), 2) as avg_duration_minutes,
    ROUND(AVG(passenger_count), 2) as avg_passengers,
    ROUND(AVG(avg_speed_mph), 2) as avg_speed,
    SUM(CASE WHEN avg_speed_mph > 30 THEN 1 ELSE 0 END) as high_speed_trips,
    SUM(CASE WHEN trip_distance > 10 THEN 1 ELSE 0 END) as long_distance_trips,
    MIN(trip_distance) as min_distance,
    MAX(trip_distance) as max_distance,
    MIN(trip_duration_minutes) as min_duration,
    MAX(trip_duration_minutes) as max_duration
FROM {{ ref('stg_taxi_trips') }}
GROUP BY 1
ORDER BY 1 DESC
