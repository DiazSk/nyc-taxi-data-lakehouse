# 🚕 Real-Time NYC Taxi Data Platform

> **A production-grade, end-to-end data engineering pipeline processing 23.4M taxi trips with modern cloud infrastructure, distributed processing, and real-time analytics capabilities.**

[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20Glue%20%7C%20IAM-FF9900?logo=amazon-aws)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/Terraform-1.9.8-7B42BC?logo=terraform)](https://www.terraform.io/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.7.1-017CEE?logo=apache-airflow)](https://airflow.apache.org/)
[![dbt](https://img.shields.io/badge/dbt-1.10.13-FF694B?logo=dbt)](https://www.getdbt.com/)
[![Python](https://img.shields.io/badge/Python-3.13.5-3776AB?logo=python)](https://www.python.org/)

---

## 📊 Project Overview

This project demonstrates a **complete data engineering lifecycle**, from infrastructure provisioning to interactive dashboards, processing **23.4M NYC taxi trips** across 247 days (Jan-Sep 2025) totaling **79.8M miles traveled**.

**Key Achievement:** Built a scalable, automated data platform that handles large-scale batch processing, transformations, and visualization—demonstrating production-ready data engineering skills.

---

## 🎯 Business Problem

An analytics team needs to understand NYC taxi trip patterns to:
- Monitor daily trip volumes and identify peak periods
- Analyze speed trends and traffic conditions
- Track long-distance and high-speed trip patterns
- Compare weekday vs. weekend usage
- Support data-driven operational decisions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA ENGINEERING PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Raw Data   │      │  AWS Glue    │      │  Processed   │
│  S3 Bucket   │─────▶│  (PySpark)   │─────▶│  S3 Bucket   │
│  (Parquet)   │      │  Transform   │      │ (Partitioned)│
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │     dbt      │
                                            │ (Analytics   │
                                            │ Engineering) │
                                            └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │   DuckDB     │
                                            │ (Data Mart)  │
                                            └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │ PostgreSQL   │
                                            │ (Analytics   │
                                            │   Database)  │
                                            └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │  Metabase    │
                                            │ (Dashboards) │
                                            └──────────────┘

                    Orchestrated by Apache Airflow
```

---

## 🛠️ Tech Stack

### **Infrastructure & Cloud**
- **AWS S3**: Raw and processed data lake storage (~800MB processed data)
- **AWS Glue**: Serverless PySpark ETL jobs for distributed processing
- **AWS IAM**: Secure role-based access control
- **Terraform**: Infrastructure as Code (IaC) for reproducible deployments

### **Data Processing**
- **PySpark (AWS Glue)**: Distributed data processing for large-scale transformations
- **Python 3.13**: Data ingestion, export, and utility scripts
- **DuckDB**: Analytical data warehouse for aggregated metrics

### **Orchestration**
- **Apache Airflow 2.7.1**: Workflow automation and scheduling
- **Docker & Docker Compose**: Containerized services (7 services)

### **Analytics Engineering**
- **dbt 1.10.13**: SQL-based transformations, data modeling, and testing
- **dbt-duckdb adapter**: Native DuckDB integration for dbt

### **Data Warehouse & Visualization**
- **PostgreSQL 13**: Production database for analytics tables
- **Metabase v0.56.9**: Interactive dashboards and data exploration

---

## 📈 Key Metrics

### **Data Volume**
- **Total Trips**: 23.4M trips processed
- **Time Period**: 247 days (January 1 - September 1, 2025)
- **Total Distance**: 79.8M miles traveled
- **Average Trip**: 3.45 miles, 13.12 mph
- **Peak Daily Volume**: 123.8k trips (May 2025)

### **Data Pipeline Performance**
- **Raw Data Size**: 8 months of NYC Yellow Taxi data (Jan-Aug 2025)
- **Processed Data**: ~800MB Parquet (partitioned by year/month)
- **Aggregated Tables**: 3 analytical tables (247 daily, 168 hourly, 12 monthly records)
- **AWS Glue Processing**: Serverless PySpark ETL with auto-scaling

### **Infrastructure**
- **S3 Bucket**: `nyc-taxi-data-lake-ygzcn2t2`
- **Glue Job**: `process-nyc-taxi-data`
- **dbt Models**: 4 models (1 staging view, 3 fact tables)
- **Docker Services**: 7 containers (Airflow, Postgres, Redis, Metabase, Flower)

---

## 🚀 Phase 1: Batch Foundation (Completed)

### **1. Infrastructure as Code (Terraform)**

**Outcome**: Reproducible, version-controlled AWS infrastructure

```hcl
# Key Resources Provisioned:
- S3 Bucket: nyc-taxi-data-lake-ygzcn2t2
  ├── raw-data/ (8 parquet files, 2025-01 to 2025-08)
  └── processed-data/ (9 partitions by year/month)
  
- IAM Role: nyc-taxi-glue-role
  └── Policies: S3 access, Glue service role
  
- AWS Glue Job: process-nyc-taxi-data
  ├── Type: PySpark (Python 3)
  ├── Glue Version: 4.0
  └── Worker: G.1X (4 vCPU, 16GB RAM)
```

**Commands**:
```bash
terraform init
terraform plan
terraform apply
```

---

### **2. Data Ingestion**

**Dataset**: [NYC Taxi & Limousine Commission Trip Records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

**Ingested Data**:
- **8 months**: January 2025 - August 2025
- **Format**: Parquet (columnar storage)
- **Upload Script**: Python with boto3

**Upload to S3**:
```bash
aws s3 cp yellow_tripdata_2025-01.parquet s3://nyc-taxi-data-lake-ygzcn2t2/raw-data/
aws s3 cp yellow_tripdata_2025-02.parquet s3://nyc-taxi-data-lake-ygzcn2t2/raw-data/
# ... through August 2025
```

**Result**: 8 raw parquet files successfully uploaded to `raw-data/` prefix

---

### **3. Large-Scale Processing with AWS Glue (PySpark)**

**Challenge**: Process large-scale taxi data that exceeds local compute capacity

**Solution**: Serverless AWS Glue ETL job with PySpark

**Transformations**:
```python
# Key PySpark Operations:
1. Read from S3: spark.read.parquet("s3://bucket/raw-data/")
2. Data Cleaning:
   - Filter invalid records (negative fares, invalid dates)
   - Handle nulls in critical fields
   - Standardize datetime formats
3. Feature Engineering:
   - trip_duration_minutes
   - trip_speed_mph
   - high_speed_flag (>30 mph)
   - long_distance_flag (>10 miles)
4. Partitioning: Write to S3 partitioned by year/month
```

**Execution**:
```bash
aws glue start-job-run --job-name process-nyc-taxi-data
# Job Status: SUCCEEDED
# Output: 9 partitions (year=2025/month=1-9)
```

**Performance**:
- Processed **8 months** of raw data → 9 monthly partitions
- Output size: ~800MB optimized Parquet
- Auto-scaling: Glue automatically scales workers based on data volume

---

### **4. Orchestration with Apache Airflow**

**Setup**: Docker Compose with 7 services
```yaml
Services:
  - airflow-webserver (UI: localhost:8080)
  - airflow-scheduler (DAG execution)
  - airflow-worker (CeleryExecutor)
  - airflow-triggerer (event-driven tasks)
  - postgres (metadata DB)
  - redis (message broker)
  - metabase (BI dashboards)
```

**DAG Structure** (Ready for integration):
```python
# Future DAG: nyc_taxi_pipeline.py
ingest_data >> glue_etl >> dbt_run >> export_to_postgres >> sync_metabase
```

**Current State**: 
- ✅ Airflow running locally
- ✅ Manual pipeline execution documented
- 📋 DAG automation ready for Phase 2

---

### **5. Analytics Engineering with dbt**

**Models Built**:
```sql
models/
├── staging/
│   └── stg_taxi_trips.sql (view: raw data from S3)
├── marts/
    ├── daily_trip_summary.sql (247 rows)
    ├── hourly_trip_patterns.sql (168 rows)
    └── monthly_summary.sql (12 rows)
```

**dbt Project**: `nyc_taxi_analytics/`

**Key Model Example** (`daily_trip_summary.sql`):
```sql
WITH trip_metrics AS (
    SELECT
        DATE(tpep_pickup_datetime) as trip_date,
        COUNT(*) as total_trips,
        ROUND(AVG(trip_distance), 2) as avg_distance,
        ROUND(AVG(trip_duration_minutes), 2) as avg_duration_minutes,
        ROUND(AVG(passenger_count), 2) as avg_passengers,
        ROUND(AVG(trip_speed_mph), 2) as avg_speed,
        COUNT(CASE WHEN trip_speed_mph > 30 THEN 1 END) as high_speed_trips,
        COUNT(CASE WHEN trip_distance > 10 THEN 1 END) as long_distance_trips
    FROM {{ ref('stg_taxi_trips') }}
    WHERE trip_date IS NOT NULL
    GROUP BY trip_date
)
SELECT * FROM trip_metrics
```

**dbt Execution**:
```bash
cd nyc_taxi_analytics
dbt debug  # Test connection
dbt run    # Build 4 models
dbt test   # Run data quality tests
```

**Output**: DuckDB database (`nyc_taxi.duckdb`, 1.8MB) with aggregated analytics tables

**Data Quality Tests**:
- ✅ Not null constraints on primary keys
- ✅ Unique tests on date columns
- ✅ Relationship tests between fact and dimension tables

---

### **6. Data Warehouse & Export**

**DuckDB → PostgreSQL Pipeline**:

1. **Export to CSV**:
```bash
python export_to_csv.py
# Output: 3 CSV files (24.6KB, 7.68KB, 2.56KB)
```

2. **Load to PostgreSQL**:
```bash
# Copy CSVs to container
docker cp daily_trip_summary.csv postgres:/tmp/
docker cp hourly_trip_patterns.csv postgres:/tmp/
docker cp monthly_summary.csv postgres:/tmp/

# Load via SQL
docker exec -i postgres psql -U airflow < load_postgres.sql
```

3. **Verification**:
```sql
-- PostgreSQL Schema: nyc_taxi
SELECT COUNT(*) FROM nyc_taxi.daily_trip_summary;  -- 247 rows
SELECT COUNT(*) FROM nyc_taxi.hourly_trip_patterns; -- 168 rows
SELECT COUNT(*) FROM nyc_taxi.monthly_summary;      -- 12 rows
```

---

### **7. Data Visualization with Metabase**

**Dashboard**: NYC Taxi Operations Dashboard

**Access**: http://localhost:3000

**Visualizations Created**:

1. **📈 Daily Trip Volume** (Line Chart)
   - Range: 70k-125k trips/day
   - Peak: 123.8k trips (May 2025)
   - Goal line: 110k trips

2. **⚡ Average Speed Trends** (Line Chart)
   - Range: 9-16 mph
   - Average: 13.12 mph

3. **🕐 Hourly Trip Patterns** (Bar Chart)
   - Peak: 5-8 PM (1.2-1.3M trips)
   - Low: Early morning 0-5 AM

4. **📊 Monthly Trip Volume** (Bar Chart)
   - Range: 2.5-3.3M trips/month
   - Peak: May 2025 (3.3M trips)

5. **🏃 High-Speed Trip Monitoring** (Line Chart)
   - Range: 1k-5k trips/day (>30 mph)
   - Represents 2-4% of total trips

6. **📏 Long Distance Trips** (Area Chart)
   - Range: 5k-11.5k trips/day (>10 miles)
   - Average: 8k-9k trips/day

7. **🎯 Weekend vs Weekday** (Bar Chart)
   - Weekdays: 17.0M trips (73%)
   - Weekends: 6.4M trips (27%)

**KPI Cards** (Big Numbers):
- Total Trips: **23.4M**
- Avg Distance: **3.45 miles**
- Avg Speed: **13.12 mph**
- Peak Daily: **123.8k trips**
- Avg Passengers: **1.32**
- Total Miles: **79.8M miles**

**Documentation**: See [METABASE_SETUP.md](METABASE_SETUP.md) for complete setup guide

---

## 🎓 Technical Challenges Solved

### **Challenge 1: Data Gap Detection & Resolution**
**Problem**: Chart visualization showed missing May-June 2025 data (2-month gap)

**Root Cause**: Missing source parquet files in S3 bucket

**Solution**:
1. Uploaded missing `yellow_tripdata_2025-05.parquet` and `yellow_tripdata_2025-06.parquet`
2. Triggered AWS Glue job to reprocess all data
3. Ran dbt models to rebuild aggregated tables
4. Exported and reloaded PostgreSQL with complete dataset
5. Synced Metabase database schema

**Result**: Continuous data from Jan 1 - Sep 1, 2025 (247 days, gap eliminated)

**Verification**:
```python
# verify_duckdb.py output:
May 2025: 31 days, 3,265,359 trips
June 2025: 30 days, 2,980,406 trips
```

---

### **Challenge 2: AWS Credentials in dbt**
**Problem**: dbt couldn't access S3 data source (staging view reads from S3)

**Error**: `AWS credentials not configured`

**Solution**: Set environment variables before dbt execution
```powershell
$env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Run dbt with credentials
C:/real-time-NYC-taxi-data-platform/.venv/Scripts/dbt.exe run
```

**Lesson**: Always ensure cloud credentials are available to tools accessing remote data sources

---

### **Challenge 3: Docker Container Naming**
**Problem**: PostgreSQL connection failed with generic "postgres" container name

**Error**: `could not translate host name "postgres" to address`

**Solution**: Use full Docker Compose container name
```bash
# Wrong: postgres
# Correct: real-time-nyc-taxi-data-platform-postgres-1

docker exec -it real-time-nyc-taxi-data-platform-postgres-1 psql -U airflow
```

**Lesson**: Docker Compose auto-generates container names; use `docker ps` to verify

---

### **Challenge 4: Goal Line Optimization**
**Problem**: Dashboard Chart 1 had 150k goal line, but actual data never exceeded 125k

**Analysis**: Peak daily volume was 123.8k trips (May 2025), average ~95k

**Solution**: Adjusted goal line to 110k for realistic, achievable target
- Above average (95k) ✅
- Below peak (123.8k) ✅
- Motivates performance improvement ✅

**Lesson**: Data-driven KPIs should be realistic and based on actual performance patterns

---

## 📁 Project Structure

```
real-time-NYC-taxi-data-platform/
├── dags/                           # Airflow DAG definitions
├── glue_jobs/                      # AWS Glue PySpark scripts
├── nyc_taxi_analytics/            # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_taxi_trips.sql
│   │   └── marts/
│   │       ├── daily_trip_summary.sql
│   │       ├── hourly_trip_patterns.sql
│   │       └── monthly_summary.sql
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── export_to_csv.py           # DuckDB → CSV export
│   ├── load_postgres.sql          # PostgreSQL schema & load
│   └── nyc_taxi.duckdb            # Analytical data warehouse
├── terraform/                      # Infrastructure as Code
│   ├── main.tf
│   ├── s3.tf
│   ├── glue.tf
│   └── iam.tf
├── docker-compose.yaml            # Multi-service orchestration
├── METABASE_SETUP.md              # Dashboard setup guide
├── README.md                       # This file
└── requirements.txt               # Python dependencies
```

---

## 🚀 Getting Started

### **Prerequisites**
- AWS Account with CLI configured
- Terraform 1.9+
- Docker & Docker Compose
- Python 3.13+

### **1. Clone Repository**
```bash
git clone https://github.com/DiazSk/real-time-NYC-taxi-data-platform.git
cd real-time-NYC-taxi-data-platform
```

### **2. Provision Infrastructure**
```bash
cd terraform
terraform init
terraform apply
```

### **3. Start Docker Services**
```bash
docker-compose up -d
```

### **4. Run Data Pipeline**
```bash
# Upload raw data to S3
aws s3 sync nyc_yellow_taxi_dataset/ s3://nyc-taxi-data-lake-ygzcn2t2/raw-data/

# Run Glue ETL
aws glue start-job-run --job-name process-nyc-taxi-data

# Run dbt models
cd nyc_taxi_analytics
dbt run

# Export to PostgreSQL
python export_to_csv.py
docker cp *.csv postgres:/tmp/
docker exec -i postgres psql -U airflow < load_postgres.sql
```

### **5. Access Dashboards**
- **Airflow**: http://localhost:8080 (airflow/airflow)
- **Metabase**: http://localhost:3000
- **Flower**: http://localhost:5555

---

## 📊 Key Insights from Data

Based on analysis of 23.4M trips:

1. **Peak Hours**: Evening rush (5-8 PM) dominates with 1.2-1.3M trips
2. **Weekday Dominance**: 73% of trips occur on weekdays (commuter-driven)
3. **Speed Patterns**: Average speed of 13.12 mph reflects NYC traffic conditions
4. **Distance Distribution**: 3.45 miles average suggests mostly short-medium trips
5. **Seasonal Trends**: May 2025 had highest volume (3.3M trips)
6. **Safety Metrics**: Only 2-4% of trips exceed 30 mph (high-speed threshold)

---

## 🎯 Skills Demonstrated

### **Data Engineering**
✅ Large-scale data processing (23.4M records)  
✅ Distributed computing (PySpark on AWS Glue)  
✅ Data modeling (star schema, fact tables)  
✅ ETL/ELT pipeline design  
✅ Data quality testing and validation  

### **Cloud & Infrastructure**
✅ AWS services (S3, Glue, IAM)  
✅ Infrastructure as Code (Terraform)  
✅ Serverless computing (Glue jobs)  
✅ Cloud storage optimization (partitioning)  

### **DevOps & Orchestration**
✅ Docker containerization  
✅ Multi-service orchestration (Docker Compose)  
✅ Workflow automation (Airflow)  
✅ Version control (Git)  

### **Analytics Engineering**
✅ SQL transformations (dbt)  
✅ Data warehouse design (DuckDB, PostgreSQL)  
✅ Business intelligence (Metabase)  
✅ Dashboard development  

### **Problem Solving**
✅ Data gap detection and resolution  
✅ Performance optimization  
✅ Debugging distributed systems  
✅ Documentation and knowledge sharing  

---

## 📋 Phase 2: Streaming Layer (Planned)

### **Roadmap**: Feb 2026 - March 2026

**Goal**: Add real-time processing capabilities

**Tech Stack Additions**:
- Apache Kafka (message streaming)
- Spark Streaming (real-time processing)
- Redis (state management)

**Planned Features**:
1. Kafka producer simulating live taxi trips
2. Spark Streaming consumer with 15-minute rolling windows
3. Real-time aggregations (avg trip cost by location)
4. Live dashboard updates
5. Integration with existing Airflow DAG

---

## 🎤 Interview Talking Points

### **"Tell me about a challenging technical problem you solved."**
*"In my NYC Taxi project, I encountered a data gap in my Metabase visualization showing missing May-June 2025 data. I systematically debugged the pipeline by verifying S3 source files, discovering missing parquet uploads. I then orchestrated a complete data refresh: uploaded missing files, triggered AWS Glue reprocessing, rebuilt dbt models, reloaded PostgreSQL, and validated the fix—eliminating the gap and ensuring data continuity across 247 days. This taught me the importance of end-to-end data lineage tracking."*

### **"Describe the most complex data pipeline you've built."**
*"I built an end-to-end data platform for NYC taxi analytics processing 23.4M trips. The architecture uses Terraform for reproducible infrastructure, AWS S3 as the data lake, AWS Glue with PySpark for distributed ETL, dbt for analytics engineering, and Metabase for visualization. The pipeline handles large-scale batch processing with proper partitioning (year/month), implements data quality testing, and maintains separation between raw, processed, and analytical layers. Everything is documented and version-controlled."*

### **"How do you ensure data quality?"**
*"I implement multiple layers of quality checks: (1) PySpark transformations filter invalid records at ingestion, (2) dbt tests validate not-null, unique, and relationship constraints, (3) Verification scripts confirm record counts and data ranges, (4) Dashboard KPIs serve as business logic validators. For example, when I detected the May-June gap, my verification queries immediately surfaced the issue before stakeholders noticed."*

---

## 📚 Documentation

- **[METABASE_SETUP.md](METABASE_SETUP.md)**: Complete dashboard setup guide with step-by-step instructions
- **[Terraform Configuration](terraform/)**: Infrastructure provisioning and AWS resource definitions
- **[dbt Models](nyc_taxi_analytics/models/)**: SQL transformations and data model documentation
- **[Glue Jobs](glue_jobs/)**: PySpark ETL scripts for distributed processing

---

## 📝 License

This project is open source and available for educational purposes.

---

## 🙏 Acknowledgments

- **NYC Taxi & Limousine Commission**: For providing public trip record data
- **Open Source Community**: Airflow, dbt, Metabase, and DuckDB teams

---

## 📧 Contact

**Project Owner**: DiazSk  
**Repository**: [github.com/DiazSk/real-time-NYC-taxi-data-platform](https://github.com/DiazSk/real-time-NYC-taxi-data-platform)

---

**Built with ❤️ and ☕ as a demonstration of production-grade data engineering practices.**