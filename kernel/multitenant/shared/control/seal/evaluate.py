import asyncio


async def evaluate_model(model_id, task_id):
    await asyncio.sleep(0.6)
    return {"accuracy": 0.72, "f1": 0.69, "model": model_id, "task": task_id}
