CREATE DATABASE IF NOT EXISTS aion;

CREATE TABLE IF NOT EXISTS aion.decisions
(
    task_id String,
    intent String,
    decision Enum8('local' = 1, 'api' = 2, 'hybrid' = 3),
    reason String,
    policy_overrides Nested(
        is_manual UInt8,
        privacy_override UInt8,
        cost_override UInt8,
        latency_override UInt8
    ),
    features Nested(
        size Nullable(Int64),
        latency_budget Nullable(Int64),
        cost_budget Nullable(Float64),
        privacy_level LowCardinality(String)
    ),
    engine_meta Nested(
        model String,
        local_module Nullable(String),
        version String
    ),
    ts_event DateTime64(3),
    _ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(ts_event)
ORDER BY (intent, ts_event)
TTL ts_event + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS aion.tasks
(
    task_id String,
    status Enum8('created' = 1, 'queued' = 2, 'running' = 3, 'succeeded' = 4, 'failed' = 5, 'timeout' = 6, 'canceled' = 7),
    agent_id Nullable(String),
    project_id Nullable(String),
    latency_ms Nullable(Int64),
    retries Int32,
    error_code Nullable(String),
    ts_event DateTime64(3),
    _ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(ts_event)
ORDER BY (task_id, ts_event)
TTL ts_event + INTERVAL 90 DAY;

CREATE TABLE IF NOT EXISTS aion.metrics
(
    component LowCardinality(String),
    cpu Float64,
    mem_mb Float64,
    gpu_util Nullable(Float64),
    queue_depth Nullable(Int32),
    rps Float64,
    p95_ms Float64,
    ts_event DateTime64(3),
    _ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(ts_event)
ORDER BY (component, ts_event)
TTL ts_event + INTERVAL 90 DAY;

CREATE TABLE IF NOT EXISTS aion.audit
(
    actor_id String,
    entity_type String,
    entity_id String,
    action String,
    meta Map(String, String),
    ts_event DateTime64(3),
    _ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(ts_event)
ORDER BY (actor_id, ts_event)
TTL ts_event + INTERVAL 180 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS aion.mv_router_daily
ENGINE = SummingMergeTree
PARTITION BY toYYYYMMDD(ts_event)
ORDER BY (intent, decision)
AS
SELECT
    intent,
    decision,
    toStartOfDay(ts_event) AS ts_event,
    count() AS total,
    sum(features_latency_budget) AS total_latency_budget,
    sum(features_cost_budget) AS total_cost_budget
FROM
(
    SELECT
        intent,
        decision,
        ts_event,
        coalesce(features.latency_budget[1], 0) AS features_latency_budget,
        coalesce(features.cost_budget[1], 0.0) AS features_cost_budget
    FROM aion.decisions
)
GROUP BY intent, decision, ts_event;
