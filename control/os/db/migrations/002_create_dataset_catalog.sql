CREATE TABLE IF NOT EXISTS dataset_catalog (
    dataset_id SERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    mapping_json JSONB NOT NULL,
    storage_location JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dataset_catalog_tenant ON dataset_catalog (tenant_id);
