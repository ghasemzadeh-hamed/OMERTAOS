ALTER TABLE router_decisions
  MODIFY TTL event_time + toIntervalDay({ttl_days:UInt16})
  SETTINGS ttl_only_drop_parts = 1;

ALTER TABLE task_latency
  MODIFY TTL event_time + toIntervalDay({ttl_days:UInt16})
  SETTINGS ttl_only_drop_parts = 1;
