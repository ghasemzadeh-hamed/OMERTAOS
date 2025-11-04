import time
from typing import Any, Dict

from .self_edit import produce_self_edits
from .inner_loop import apply_updates
from .evaluate import evaluate_model
from .safety import passed_gates


async def run_job(job_id: str, jobs: Dict[str, Dict[str, Any]]):
    job = jobs[job_id]
    job["state"] = "running"
    request = job["req"]
    model_in = request["model_id"]

    edits = await produce_self_edits(model_in, request["task_id"])
    job.setdefault("events", []).append({"t": time.time(), "msg": f"self_edits={len(edits)}"})

    model_out = await apply_updates(model_in, edits, request["strategy"], request["budget"])
    job["events"].append({"t": time.time(), "msg": f"updated_model={model_out}"})

    base_eval = await evaluate_model(model_in, request["task_id"])
    new_eval = await evaluate_model(model_out, request["task_id"])
    job["eval"] = {"base": base_eval, "new": new_eval}

    ok = passed_gates(base_eval, new_eval, request["objective"])
    job["rollout"] = "canary" if ok else "blocked"
    job["model_out"] = model_out
    job["state"] = "finished"


def get_status(job_id: str, jobs: Dict[str, Dict[str, Any]]):
    job = jobs[job_id]
    return {key: job.get(key) for key in ("state", "eval", "rollout", "model_out")}
