from control.task_queue import Task, TaskQueue


def test_task_queue_executes_callback() -> None:
    queue = TaskQueue(worker_threads=1)
    result = {"payload": None}

    def callback(payload):
        result["payload"] = payload

    queue.submit(Task(task_id="1", payload={"value": 5}, callback=callback, priority=0))
    queue.shutdown()
    assert result["payload"] == {"value": 5}
    metrics = queue.metrics()
    assert metrics["completed"] == 1
