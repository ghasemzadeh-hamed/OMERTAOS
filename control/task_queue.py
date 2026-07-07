"""Bounded in-memory queue for tests and single-process development.

Production scheduling is designed around durable tenant-partitioned leases. This
module preserves the historical import without pretending to be that scheduler.
"""
from __future__ import annotations

import itertools
import queue
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass(slots=True)
class Task:
    task_id: str
    payload: Dict[str, Any]
    queue: str = "standard"
    priority: int = 5
    callback: Optional[Callable[[Dict[str, Any]], Any]] = None
    tenant_id: str = "default"


@dataclass(order=True, slots=True)
class _QueueItem:
    priority: int
    sequence: int
    task: Task | None = field(compare=False)


class TaskQueue:
    def __init__(self, worker_threads: int = 2, max_size: int = 1024) -> None:
        if worker_threads < 1:
            raise ValueError("worker_threads must be greater than zero")
        self._queue: queue.PriorityQueue[_QueueItem] = queue.PriorityQueue(maxsize=max_size)
        self._sequence = itertools.count()
        self._closed = False
        self._metrics_lock = threading.Lock()
        self._metrics: Dict[str, int] = {"queued": 0, "completed": 0, "failed": 0}
        self._workers = [
            threading.Thread(target=self._consume, name=f"task-queue-{index}", daemon=True)
            for index in range(worker_threads)
        ]
        for worker in self._workers:
            worker.start()

    def submit(self, task: Task, timeout: float | None = None) -> None:
        if self._closed:
            raise RuntimeError("task queue is shut down")
        self._queue.put(_QueueItem(task.priority, next(self._sequence), task), timeout=timeout)
        self._increment("queued")

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._queue.join()
        for _ in self._workers:
            self._queue.put(_QueueItem(10_000, next(self._sequence), None))
        for worker in self._workers:
            worker.join(timeout=2.0)

    def metrics(self) -> Dict[str, int]:
        with self._metrics_lock:
            return dict(self._metrics)

    def _increment(self, key: str) -> None:
        with self._metrics_lock:
            self._metrics[key] += 1

    def _consume(self) -> None:
        while True:
            item = self._queue.get()
            try:
                if item.task is None:
                    return
                if item.task.callback is not None:
                    try:
                        item.task.callback(item.task.payload)
                    except Exception:
                        self._increment("failed")
                    else:
                        self._increment("completed")
            finally:
                self._queue.task_done()


__all__ = ["Task", "TaskQueue"]
