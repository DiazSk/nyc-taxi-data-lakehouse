# dags/nyc_taxi_pipeline_dag.py

from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import GlueJobSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


# ── Configuration ───────────────────────────────────────────────────────────
# Pull bucket name from Airflow Variables (set via UI or CLI)
# Default is provided for local development
S3_BUCKET = Variable.get("nyc_taxi_s3_bucket", default_var="nyc-taxi-data-lake-ygzcn2t2")
RAW_DATA_PREFIX = "raw-data"
PROCESSED_DATA_PREFIX = "processed-data"
GLUE_JOB_NAME = "process-nyc-taxi-data"
AWS_CONN_ID = "aws_default"
AWS_REGION = "us-east-1"


# ── Task Callables ──────────────────────────────────────────────────────────
def verify_processed_data(**context):
    """
    Verify that the Glue job produced output files in the processed-data prefix.
    Pushes the file count to XCom for downstream tasks.
    """
    hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    keys = hook.list_keys(
        bucket_name=S3_BUCKET,
        prefix=f"{PROCESSED_DATA_PREFIX}/",
    )

    # Filter out the prefix-only key (the "folder" itself)
    parquet_files = [k for k in (keys or []) if k.endswith(".parquet")]
    file_count = len(parquet_files)

    if file_count == 0:
        raise ValueError(
            f"No parquet files found in s3://{S3_BUCKET}/{PROCESSED_DATA_PREFIX}/. "
            "Glue job may have failed silently."
        )

    print(f"✔ Found {file_count} processed parquet file(s)")
    context["ti"].xcom_push(key="processed_file_count", value=file_count)


def log_pipeline_summary(**context):
    """
    Pull metadata from upstream tasks and log a summary of the pipeline run.
    This acts as a final audit step.
    """
    ti = context["ti"]
    file_count = ti.xcom_pull(
        task_ids="verify_processed_output", key="processed_file_count"
    )

    summary = f"""
{'=' * 60}
PIPELINE RUN SUMMARY
{'=' * 60}
Run ID:              {context['run_id']}
Execution Date:      {context['logical_date']}
S3 Bucket:           {S3_BUCKET}
Raw Data Prefix:     {RAW_DATA_PREFIX}
Processed Prefix:    {PROCESSED_DATA_PREFIX}
Processed Files:     {file_count}
Status:              ✔ SUCCESS
{'=' * 60}
"""
    print(summary)


# ── DAG Definition ──────────────────────────────────────────────────────────
with DAG(
    dag_id="nyc_taxi_data_pipeline",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    schedule="@daily",
    tags=["nyc-taxi", "glue", "data-engineering"],
    description="Daily NYC Taxi data processing pipeline using AWS Glue",
    doc_md="""
    ### NYC Taxi Data Pipeline

    **Owner:** Data Engineering

    This DAG orchestrates the daily processing of NYC Yellow Taxi trip data:

    1. **Sense** raw data landing in S3
    2. **Process** via AWS Glue (PySpark) — cleaning, validation, partitioning
    3. **Verify** that processed output was written successfully
    4. **Log** a pipeline run summary for auditability
    """,
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": pendulum.duration(minutes=5),
    },
) as dag:

    # ── Task 1: Wait for raw data to be available in S3 ─────────────────────
    sense_raw_data = S3KeySensor(
        task_id="sense_raw_data",
        bucket_name=S3_BUCKET,
        bucket_key=f"{RAW_DATA_PREFIX}/*.parquet",
        wildcard_match=True,
        aws_conn_id=AWS_CONN_ID,
        timeout=60 * 30,  # 30 minute timeout
        poke_interval=60,  # Check every 60 seconds
        mode="poke",
    )

    # ── Task 2: Trigger the AWS Glue job (don't wait - use sensor instead) ──
    trigger_glue_job = GlueJobOperator(
        task_id="trigger_glue_job",
        job_name=GLUE_JOB_NAME,
        script_args={
            "--input_path": f"s3://{S3_BUCKET}/{RAW_DATA_PREFIX}/",
            "--output_path": f"s3://{S3_BUCKET}/{PROCESSED_DATA_PREFIX}/",
        },
        aws_conn_id=AWS_CONN_ID,
        region_name=AWS_REGION,
        wait_for_completion=False,  # Don't wait - sensor will handle this
        verbose=True,
    )

    # ── Task 2b: Wait for Glue job to complete ────────────────────────────────
    wait_for_glue_job = GlueJobSensor(
        task_id="wait_for_glue_job",
        job_name=GLUE_JOB_NAME,
        run_id="{{ task_instance.xcom_pull(task_ids='trigger_glue_job') }}",
        aws_conn_id=AWS_CONN_ID,
        timeout=60 * 60,  # 60 minute timeout
        poke_interval=60,  # Check every 60 seconds
    )

    # ── Task 3: Verify processed data exists in S3 ──────────────────────────
    verify_processed_output = PythonOperator(
        task_id="verify_processed_output",
        python_callable=verify_processed_data,
    )

    # ── Task 4: Log pipeline summary ────────────────────────────────────────
    pipeline_summary = PythonOperator(
        task_id="pipeline_summary",
        python_callable=log_pipeline_summary,
    )

    # ── Task Dependencies ───────────────────────────────────────────────────
    sense_raw_data >> trigger_glue_job >> wait_for_glue_job >> verify_processed_output >> pipeline_summary