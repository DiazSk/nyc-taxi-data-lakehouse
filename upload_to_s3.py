import boto3
import os
from pathlib import Path

def get_existing_s3_files(bucket, prefix):
    """Get list of existing files in S3 bucket with prefix"""
    s3_client = boto3.client('s3')
    existing_files = set()
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Extract just the filename from the key
                    filename = obj['Key'].split('/')[-1]
                    existing_files.add(filename)
    except Exception as e:
        print(f"Warning: Could not list existing files: {e}")
    
    return existing_files

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
    :return: Tuple of (successful_count, failed_count, skipped_count)
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"✗ Error: Directory {directory} does not exist.")
        return 0, 0, 0
    
    # Find all parquet files
    parquet_files = list(directory_path.glob("*.parquet"))
    
    if not parquet_files:
        print(f"✗ No .parquet files found in {directory}")
        return 0, 0, 0
    
    print(f"Found {len(parquet_files)} parquet file(s) in local directory\n")
    
    # Get existing files in S3 to skip re-uploads
    print("Checking existing files in S3...")
    existing_files = get_existing_s3_files(bucket, s3_prefix)
    print(f"Found {len(existing_files)} existing file(s) in S3\n")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, file_path in enumerate(parquet_files, 1):
        s3_key = f"{s3_prefix}/{file_path.name}"
        print(f"[{i}/{len(parquet_files)}]", end=" ")
        
        # Skip if file already exists in S3
        if file_path.name in existing_files:
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ⏭️  Skipping {file_path.name} ({file_size:.2f} MB) - already exists in S3")
            skipped += 1
            continue
        
        if upload_file_to_s3(str(file_path), bucket, s3_key):
            successful += 1
        else:
            failed += 1
    
    return successful, failed, skipped

if __name__ == "__main__":
    BUCKET_NAME = "nyc-taxi-data-lake-ygzcn2t2"
    DATA_DIRECTORY = "nyc_yellow_taxi_dataset"
    
    print(f"Starting batch upload to s3://{BUCKET_NAME}/raw-data/\n")
    print("=" * 70)
    
    success_count, fail_count, skip_count = upload_directory_to_s3(DATA_DIRECTORY, BUCKET_NAME)
    
    print("=" * 70)
    print(f"\nUpload Summary:")
    print(f"  ✓ Uploaded: {success_count}")
    print(f"  ⏭️  Skipped:  {skip_count} (already in S3)")
    print(f"  ✗ Failed:   {fail_count}")
    print(f"  Total:     {success_count + fail_count + skip_count}")
    
    if fail_count == 0 and (success_count > 0 or skip_count > 0):
        print(f"\n🎉 Upload complete! Data available at s3://{BUCKET_NAME}/raw-data/")
    elif fail_count > 0:
        print(f"\n⚠️  {fail_count} file(s) failed to upload. Check errors above.")