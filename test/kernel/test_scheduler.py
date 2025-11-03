import time

from kernel.scheduler import KernelScheduler


def test_scheduler_prefers_critical_queue() -> None:
    scheduler = KernelScheduler()
    order: list[str] = []

    def standard_callback() -> None:
        order.append("standard")

    def critical_callback() -> None:
        order.append("critical")

    scheduler.schedule(queue="standard", delay=0.05, priority=1, callback=standard_callback)
    scheduler.schedule(queue="critical", delay=0.05, priority=1, callback=critical_callback)
    time.sleep(0.2)
    scheduler.stop()
    assert order[0] == "critical"
