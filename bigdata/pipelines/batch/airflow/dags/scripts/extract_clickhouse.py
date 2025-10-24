"""Extract router decision history from ClickHouse."""
import clickhouse_driver

client = clickhouse_driver.Client(host="clickhouse", user="default", password="", database="default")
rows = client.execute("""
    SELECT task_id, intent, route, reason, tier, ingested_at
    FROM router_decisions
    WHERE ingested_at >= now() - INTERVAL 1 DAY
""")
print(f"Extracted {len(rows)} rows")
