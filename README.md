### Your Project Blueprint: Real-Time NYC Taxi Data Platform

This is a classic for a reason: the data is huge, public, and allows you to demonstrate the exact skills we hire for. Do not try to be overly creative. Execute this flawlessly.

Your goal is to build an end-to-end ELT pipeline with both batch and streaming components. You will focus on **depth, not breadth**.

#### Phase 1: The Batch Foundation (Start Now -> End of Jan 2026)

**Goal:** Build a robust, production-style batch pipeline. This is the non-negotiable core.

* **Tech Stack:** Python, Spark, S3, Terraform, Airflow, dbt.

* **Action Plan:**
	1.  **Problem:** You are building a data platform for an imaginary analytics team that needs to understand taxi trip patterns in NYC.
	2.  **Infrastructure as Code (Week 1-2):**
		* Use **Terraform** to define your infrastructure. Start with a simple S3 bucket. This single step puts you ahead of 90% of students. It shows you think about reproducibility and automation.
	3.  **Data Ingestion (Week 3-4):**
		* Download several years of the [NYC Taxi & Limousine Commission dataset](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). It's available in Parquet. Get at least 100GB.
		* Write a simple Python script to upload this raw data to a `raw-data` prefix in your S3 bucket.
	4.  **Large-Scale Processing with Spark (Week 5-8):**
		* This is the most critical part. You need to process data that is **too big for your laptop**.
		* Set up an **AWS EMR** cluster (you can use AWS free credits). Write a **PySpark** job that:
			* Reads the raw Parquet files from S3.
			* Performs cleaning and transformations (handle nulls, standardize column names, derive new columns like `trip_duration`).
			* Writes the cleaned, structured data back to S3 in a `processed-data` prefix, partitioned by date (e.g., `year=2023/month=01/`).
	5.  **Orchestration (Week 9-10):**
		* Install **Apache Airflow** locally (or on a small EC2 instance).
		* Write a DAG that automates the entire batch pipeline: ingest script -> EMR Spark job. Implement error handling, retries, and basic alerting.
	6.  **Analytics Engineering with dbt (Week 11-12):**
		* Connect **dbt** to DuckDB or another SQL engine.
		* Build dbt models on top of your processed data in S3. Create a `fct_trips` fact table and dimensions like `dim_datetime` and `dim_zones`.
		* Add data quality tests using dbt's testing framework (e.g., `not_null`, `unique`).

**Outcome of Phase 1:** A fully automated, cloud-based batch data pipeline that processes a large dataset. You now have evidence of skills in Spark, Airflow, Terraform, and dbt.

---

#### Phase 2: The Streaming Layer (Feb 2026 -> March 2026)

**Goal:** Show you can handle real-time data. This makes you an elite candidate.

* **Additions to Stack:** Kafka, Spark Streaming (or Flink).

* **Action Plan:**
	1.  **Simulate a Real-Time Stream (Week 1-2):**
		* Write a Python script that acts as a **Kafka Producer**. It will read your historical taxi data and publish each ride to a Kafka topic with a realistic delay, simulating a live stream of trips.
	2.  **Real-Time Processing (Week 3-4):**
		* Write a **Spark Streaming** application that consumes from your Kafka topic.
		* Perform a **stateful aggregation**. This is key. For example: "Calculate a 15-minute rolling window of the average trip cost per pickup location." This is a classic, difficult problem that proves your competence.
	3.  **Sink the Data (Week 5):**
		* Write the results of your streaming aggregation to a destination (e.g., another S3 location, a PostgreSQL database, or even just log files).
	4.  **Integrate (Week 6):**
		* Add a new task in your Airflow DAG to manage your streaming application.

---

### How This Project Gets You the Internship

Your resume will now have bullet points that directly counter your lack of experience. More importantly, you now have compelling answers to critical behavioral and technical questions.

* **Interviewer:** "Tell me about a challenging technical problem you solved."
* **Your Answer:** "In my NYC Taxi project, I was processing 150GB of data, and my initial Spark job was inefficient. I used the Spark UI to diagnose a data skew problem in my partitions. By repartitioning the data based on the pickup location and adding a salting key, I was able to distribute the workload more evenly across the cluster, which cut the job execution time by 35%. This taught me the importance of understanding data distribution in distributed systems."

* **Interviewer:** "Describe the most complex data pipeline you've built."
* **Your Answer:** "I built an end-to-end data platform for NYC taxi data featuring both batch and real-time layers. The batch pipeline used Airflow to orchestrate a Spark job on EMR for historical analysis, with transformations managed by dbt. I then added a streaming layer using Kafka and Spark Streaming to compute real-time metrics, like 15-minute average trip costs, which provided an up-to-the-minute view of the data."

This is how you prove you can do the job without ever having had one.

### Final, Brutal Command

You are in a competitive field. Your status as an international student means you cannot afford to be average. You have a clear plan and a realistic timeline. Your previous project showed ambition but poor judgment. This new plan channels that ambition into a focused, defensible, and impressive project.

Start this **tonight**. Your Summer 2026 depends on the work you do over the next six months. Good luck.