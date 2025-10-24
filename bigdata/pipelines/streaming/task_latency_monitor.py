"""Structured Streaming job calculating rolling latency windows and pushing KPIs to ClickHouse and Redis."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import redis
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (IntegerType, LongType, StringType, StructField,
                               StructType)

CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "jdbc:clickhouse://clickhouse:9000/aion")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

KAFKA_OPTIONS: Dict[str, Any] = {
    "kafka.bootstrap.servers": os.getenv("KAFKA_BROKERS", "kafka:9092"),
    "subscribe": "aion.tasks.lifecycle",
    "startingOffsets": "latest",
    "kafka.security.protocol": "SASL_PLAINTEXT",
    "kafka.sasl.mechanism": "SCRAM-SHA-512",
    "kafka.sasl.jaas.config": "org.apache.kafka.common.security.scram.ScramLoginModule required username='%s' password='%s';"
    % (os.getenv("KAFKA_SASL_USERNAME", "router"), os.getenv("KAFKA_SASL_PASSWORD", "router-secret")),
}

SCHEMA = StructType(
    [
        StructField("task_id", StringType()),
        StructField("status", StringType()),
        StructField("agent_id", StringType()),
        StructField("project_id", StringType()),
        StructField("latency_ms", LongType()),
        StructField("retries", IntegerType()),
        StructField("error_code", StringType()),
        StructField("ts_event", LongType()),
    ]
)


def _write_batch(batch_df: DataFrame, batch_id: int) -> None:
    if batch_df.isEmpty():
        return

    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True) as client:
        for row in batch_df.collect():
            key = f"task_latency:{row.status}"
            client.hset(key, mapping={
                "latency_ms": row.latency_ms or 0,
                "retries": row.retries or 0,
                "ts_event": row.ts_event,
            })

    (batch_df.write.mode("append")
     .format("jdbc")
     .option("url", CLICKHOUSE_URL)
     .option("driver", "com.clickhouse.jdbc.ClickHouseDriver")
     .option("user", CLICKHOUSE_USER)
     .option("password", CLICKHOUSE_PASSWORD)
     .option("dbtable", "tasks")
     .save())


def main() -> None:
    spark = (
        SparkSession.builder.appName("task_latency_monitor")
        .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTITIONS", "4"))
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,ru.yandex.clickhouse:clickhouse-jdbc:0.3.2")
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

    metrics = (
        raw_stream
        .withColumn("ts", (F.col("ts_event") / 1000).cast("timestamp"))
        .groupBy(F.window("ts", "1 minute", "30 seconds"), "status")
        .agg(
            F.expr("percentile_approx(latency_ms, 0.95)").alias("p95_latency"),
            F.avg("latency_ms").alias("avg_latency"),
            F.count("task_id").alias("tasks"),
            F.sum("retries").alias("retries"),
        )
        .select(
            F.col("status"),
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "p95_latency",
            "avg_latency",
            "tasks",
            "retries",
            F.current_timestamp().alias("_ingested_at"),
        )
    )

    query = (
        metrics.writeStream.outputMode("update")
        .foreachBatch(_write_batch)
        .option("checkpointLocation", os.getenv("CHECKPOINT_PATH", "s3a://aion-processed/checkpoints/task_latency_monitor"))
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
