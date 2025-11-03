"""Distributed task queue abstraction for the control plane."""
from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task: "Task" = field(compare=False)
    created_at: float = field(default_factory=time.time, compare=False)


@dataclass
class Task:
    """Represents a queued task."""

    task_id: str
    payload: Dict[str, Any]
    queue: str = "standard"
    priority: int = 5
    callback: Optional[Callable[[Dict[str, Any]], Any]] = None


class TaskQueue:
    """Thread-safe in-memory task queue with callback support."""

    def __init__(self, worker_threads: int = 2) -> None:
        self._queue: "queue.PriorityQueue[PrioritizedTask]" = queue.PriorityQueue()
        self._stop = threading.Event()
        self._workers: list[threading.Thread] = []
        self._metrics: Dict[str, int] = {"queued": 0, "completed": 0, "failed": 0}
        for index in range(worker_threads):
            worker = threading.Thread(target=self._consume, name=f"task-queue-{index}", daemon=True)
            worker.start()
            self._workers.append(worker)

    def submit(self, task: Task) -> None:
        self._metrics["queued"] += 1
        prioritized = PrioritizedTask(priority=task.priority, task=task)
        self._queue.put(prioritized)

    def shutdown(self) -> None:
        self._stop.set()
        for _ in self._workers:
            self._queue.put(PrioritizedTask(priority=10, task=Task("__shutdown__", {})))
        for worker in self._workers:
            worker.join(timeout=2.0)

    def metrics(self) -> Dict[str, int]:
        return dict(self._metrics)

    def _consume(self) -> None:
        while not self._stop.is_set():
            prioritized = self._queue.get()
            task = prioritized.task
            if task.task_id == "__shutdown__":
                self._queue.task_done()
                break
            if task.callback:
                try:
                    task.callback(task.payload)
                    self._metrics["completed"] += 1
                except Exception:  # pragma: no cover - logging hook
                    self._metrics["failed"] += 1
            self._queue.task_done()


__all__ = ["TaskQueue", "Task"]
