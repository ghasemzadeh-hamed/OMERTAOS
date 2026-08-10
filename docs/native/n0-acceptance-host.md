# N0 Native acceptance host

N0 creates one disposable Hyper-V acceptance VM for OMERTAOS. It does not
install OMERTAOS services, databases, migrations, or application secrets; those
operations remain separately approved N1-N8 stages.

When Hyper-V is unavailable, `deploy/native/host-sim/compose.yml` provides an
explicitly non-equivalent experimental fallback. It runs Ubuntu 24.04 with
systemd as PID 1 and cgroups v2, admits SSH only through host loopback, mounts a
clean exact-commit release snapshot read-only, and keeps the runtime network
internal. A passing simulation prepares the contracts for N1 testing but does
not close the real Hyper-V, kernel, reboot or Native host gate.

## Contract

- Ubuntu Server 24.04 LTS released cloud image, verified before extraction.
- Hyper-V generation 2 VM with 4 vCPU, static 8 GiB RAM, and a dynamic 100 GiB
  OS disk.
- Hyper-V `Default Switch` only, guest firewall default-deny inbound, and only
  rate-limited SSH admitted.
- Password and root SSH login disabled; a dedicated host-side SSH key is kept
  outside Git.
- `/etc/omertaos` exists as `0750 root:root`; application secrets are not
  created during N0.
- The exact reviewed CAPO commit is checked out detached under
  `/srv/omertaos-source` and compared to the Windows commit.
- Acceptance verifies Ubuntu version, systemd as PID 1, cgroups v2, SSH,
  firewall, repository SHA, secret-directory ownership, and root filesystem.
- A checkpoint is created only after every remote validation passes.

## Provisioner

Run `deploy/native/host/New-OmertaN0Host.ps1` from elevated PowerShell with the
verified Ubuntu Azure VHD archive, exact release commit, and a public SSH key.
The script fails closed if the image hash differs, the restricted switch is
missing, or a VM/destination disk already exists. It never deletes or replaces
an existing VM.

Runtime evidence is written outside Git to
`E:\Hyper-V\OMERTAOS-N0\evidence\n0-result.json`. This document is updated with
the non-secret evidence after the live N0 run.

## Experimental Docker fallback

Run `host-sim/Invoke-N0Simulation.ps1 -CommitSha <full-sha>`. It creates a
dedicated SSH key and clean release clone outside Git, renders Compose, builds
the Ubuntu image, waits for health, then validates both inside the container and
through SSH. The healthy container remains running for the next explicitly
approved test stage. Evidence is stored below
`E:\Hyper-V\OMERTAOS-N0-SIM\evidence`.

Simulation status is always reported as `passed-simulated`; it must never be
reported as passed Hyper-V or reboot acceptance.

## Current experimental result

Date: 2026-08-10 (Asia/Tehran)

Status: **passed-simulated; ready for N1 contract testing**

- Docker Desktop Linux engine built the pinned `ubuntu:24.04` image as Ubuntu
  24.04.4 LTS.
- The acceptance host and unprivileged SSH relay are both healthy.
- systemd is PID 1 and `/sys/fs/cgroup` reports `cgroup2fs`.
- SSH is active only through `127.0.0.1:2222`; the acceptance host itself stays
  on an internal Docker network.
- The exact clean CAPO release clone is mounted read-only and its full Git SHA
  is checked during bootstrap and over SSH.
- `/etc/omertaos` is `0750 root:root`; no application secret was created.
- Exact commit, image ID, container ID and remote evidence are recorded outside
  Git in the phase-specific JSON evidence file.

Hyper-V resource sizing, a real Linux kernel boundary, boot/reboot recovery and
snapshot acceptance remain **not run**. N1 may use this host only for
experimental contract validation and must preserve that qualification.

## Rollback

N0 rollback is intentionally manual: stop the disposable VM and retain its
checkpoint, disks, verified source archive, SSH key and evidence until human
review. Deleting the VM or its files requires separate explicit approval.
