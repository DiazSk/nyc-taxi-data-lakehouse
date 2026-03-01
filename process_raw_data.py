import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, when
from datetime import datetime

def process_taxi_data(spark, input_path, output_path):
    """
    Reads raw taxi data, performs cleaning and transformation, and writes the processed data back to S3, partitioned by date.

    :param spark: SparkSession object
    :param input_path: S3 path to the raw data
    :param output_path: S3 path to write the processed data
    """
    try:
        # Read the raw data from S3
        print(f"[{datetime.now()}] Reading raw taxi data from {input_path}")
        df = spark.read.parquet(input_path)
        
        initial_count = df.count()
        print(f"[{datetime.now()}] Initial record count: {initial_count:,}")
        
        # Display schema for debugging
        print(f"[{datetime.now()}] Schema:")
        df.printSchema()

        # Data Cleaning and Transformation

        # Standardize column names (lowercase, replace spaces with underscores)
        print(f"[{datetime.now()}] Standardizing column names...")
        standardized_columns = [c.lower().replace(" ", "_") for c in df.columns]
        df = df.toDF(*standardized_columns)

        # Filter out rows missing critical fields
        print(f"[{datetime.now()}] Filtering out records with null critical fields...")
        df = df.filter(
            col("tpep_pickup_datetime").isNotNull() &
            col("tpep_dropoff_datetime").isNotNull() &
            col("trip_distance").isNotNull() &
            (col("trip_distance") > 0)  # Remove zero/negative distances
        )
        
        after_null_filter = df.count()
        print(f"[{datetime.now()}] Records after null filter: {after_null_filter:,} (removed {initial_count - after_null_filter:,})")

        # Derive trip duration in minutes
        # Timestamps are already in timestamp format in parquet, no need for to_timestamp()
        print(f"[{datetime.now()}] Calculating trip duration...")
        df = df.withColumn(
            "trip_duration_minutes",
            ((col("tpep_dropoff_datetime").cast("long") - col("tpep_pickup_datetime").cast("long")) / 60.0)
        )

        # Apply data quality filters
        print(f"[{datetime.now()}] Applying data quality filters...")
        df = df.filter(
            (col("trip_duration_minutes") > 0) &  # Remove negative/zero durations
            (col("trip_duration_minutes") < 1440) &  # Remove trips longer than 24 hours
            (col("trip_distance") < 100) &  # Remove unrealistic distances (>100 miles)
            (col("passenger_count").isNotNull()) &
            (col("passenger_count") > 0) &
            (col("passenger_count") <= 8)  # Reasonable passenger count
        )
        
        after_quality_filter = df.count()
        print(f"[{datetime.now()}] Records after quality filters: {after_quality_filter:,} (removed {after_null_filter - after_quality_filter:,})")

        # Add derived metrics
        print(f"[{datetime.now()}] Adding derived columns...")
        df = df.withColumn("avg_speed_mph", 
            when(col("trip_duration_minutes") > 0, 
                 (col("trip_distance") / (col("trip_duration_minutes") / 60.0)))
            .otherwise(0)
        )

        # Create partitioning columns
        print(f"[{datetime.now()}] Creating partition columns...")
        df = df.withColumn("year", year(col("tpep_pickup_datetime")))
        df = df.withColumn("month", month(col("tpep_pickup_datetime")))

        # Select final columns (exclude partition columns from data to avoid redundancy)
        # Note: Spark will still use them for partitioning, but they won't be duplicated in parquet files
        final_columns = [c for c in df.columns if c not in ["year", "month"]]
        df_final = df.select(final_columns + ["year", "month"])

        # Write the processed data to S3, partitioned by year and month
        print(f"[{datetime.now()}] Writing processed data to {output_path}, partitioned by year and month...")
        print(f"[{datetime.now()}] Final record count to write: {df_final.count():,}")
        
        df_final.write \
            .partitionBy("year", "month") \
            .mode("overwrite") \
            .parquet(output_path)

        print(f"[{datetime.now()}] ✓ Data processing complete successfully!")
        
        # Summary statistics
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Initial records:           {initial_count:,}")
        print(f"After null filter:         {after_null_filter:,}")
        print(f"After quality filter:      {after_quality_filter:,}")
        print(f"Final records written:     {after_quality_filter:,}")
        print(f"Data loss:                 {((initial_count - after_quality_filter) / initial_count * 100):.2f}%")
        print(f"Output location:           {output_path}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ✗ ERROR: Data processing failed!")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process raw NYC taxi data and write processed data to S3.")
    parser.add_argument("--input-path", type=str, required=True, 
                       help="S3 path to the raw data (e.g., s3://bucket/raw-data/)")
    parser.add_argument("--output-path", type=str, required=True, 
                       help="S3 path to write the processed data (e.g., s3://bucket/processed-data/)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("NYC TAXI DATA PROCESSING JOB")
    print(f"{'='*60}")
    print(f"Input path:  {args.input_path}")
    print(f"Output path: {args.output_path}")
    print(f"Started at:  {datetime.now()}")
    print(f"{'='*60}\n")

    # Initialize Spark session with optimizations
    spark = SparkSession.builder \
        .appName("NYCTaxiDataProcessing") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()
    
    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")

    success = process_taxi_data(spark, args.input_path, args.output_path)
    
    spark.stop()
    
    print(f"\n[{datetime.now()}] Job finished.")
    sys.exit(0 if success else 1)
