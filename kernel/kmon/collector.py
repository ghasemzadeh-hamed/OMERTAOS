"""Lightweight telemetry collector approximating KMON functionality."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict


class SystemTelemetryCollector:
    """Collects CPU, memory, IO, and network indicators from /proc."""

    def __init__(self) -> None:
        self._prev_cpu_total = None
        self._prev_cpu_idle = None
        self._prev_net = self._read_net()
        self._prev_ts = time.time()

    def snapshot(self) -> Dict[str, float]:
        cpu = self._read_cpu()
        mem = self._read_mem()
        net = self._read_net()
        disk = self._read_disk()
        now = time.time()
        delta_t = max(now - self._prev_ts, 1e-6)

        net_delta = {
            key: (net[key] - self._prev_net.get(key, 0.0)) / delta_t
            for key in net
        }
        self._prev_net = net
        self._prev_ts = now

        metrics = {
            "cpu_usage_pct": cpu,
            "mem_usage_pct": mem,
            "disk_iops": disk,
            "net_rx_bytes_per_s": net_delta.get("rx", 0.0),
            "net_tx_bytes_per_s": net_delta.get("tx", 0.0),
        }
        return metrics

    def _read_cpu(self) -> float:
        with Path("/proc/stat").open() as handle:
            line = handle.readline()
        parts = [float(p) for p in line.split()[1:]]
        idle = parts[3]
        total = sum(parts)
        if self._prev_cpu_total is None:
            self._prev_cpu_total = total
            self._prev_cpu_idle = idle
            return 0.0
        total_delta = total - self._prev_cpu_total
        idle_delta = idle - self._prev_cpu_idle
        self._prev_cpu_total = total
        self._prev_cpu_idle = idle
        if total_delta <= 0:
            return 0.0
        return max(0.0, min(100.0, (1.0 - idle_delta / total_delta) * 100.0))

    @staticmethod
    def _read_mem() -> float:
        meminfo: Dict[str, float] = {}
        with Path("/proc/meminfo").open() as handle:
            for line in handle:
                key, value, *_ = line.split()
                meminfo[key.rstrip(":")] = float(value)
        total = meminfo.get("MemTotal", 1.0)
        available = meminfo.get("MemAvailable", total)
        used = total - available
        return max(0.0, min(100.0, (used / total) * 100.0))

    @staticmethod
    def _read_net() -> Dict[str, float]:
        rx = 0.0
        tx = 0.0
        with Path("/proc/net/dev").open() as handle:
            for line in handle.readlines()[2:]:
                parts = line.split()
                if len(parts) >= 17:
                    rx += float(parts[1])
                    tx += float(parts[9])
        return {"rx": rx, "tx": tx}

    @staticmethod
    def _read_disk() -> float:
        path = Path("/proc/diskstats")
        if not path.exists():
            return 0.0
        iops = 0.0
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) < 14:
                continue
            read_ios = float(parts[3])
            write_ios = float(parts[7])
            iops += read_ios + write_ios
        return iops
