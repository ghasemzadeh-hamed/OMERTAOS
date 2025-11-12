# Enterprise profile ISO boot playbook

This guide extends the base kiosk ISO instructions for teams that need the full enterprise profile (Gateway, control plane, console, MLflow, LDAP, and the SEAL-style memory stack) to come online directly after first boot.

## Audience

- Platform engineers responsible for shipping the hardened ISO to regulated tenants.
- Site reliability teams that need deterministic, boot-to-ready timelines for the enterprise profile.
- Security leads validating that the self-adaptive SEAL services respect isolation and rollback policies.

## Prerequisites

1. Build the ISO following [`install/iso.md`](iso.md). Ensure the build host has access to:
   - `core/iso/cache/` packages mirrored for air-gapped installs.
   - The SEAL stack container images (`services/aion-memory`, `services/aion-seal-adapter`, `services/aion-model-registry`). Push them to your internal registry and mirror the digests inside `core/iso/cache/images/` if offline.
2. Export the following environment variables before running `make iso` so the profile defaults ship with enterprise toggles:
   ```bash
   export AION_PROFILE=enterprise
   export AION_ENABLE_SEAL=1
   export AION_SEAL_REGISTRY_URL="https://registry.internal/aion"
   export AION_SEAL_IMAGE_TAG="v1"
   ```
   The build embeds these values into `/etc/aionos/profile.env` for use during first boot.
3. Generate LDAP credentials, TLS bundles, and signing keys. Place them under `core/iso/secrets/enterprise/` so the wizard can copy them into `/var/lib/aionos/secrets/`.

## Image customisation

1. Update `core/iso/overlay/etc/aionos/services.d/` with systemd unit overrides that enable the SEAL services on boot:
   - `aion-memory.service`
   - `aion-seal-adapter.service`
   - `aion-model-registry.service`
   Each unit should `After=docker.service` and source `/etc/aionos/profile.env`.
2. Extend `core/iso/overlay/etc/docker/compose/enterprise.override.yml` with the three SEAL services. Mount volumes:
   - `/var/lib/aion/memory` for persisted interactions.
   - `/var/lib/aion/model-registry` for model lineage metadata.
   - `/var/lib/aion/seal-artifacts` for LoRA checkpoints.
3. Add health checks to the override file so the orchestrator routes traffic only after all SEAL services report `200` on `/healthz`.
4. Run `make iso` once more to bake the overrides and verify `core/iso/out/aionos-enterprise.iso` reports the correct build metadata with `isoinfo -d`.

## Boot and provisioning sequence

1. Boot from the USB media and wait for the Chromium kiosk to load the installer wizard.
2. On the profile step, ensure `Enterprise` is pre-selected (this comes from the environment variables baked into the ISO).
3. Toggle **Secure Boot** and **Full-disk encryption** under storage. The wizard renders both switches because the enterprise profile defaults enable them.
4. Confirm the network page shows connectivity to your internal container registry. If offline, upload the mirrored tarballs when prompted.
5. On the services screen, verify that `SEAL Memory Stack` lists the three services with the expected image tags. Override tags only if you need to hotfix specific tenants.
6. Apply disk changes by following the standard gate procedure (`export AIONOS_ALLOW_INSTALL=1`). Installation typically completes within 18 minutes on NVMe.
7. The installer drops a first-boot job under `/etc/systemd/system/aionos-firstboot.service`. Do **not** remove it—this job seeds the SEAL database schemas.

## First boot validation checklist

After the first reboot into the installed system:

1. Confirm profile selection:
   ```bash
   sudo cat /etc/aionos/profile.env
   ```
   Ensure `AION_PROFILE=enterprise` and `AION_ENABLE_SEAL=1` are present.
2. Validate container health:
   ```bash
   sudo docker compose -f /opt/aionos/docker-compose.yml --profile enterprise ps
   ```
   Look for the SEAL services in the `Up (healthy)` state.
3. Verify database migrations:
   ```bash
   sudo docker exec aion-memory psql -c "\dt"
   ```
   Tables `interactions` and `self_edits` must exist with encryption extensions loaded.
4. Check adapter schedules:
   ```bash
   sudo systemctl status aion-seal-adapter.timer
   ```
   The timer should be `active (waiting)` with a 15-minute cadence.
5. Confirm registry routing:
   ```bash
   curl -s https://localhost:7443/v1/models | jq 'map(select(.tags[] == "enterprise"))'
   ```
   Expect the base enterprise model plus the SEAL adapters registered during first boot.
6. Review `/var/log/aionos-firstboot.log` for `SEAL stack bootstrap complete` before handing off to tenant operations.

## Troubleshooting tips

- **SEAL services not starting:** Ensure the ISO shipped with `AION_ENABLE_SEAL=1` and that the compose override paths exist. Missing secrets in `/var/lib/aionos/secrets/` will cause the services to exit immediately.
- **Registry rejects uploads:** Double-check the TLS bundle copied from `core/iso/secrets/enterprise/`. A mismatch prevents the bootstrap job from registering adapters.
- **Offline installs stall on image import:** Pre-load the `*.tar.zst` images into `core/iso/cache/images/` and verify the wizard checksum step before starting the install.
- **LDAP binds failing:** Confirm the wizard copied `ldap.conf` and credentials from the secrets bundle; otherwise rerun `/opt/aionos/bin/aionos-ldap-setup`.

## Next steps

With the enterprise ISO baseline deployed, reference [`aion_seal_memory_execution_plan.md`](../aion_seal_memory_execution_plan.md) to schedule ongoing SEAL iterations and model promotion workflows.
