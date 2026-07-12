from __future__ import annotations

import pytest

from control.orchestration import Dag, ResourceRequest, Scheduler, TaskNode, TaskSpec


def test_dag_returns_stable_topological_order() -> None:
    dag = Dag()
    dag.add(TaskNode("publish", {"test", "build"}))
    dag.add(TaskNode("test", {"build"}))
    dag.add(TaskNode("build"))
    dag.add(TaskNode("audit", {"build"}))

    assert dag.topological() == ["build", "audit", "test", "publish"]


def test_dag_rejects_duplicate_unknown_self_and_cycle() -> None:
    dag = Dag()
    dag.add(TaskNode("one"))
    with pytest.raises(ValueError, match="duplicate"):
        dag.add(TaskNode("one"))

    missing = Dag()
    missing.add(TaskNode("one", {"missing"}))
    with pytest.raises(ValueError, match="unknown task dependencies: missing"):
        missing.topological()

    with pytest.raises(ValueError, match="cannot depend on itself"):
        TaskNode("one", {"one"})

    cyclic = Dag()
    cyclic.add(TaskNode("one", {"two"}))
    cyclic.add(TaskNode("two", {"one"}))
    with pytest.raises(ValueError, match="cycle detected"):
        cyclic.topological()


def test_task_and_resource_validation() -> None:
    with pytest.raises(ValueError, match="cpu_millis"):
        ResourceRequest(0, 128, False)
    with pytest.raises(ValueError, match="memory_mb"):
        ResourceRequest(100, 0, False)
    with pytest.raises(ValueError, match="task_id"):
        TaskSpec("", "tenant-1", ResourceRequest(100, 128, False))
    with pytest.raises(ValueError, match="tenant_id"):
        TaskSpec("task-1", "", ResourceRequest(100, 128, False))


@pytest.mark.asyncio
async def test_scheduler_preserves_resource_priority_with_stable_tie_break() -> None:
    scheduler = Scheduler()
    tasks = [
        TaskSpec("cpu-large", "tenant-1", ResourceRequest(500, 512, False)),
        TaskSpec("gpu-b", "tenant-1", ResourceRequest(100, 256, True)),
        TaskSpec("gpu-a", "tenant-2", ResourceRequest(100, 256, True)),
        TaskSpec("cpu-small", "tenant-2", ResourceRequest(100, 128, False)),
    ]

    result = await scheduler.schedule(tasks)

    assert [task.task_id for task in result] == ["gpu-a", "gpu-b", "cpu-small", "cpu-large"]


@pytest.mark.asyncio
async def test_scheduler_rejects_duplicate_task_ids() -> None:
    scheduler = Scheduler()
    request = ResourceRequest(100, 128, False)

    with pytest.raises(ValueError, match="duplicate task_id"):
        await scheduler.schedule(
            [
                TaskSpec("same", "tenant-1", request),
                TaskSpec("same", "tenant-2", request),
            ]
        )


def test_legacy_orchestration_modules_export_canonical_types() -> None:
    from orchestration.dag import Dag as LegacyDag
    from orchestration.scheduler import Scheduler as LegacyScheduler

    assert LegacyDag is Dag
    assert LegacyScheduler is Scheduler
