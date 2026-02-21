# MULTI_TENANT_KERNEL

## Tenant Isolation
- Tenant identity is resolved at ingress and propagated through runtime.
- Data and policy scopes are enforced per tenant.

## Resource Management
- Scheduler and execution limits are applied per tenant profile.
- Kernel controls resource arbitration for concurrent agents.

## Policy Enforcement
- Policy bundles gate actions, tool access, and model routing.
- Violations are denied before execution dispatch.
