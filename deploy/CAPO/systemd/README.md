# CAPO systemd units

Phase 5 adds isolated `omertaos-*` units and `omertaos.target` here. Units use
the non-root `omertaos` account, `/etc/omertaos/omertaos.env`, bounded restart
behavior, and the audited Runtime -> Control -> Gateway -> Console ordering.
