# BIGDATA_PIPELINES

## ETL Flow
```mermaid
flowchart LR
  Sources[Operational Events] --> Stream[Streaming Pipelines]
  Sources --> Batch[Batch ETL]
  Stream --> Lake[(Storage)]
  Batch --> Lake
  Lake --> Features[Feature/Analytics Views]
  Features --> Control[Control-plane Insights]
```

## Schema Separation
- Operational schemas are separated from analytics schemas.
- Pipeline contracts provide stable ingestion and query boundaries.

## Data Storage Boundaries
- Control data and analytics data are decoupled.
- BigData jobs should not execute in control-plane request handlers.
