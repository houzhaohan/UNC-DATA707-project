
# ============================================================
# SCRIPT 02: MBTA Station Efficiency Analysis - 2026
# Platform: Microsoft Fabric / PySpark
# ============================================================

from pyspark.sql import functions as F

BASE = "Files/analysis_2026/station_analysis"

# 1. Load data
df = spark.table("dbo.subway_performance_2026")
stops = spark.table("dbo.lamp_static_stops")

total_records = df.count()

# 2. Prepare station dimension
stop_dim = (
    stops.groupBy("stop_id")
    .agg(
        F.first("stop_name", ignorenulls=True).alias("stop_name"),
        F.first("parent_station", ignorenulls=True).alias("dim_parent_station")
    )
)

# 3. Join station information
df = df.join(stop_dim, on="stop_id", how="left")

# Prefer parent_station as the station identifier
df = df.withColumn(
    "station_id",
    F.coalesce("parent_station", "dim_parent_station", "stop_id")
)

df = df.withColumn(
    "station_name",
    F.coalesce("stop_name", "station_id")
)

# 4. Station-level statistical analysis
station_summary = (
    df.groupBy("station_id", "station_name")
    .agg(
        F.count("*").alias("total_records"),

        F.countDistinct("trip_id").alias("total_trips"),

        F.countDistinct("route_id").alias("route_count"),

        F.countDistinct("stop_id").alias("platform_count"),

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
    .withColumn(
        "avg_dwell_time_minutes",
        F.col("avg_dwell_time_seconds") / 60
    )
)

# 5. Rank stations
from pyspark.sql.window import Window

w = Window.orderBy(F.desc("total_records"))

station_summary = station_summary.withColumn(
    "record_rank",
    F.row_number().over(w)
)

# 6. Top 10 stations by dwell time
top_dwell = (
    station_summary
    .filter(F.col("avg_dwell_time_seconds").isNotNull())
    .orderBy(F.desc("avg_dwell_time_seconds"))
    .limit(10)
)

# 7. Top 10 stations by record count
top_records = (
    station_summary
    .orderBy(F.desc("total_records"))
    .limit(10)
)

# 8. Display results
print("========== STATION SUMMARY ==========")
display(station_summary.orderBy(F.desc("total_records")))

print("========== TOP 10 DWELL TIME ==========")
display(top_dwell)

print("========== TOP 10 RECORD COUNT ==========")
display(top_records)

# 9. Export CSV files
outputs = {
    "station_summary": station_summary,
    "top_dwell_stations": top_dwell,
    "top_record_stations": top_records
}

for name, result in outputs.items():
    (
        result.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(BASE + "/" + name)
    )

# 10. Generate report
station_count = station_summary.count()

valid_dwell_count = station_summary.filter(
    F.col("avg_dwell_time_seconds").isNotNull()
).count()

top10 = top_dwell.collect()

report = f"""
MBTA STATION EFFICIENCY REPORT - 2026
=====================================

DATA OVERVIEW
-------------
Total records: {total_records:,}
Number of stations: {station_count:,}

DWELL TIME DATA COVERAGE
------------------------
Stations with valid dwell time: {valid_dwell_count:,}

TOP 10 STATIONS BY AVERAGE DWELL TIME
-------------------------------------
"""

for i, r in enumerate(top10, 1):
    report += (
        f"{i}. {r['station_name']}: "
        f"{r['avg_dwell_time_seconds']:.2f} seconds\n"
    )

report += """
INTERPRETATION
--------------
A longer average dwell time indicates longer observed stopping time.
It does not necessarily mean lower station efficiency because
station design, service patterns, passenger activity and data
coverage can affect dwell time.

Record count represents observed records, not passenger volume.
"""

print(report)

spark.createDataFrame([(report,)], ["value"]) \
    .write.mode("overwrite").text(BASE + "/station_report")

print("Station analysis completed.")
print("Output folder:", BASE)
