"""Export DuckDB tables to CSV files for PostgreSQL import."""

import duckdb

# Connect to DuckDB
print("🔌 Connecting to DuckDB...")
conn = duckdb.connect('nyc_taxi.duckdb', read_only=True)

# Tables to export
tables = ['daily_trip_summary', 'hourly_trip_patterns', 'monthly_summary']

# Export each table
for table in tables:
    print(f"\n📊 Exporting {table}...")
    
    # Count rows
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"   Found {count} rows")
    
    # Export to CSV
    conn.execute(f"COPY {table} TO '{table}.csv' (HEADER, DELIMITER ',')")
    print(f"   ✅ Exported to {table}.csv")

conn.close()

print("\n🎉 All tables exported successfully!")
print("\nNext steps:")
print("1. Copy CSV files to PostgreSQL container")
print("2. Load data into PostgreSQL")
print("3. Connect Metabase to PostgreSQL")
