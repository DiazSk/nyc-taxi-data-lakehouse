{{
    config(
        materialized='view'
    )
}}

SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    trip_duration_minutes,
    avg_speed_mph,
    year,
    month
FROM read_parquet('s3://nyc-taxi-data-lake-ygzcn2t2/processed-data/**/*.parquet')
WHERE trip_duration_minutes > 0
  AND trip_distance > 0