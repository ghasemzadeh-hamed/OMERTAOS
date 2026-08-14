# Cluster membership

**Status:** design target; not implemented.

Membership should provide authenticated join, renewal, draining, removal, and
failure suspicion while distinguishing process failure, network delay, and
administrative isolation. The authoritative membership view belongs to
Control; Runtime supplies bounded observations.

## Required properties

- unique, stable node identities and replay-resistant registration;
- explicit states such as joining, ready, draining, suspect, and removed;
- monotonic epochs or terms for fencing stale participants;
- bounded heartbeat and suspicion windows;
- auditable administrative transitions;
- compatibility checks for contracts and isolation capabilities.

Any protocol choice must state its consistency assumptions and behavior during
network partitions. A heartbeat endpoint alone is not a membership protocol.
