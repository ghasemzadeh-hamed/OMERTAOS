ALTER TABLE IF EXISTS tasks ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE IF EXISTS task_results ADD COLUMN IF NOT EXISTS tenant_id TEXT;
CREATE INDEX IF NOT EXISTS idx_tasks_tenant_id_task_id ON tasks(tenant_id, task_id);
CREATE INDEX IF NOT EXISTS idx_results_tenant_id_task_id ON task_results(tenant_id, task_id);
