import boto3

def list_s3_bucket_contents(bucket_name):
    """List all objects in an S3 bucket"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print(f"Bucket '{bucket_name}' is empty.")
            return
        
        print(f"Contents of bucket '{bucket_name}':\n")
        print(f"{'Key':<60} {'Size (MB)':<15} {'Last Modified'}")
        print("-" * 90)
        
        for obj in response['Contents']:
            size_mb = obj['Size'] / (1024 * 1024)
            print(f"{obj['Key']:<60} {size_mb:<15.2f} {obj['LastModified']}")
        
        total_size = sum(obj['Size'] for obj in response['Contents']) / (1024 * 1024)
        print("-" * 90)
        print(f"Total: {len(response['Contents'])} objects, {total_size:.2f} MB")
        
    except Exception as e:
        print(f"Error listing bucket contents: {e}")

if __name__ == "__main__":
    BUCKET_NAME = "nyc-taxi-data-lake-ygzcn2t2"
    list_s3_bucket_contents(BUCKET_NAME)
