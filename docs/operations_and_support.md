# Operations & Support Review

## 1. Runbook / SOP for Day-to-Day Operations

### SOP: Start/Stop Core Services
- **Purpose:** Controlled start/stop of gateway, control plane, data services (PostgreSQL/Redis/Kafka/MinIO), and console.
- **Responsible:** Platform SRE on-call.
- **Prerequisites:** Access to deployment cluster (kubectl/docker-compose), current `.env`/secrets synced, change window open.
- **Steps:**
  1. Announce maintenance window in #ops and status page; place systems in "maintenance" if prod.
  2. Validate health dashboards show green (baseline) and capture timestamps for post-checks.
  3. **Stop (if required):**
     - `kubectl -n aion scale deploy gateway control console --replicas=0`
     - Pause stateful deps only if necessary: `kubectl -n data scale statefulset redis-postgresql kafka minio --replicas=0` (prefer leave running).
  4. **Start:**
     - `kubectl -n data scale statefulset redis-postgresql kafka minio --replicas=1` (or desired) and wait for Ready.
     - `kubectl -n aion scale deploy gateway control console --replicas=<profile>`; confirm pods Ready.
  5. Run smoke: `curl https://<fqdn>/healthz`, `kubectl -n aion logs deploy/gateway | tail` for errors.
- **Expected outcome:** Services Running/Ready; health endpoints return 200.
- **Rollback:** Re-apply last known-good release manifest `kubectl apply -f deploy/releases/<tag>.yaml`; scale replicas back; restore saved `.env` if changed.
- **Verification:** Grafana dashboards (Gateway p95 latency, Control error rate), `kubectl get pods -n aion`, synthetic ping monitors green.

### SOP: Manual Deploy (Rolling)
- **Purpose:** Deploy tagged release when automation unavailable or change window requires manual gate.
- **Responsible:** Release engineer + SRE approver.
- **Prerequisites:** Release image signed (Cosign), manifests rendered for environment, backups for data stores.
- **Steps:**
  1. Announce deployment; create change ticket with scope and rollback plan.
  2. Validate container signatures: `cosign verify <image> --key cosign.pub`.
  3. Apply manifests: `kubectl apply -f deploy/releases/<tag>.yaml`.
  4. Monitor rollout: `kubectl -n aion rollout status deploy/gateway control console`.
  5. Run post-deploy smoke: `/healthz`, list agents `/api/agents`, console login.
- **Expected outcome:** New version serving traffic with zero 5xx spike.
- **Rollback:** `kubectl rollout undo deploy/<name>` or reapply prior manifest. Clear any incompatible config and restart pods.
- **Verification:** Compare Grafana p95/p99 vs baseline for 15m; error budget unchanged.

### SOP: Manual Rollback
- **Purpose:** Return to last stable build when incident linked to recent change.
- **Responsible:** On-call SRE; approve with incident commander (IC) for Sev1/Sev2.
- **Prerequisites:** Prior release manifest, database backup timestamp, RBAC to deploy.
- **Steps:**
  1. Notify IC and stakeholders; freeze further changes.
  2. `kubectl rollout undo deploy/gateway control console` (or apply previous manifest).
  3. Restore config map/secret versions if altered (Git tag). Recreate pods.
  4. If data migration occurred, execute rollback script or restore DB snapshot.
- **Expected outcome:** Stable version active; incident impact reduced.
- **Verification:** Traffic health restored, alert noise subsides, functional smoke passes.

### SOP Template / Checklist
- Purpose & scope
- Owner / approver
- Preconditions (backups, access, maintenance window)
- Step-by-step commands
- Validation steps (health checks, dashboards)
- Rollback steps & data considerations
- Communication (channels, status page)

### Runbook vs SOP
- **SOP:** Routine actions (start/stop, deploy) executed predictably.
- **Runbook:** Incident guides triggered by alerts or user-impact; include triage, containment, and communication flows.

## 2. Incident Management

- **Detection:** Prometheus/Alertmanager thresholds (p95 latency >3s, 5xx rate >1%, queue depth >1000), synthetic checks, log anomaly alerts, user tickets.
- **Severity levels:**
  - **Sev1 (Critical):** Complete outage/data loss/security breach; ACK <5 min, IC engaged, hourly updates.
  - **Sev2 (High):** Degraded core path (deploy agents, login) or prolonged SLA breach; ACK <10 min, updates every 30 min.
  - **Sev3 (Medium):** Minor feature impairment; ACK <30 min, daily updates.
  - **Sev4 (Low):** Cosmetic/operational questions; planned work.
- **Escalation:**
  - Page on-call SRE via PagerDuty; if no ACK in 5 min escalate to secondary then manager.
  - Engage domain SMEs: DB on-call for data issues; Security on-call for auth/policy events; Network team for ingress issues.
- **On-call / Contacts:** Weekly rotation; handoff doc recorded in on-call calendar; contacts via PagerDuty/Slack #incidents; after-hours coverage for Sev1/Sev2 only.
- **Communication:** Status page updates for Sev1/Sev2; Slack bridge with IC, scribe, comms lead; customer email templates for outages.
- **Post-incident:**
  - Within 24h: draft incident report (timeline, impact, root cause, contributing factors, actions).
  - Within 5 business days: complete RCA with 5-Whys, assign corrective actions with owners/dates, update runbooks/tests/monitors.

## 3. Playbooks for Specific Scenarios

### Database Down
- **Symptoms:** 5xx on control/gateway, DB connection errors, readiness failing.
- **Immediate actions:**
  - Declare severity (likely Sev1/Sev2); freeze deploys.
  - Check DB pod/statefulset status, storage health, recent changes.
  - Failover to replica if available; promote standby.
- **Investigation:** Inspect logs for OOM/disk, verify credentials/rotation, check connection pool saturation.
- **Mitigation:** Increase resources, restart DB pod, clear long-running queries, move traffic to healthy replica.
- **Workaround:** Reduce load via rate limiting or queue draining; switch read-only mode for console.
- **Long-term fix:** Optimize queries, add read replicas, ensure liveness probes tuned, add connection pool alarms.
- **Comms:** Status page + Slack updates every 30–60 min until resolved.

### Disk Space Full
- **Symptoms:** Node pressure alerts, failed writes/backups, pod evictions.
- **Immediate actions:**
  - Identify affected node/volume; prune container images/logs `kubectl get events` for eviction reasons.
  - Pause backups or heavy jobs; extend volume if cloud provider allows.
- **Investigation:** Locate largest consumers (logs, tmp uploads, checkpoints), check MinIO/Kafka retention settings.
- **Mitigation:** Clean old logs via retention tooling, rotate and compress; adjust TTL for ClickHouse/MinIO; rebalance pods to nodes with capacity.
- **Workaround:** Attach temporary volume; redirect logs to central store.
- **Long-term fix:** Set disk usage alerts at 70/85/95%; enforce lifecycle rules and quotas; right-size PVCs.
- **Comms:** Notify IC; document cleanup performed.

### Severe Performance Degradation
- **Symptoms:** p95 latency > SLO, queue depth rising, CPU/GPU saturated, timeouts.
- **Immediate actions:**
  - Confirm scale-out: `kubectl top pods/nodes`, check HPA events.
  - Enable/raise rate limits to protect upstreams; shed non-critical traffic.
- **Investigation:**
  - Check recent deploys/feature flags; revert if correlated.
  - Profile hot endpoints; review DB and cache hit rates; examine Kafka lag.
- **Mitigation:** Scale gateway/control pods and caches; add GPUs for heavy models; warm caches; optimize N+1 queries.
- **Workaround:** Temporarily reduce response payloads, disable expensive features, increase timeouts for internal callers.
- **Long-term fix:** Capacity model update, load tests before peak events, implement autoscaling for critical components.
- **Comms:** Regular incident channel updates; close with impact summary.

## 4. Monitoring Dashboards & Metrics

- **Tools:** Prometheus + Alertmanager + Grafana; optional Datadog/Splunk for logs; Jaeger/OTel for tracing.
- **Key metrics & thresholds (examples):**
  - Gateway/Control uptime (SLO 99.9% monthly).
  - HTTP p95 latency <3s; error rate <1%.
  - Queue depth <1000 messages; consumer lag <60s.
  - CPU <75%, memory <80% sustained; GPU <85%.
  - DB connections <80% max; replication lag <5s.
  - Object store free space >20%; disk usage alert at 70/85/95%.
- **Dashboards:**
  - **Gateway:** latency, throughput, 4xx/5xx, rate-limit hits, cache hit.
  - **Control:** task duration, policy evaluation latency, worker queue depth.
  - **Data layer:** DB health, replication lag, Redis/Kafka/MinIO status.
  - **Infrastructure:** node pressure, pod restart counts, HPA activity.
- **Ownership:** Each service team owns their panels/alerts; SRE owns platform dashboards and alert routing.
- **Reporting:** Weekly ops review of alert volume, SLO burn rate, and capacity trends.

## 5. Logging Convention

- **Format:** JSON logs with fields: `timestamp` (ISO8601), `level`, `service`, `component`, `message`, `request_id`, `trace_id`, `span_id`, `correlation_id`, `tenant_id`, `user_id` (when present), `status`, `duration_ms`, `path`, `host`, `severity_label`.
- **Levels:**
  - DEBUG (dev only), INFO (normal ops), WARN (non-blocking anomalies), ERROR (failed requests), FATAL (process abort).
- **Aggregation:** Ship via Fluent Bit/Vector to ELK or Splunk; index by service and trace_id. Retention: 7–14 days non-prod, 30–90 days prod (per security policy).
- **Usage:** Correlate requests via `trace_id`/`request_id`; derive metrics (error rate, latency) from structured logs; enable audit trails for auth/policy changes.
- **Access & Governance:** Least-privilege roles for log search; PII masking at source; rotate credentials for log sinks; ensure logs encrypted in transit and at rest.
