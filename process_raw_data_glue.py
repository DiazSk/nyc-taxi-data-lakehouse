"""
AWS Glue Job: Process NYC Taxi Data

This script is optimized for AWS Glue and processes raw NYC taxi parquet files
from S3, applies data quality filters, and writes partitioned output.
"""

import sys
from datetime import datetime

try:
    from awsglue.transforms import *
    from awsglue.utils import getResolvedOptions
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from pyspark.context import SparkContext
    from pyspark.sql.functions import col, year, month, when, unix_timestamp
except ImportError:
    # For local development - mock the AWS Glue imports
    print("Running in local development mode - AWS Glue imports not available")
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, year, month, when, unix_timestamp
    
    def getResolvedOptions(argv, options):
        # Mock function for local testing
        return {
            'JOB_NAME': 'test_job',
            'input_path': 's3://test-bucket/input/',
            'output_path': 's3://test-bucket/output/'
        }

# Get job parameters from Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print(f"\n{'='*60}")
print("NYC TAXI DATA PROCESSING JOB (AWS Glue)")
print(f"{'='*60}")
print(f"Job Name:    {args['JOB_NAME']}")
print(f"Input path:  {args['input_path']}")
print(f"Output path: {args['output_path']}")
print(f"Started at:  {datetime.now()}")
print(f"{'='*60}\n")

try:
    # Read the raw data from S3
    print(f"[{datetime.now()}] Reading raw taxi data from {args['input_path']}")
    df = spark.read.parquet(args['input_path'])
    
    initial_count = df.count()
    print(f"[{datetime.now()}] Initial record count: {initial_count:,}")
    
    # Display schema for debugging
    print(f"[{datetime.now()}] Schema:")
    df.printSchema()

    # Data Cleaning and Transformation

    # 1. Standardize column names (lowercase, replace spaces with underscores)
    print(f"[{datetime.now()}] Standardizing column names...")
    standardized_columns = [c.lower().replace(" ", "_") for c in df.columns]
    df = df.toDF(*standardized_columns)

    # 2. Handle missing values in critical columns
    print(f"[{datetime.now()}] Filtering out records with null critical fields...")
    df = df.filter(
        col("tpep_pickup_datetime").isNotNull() &
        col("tpep_dropoff_datetime").isNotNull() &
        col("trip_distance").isNotNull() &
        (col("trip_distance") > 0)  # Remove zero/negative distances
    )
    
    after_null_filter = df.count()
    print(f"[{datetime.now()}] Records after null filter: {after_null_filter:,} (removed {initial_count - after_null_filter:,})")

    # 3. Derive trip duration (in minutes)
    print(f"[{datetime.now()}] Calculating trip duration...")
    df = df.withColumn(
        "trip_duration_minutes",
        (
            unix_timestamp(col("tpep_dropoff_datetime")) -
            unix_timestamp(col("tpep_pickup_datetime"))
        ) / 60.0
    )

    # 4. Data Quality Filters
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

    # 5. Add additional useful columns
    print(f"[{datetime.now()}] Adding derived columns...")
    df = df.withColumn("avg_speed_mph", 
        when(col("trip_duration_minutes") > 0, 
             (col("trip_distance") / (col("trip_duration_minutes") / 60.0)))
        .otherwise(0)
    )

    # 6. Create partitioning columns
    print(f"[{datetime.now()}] Creating partition columns...")
    df = df.withColumn("year", year(col("tpep_pickup_datetime")))
    df = df.withColumn("month", month(col("tpep_pickup_datetime")))

    # 7. Write the processed data to S3, partitioned by year and month
    print(f"[{datetime.now()}] Writing processed data to {args['output_path']}, partitioned by year and month...")
    print(f"[{datetime.now()}] Final record count to write: {df.count():,}")
    
    df.write \
        .partitionBy("year", "month") \
        .mode("overwrite") \
        .parquet(args['output_path'])

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
    print(f"Output location:           {args['output_path']}")
    print(f"{'='*60}\n")
    
    job.commit()
    print(f"[{datetime.now()}] Job committed successfully.")
    
except Exception as e:
    print(f"[{datetime.now()}] ✗ ERROR: Data processing failed!")
    print(f"Error details: {str(e)}")
    import traceback
    traceback.print_exc()
    job.commit()  # Commit even on failure to release resources
    sys.exit(1)
