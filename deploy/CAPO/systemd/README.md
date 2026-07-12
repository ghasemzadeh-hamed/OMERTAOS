# CAPO systemd units

The isolated `omertaos-*` units and aggregate `omertaos.target` use the non-root
`omertaos` account, require `/etc/omertaos/omertaos.env`, and implement the
audited Runtime -> Control -> Gateway -> Console ordering. PostgreSQL and Redis
must be ready before Control. Every application service is `PartOf` the target,
so stopping the target stops the complete application stack without stopping or
altering the data services.

Failures restart at most three times per 60-second window with a five-second
delay. Runtime receives configuration only through its supported environment
variables; no unsupported CLI flags are used. Install these files with
`../scripts/setup-systemd.sh`, then start or stop them through the lifecycle
scripts. Native verification remains pending on a supported Linux host.
