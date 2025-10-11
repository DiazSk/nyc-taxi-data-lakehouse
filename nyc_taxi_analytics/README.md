# NYC Taxi Analytics (dbt + DuckDB)

Short description
- Small dbt project that transforms NYC taxi parquet into marts (daily, hourly, monthly) using DuckDB for local dev.

Quick start (local, no cloud)
1. Create a virtualenv and install:
   pip install dbt-core dbt-duckdb
2. Use the bundled DuckDB file (nyc_taxi.duckdb) or point profiles.yml to your own DuckDB/warehouse.
3. Run:
   - dbt deps
   - dbt seed
   - dbt run
   - dbt test

Project structure
- models/staging: staging SQL
- models/marts: aggregated marts (daily/hourly/monthly)
- nyc_taxi.duckdb: local warehouse for dev

Notes
- This README replaces the default starter text. Keep it updated with run instructions and brief cost notes if you run transformations in Glue/Athena.
- To demo in interviews: run locally (DuckDB) and record a short walkthrough or provide a GIF of dbt run + Metabase dashboard screenshots.
