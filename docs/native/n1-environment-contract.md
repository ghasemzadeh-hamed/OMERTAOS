# N1 Native environment contract

N1 validates the Native host boundary without installing packages, rendering
secrets, creating databases, starting OMERTAOS services, or changing systemd.

## Experimental result

The Docker-based N0 fallback is accepted for **contract testing only**. N1
checks the supported Ubuntu release and architecture, systemd as PID 1, cgroups
v2, acceptance operator, exact clean CAPO commit, empty and protected
`/etc/omertaos`, and availability of canonical ports before installation.

The declared tool policy remains Python 3.11/3.12, Node.js 22 LTS and stable
Rust. On the minimal N0 simulation these tools, the non-root `omertaos` service
account, and operational state/log/release paths are intentionally absent and
reported as deferred to N2/N4/N8. A deferred item is not reported as installed
or runtime-validated.

Run the host contract through SSH with:

```powershell
deploy/native/host-sim/Invoke-N1Simulation.ps1 -CommitSha (git rev-parse HEAD)
```

Exact non-secret output is stored outside Git under
`E:\Hyper-V\OMERTAOS-N0-SIM\evidence\n1-simulation-<commit>.json`.

## Gate semantics

`passed-contract-simulated` means the environment contract and pre-install host
boundaries are coherent and the simulator is ready for N2. It does not mean
packages, Node/Rust/Python builds, Hyper-V, reboot, Native isolation, data
services or OMERTAOS runtime have passed.

## Rollback

N1 is read-only apart from its external evidence JSON. Reverting the N1 commit
removes the validator and documentation; the healthy N0 simulation, external
SSH key and release snapshots remain intact. No database or secret rollback is
required.
