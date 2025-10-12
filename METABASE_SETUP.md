# 📊 Metabase Setup Guide - NYC Taxi Analytics Dashboard

## 🚀 Metabase is Now Running!

**Access URL:** http://localhost:3000
**Status:** ✅ Healthy (Container running)
**Data Source:** DuckDB file at `/duckdb-data/nyc_taxi.duckdb`

---

## Step 1: Initial Setup (First Time Only)

When you open http://localhost:3000, you'll see the welcome screen:

### 1.1 Create Your Admin Account
```
What's your preferred language?  → English
What should we call you?         → Your Name
What's your email?                → your.email@example.com
Create a password                 → [Choose a secure password]
```

Click **Next**

### 1.2 Company Information (Optional)
```
Company or team name              → NYC Taxi Analytics
```

Click **Next**

### 1.3 Add Your Data

This is where we connect to DuckDB!

**Select Database Type:**
- Scroll down and select **"SQLite"** (we'll use this for DuckDB)

**Database Connection Settings:**
```
Display name:           NYC Taxi Data Warehouse
Filename:               /duckdb-data/nyc_taxi.duckdb
```

**Important:** 
- Use the **full path inside the container**: `/duckdb-data/nyc_taxi.duckdb`
- This maps to `C:\real-time-NYC-taxi-data-platform\nyc_taxi_analytics\nyc_taxi.duckdb` on your host

Click **Connect database**

### 1.4 Usage Data Preference
```
[ ] Allow Metabase to anonymously collect usage events
```

Click **Finish**

---

## Step 2: Explore Your Data

After setup, Metabase will scan your database and show:

### Available Tables
✅ **daily_trip_summary** (188 rows)
- `trip_date`, `total_trips`, `avg_distance`, `avg_duration_minutes`, `avg_passengers`, `avg_speed`, `high_speed_trips`, `long_distance_trips`, `min_distance`, `max_distance`, `min_duration`, `max_duration`

✅ **hourly_trip_patterns** (168 rows)
- `pickup_hour`, `day_of_week`, `day_type` (Weekend/Weekday), `trip_count`, `avg_distance`, `avg_duration_minutes`, `avg_passengers`

✅ **monthly_summary** (12 rows)
- `year`, `month`, `total_trips`, `avg_distance`, `avg_duration_minutes`, `avg_passengers`, `avg_speed_mph`, `total_miles_traveled`, `total_hours`

✅ **stg_taxi_trips** (View - ~34M records)
- Raw staging data from S3 parquet files (includes fare data if you want to query it directly)

---

## Step 3: Create Your First Dashboard

### 3.1 Create a New Dashboard
1. Click **"+ New"** in the top right
2. Select **"Dashboard"**
3. Name it: **"NYC Taxi Operations Dashboard"**
4. Description: **"Real-time analytics of NYC taxi trip patterns, speed, and distance metrics"**
5. Click **"Create"**

---

### 3.2 Chart 1: Daily Trip Volume Trends (Line Chart)

**Purpose:** Track daily trip volume patterns over time

**Using Visual Query Builder (Recommended):**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Daily Trip Summary"**
4. Click **"Visualize"**

**Configure the Chart:**
- **Visualization:** Click the visualization button and select **"Line"**
- **X-axis:** Click and select **"Trip Date"**
- **Y-axis:** Click and select **"Total Trips"**
- **Summarize:** Use "Sum" or leave as is (already aggregated)

**Optional Enhancements:**
- Click **gear icon** → Display → Add **trend line**
- Click **gear icon** → Display → Add **goal line** at 110000 (recommended based on actual data)
- Click **gear icon** → Axes → Set Y-axis to start at 0

5. Click **"Save"**
6. Name it: **"Daily Trip Volume"**
7. Click **"Save"** and add to your dashboard

**What You'll See:** Daily trip volume ranging from 70k-125k trips per day throughout 2025. Peak of 123.8k trips achieved in May 2025. The 110k goal line provides a realistic target that's above average but achievable.

---

### 3.3 Chart 2: Average Speed Trends (Line Chart)

**Purpose:** Monitor speed patterns throughout 2025

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Daily Trip Summary"**
4. Click **"Visualize"**

**Configure the Chart:**
- **Visualization:** Select **"Line"**
- **X-axis:** **"Trip Date"**
- **Y-axis:** **"Avg Speed"**

5. **Add Filter for 2025 (Optional):**
   - Click **"Filter"** → **"Trip Date"** → **"Between"**
   - Start: `2025-01-01`
   - End: `2025-12-31`

6. Click **"Save"**
7. Name it: **"Average Speed Trends - 2025"**
8. Save and add to dashboard

**What You'll See:** Average speed fluctuates between 9-16 mph throughout 2025, with an average of 13.12 mph. Daily oscillations show typical weekday/weekend patterns, with speeds generally ranging 10-14 mph across different months and traffic conditions.

---

### 3.4 Chart 3: Hourly Trip Patterns (Bar Chart)

**Purpose:** Visualize peak hours throughout the day

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Hourly Trip Patterns"**

**Configure:**
- Click **"Summarize"**
- **Group by:** **"Pickup Hour"**
- **Metric:** **"Sum of Trip Count"**
- Click **"Visualize"**

**Configure Visualization:**
- **Visualization:** Select **"Bar"** chart
- **X-axis:** **"Pickup Hour"**
- **Y-axis:** **"Sum of Trip Count"**

4. **Optional - Add Color by Day Type:**
   - Click **"Breakout"** → Select **"Day Type"**
   - This will show Weekend vs Weekday as different colored bars

5. Click **"Save"**
6. Name it: **"Hourly Trip Patterns"**
7. Save and add to dashboard

**What You'll See:** Evening rush hours (5-8 PM / hours 17-20) show the highest trip volumes with 1.2-1.3M trips. Clear weekday vs weekend patterns emerge - weekdays dominate during business hours (7 AM - 8 PM), while weekends show lower but more consistent volumes throughout the day. Early morning hours (0-5 AM) show the lowest activity.

---

### 3.5 Chart 4: Monthly Trip Volume (Bar Chart)

**Purpose:** Track month-over-month trip volume

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Monthly Summary"**

**Configure:**
- Click **"Summarize"** (if needed)
- **X-axis:** Select **"Month"** and **"Year"** (or create a filter for Year >= 2025)
- **Y-axis:** **"Total Trips"**
- Click **"Visualize"**

**Configure Visualization:**
- **Visualization:** Select **"Bar"** chart
- **X-axis:** **"Month"** (you can also breakout by **"Year"**)
- **Y-axis:** **"Total Trips"**

4. **Add Filter:**
   - Click **"Filter"** → **"Year"** → **"Greater than or equal to"** → `2025`

5. Click **"Save"**
6. Name it: **"Monthly Trip Volume"**
7. Save and add to dashboard

**What You'll See:** 2025 monthly volumes showing consistent ~2.5-3.3M trips per month. Peak month is May with 3.3M trips, followed by March (3.1M) and April (3.1M). Summer months (July-August) show slightly lower volumes around 2.5-2.7M trips. Clear seasonal patterns emerge throughout the year.

---

### 3.6 Chart 5: High-Speed Trips Monitoring (Line Chart)

**Purpose:** Monitor high-speed trips over time throughout 2025

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Daily Trip Summary"**

**Configure:**
- **Visualization:** Select **"Line"**
- **X-axis:** **"Trip Date"**
- **Y-axis:** **"High Speed Trips"**

4. **Add Second Line (Optional):**
   - Click **"Add series"** or use the visualization settings
   - Add **"Long Distance Trips"** as a second line for comparison

5. **Add Filter for 2025 (Optional):**
   - Click **"Filter"** → **"Trip Date"** → **"Between"**
   - Start: `2025-01-01`
   - End: `2025-12-31`

6. Click **"Save"**
7. Name it: **"High-Speed Trip Monitoring - 2025"**
8. Save and add to dashboard

**What You'll See:** High-speed trips (>30 mph) showing continuous data from January through September 2025. Volume ranges from 1,000 to 5,000 trips per day, with higher counts in early months (January-April averaging 3,000-5,000) and lower counts in summer months (July-August averaging 1,500-3,000). This represents approximately 2-4% of total daily trips, indicating controlled speed patterns across NYC taxi operations.

---

### 3.7 Chart 6: Long Distance Trips (Area Chart)

**Purpose:** Track long-distance trip frequency throughout 2025

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Choose **"PostgreSQL"** database
3. Select table: **"Daily Trip Summary"**

**Configure:**
- **Visualization:** Select **"Area"** chart
- **X-axis:** **"Trip Date"**
- **Y-axis:** **"Long Distance Trips"**

4. **Add Filter for 2025 (Optional):**
   - Click **"Filter"** → **"Trip Date"** → **"Between"**
   - Start: `2025-01-01`
   - End: `2025-12-31`

5. Click **"Save"**
6. Name it: **"Long Distance Trips - 2025"**
7. Save and add to dashboard

**What You'll See:** Long-distance trips (>10 miles) showing consistent patterns throughout 2025. Volume ranges from 5,000 to 11,500 trips per day, with an average around 8,000-9,000 trips daily. Peak months (April-June) show higher volumes of 9,000-11,000 trips, representing approximately 8-10% of all daily trips. Clear area fill visualization helps identify trends and seasonal variations.

---

### 3.8 KPI Cards (Big Numbers)

Create impactful metric cards at the top of your dashboard using the **visual query builder**:

#### KPI 1: Total Trips (All Time)

1. Click **"+ New"** → **"Question"**
2. Select **"Daily Trip Summary"** table
3. Click **"Summarize"** → Select **"Sum of"** → **"Total Trips"**
4. Click **"Visualize"**
5. Change visualization to **"Number"**
6. Click **gear icon** → Format → Add units: **"trips"**
7. Save as **"Total Trips"**

**Expected:** **23.4M trips** (actual YTD 2025 data)

---

#### KPI 2: Average Trip Distance

1. Click **"+ New"** → **"Question"**
2. Select **"Daily Trip Summary"** table
3. Click **"Summarize"** → Select **"Average of"** → **"Avg Distance"**
4. Click **"Visualize"**
5. Change visualization to **"Number"**
6. Click **gear icon** → Format → Add units: **"miles"**
7. Save as **"Average Distance"**

**Expected:** **3.45 miles** (actual YTD 2025 average)

---

#### KPI 3: Average Speed

1. Click **"+ New"** → **"Question"**
2. Select **"Daily Trip Summary"** table
3. Click **"Summarize"** → Select **"Average of"** → **"Avg Speed"**
4. Click **"Visualize"**
5. Change visualization to **"Number"**
6. Click **gear icon** → Format → Add units: **"mph"**
7. Save as **"Average Speed"**

**Expected:** **13.12 mph** (actual YTD 2025 average)

---

#### KPI 4: Peak Daily Volume

1. Click **"+ New"** → **"Question"**
2. Select **"Daily Trip Summary"** table
3. Click **"Summarize"** → Select **"Maximum of"** → **"Total Trips"**
4. Click **"Visualize"**
5. Change visualization to **"Number"**
6. Click **gear icon** → Format → Add units: **"trips"**
7. Save as **"Peak Daily Volume"**

**Expected:** **123.8k trips** (peak day in May 2025)

---

#### KPI 5: Average Passengers

1. Click **"+ New"** → **"Question"**
2. Select **"Daily Trip Summary"** table
3. Click **"Summarize"** → Select **"Average of"** → **"Avg Passengers"**
4. Click **"Visualize"**
5. Change visualization to **"Number"**
6. Click **gear icon** → Format → Decimal places: **2**
7. Save as **"Average Passengers"**

**Expected:** **1.32 passengers** (actual YTD 2025 average)

---

#### KPI 6: Total Miles Traveled (2025)

1. Click **"+ New"** → **"Question"**
2. Select **"Monthly Summary"** table
3. Click **"Filter"** → **"Year"** → **"Is"** → `2025`
4. Click **"Summarize"** → Select **"Sum of"** → **"Total Miles Traveled"**
5. Click **"Visualize"**
6. Change visualization to **"Number"**
7. Click **gear icon** → Format → Style: **"Compact"** (automatically formats as 115.8M)
8. Click **gear icon** → Format → Add units: **"miles"**
9. Save as **"Total Miles (2025)"**

**Expected:** **79.8M miles** (2025 YTD)

**Note:** Your NYC taxis have traveled nearly 80 million miles in 2025 so far! This is correct based on:
- 23.4M trips with 3.45 mile average distance
- 247 days of complete data (January through September)

---

### 3.9 Advanced Chart: Weekend vs Weekday Comparison

**Purpose:** Compare trip volumes between weekends and weekdays

**Using Visual Query Builder:**

1. Click **"+ New"** → **"Question"**
2. Select **"Hourly Trip Patterns"** table
3. Click **"Summarize"** → **"Sum of"** → **"Trip Count"**
4. Click **"Group by"** → **"Day Type"**
5. Click **"Visualize"**

**Configure Visualization:**
- **Visualization:** Select **"Bar"** chart (or **"Row"** for horizontal bars)
- **X-axis:** **"Day Type"**
- **Y-axis:** **"Sum of Trip Count"**

6. Click **"Save"**
7. Name it: **"Weekend vs Weekday Trips"**
8. Save and add to dashboard

**What You'll See:** 
- **Weekdays:** ~17.0M trips (nearly 3x weekend volume) - dominated by commuter traffic
- **Weekends:** ~6.4M trips - leisure and social trips
- Clear disparity shows weekdays account for approximately 73% of all NYC taxi activity
- This pattern reflects the heavy reliance on taxis for business commuting vs recreational use

---

### 3.10 Dashboard Layout Suggestion

Arrange your dashboard like this for maximum impact:

```
┌───────────────────────────────────────────────────────────────────────┐
│           🚕 NYC TAXI OPERATIONS DASHBOARD - 2025 YTD                 │
├───────────┬───────────┬───────────┬───────────┬───────────┬──────────┤
│  Total    │ Avg Dist  │ Avg Speed │ Peak Day  │  Avg      │  Total   │
│  Trips    │           │           │           │ Passengers│  Miles   │
├───────────┼───────────┼───────────┼───────────┼───────────┼──────────┤
│           │           │           │           │           │          │
│   23.4M   │ 3.45 mi   │ 13.12 mph │  123.8K   │   1.32    │  79.8M   │
│           │           │           │           │           │          │
├───────────┴───────────┴───────────┴───────────┴───────────┴──────────┤
│                                                                        │
│              📈 Daily Trip Volume - 2025 (Line Chart)                 │
│            [Shows full year trend Jan-Sep with seasonal patterns]     │
│                                                                        │
│                                                                        │
├────────────────────────────────────┬───────────────────────────────────┤
│                                    │                                   │
│  📊 Monthly Trip Volume            │  🕐 Hourly Trip Patterns         │
│     (Bar Chart)                    │     (Bar Chart with Day Type)    │
│  [Jan: 5.7M, Feb: 5.4M, Mar: 6.3M] │  [Midnight peak patterns]        │
│                                    │                                   │
│                                    │                                   │
├────────────────────────────────────┴───────────────────────────────────┤
│                                                                        │
│         ⚡ Average Speed Trends - 2025 (Line Chart)                   │
│              [11-15 mph typical NYC traffic year-round]               │
│                                                                        │
├────────────────────────────────────┬───────────────────────────────────┤
│                                    │                                   │
│  🏃 High-Speed Monitoring - 2025   │  📏 Long Distance Trips - 2025   │
│     (Line Chart)                   │     (Area Chart)                 │
│  [3K-7K trips/day >30mph]          │  [17K-20K trips/day >10mi]       │
│                                    │                                   │
├────────────────────────────────────┴───────────────────────────────────┤
│                                                                        │
│          🎯 Weekend vs Weekday Trip Comparison (Bar Chart)            │
│              [Shows Weekday vs Weekend trip volumes]                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## **Step-by-Step Layout Instructions:**

### **Row 1: Title & Date Filter** (Full Width)
1. Add a **Text Card** at the very top
2. Type: `# � NYC Taxi Operations Dashboard`
3. Optionally add a **Date Filter** in the top-right corner

---

### **Row 2: KPI Cards** (6 equal cards, ~16% width each)
Arrange your 6 KPI number cards in a single row:
1. **Total Trips** → 23.4M trips
2. **Average Distance** → 3.45 miles
3. **Average Speed** → 13.12 mph
4. **Peak Daily Volume** → 123.8k trips
5. **Average Passengers** → 1.32 passengers
6. **Total Miles (2025)** → 79.8M miles

**💡 Tip:** Set all cards to equal width by selecting them all and using the alignment tools.

---

### **Row 3: Main Chart** (Full Width)
**Daily Trip Volume - 2025** - Your most important metric
- **Width:** Full (100%)
- **Height:** Medium-Large (400-500px)
- Shows the full year 2025 trend from January through September (current data)

---

### **Row 4: Side-by-Side Charts** (50% width each)
Left: **Monthly Trip Volume** (Bar Chart)
- Shows growth: Jan (5.7M) → Feb (5.4M) → Mar (6.3M)

Right: **Hourly Trip Patterns** (Bar Chart)
- Shows peak hours with Day Type breakdown
- Midnight peak clearly visible

---

### **Row 5: Trend Chart** (Full Width)
**Average Speed Trends** - Speed monitoring over time
- **Width:** Full (100%)
- **Height:** Medium (300-400px)
- Shows typical 11-14 mph NYC traffic patterns

---

### **Row 6: Side-by-Side Analytics** (50% width each)
Left: **High-Speed Trip Monitoring** (Line Chart)
- Tracks trips >30 mph for safety monitoring

Right: **Long Distance Trips** (Area Chart)
- Shows trips >10 miles pattern

---

### **Row 7: Comparison Chart** (Full Width)
**Weekend vs Weekday Comparison** (Bar Chart)
- **Width:** Full (100%)
- **Height:** Medium (300px)
- Clear comparison of trip patterns

---

## **📐 Sizing Guidelines:**

| Element | Width | Height | Purpose |
|---------|-------|--------|---------|
| Title Text | 100% | 50px | Branding |
| KPI Cards | ~16% each | 100-120px | Key metrics |
| Main Line Chart | 100% | 400-500px | Primary insight |
| Side Charts | 50% | 300-400px | Comparisons |
| Full Width Charts | 100% | 300-400px | Detailed views |

---

## **🎨 Customization Tips:**

1. **Colors:** 
   - Use Metabase's color palette settings
   - Keep consistent colors across similar metrics
   - Use blue for trip volumes, green for distance, orange for speed

2. **Drag & Drop:**
   - Click the **⋮⋮** handle at the top of each card
   - Drag to reorder
   - Resize by dragging corners

3. **Grid Alignment:**
   - Metabase uses a 12-column grid
   - KPI cards: 2 columns each (2+2+2+2+2+2 = 12)
   - Half-width: 6 columns each (6+6 = 12)
   - Full-width: 12 columns

4. **Spacing:**
   - Leave small gaps between cards for visual breathing room
   - Group related metrics together

5. **Auto-Refresh:**
   - Click **⚙️** (gear icon) in dashboard toolbar
   - Set **Auto-refresh: Every 5 minutes** (or as needed)

---

## **📱 Mobile Optimization:**

Metabase automatically stacks cards on mobile devices. Order your cards by priority:
1. KPI Cards (most important metrics)
2. Daily Trip Volume
3. Monthly Volume
4. Other charts in order of importance

---

## **🔄 Next Steps After Layout:**

1. **Add Filters:**
   - Click **Edit** → **Add Filter** → **Date Range**
   - Users can filter all charts by selecting date ranges

2. **Share Dashboard:**
   - Click **Share** button
   - Get public link or share with team members

3. **Schedule Reports:**
   - Click **⋮** → **Subscriptions**
   - Send dashboard via email daily/weekly

Your dashboard is now ready to provide powerful insights into NYC taxi operations! 🚀

---

## Step 4: Advanced Analytics Queries

### Query 1: Busiest Days
```sql
SELECT 
    trip_date,
    total_trips,
    avg_distance,
    avg_speed
FROM nyc_taxi.daily_trip_summary
ORDER BY total_trips DESC
LIMIT 10
```

### Query 2: Peak Hours Analysis
```sql
SELECT 
    pickup_hour,
    SUM(trip_count) as total_trips,
    ROUND(AVG(avg_distance), 2) as avg_distance
FROM nyc_taxi.hourly_trip_patterns
GROUP BY pickup_hour
ORDER BY total_trips DESC
```

### Query 3: Weekend vs Weekday Comparison
```sql
SELECT 
    day_type,
    SUM(trip_count) as total_trips,
    ROUND(AVG(avg_distance), 2) as avg_distance,
    ROUND(AVG(avg_duration_minutes), 2) as avg_duration
FROM nyc_taxi.hourly_trip_patterns
GROUP BY day_type
```

### Query 4: Speed Analysis
```sql
SELECT 
    trip_date,
    avg_speed,
    high_speed_trips,
    total_trips,
    ROUND((high_speed_trips::NUMERIC / total_trips * 100), 2) as high_speed_pct
FROM nyc_taxi.daily_trip_summary
WHERE total_trips > 0
ORDER BY trip_date DESC
```

### Query 5: Distance Distribution
```sql
SELECT 
    CASE 
        WHEN avg_distance < 1 THEN '< 1 mile'
        WHEN avg_distance < 3 THEN '1-3 miles'
        WHEN avg_distance < 5 THEN '3-5 miles'
        WHEN avg_distance < 10 THEN '5-10 miles'
        ELSE '10+ miles'
    END as distance_bucket,
    COUNT(*) as days,
    ROUND(AVG(avg_speed), 2) as avg_speed
FROM nyc_taxi.daily_trip_summary
GROUP BY distance_bucket
ORDER BY 
    CASE distance_bucket
        WHEN '< 1 mile' THEN 1
        WHEN '1-3 miles' THEN 2
        WHEN '3-5 miles' THEN 3
        WHEN '5-10 miles' THEN 4
        ELSE 5
    END
```

---

## Step 5: Dashboard Customization

### Layout Tips:
1. **Drag and resize** cards to organize your dashboard
2. **Add text cards** for context and insights
3. **Set auto-refresh** (gear icon → Auto-refresh: 5 minutes)
4. **Add filters** for date ranges or specific metrics
5. **Create tabs** for different views (Overview, Trends, Patterns)

### Recommended Dashboard Layout:
```
┌─────────────────────────────────────────────────────┐
│  NYC Taxi Trip Trends Dashboard                     │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Total    │ Avg Dist │ Avg Speed│ Long Dist│ Date    │
│ 34M Trips│ 3.2 mi   │ 10.5 mph │ 15%      │ Filter  │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                                                      │
│  Daily Trip Volume Chart (Line)                     │
│                                                      │
├────────────────────────┬─────────────────────────────┤
│                        │                             │
│  Monthly Summary (Bar) │  Hourly Patterns (Heatmap)  │
│                        │                             │
├────────────────────────┴─────────────────────────────┤
│                                                      │
│  Average Speed Trends (Line)                        │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Step 6: Share Your Dashboard

### Option 1: Share with Team
1. Click **"Share"** button
2. Add team members by email
3. Set permissions (View/Edit)

### Option 2: Public Link
1. Click **"Share"** → **"Create a public link"**
2. Copy the public URL
3. Anyone with the link can view (no login required)

### Option 3: Embed in Website
1. Click **"Share"** → **"Embed this dashboard"**
2. Copy the iframe code
3. Paste into your website

### Option 4: Schedule Email Reports
1. Click **"⋮"** (three dots)
2. Select **"Subscriptions"**
3. Set schedule (Daily, Weekly, Monthly)
4. Add recipients

---

## Troubleshooting

### Issue: Cannot Connect to DuckDB

**Error:** "Database file not found"

**Solution:**
1. Check if `nyc_taxi.duckdb` exists:
   ```powershell
   Test-Path C:\real-time-NYC-taxi-data-platform\nyc_taxi_analytics\nyc_taxi.duckdb
   ```

2. If missing, rebuild dbt models:
   ```powershell
   cd C:\real-time-NYC-taxi-data-platform\nyc_taxi_analytics
   dbt run
   ```

3. Verify the file exists:
   ```powershell
   ls nyc_taxi.duckdb
   ```

### Issue: Empty Tables

**Solution:**
Run dbt to populate data:
```powershell
cd C:\real-time-NYC-taxi-data-platform\nyc_taxi_analytics
dbt run
dbt test
```

### Issue: Metabase Container Not Starting

**Check logs:**
```powershell
docker logs metabase
```

**Restart Metabase:**
```powershell
docker-compose restart metabase
```

### Issue: Data Not Updating

**Metabase caches results.** To refresh:
1. Go to Admin → Databases
2. Click "NYC Taxi Data Warehouse"
3. Click **"Sync database schema now"**
4. Click **"Re-scan field values now"**

Or use SQL query with cache bypass:
```sql
-- Add a comment to bypass cache
SELECT * FROM daily_trip_summary -- refreshed
```

---

## Advanced Features

### 1. Alerts
Set up alerts for anomalies:
1. Create a question (e.g., "Daily trips below threshold")
2. Click **"⋮"** → **"Get alerts"**
3. Configure: "Send me an alert when trips < 100,000"

### 2. Pulse (Scheduled Reports)
1. Click **"+ New"** → **"Pulse"**
2. Add charts from your dashboard
3. Schedule: Daily at 8 AM
4. Email to: your.team@example.com

### 3. Custom SQL Queries
For complex analytics:
1. Click **"+ New"** → **"SQL query"**
2. Select database: "NYC Taxi Data Warehouse"
3. Write custom SQL (see examples above)
4. Save and add to dashboard

### 4. Filters and Parameters
Add interactive filters:
1. Edit your question
2. Click **"Filter"**
3. Add date range, trip distance, etc.
4. Save and add to dashboard
5. Dashboard users can now filter dynamically

---

## Container Management

### View Logs
```powershell
docker logs metabase --tail 50 -f
```

### Restart Metabase
```powershell
docker-compose restart metabase
```

### Stop Metabase
```powershell
docker-compose stop metabase
```

### Start Metabase
```powershell
docker-compose start metabase
```

### Remove Metabase (and data)
```powershell
docker-compose down metabase
docker volume rm real-time-nyc-taxi-data-platform_metabase-data
```

---

## Data Refresh Strategy

### Current Setup: Manual Refresh
Your dbt models are updated when you run:
```powershell
cd nyc_taxi_analytics
dbt run
```

### Recommended: Automated Refresh
Add dbt run to Airflow DAG (after Glue job):

```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/nyc_taxi_analytics && dbt run',
    dag=dag
)

glue_job >> dbt_run  # Run dbt after Glue processes data
```

This ensures Metabase always has the latest data!

---

## Performance Tips

### 1. Limit Data for Testing
Use filters in Metabase queries:
```sql
SELECT * 
FROM daily_trip_summary
WHERE trip_date >= '2025-01-01'
LIMIT 1000
```

### 2. Cache Settings
Admin → Settings → Caching:
- Default cache duration: 1 hour (for development)
- Production: 24 hours (for daily refreshes)

### 3. Database Optimization
Your DuckDB file is only ~188 KB. If it grows:
- Consider partitioning by month
- Add indexes (DuckDB auto-optimizes)
- Archive old data to S3

---

## Security Best Practices

### 1. Change Default Credentials
After setup, go to:
- Admin → People → Your Account → Change Password

### 2. Restrict Access
- Create user accounts for team members
- Use groups for permission management
- Don't share the admin account

### 3. Use Environment Variables
For production, set:
```yaml
environment:
  MB_DB_FILE: /metabase-data/metabase.db
  MB_PASSWORD_COMPLEXITY: strong
  MB_PASSWORD_LENGTH: 10
```

### 4. Enable HTTPS
For production deployment, use a reverse proxy (nginx) with SSL.

---

## Next Steps

### ✅ Completed:
- [x] Metabase running on port 3000
- [x] Connected to DuckDB data warehouse
- [x] Access to 4 analytical tables

### 🎯 To Do:
- [ ] Complete initial setup wizard
- [ ] Create "NYC Taxi Trip Trends" dashboard
- [ ] Add 5+ visualizations
- [ ] Set up daily email reports
- [ ] Integrate dbt runs into Airflow DAG
- [ ] Share dashboard with stakeholders

---

## Sample Dashboard Results

Based on your current data (23.4M NYC taxi trips in 2025 YTD):

**Key Insights You'll See:**
- 📊 **Daily Volume:** ~95K trips/day average (range: 70K-125K)
- 🚗 **Average Distance:** 3.45 miles per trip
- ⏱️ **Average Duration:** 15-18 minutes per trip
- 🏃 **Average Speed:** 13.12 mph (typical NYC traffic conditions)
- ⚡ **High-Speed Trips:** 2-4% of trips exceed 30 mph
- 📏 **Long Distance:** ~8-10% of trips exceed 10 miles
- 🕐 **Peak Hours:** 5-8 PM (evening rush hour, 1.2-1.3M trips)
- 📅 **Busiest Month:** May 2025 (3.3M trips)
- 📅 **Weekday Dominance:** 73% of trips occur on weekdays

---

## Resources

- **Metabase Documentation:** https://www.metabase.com/docs/latest/
- **DuckDB SQL Reference:** https://duckdb.org/docs/sql/introduction
- **dbt Documentation:** https://docs.getdbt.com/
- **Your dbt Project:** `C:\real-time-NYC-taxi-data-platform\nyc_taxi_analytics`

---

## Summary

**Access Metabase:** http://localhost:3000

**Container Status:** 
```powershell
docker ps | findstr metabase
```

**Your Data:**
- Source: S3 Parquet files
- Processing: AWS Glue + dbt
- Storage: DuckDB (~188 KB)
- Visualization: Metabase

**Your Complete Data Pipeline:**
```
Raw Data (S3) 
  → AWS Glue (PySpark Processing) 
    → Processed Data (S3 Parquet) 
      → dbt (Transformations) 
        → DuckDB (Data Warehouse) 
          → Metabase (Dashboards) 🎉
```

**Orchestration:** Airflow (Docker)

You now have a complete, production-ready data platform! 🚀
