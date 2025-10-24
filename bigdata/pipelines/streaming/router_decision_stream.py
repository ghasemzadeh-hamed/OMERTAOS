"""Spark Structured Streaming job to land router decisions into ClickHouse and MinIO."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (DoubleType, LongType, StringType, StructField,
                               StructType)

CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "jdbc:clickhouse://clickhouse:9000/aion")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
RAW_BUCKET = os.getenv("RAW_BUCKET", "aion-raw")

KAFKA_OPTIONS: Dict[str, Any] = {
    "kafka.bootstrap.servers": os.getenv("KAFKA_BROKERS", "kafka:9092"),
    "subscribe": "aion.router.decisions",
    "startingOffsets": "latest",
    "kafka.security.protocol": "SASL_PLAINTEXT",
    "kafka.sasl.mechanism": "SCRAM-SHA-512",
    "kafka.sasl.jaas.config": "org.apache.kafka.common.security.scram.ScramLoginModule required username='%s' password='%s';"
    % (os.getenv("KAFKA_SASL_USERNAME", "router"), os.getenv("KAFKA_SASL_PASSWORD", "router-secret")),
}

SCHEMA = StructType(
    [
        StructField("task_id", StringType()),
        StructField("intent", StringType()),
        StructField("decision", StringType()),
        StructField("reason", StringType()),
        StructField(
            "policy_overrides",
            StructType(
                [
                    StructField("is_manual", StringType()),
                    StructField("privacy_override", StringType()),
                    StructField("cost_override", StringType()),
                    StructField("latency_override", StringType()),
                ]
            ),
        ),
        StructField(
            "features",
            StructType(
                [
                    StructField("size", LongType()),
                    StructField("latency_budget", LongType()),
                    StructField("cost_budget", DoubleType()),
                    StructField("privacy_level", StringType()),
                ]
            ),
        ),
        StructField(
            "engine_meta",
            StructType(
                [
                    StructField("model", StringType()),
                    StructField("local_module", StringType()),
                    StructField("version", StringType()),
                ]
            ),
        ),
        StructField("ts_event", LongType()),
    ]
)


def _write_batch(batch_df: DataFrame, batch_id: int) -> None:
    """Persist the micro-batch into ClickHouse and MinIO."""
    if batch_df.isEmpty():
        return

    transformed = batch_df.select(
        "task_id",
        "intent",
        F.lower("decision").alias("decision"),
        F.expr("substring(reason, 1, 1024)").alias("reason"),
        F.col("policy_overrides.is_manual").cast("UInt8").alias("policy_overrides.is_manual"),
        F.col("policy_overrides.privacy_override").cast("UInt8").alias("policy_overrides.privacy_override"),
        F.col("policy_overrides.cost_override").cast("UInt8").alias("policy_overrides.cost_override"),
        F.col("policy_overrides.latency_override").cast("UInt8").alias("policy_overrides.latency_override"),
        "features.size",
        "features.latency_budget",
        "features.cost_budget",
        "features.privacy_level",
        "engine_meta.model",
        "engine_meta.local_module",
        "engine_meta.version",
        (F.col("ts_event") / 1000).cast("timestamp").alias("ts_event"),
        F.current_timestamp().alias("_ingested_at"),
    )

    (transformed.write.mode("append")
     .format("jdbc")
     .option("url", CLICKHOUSE_URL)
     .option("driver", "com.clickhouse.jdbc.ClickHouseDriver")
     .option("user", CLICKHOUSE_USER)
     .option("password", CLICKHOUSE_PASSWORD)
     .option("dbtable", "decisions")
     .save())

    date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
    (transformed.write.mode("append")
     .format("parquet")
     .option("path", f"s3a://{RAW_BUCKET}/decisions/{date_prefix}")
     .save())


def main() -> None:
    spark = (
        SparkSession.builder.appName("router_decision_stream")
        .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTITIONS", "4"))
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,ru.yandex.clickhouse:clickhouse-jdbc:0.3.2")
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )

    raw_stream = (
        spark.readStream.format("kafka")
        .options(**KAFKA_OPTIONS)
        .load()
        .selectExpr("CAST(value AS STRING) AS json")
        .select(F.from_json("json", SCHEMA).alias("data"))
        .select("data.*")
    )

    query = (
        raw_stream.writeStream.outputMode("append")
        .foreachBatch(_write_batch)
        .option("checkpointLocation", os.getenv("CHECKPOINT_PATH", "s3a://aion-processed/checkpoints/router_decision_stream"))
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
