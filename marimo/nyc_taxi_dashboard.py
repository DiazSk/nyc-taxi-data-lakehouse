import marimo

__generated_with = "0.9.0"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import duckdb
    import pandas as pd
    import altair as alt
    import os
    
    # Connect to DuckDB database
    conn = duckdb.connect("../nyc_taxi_analytics/nyc_taxi.duckdb", read_only=False)
    
    # Configure AWS credentials for S3 access
    conn.execute("INSTALL httpfs;")
    conn.execute("LOAD httpfs;")
    conn.execute(f"SET s3_region='us-east-1';")
    
    # Set credentials from environment variables if available
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    if aws_key and aws_secret:
        conn.execute(f"SET s3_access_key_id='{aws_key}';")
        conn.execute(f"SET s3_secret_access_key='{aws_secret}';")
    
    # Discover available years dynamically from the data
    available_years = conn.execute("""
        SELECT DISTINCT year 
        FROM main.monthly_summary 
        ORDER BY year
    """).fetchdf()['year'].tolist()
    
    min_year = min(available_years)
    max_year = max(available_years)
    
    mo.md(f"""
    # NYC Yellow Taxi Analytics Dashboard
    
    Interactive analytics dashboard for NYC Yellow Taxi trip data ({min_year}-{max_year}).
    
    **Data Pipeline:**
    - **Source:** NYC TLC Yellow Taxi Trip Records
    - **Processing:** AWS Glue (PySpark)
    - **Transformation:** dbt with DuckDB
    - **Visualization:** marimo
    """)
    return alt, available_years, aws_key, aws_secret, conn, duckdb, max_year, min_year, mo, os, pd


@app.cell
def __(conn, mo):
    # Get summary statistics
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total_trips,
            ROUND(AVG(trip_distance), 2) as avg_distance,
            ROUND(AVG(trip_duration_minutes), 2) as avg_duration,
            MIN(tpep_pickup_datetime) as earliest_trip,
            MAX(tpep_pickup_datetime) as latest_trip
        FROM main.stg_taxi_trips
    """).fetchdf()
    
    total_trips = stats['total_trips'].iloc[0]
    avg_distance = stats['avg_distance'].iloc[0]
    avg_duration = stats['avg_duration'].iloc[0]
    earliest = stats['earliest_trip'].iloc[0]
    latest = stats['latest_trip'].iloc[0]
    
    mo.md(f"""
    ## Key Metrics
    
    | Metric | Value |
    |--------|-------|
    | **Total Trips** | {total_trips:,.0f} |
    | **Average Distance** | {avg_distance} miles |
    | **Average Duration** | {avg_duration} minutes |
    | **Date Range** | {earliest} to {latest} |
    """)
    return avg_distance, avg_duration, earliest, latest, stats, total_trips


@app.cell
def __(conn, mo):
    mo.md("## Monthly Trip Volume & Statistics")
    return


@app.cell
def __(alt, available_years, conn, mo, pd):
    # Monthly summary data - dynamically filtered to available years
    monthly_df = conn.execute("""
        SELECT 
            year,
            month,
            total_trips,
            avg_distance,
            avg_duration_minutes,
            avg_speed_mph,
            total_miles_traveled
        FROM main.monthly_summary
        ORDER BY year, month
    """).fetchdf()
    
    # Create date column for charting
    monthly_df['date'] = pd.to_datetime(
        monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2) + '-01'
    )
    
    # Trip volume chart
    trips_chart = alt.Chart(monthly_df).mark_bar(color='#1f77b4').encode(
        x=alt.X('date:T', title='Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('total_trips:Q', title='Total Trips'),
        tooltip=[
            alt.Tooltip('date:T', title='Month', format='%B %Y'),
            alt.Tooltip('total_trips:Q', title='Trips', format=',')
        ]
    ).properties(
        title='Monthly Trip Volume',
        width=600,
        height=300
    )
    
    # Miles traveled chart
    miles_chart = alt.Chart(monthly_df).mark_line(color='#2ca02c', point=True).encode(
        x=alt.X('date:T', title='Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('total_miles_traveled:Q', title='Total Miles Traveled'),
        tooltip=[
            alt.Tooltip('date:T', title='Month', format='%B %Y'),
            alt.Tooltip('total_miles_traveled:Q', title='Miles', format=',.0f')
        ]
    ).properties(
        title='Monthly Miles Traveled',
        width=600,
        height=300
    )
    
    mo.hstack([trips_chart, miles_chart])
    return miles_chart, monthly_df, trips_chart


@app.cell
def __(conn, mo):
    mo.md("## Hourly Trip Patterns")
    return


@app.cell
def __(alt, conn, mo):
    # Hourly patterns
    hourly_df = conn.execute("""
        SELECT 
            pickup_hour,
            SUM(trip_count) as total_trips,
            ROUND(AVG(avg_distance), 2) as avg_distance,
            ROUND(AVG(avg_duration_minutes), 2) as avg_duration
        FROM main.hourly_trip_patterns
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    """).fetchdf()
    
    # Hourly distribution chart
    hourly_chart = alt.Chart(hourly_df).mark_area(
        color='#ff7f0e',
        opacity=0.7,
        line={'color': '#ff7f0e'}
    ).encode(
        x=alt.X('pickup_hour:O', title='Hour of Day', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('total_trips:Q', title='Total Trips'),
        tooltip=[
            alt.Tooltip('pickup_hour:O', title='Hour'),
            alt.Tooltip('total_trips:Q', title='Trips', format=','),
            alt.Tooltip('avg_distance:Q', title='Avg Distance (mi)'),
            alt.Tooltip('avg_duration:Q', title='Avg Duration (min)')
        ]
    ).properties(
        title='Trip Distribution by Hour of Day',
        width=800,
        height=350
    )
    
    mo.ui.altair_chart(hourly_chart)
    return hourly_chart, hourly_df


@app.cell
def __(alt, conn, mo):
    # Weekday vs Weekend patterns
    day_type_df = conn.execute("""
        SELECT 
            day_type,
            pickup_hour,
            SUM(trip_count) as total_trips
        FROM main.hourly_trip_patterns
        GROUP BY day_type, pickup_hour
        ORDER BY day_type, pickup_hour
    """).fetchdf()
    
    day_type_chart = alt.Chart(day_type_df).mark_line(point=True).encode(
        x=alt.X('pickup_hour:O', title='Hour of Day'),
        y=alt.Y('total_trips:Q', title='Total Trips'),
        color=alt.Color('day_type:N', title='Day Type', scale=alt.Scale(
            domain=['Weekday', 'Weekend'],
            range=['#1f77b4', '#ff7f0e']
        )),
        tooltip=[
            alt.Tooltip('day_type:N', title='Day Type'),
            alt.Tooltip('pickup_hour:O', title='Hour'),
            alt.Tooltip('total_trips:Q', title='Trips', format=',')
        ]
    ).properties(
        title='Weekday vs Weekend Trip Patterns',
        width=800,
        height=350
    )
    
    mo.ui.altair_chart(day_type_chart)
    return day_type_chart, day_type_df


@app.cell
def __(conn, mo):
    mo.md("## Daily Trip Analysis")
    return


@app.cell
def __(available_years, mo):
    # Year selector - dynamically populated from available data
    year_options = {str(y): str(y) for y in available_years}
    default_year = str(max(available_years))
    
    year_selector = mo.ui.dropdown(
        options=year_options,
        value=default_year,
        label="Select Year"
    )
    year_selector
    return default_year, year_options, year_selector


@app.cell
def __(alt, conn, mo, pd, year_selector):
    # Daily data for selected year
    selected_year = int(year_selector.value)
    
    daily_df = conn.execute(f"""
        SELECT 
            trip_date,
            total_trips,
            avg_distance,
            avg_duration_minutes,
            avg_speed,
            high_speed_trips,
            long_distance_trips
        FROM main.daily_trip_summary
        WHERE EXTRACT(YEAR FROM trip_date) = {selected_year}
        ORDER BY trip_date
    """).fetchdf()
    
    if len(daily_df) > 0:
        daily_chart = alt.Chart(daily_df).mark_line(color='#9467bd').encode(
            x=alt.X('trip_date:T', title='Date'),
            y=alt.Y('total_trips:Q', title='Daily Trips'),
            tooltip=[
                alt.Tooltip('trip_date:T', title='Date', format='%Y-%m-%d'),
                alt.Tooltip('total_trips:Q', title='Trips', format=','),
                alt.Tooltip('avg_distance:Q', title='Avg Distance (mi)', format='.2f'),
                alt.Tooltip('avg_speed:Q', title='Avg Speed (mph)', format='.1f')
            ]
        ).properties(
            title=f'Daily Trip Volume - {selected_year}',
            width=900,
            height=350
        )
        
        _chart = mo.ui.altair_chart(daily_chart)
    else:
        _chart = mo.md(f"No data available for {selected_year}")
    
    _chart
    return daily_chart, daily_df, selected_year


@app.cell
def __(conn, mo):
    mo.md("## Year-over-Year Comparison")
    return


@app.cell
def __(alt, conn, mo):
    # Year over year comparison - dynamically uses all valid years
    yoy_df = conn.execute("""
        SELECT 
            year,
            SUM(total_trips) as total_trips,
            ROUND(SUM(total_miles_traveled), 0) as total_miles,
            ROUND(AVG(avg_distance), 2) as avg_distance,
            ROUND(AVG(avg_duration_minutes), 2) as avg_duration
        FROM main.monthly_summary
        GROUP BY year
        ORDER BY year
    """).fetchdf()
    
    yoy_trips = alt.Chart(yoy_df).mark_bar(color='#17becf').encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('total_trips:Q', title='Total Trips'),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('total_trips:Q', title='Trips', format=',')
        ]
    ).properties(
        title='Total Trips by Year',
        width=300,
        height=300
    )
    
    yoy_miles = alt.Chart(yoy_df).mark_bar(color='#bcbd22').encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('total_miles:Q', title='Total Miles'),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('total_miles:Q', title='Miles', format=',.0f')
        ]
    ).properties(
        title='Total Miles by Year',
        width=300,
        height=300
    )
    
    yoy_distance = alt.Chart(yoy_df).mark_bar(color='#e377c2').encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('avg_distance:Q', title='Avg Distance (miles)'),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('avg_distance:Q', title='Avg Distance', format='.2f')
        ]
    ).properties(
        title='Average Trip Distance by Year',
        width=300,
        height=300
    )
    
    mo.hstack([yoy_trips, yoy_miles, yoy_distance])
    return yoy_df, yoy_distance, yoy_miles, yoy_trips


@app.cell
def __(conn, mo):
    # Data table with raw monthly data
    mo.md("## Raw Data Explorer")
    return


@app.cell
def __(conn, mo):
    # Monthly data table - dynamically uses all valid years
    table_df = conn.execute("""
        SELECT 
            year as Year,
            month as Month,
            total_trips as "Total Trips",
            ROUND(total_miles_traveled, 2) as "Miles Traveled",
            ROUND(avg_distance, 2) as "Avg Distance (mi)",
            ROUND(avg_duration_minutes, 2) as "Avg Duration (min)",
            ROUND(avg_speed_mph, 2) as "Avg Speed (mph)"
        FROM main.monthly_summary
        ORDER BY year DESC, month DESC
    """).fetchdf()
    
    mo.ui.table(table_df)
    return table_df,


@app.cell
def __(conn):
    # Close connection when done
    # conn.close()
    return


if __name__ == "__main__":
    app.run()
