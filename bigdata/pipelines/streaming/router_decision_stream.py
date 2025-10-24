"""Spark Structured Streaming job to persist router decisions."""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType

ROUTER_SCHEMA = StructType([
    StructField("task_id", StringType()),
    StructField("tenant_id", StringType()),
    StructField("intent", StringType()),
    StructField("route", StringType()),
    StructField("reason", StringType()),
    StructField("tier", StringType()),
    StructField("timestamp", StringType()),
])


def main() -> None:
    spark = (
        SparkSession.builder.appName("aionos-router-decisions")
        .config("spark.sql.shuffle.partitions", 2)
        .getOrCreate()
    )

    kafka_options = {
        "kafka.bootstrap.servers": "kafka:9092",
        "subscribe": "aion.router.decisions",
        "startingOffsets": "latest",
    }

    df = (
        spark.readStream.format("kafka")
        .options(**kafka_options)
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
        .select(from_json(col("json"), ROUTER_SCHEMA).alias("data"))
        .select("data.*", current_timestamp().alias("ingested_at"))
    )

    (
        df.writeStream.outputMode("append")
        .format("parquet")
        .option("path", "s3a://aion-router-decisions/")
        .option("checkpointLocation", "/tmp/checkpoints/router_decisions")
        .start()
    )

    (
        df.writeStream.outputMode("append")
        .format("jdbc")
        .option("url", "jdbc:clickhouse://clickhouse:8123/default")
        .option("dbtable", "router_decisions")
        .option("checkpointLocation", "/tmp/checkpoints/router_decisions_clickhouse")
        .start()
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
