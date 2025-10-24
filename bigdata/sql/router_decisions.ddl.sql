CREATE TABLE IF NOT EXISTS router_decisions
(
    task_id String,
    tenant_id String,
    intent String,
    route String,
    reason String,
    tier String,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toDate(ingested_at)
ORDER BY (intent, ingested_at)
TTL ingested_at + INTERVAL 90 DAY;
