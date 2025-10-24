"""Spark Structured Streaming job to compute task latency KPIs."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

LIFECYCLE_SCHEMA = StructType([
    StructField("task_id", StringType()),
    StructField("tenant_id", StringType()),
    StructField("intent", StringType()),
    StructField("status", StringType()),
    StructField("timestamp", StringType()),
    StructField("metadata", StringType()),
])


def main() -> None:
    spark = SparkSession.builder.appName("aionos-task-latency").getOrCreate()
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "aion.tasks.lifecycle")
        .load()
        .selectExpr("CAST(value AS STRING) json")
        .select(from_json(col("json"), LIFECYCLE_SCHEMA).alias("data"))
        .select("data.*")
    )

    latency_df = (
        df.where(col("status") == "OK")
        .groupBy(window(col("timestamp"), "5 minutes"), col("intent"))
        .agg(avg(col("metadata.latency_ms")).alias("latency_p95"))
    )

    query = (
        latency_df.writeStream.outputMode("update")
        .format("memory")
        .queryName("latency_metrics")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
