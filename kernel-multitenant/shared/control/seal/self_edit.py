async def produce_self_edits(model_id, task_id):
    return [
        {"type": "data_aug", "n": 128},
        {"type": "ft_cfg", "lr": 5e-5, "steps": 120, "adapter": "lora", "rank": 8}
    ]
