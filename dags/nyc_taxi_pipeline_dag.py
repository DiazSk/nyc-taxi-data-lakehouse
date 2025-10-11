# dags/nyc_taxi_pipeline_dag.py

from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

with DAG(
    dag_id="nyc_taxi_data_pipeline",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    schedule="@daily",
    tags=["nyc-taxi", "glue", "data-engineering"],
    description="Daily NYC Taxi data processing pipeline using AWS Glue",
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": pendulum.duration(minutes=5),
    },
) as dag:
    # This task triggers the AWS Glue job you already created
    trigger_glue_job = GlueJobOperator(
        task_id="trigger_glue_job",
        job_name="process-nyc-taxi-data",  # The exact name of your Glue job
        script_args={
            "--input_path": "s3://nyc-taxi-data-lake-ygzcn2t2/raw-data/",
            "--output_path": "s3://nyc-taxi-data-lake-ygzcn2t2/processed-data/",
        },
        aws_conn_id="aws_default",  # This uses the default AWS connection
        region_name="us-east-1",
        wait_for_completion=True,  # Wait for the Glue job to complete
        verbose=True,  # This will print the Glue job logs in the Airflow task logs
        deferrable=False,  # Run synchronously
        # Increase retry delay to avoid concurrent run issues
        retry_delay=pendulum.duration(minutes=10),
    )