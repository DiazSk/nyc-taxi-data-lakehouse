"""
AWS Glue Job: Process NYC Taxi Data

This script handles schema evolution in NYC Taxi data by reading files
individually and unioning them with a consistent schema.
"""

import sys
from datetime import datetime

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import col, year, month, when, unix_timestamp, lit
from pyspark.sql.types import (
    StructType, StructField, LongType, DoubleType, 
    StringType, TimestampType, IntegerType
)

# Get job parameters from Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Disable vectorized reader for better type handling
spark.conf.set("spark.sql.parquet.enableVectorizedReader", "false")

print(f"\n{'='*60}")
print("NYC TAXI DATA PROCESSING JOB (AWS Glue)")
print(f"{'='*60}")
print(f"Job Name:    {args['JOB_NAME']}")
print(f"Input path:  {args['input_path']}")
print(f"Output path: {args['output_path']}")
print(f"Started at:  {datetime.now()}")
print(f"{'='*60}\n")

# Define the target schema - use the most inclusive types
# This handles schema evolution across different years of NYC Taxi data
TARGET_COLUMNS = {
    "VendorID": "long",
    "tpep_pickup_datetime": "timestamp",
    "tpep_dropoff_datetime": "timestamp",
    "passenger_count": "double",
    "trip_distance": "double",
    "RatecodeID": "double",
    "store_and_fwd_flag": "string",
    "PULocationID": "long",
    "DOLocationID": "long",
    "payment_type": "long",
    "fare_amount": "double",
    "extra": "double",
    "mta_tax": "double",
    "tip_amount": "double",
    "tolls_amount": "double",
    "improvement_surcharge": "double",
    "total_amount": "double",
    "congestion_surcharge": "double",
    "airport_fee": "double"
}

def standardize_dataframe(df):
    """
    Cast all columns to the target schema types.
    This handles schema evolution by ensuring consistent types.
    """
    # Lowercase all column names first
    for old_col in df.columns:
        df = df.withColumnRenamed(old_col, old_col.lower())
    
    # Cast each column to target type if it exists
    for col_name, col_type in TARGET_COLUMNS.items():
        col_lower = col_name.lower()
        if col_lower in [c.lower() for c in df.columns]:
            # Find the actual column name (case-insensitive)
            actual_col = [c for c in df.columns if c.lower() == col_lower][0]
            df = df.withColumn(actual_col, col(actual_col).cast(col_type))
    
    return df

try:
    # List all parquet files in the input path
    print(f"[{datetime.now()}] Listing parquet files in {args['input_path']}...")
    
    # Use Hadoop FileSystem to list files
    hadoop_conf = sc._jsc.hadoopConfiguration()
    fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
        sc._jvm.java.net.URI(args['input_path']), 
        hadoop_conf
    )
    path = sc._jvm.org.apache.hadoop.fs.Path(args['input_path'])
    
    # Get all parquet files
    file_statuses = fs.listStatus(path)
    parquet_files = [
        str(status.getPath()) 
        for status in file_statuses 
        if str(status.getPath()).endswith('.parquet')
    ]
    
    print(f"[{datetime.now()}] Found {len(parquet_files)} parquet files")
    
    if len(parquet_files) == 0:
        raise Exception(f"No parquet files found in {args['input_path']}")
    
    # Read each file individually and union them
    print(f"[{datetime.now()}] Reading and standardizing each file...")
    
    combined_df = None
    files_processed = 0
    
    for file_path in parquet_files:
        try:
            # Read single file
            file_df = spark.read.parquet(file_path)
            
            # Standardize schema
            file_df = standardize_dataframe(file_df)
            
            # Union with combined dataframe
            if combined_df is None:
                combined_df = file_df
            else:
                # Use unionByName to handle column order differences
                combined_df = combined_df.unionByName(file_df, allowMissingColumns=True)
            
            files_processed += 1
            if files_processed % 10 == 0:
                print(f"[{datetime.now()}] Processed {files_processed}/{len(parquet_files)} files...")
                
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Error processing {file_path}: {str(e)}")
            continue
    
    print(f"[{datetime.now()}] Successfully processed {files_processed} files")
    
    if combined_df is None:
        raise Exception("No files could be processed successfully")
    
    df = combined_df
    initial_count = df.count()
    print(f"[{datetime.now()}] Initial record count: {initial_count:,}")
    
    # Display schema for debugging
    print(f"[{datetime.now()}] Combined DataFrame Schema:")
    df.printSchema()

    # Data Cleaning and Transformation
    
    # Filter out rows missing critical fields
    print(f"[{datetime.now()}] Filtering out records with null critical fields...")
    df = df.filter(
        col("tpep_pickup_datetime").isNotNull() &
        col("tpep_dropoff_datetime").isNotNull() &
        col("trip_distance").isNotNull() &
        (col("trip_distance") > 0)
    )
    
    after_null_filter = df.count()
    print(f"[{datetime.now()}] Records after null filter: {after_null_filter:,} (removed {initial_count - after_null_filter:,})")

    # Derive trip duration in minutes
    print(f"[{datetime.now()}] Calculating trip duration...")
    df = df.withColumn(
        "trip_duration_minutes",
        (
            unix_timestamp(col("tpep_dropoff_datetime")) -
            unix_timestamp(col("tpep_pickup_datetime"))
        ) / 60.0
    )

    # Determine the valid year range from file names
    #    Extract years from filenames like yellow_tripdata_2022-01.parquet
    current_year = datetime.now().year
    file_years = set()
    for fp in parquet_files:
        try:
            # Extract year from filename pattern: yellow_tripdata_YYYY-MM.parquet
            fname = fp.split('/')[-1]
            yr = int(fname.split('_')[-1].split('-')[0])
            file_years.add(yr)
        except (ValueError, IndexError):
            continue
    
    min_valid_year = min(file_years) if file_years else 2020
    max_valid_year = max(max(file_years), current_year) if file_years else current_year
    print(f"[{datetime.now()}] Valid year range from filenames: {min_valid_year}-{max_valid_year}")
    
    # Apply data quality filters
    print(f"[{datetime.now()}] Applying data quality filters...")
    df = df.filter(
        (col("trip_duration_minutes") > 0) &
        (col("trip_duration_minutes") < 1440) &
        (col("trip_distance") < 100) &
        (col("passenger_count").isNotNull()) &
        (col("passenger_count") > 0) &
        (col("passenger_count") <= 8) &
        # Filter to valid years only - derived from actual file names
        # This prevents bad dates (e.g., 2001, 2099) from creating junk partitions
        (year(col("tpep_pickup_datetime")) >= min_valid_year) &
        (year(col("tpep_pickup_datetime")) <= max_valid_year)
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

    # Write processed data to S3 partitioned by year and month
    print(f"[{datetime.now()}] Writing processed data to {args['output_path']}...")
    final_count = df.count()
    print(f"[{datetime.now()}] Final record count to write: {final_count:,}")
    
    df.write \
        .partitionBy("year", "month") \
        .mode("overwrite") \
        .parquet(args['output_path'])

    print(f"[{datetime.now()}] Data processing complete successfully!")
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed:           {files_processed}")
    print(f"Initial records:           {initial_count:,}")
    print(f"After null filter:         {after_null_filter:,}")
    print(f"After quality filter:      {after_quality_filter:,}")
    print(f"Final records written:     {final_count:,}")
    print(f"Data loss:                 {((initial_count - after_quality_filter) / initial_count * 100):.2f}%")
    print(f"Output location:           {args['output_path']}")
    print(f"{'='*60}\n")
    
    job.commit()
    print(f"[{datetime.now()}] Job committed successfully.")
    
except Exception as e:
    print(f"[{datetime.now()}] ERROR: Data processing failed!")
    print(f"Error details: {str(e)}")
    import traceback
    traceback.print_exc()
    job.commit()
    sys.exit(1)
