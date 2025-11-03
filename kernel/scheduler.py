"""Kernel-level cooperative scheduler for agent workloads."""
from __future__ import annotations

import heapq
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass(order=True)
class ScheduledTask:
    """Represents a scheduled workload."""

    sort_index: float
    deadline: float = field(compare=False)
    priority: int = field(compare=False)
    queue: str = field(compare=False)
    callback: Callable[[], Any] = field(compare=False)
    metadata: Optional[Dict[str, Any]] = field(default=None, compare=False)


class KernelScheduler:
    """Priority-based task scheduler with cooperative execution."""

    def __init__(self, queue_weights: Optional[Dict[str, int]] = None) -> None:
        self._queue: List[ScheduledTask] = []
        self._cv = threading.Condition()
        self._stop = False
        self._weights = queue_weights or {"critical": 0, "priority": 1, "standard": 2, "review": 3, "bulk": 4}
        self._worker = threading.Thread(target=self._run, name="kernel-scheduler", daemon=True)
        self._worker.start()

    def schedule(
        self,
        *,
        queue: str,
        delay: float,
        priority: int,
        callback: Callable[[], Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Schedule a callback to execute after a delay."""
        deadline = time.time() + max(delay, 0.0)
        weight = self._weights.get(queue, 5)
        sort_index = deadline + (weight * 0.1) - (priority * 0.01)
        task = ScheduledTask(
            sort_index=sort_index,
            deadline=deadline,
            priority=priority,
            queue=queue,
            callback=callback,
            metadata=metadata,
        )
        with self._cv:
            heapq.heappush(self._queue, task)
            self._cv.notify()

    def stop(self) -> None:
        """Stop the scheduler thread."""
        with self._cv:
            self._stop = True
            self._cv.notify_all()
        self._worker.join(timeout=2.0)

    def _run(self) -> None:
        while True:
            with self._cv:
                while not self._queue and not self._stop:
                    self._cv.wait()
                if self._stop:
                    return
                task = heapq.heappop(self._queue)
                now = time.time()
                if task.deadline > now:
                    self._cv.wait(timeout=max(task.deadline - now, 0.0))
                    if self._stop:
                        return
                    heapq.heappush(self._queue, task)
                    continue
            try:
                task.callback()
            except Exception as exc:  # pragma: no cover - logging hook
                print(f"scheduler callback failed: {exc}")


__all__ = ["KernelScheduler", "ScheduledTask"]
