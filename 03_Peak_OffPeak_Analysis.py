
# ============================================================
# SCRIPT 03: MBTA Peak vs Off-Peak Analysis - 2026
# Platform: Microsoft Fabric / PySpark
# ============================================================

from pyspark.sql import functions as F

BASE = "Files/analysis_2026/peak_analysis"

# 1. Set timezone
spark.conf.set(
    "spark.sql.session.timeZone",
    "America/New_York"
)

# 2. Load 2026 data
df = spark.table("dbo.subway_performance_2026")

total_records = df.count()

# 3. Create event timestamp
df = df.withColumn(
    "event_timestamp",
    F.coalesce(
        F.col("stop_timestamp"),
        F.col("move_timestamp")
    ).cast("long")
)

# Keep records with valid timestamps
df = df.filter(
    F.col("event_timestamp").isNotNull()
)

# Convert Unix timestamp to local datetime
df = df.withColumn(
    "event_datetime",
    F.from_unixtime("event_timestamp").cast("timestamp")
)

# 4. Extract time features
df = (
    df.withColumn("hour", F.hour("event_datetime"))
      .withColumn("event_date", F.to_date("event_datetime"))
      .withColumn("day_of_week", F.dayofweek("event_datetime"))
)

# dayofweek:
# 1 = Sunday, 7 = Saturday
df = df.withColumn(
    "day_type",
    F.when(
        F.col("day_of_week").isin(1, 7),
        "Weekend"
    ).otherwise("Weekday")
)

# 5. Classify time periods
df = df.withColumn(
    "period_detail",
    F.when(
        (F.col("day_type") == "Weekday") &
        F.col("hour").between(7, 9),
        "Morning Peak"
    )
    .when(
        (F.col("day_type") == "Weekday") &
        F.col("hour").between(16, 18),
        "Evening Peak"
    )
    .otherwise("Off-Peak")
)

df = df.withColumn(
    "period_type",
    F.when(
        F.col("period_detail") == "Off-Peak",
        "Off-Peak"
    ).otherwise("Peak")
)

# 6. Peak vs Off-Peak comparison
peak_comparison = (
    df.groupBy("period_type")
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.countDistinct("stop_id").alias("total_stops"),

        F.avg(
            F.when(F.col("dwell_time_seconds") > 0,
                   F.col("dwell_time_seconds"))
        ).alias("avg_dwell_time_seconds"),

        F.avg(
            F.when(F.col("headway_trunk_seconds") > 0,
                   F.col("headway_trunk_seconds"))
        ).alias("avg_headway_seconds"),

        F.avg(
            F.when(F.col("travel_time_seconds") > 0,
                   F.col("travel_time_seconds"))
        ).alias("avg_travel_time_seconds")
    )
)

# 7. Morning / Evening / Off-Peak comparison
period_detail_summary = (
    df.groupBy("period_detail")
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.avg(
            F.when(F.col("dwell_time_seconds") > 0,
                   F.col("dwell_time_seconds"))
        ).alias("avg_dwell_time_seconds"),

        F.avg(
            F.when(F.col("headway_trunk_seconds") > 0,
                   F.col("headway_trunk_seconds"))
        ).alias("avg_headway_seconds")
    )
)

# 8. Hourly analysis
hourly_summary = (
    df.groupBy("hour")
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.avg(
            F.when(F.col("dwell_time_seconds") > 0,
                   F.col("dwell_time_seconds"))
        ).alias("avg_dwell_time_seconds"),

        F.avg(
            F.when(F.col("headway_trunk_seconds") > 0,
                   F.col("headway_trunk_seconds"))
        ).alias("avg_headway_seconds")
    )
    .orderBy("hour")
)

# 9. Route-level peak analysis
route_peak_summary = (
    df.groupBy(
        "route_id",
        "period_type"
    )
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.avg(
            F.when(F.col("dwell_time_seconds") > 0,
                   F.col("dwell_time_seconds"))
        ).alias("avg_dwell_time_seconds"),

        F.avg(
            F.when(F.col("headway_trunk_seconds") > 0,
                   F.col("headway_trunk_seconds"))
        ).alias("avg_headway_seconds")
    )
)

# 10. Display results
print("========== PEAK VS OFF-PEAK ==========")
display(peak_comparison)

print("========== MORNING / EVENING / OFF-PEAK ==========")
display(period_detail_summary)

print("========== HOURLY SUMMARY ==========")
display(hourly_summary)

print("========== ROUTE PEAK COMPARISON ==========")
display(route_peak_summary)

# 11. Export CSV
outputs = {
    "peak_comparison": peak_comparison,
    "period_detail_summary": period_detail_summary,
    "hourly_summary": hourly_summary,
    "route_peak_summary": route_peak_summary
}

for name, result in outputs.items():
    (
        result.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(BASE + "/" + name)
    )

# 12. Generate statistical report
rows = peak_comparison.collect()
detail_rows = period_detail_summary.collect()

report = f"""
MBTA PEAK VS OFF-PEAK REPORT - 2026
====================================

DATA OVERVIEW
-------------
Original records: {total_records:,}
Records with valid event timestamps: {df.count():,}

TIME DEFINITIONS
----------------
Morning Peak: Weekdays 07:00-09:59
Evening Peak: Weekdays 16:00-18:59
Off-Peak: All other observed periods, including weekends

PEAK VS OFF-PEAK RESULTS
------------------------
"""

for r in rows:
    report += (
        f"\nPeriod: {r['period_type']}\n"
        f"Records: {r['total_records']:,}\n"
        f"Trips: {r['total_trips']:,}\n"
        f"Average dwell time: {r['avg_dwell_time_seconds']}\n"
        f"Average headway: {r['avg_headway_seconds']}\n"
    )

report += "\nDETAILED PERIOD RESULTS\n-----------------------\n"

for r in detail_rows:
    report += (
        f"\n{r['period_detail']}: "
        f"{r['total_records']:,} records, "
        f"{r['total_trips']:,} trips, "
        f"Average dwell: {r['avg_dwell_time_seconds']}, "
        f"Average headway: {r['avg_headway_seconds']}\n"
    )

report += """
INTERPRETATION
--------------
Peak and off-peak statistics describe observed operational records.
They do not directly measure passenger demand or service reliability.
Headway is based on available positive observed headway values.

Comparisons should account for missing timestamps and incomplete
coverage of the observation period.
"""

print(report)

spark.createDataFrame([(report,)], ["value"]) \
    .write.mode("overwrite").text(BASE + "/peak_report")

print("Peak analysis completed.")
print("Output folder:", BASE)
