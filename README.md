# NYC Taxi Data Platform

Welcome to the **NYC Taxi Data Platform** repository!  
A production-ready data engineering solution featuring cloud-based batch processing, infrastructure as code, and analytics-ready data transformations using the NYC TLC Trip Record dataset.

---

## Data Architecture

This project implements a **Lakehouse Architecture** on AWS with raw and processed data layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NYC Taxi Data Platform                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Raw Data   │───▶│  AWS Glue    │───▶│  Processed   │───▶│    dbt    │ │
│  │   (Parquet)  │    │  (PySpark)   │    │    Data      │    │  (DuckDB) │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                   │                   │       │
│         ▼                   ▼                   ▼                   ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ S3: raw-data │    │   Airflow    │    │ S3: processed│    │  marimo   │ │
│  │              │    │  Orchestrator│    │   -data      │    │ Dashboard │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Raw Layer**: Original Parquet files from NYC TLC stored in S3 `raw-data/` prefix
2. **Processed Layer**: Cleaned, validated data partitioned by `year/month` in S3 `processed-data/`
3. **Analytics Layer**: dbt models creating daily, hourly, and monthly aggregations

---

## Project Overview

This project demonstrates:

- **Infrastructure as Code**: Terraform for AWS resource provisioning
- **Cloud Data Lake**: S3-based storage with intelligent partitioning
- **Large-Scale Processing**: PySpark on AWS Glue for 100GB+ datasets
- **Orchestration**: Apache Airflow for automated ETL pipelines
- **Analytics Engineering**: dbt with DuckDB for data transformations
- **Data Visualization**: marimo for reactive Python notebooks

Ideal for showcasing expertise in: `AWS` `Terraform` `Spark` `Airflow` `dbt` `Docker` `Python` `marimo` `Data Engineering`

---

## Data Source

| Source                                                                               | Format  | Size   | Description                                                                 |
| ------------------------------------------------------------------------------------ | ------- | ------ | --------------------------------------------------------------------------- |
| [NYC TLC Trip Records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | Parquet | 100GB+ | Yellow taxi trip data including pickup/dropoff times, distances, passengers |

**Dataset Features:**

- Pickup and dropoff timestamps
- Trip distance and duration
- Passenger count
- Location IDs

---

## Tools & Technologies

| Category      | Tool                                          | Purpose                     |
| ------------- | --------------------------------------------- | --------------------------- |
| Cloud         | [AWS S3](https://aws.amazon.com/s3/)          | Data lake storage           |
| Processing    | [AWS Glue](https://aws.amazon.com/glue/)      | Serverless Spark jobs       |
| IaC           | [Terraform](https://www.terraform.io/)        | Infrastructure provisioning |
| Orchestration | [Apache Airflow](https://airflow.apache.org/) | Pipeline automation         |
| Analytics     | [dbt](https://www.getdbt.com/)                | Data transformations        |
| Query Engine  | [DuckDB](https://duckdb.org/)                 | Analytics queries           |
| Visualization | [marimo](https://marimo.io/)                  | Reactive Python notebooks   |
| Container     | [Docker](https://www.docker.com/)             | Local development           |
| Language      | [Python](https://www.python.org/)             | ETL scripts                 |

---

## Infrastructure

**AWS Resources (via Terraform):**

| Resource     | Purpose                                                            |
| ------------ | ------------------------------------------------------------------ |
| S3 Bucket    | `nyc-taxi-data-lake-*` - Data lake with raw and processed prefixes |
| AWS Glue Job | Serverless PySpark for large-scale data processing                 |
| IAM Roles    | Secure access for Glue and Airflow                                 |

**Local Services (via Docker Compose):**

| Container         | Port | Purpose           |
| ----------------- | ---- | ----------------- |
| Airflow Webserver | 8080 | DAG management UI |
| Airflow Scheduler | -    | Task scheduling   |
| Airflow Worker    | -    | Task execution    |
| PostgreSQL        | 5432 | Airflow metadata  |
| Redis             | 6379 | Celery broker     |

**Analytics (runs locally):**

| Tool   | Port | Purpose                   |
| ------ | ---- | ------------------------- |
| marimo | 2718 | Reactive Python notebooks |

---

## Airflow DAG Pipeline

```
┌────────────────────────────────────────────────────────┐
│           nyc_taxi_data_pipeline (Daily)               │
├────────────────────────────────────────────────────────┤
│                                                        │
│    ┌──────────────────────────────────────────┐        │
│    │          trigger_glue_job                │        │
│    │    (GlueJobOperator)                     │        │
│    │                                          │        │
│    │    • Reads from s3://raw-data/           │        │
│    │    • Processes with PySpark              │        │
│    │    • Writes to s3://processed-data/      │        │
│    └──────────────────────────────────────────┘        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Pipeline Features:**

- Automated daily scheduling
- AWS Glue integration
- Retry logic with 2 attempts
- Verbose logging for debugging

---

## dbt Data Models

| Layer   | Model                  | Materialization | Description                               |
| ------- | ---------------------- | --------------- | ----------------------------------------- |
| Staging | `stg_taxi_trips`       | View            | Base model reading from S3 processed data |
| Marts   | `daily_trip_summary`   | Table           | Daily aggregations with trip statistics   |
| Marts   | `hourly_trip_patterns` | Table           | Hour-of-day and day-of-week patterns      |
| Marts   | `monthly_summary`      | Table           | Monthly rollups with totals               |

**Data Quality Tests:**

- `not_null` on critical columns
- `accepted_range` for trip distance (0-100 miles)
- `accepted_range` for duration (0-1440 minutes)
- `accepted_values` for passenger count (1-8)

---

## Repository Structure

```
real-time-NYC-taxi-data-platform/
│
├── dags/                           # Airflow DAGs
│   └── nyc_taxi_pipeline_dag.py    # Main ETL pipeline
│
├── nyc_taxi_analytics/             # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml         # Source definitions
│   │   │   └── stg_taxi_trips.sql  # Staging model
│   │   └── marts/
│   │       ├── daily_trip_summary.sql
│   │       ├── hourly_trip_patterns.sql
│   │       └── monthly_summary.sql
│   ├── tests/
│   │   └── schema.yml              # Data quality tests
│   ├── dbt_project.yml             # dbt configuration
│   └── packages.yml                # dbt packages (dbt_utils)
│
├── marimo/                         # Analytics dashboards
│   └── dashboard.py                # Interactive analytics notebook
│
├── main.tf                         # Terraform infrastructure
├── docker-compose.yaml             # Local services
├── process_raw_data.py             # Local Spark processing
├── process_raw_data_glue.py        # AWS Glue job script
├── upload_to_s3.py                 # S3 upload utility
├── verify_upload.py                # Upload verification
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- [Terraform](https://www.terraform.io/downloads) installed
- Python 3.9+

### Infrastructure Setup

```bash
# 1. Clone repository
git clone https://github.com/zaid-ahmad-shaikhh/real-time-NYC-taxi-data-platform.git
cd real-time-NYC-taxi-data-platform

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Provision AWS infrastructure
terraform init
terraform apply

# 4. Start local services
docker-compose up -d

# 5. Wait for Airflow initialization (~2-3 minutes)
docker-compose logs -f airflow-init
```

### Run ETL Pipeline

1. Open Airflow UI at `http://localhost:8080`
2. Login with `airflow` / `airflow`
3. Find `nyc_taxi_data_pipeline` DAG
4. Click the **Play** button to trigger
5. Monitor the AWS Glue job execution

### Run dbt Transformations

```bash
cd nyc_taxi_analytics
dbt deps        # Install dbt packages
dbt run         # Run all models
dbt test        # Run data quality tests
```

### Run Analytics Dashboard

```bash
cd marimo
marimo edit dashboard.py
```

Open http://localhost:2718 in your browser

---

## Interactive Analytics (marimo)

The project includes a reactive analytics dashboard built with marimo:

```bash
cd marimo
marimo edit dashboard.py
```

**Features:**

- Reactive UI with auto-updating charts
- DuckDB SQL queries on processed data
- Aligned with dbt mart models
- Deployable as web app

---

## Service Access

| Service        | URL                   | Credentials           |
| -------------- | --------------------- | --------------------- |
| **Airflow**    | http://localhost:8080 | `airflow` / `airflow` |
| **marimo**     | http://localhost:2718 | (local, no auth)      |
| **PostgreSQL** | localhost:5432        | `airflow` / `airflow` |

---

## Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View Airflow logs
docker-compose logs -f airflow-scheduler

# View all service status
docker-compose ps

# Reset everything (WARNING: deletes all data)
docker-compose down -v

# Upload data to S3
python upload_to_s3.py

# Verify S3 upload
python verify_upload.py

# Run dbt models
cd nyc_taxi_analytics && dbt run

# Run dbt tests
cd nyc_taxi_analytics && dbt test

# Run marimo dashboard
marimo edit dashboard.py

# Terraform commands
terraform plan      # Preview changes
terraform apply     # Apply changes
terraform destroy   # Tear down infrastructure
```

---

## Data Processing Pipeline

### Spark Transformations

The AWS Glue job performs the following data quality operations:

| Step | Operation              | Description                                       |
| ---- | ---------------------- | ------------------------------------------------- |
| 1    | Column Standardization | Lowercase names, replace spaces                   |
| 2    | Null Filtering         | Remove records with null critical fields          |
| 3    | Duration Calculation   | Derive `trip_duration_minutes`                    |
| 4    | Quality Filters        | Remove trips >24h, >100 miles, invalid passengers |
| 5    | Speed Calculation      | Derive `avg_speed_mph`                            |
| 6    | Partitioning           | Add `year` and `month` columns                    |

### Sample Processing Summary

```
============================================================
PROCESSING SUMMARY
============================================================
Initial records:           2,847,234
After null filter:         2,842,891
After quality filter:      2,756,432
Final records written:     2,756,432
Data loss:                 3.19%
Output location:           s3://nyc-taxi-data-lake-*/processed-data/
============================================================
```

---

## Data Attribution

| Dataset                      | Source                                                                  | License       |
| ---------------------------- | ----------------------------------------------------------------------- | ------------- |
| NYC Yellow Taxi Trip Records | [NYC TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | Public Domain |

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and share this project with proper attribution.

---

## About Me

Hi! I'm **Zaid Shaikh**, an MS Computer Science student at **Northeastern University Seattle**, passionate about Data Engineering and building scalable data solutions.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/zaidshaikhengineer/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/zaid-ahmad-shaikhh)
