{{
    config(
        materialized='table'
    )
}}

SELECT
    EXTRACT(HOUR FROM tpep_pickup_datetime) as pickup_hour,
    EXTRACT(DOW FROM tpep_pickup_datetime) as day_of_week,
    CASE 
        WHEN EXTRACT(DOW FROM tpep_pickup_datetime) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    COUNT(*) as trip_count,
    ROUND(AVG(trip_distance), 2) as avg_distance,
    ROUND(AVG(trip_duration_minutes), 2) as avg_duration_minutes,
    ROUND(AVG(passenger_count), 2) as avg_passengers
FROM {{ ref('stg_taxi_trips') }}
GROUP BY 1, 2, 3
ORDER BY 1, 2
