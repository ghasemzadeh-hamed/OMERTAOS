#!/usr/bin/env bash
set -euo pipefail

source /run/n0/n0.env
source /etc/os-release

[[ "$VERSION_ID" == "24.04" ]]
[[ "$(ps -p 1 -o comm=)" == "systemd" ]]
[[ "$(stat -fc %T /sys/fs/cgroup)" == "cgroup2fs" ]]
systemctl is-active --quiet omertaos-n0-sim.service
systemctl is-active --quiet ssh.service
[[ "$(stat -c '%a:%U:%G' /etc/omertaos)" == "750:root:root" ]]
[[ "$(cat /var/lib/omertaos-n0/release-commit)" == "$OMERTAOS_COMMIT_SHA" ]]
[[ -f /var/lib/omertaos-n0/ready ]]
