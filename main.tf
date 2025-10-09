provider "aws" {
    region = "us-east-1"
}

resource "random_string" "bucket_suffix" {
    length  = 8
    special = false
    upper   = false
}

resource "aws_s3_bucket" "nyc_taxi_data_lake" {
    bucket = "nyc-taxi-data-lake-${random_string.bucket_suffix.result}"

    tags = {
        Name        = "NYC Taxi Data Lake"
        Environment = "DE Portfolio Project"
        ManagedBy   = "Terraform"
    }
}

resource "aws_s3_bucket_public_access_block" "data_lake_public_access" {
    bucket = aws_s3_bucket.nyc_taxi_data_lake.id

    block_public_acls       = true
    ignore_public_acls      = true
    block_public_policy     = true
    restrict_public_buckets = true
}

output "data_lake_bucket_name" {
    value       = aws_s3_bucket.nyc_taxi_data_lake.bucket
    description = "The name of the S3 bucket for the NYC Taxi Data Lake"
}