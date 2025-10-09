import boto3
import os
from pathlib import Path

def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        file_size = os.path.getsize(file_name) / (1024 * 1024)  # Size in MB
        print(f"  Uploading {os.path.basename(file_name)} ({file_size:.2f} MB)...", end=" ")
        s3_client.upload_file(file_name, bucket, object_name)
        print("✓")
        return True
    except Exception as e:
        print(f"✗\n  Error: {e}")
        return False

def upload_directory_to_s3(directory, bucket, s3_prefix="raw-data"):
    """Upload all parquet files from a directory to S3
    
    :param directory: Local directory containing files
    :param bucket: S3 bucket name
    :param s3_prefix: S3 prefix/folder for uploaded files
    :return: Tuple of (successful_count, failed_count)
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"✗ Error: Directory {directory} does not exist.")
        return 0, 0
    
    # Find all parquet files
    parquet_files = list(directory_path.glob("*.parquet"))
    
    if not parquet_files:
        print(f"✗ No .parquet files found in {directory}")
        return 0, 0
    
    print(f"Found {len(parquet_files)} parquet file(s) to upload\n")
    
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(parquet_files, 1):
        s3_key = f"{s3_prefix}/{file_path.name}"
        print(f"[{i}/{len(parquet_files)}]", end=" ")
        
        if upload_file_to_s3(str(file_path), bucket, s3_key):
            successful += 1
        else:
            failed += 1
    
    return successful, failed

if __name__ == "__main__":
    BUCKET_NAME = "nyc-taxi-data-lake-p7laxsjo"
    DATA_DIRECTORY = "nyc_yellow_taxi_dataset"
    
    print(f"Starting batch upload to s3://{BUCKET_NAME}/raw-data/\n")
    print("=" * 70)
    
    success_count, fail_count = upload_directory_to_s3(DATA_DIRECTORY, BUCKET_NAME)
    
    print("=" * 70)
    print(f"\nUpload Summary:")
    print(f"  ✓ Successful: {success_count}")
    print(f"  ✗ Failed: {fail_count}")
    print(f"  Total: {success_count + fail_count}")
    
    if fail_count == 0 and success_count > 0:
        print(f"\n🎉 All files uploaded successfully to s3://{BUCKET_NAME}/raw-data/")
    elif fail_count > 0:
        print(f"\n⚠️  {fail_count} file(s) failed to upload. Check errors above.")