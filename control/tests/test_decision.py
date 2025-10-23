import pytest

from app.schemas import TaskCreate
from app.services.router import heuristic_decision


def test_heuristic_respects_preference():
    decision = heuristic_decision(TaskCreate(task_id='1', intent='anything', params={}, preferred_engine='local'))
    assert decision.decision == 'local'


def test_heuristic_summarize_local():
    decision = heuristic_decision(TaskCreate(task_id='2', intent='summarize report', params={}))
    assert decision.decision == 'local'
