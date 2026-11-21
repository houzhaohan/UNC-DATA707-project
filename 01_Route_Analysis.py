
# ============================================================
# SCRIPT 01: MBTA Route Performance Analysis - 2026
# Platform: Microsoft Fabric / PySpark
# ============================================================

from pyspark.sql import functions as F

BASE = "Files/analysis_2026/route_analysis"

# 1. Load 2026 data
df = spark.table("dbo.subway_performance_2026")
routes = spark.table("dbo.lamp_static_routes")

total_records = df.count()

# 2. Prepare route dimension
route_dim = (
    routes
    .groupBy("route_id")
    .agg(
        F.first("route_short_name", ignorenulls=True).alias("route_short_name"),
        F.first("route_long_name", ignorenulls=True).alias("route_long_name"),
        F.first("route_type", ignorenulls=True).alias("route_type")
    )
)

# 3. Define analysis route
df = df.withColumn(
    "analysis_route_id",
    F.coalesce("trunk_route_id", "route_id")
)

# Join route information
df = df.join(
    route_dim.withColumnRenamed("route_id", "analysis_route_id"),
    on="analysis_route_id",
    how="left"
)

df = df.withColumn(
    "route_name",
    F.coalesce("route_long_name", "route_short_name",
               "analysis_route_id")
)

# 4. Route-level statistical analysis
route_summary = (
    df.groupBy("analysis_route_id", "route_name")
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.countDistinct("stop_id").alias("total_stops"),

        F.avg(
            F.when(F.col("travel_time_seconds") > 0,
                   F.col("travel_time_seconds"))
        ).alias("avg_travel_time_seconds"),

        F.avg(
            F.when(F.col("dwell_time_seconds") > 0,
                   F.col("dwell_time_seconds"))
        ).alias("avg_dwell_time_seconds"),

        F.avg(
            F.when(F.col("headway_trunk_seconds") > 0,
                   F.col("headway_trunk_seconds"))
        ).alias("avg_headway_trunk_seconds"),

        F.avg(
            F.when(F.col("headway_branch_seconds") > 0,
                   F.col("headway_branch_seconds"))
        ).alias("avg_headway_branch_seconds")
    )
    .withColumn(
        "avg_travel_time_minutes",
        F.col("avg_travel_time_seconds") / 60
    )
    .withColumn(
        "avg_dwell_time_minutes",
        F.col("avg_dwell_time_seconds") / 60
    )
    .orderBy(F.desc("total_records"))
)

# 5. Display results
print("========== ROUTE PERFORMANCE SUMMARY ==========")
print("Total records:", total_records)

display(route_summary)

# 6. Export CSV
(
    route_summary.coalesce(1)
    .write.mode("overwrite")
    .option("header", True)
    .csv(BASE + "/route_summary")
)

# 7. Generate statistical report
route_count = route_summary.count()

valid_travel = route_summary.filter(
    F.col("avg_travel_time_seconds").isNotNull()
).count()

valid_dwell = route_summary.filter(
    F.col("avg_dwell_time_seconds").isNotNull()
).count()

top_routes = route_summary.select(
    "route_name", "total_records", "total_trips"
).limit(10).collect()

report = f"""
MBTA ROUTE PERFORMANCE REPORT - 2026
=====================================

DATA OVERVIEW
-------------
Total records: {total_records:,}
Number of routes: {route_count}

METRIC COVERAGE
---------------
Routes with valid average travel time: {valid_travel}
Routes with valid average dwell time: {valid_dwell}

TOP ROUTES BY RECORD COUNT
--------------------------
"""

for i, r in enumerate(top_routes, 1):
    report += (
        f"{i}. {r['route_name']}: "
        f"{r['total_records']:,} records, "
        f"{r['total_trips']:,} trips\n"
    )

report += """
INTERPRETATION
--------------
Record count reflects observed data volume, not passenger ridership.
Average travel time and dwell time are reported only where valid
positive observations are available.

See route_summary for detailed statistics.
"""

print(report)

spark.createDataFrame([(report,)], ["value"]) \
    .write.mode("overwrite").text(BASE + "/route_report")

print("Route analysis completed.")
print("Output folder:", BASE)
