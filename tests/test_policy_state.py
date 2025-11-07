import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.control.app.core.state import ControlState


@pytest.mark.asyncio
async def test_policy_versioning_and_rollback():
    state = ControlState()
    base_doc = {"version": "1.0.0", "default": "local", "rules": []}
    policy = await state.set_router_policy(base_doc)
    assert policy.revision == 1
    assert policy.version == "1.0.0"
    first_checksum = policy.checksum

    updated_doc = {"version": "1.1.0", "default": "api", "rules": []}
    policy_updated = await state.set_router_policy(updated_doc)
    assert policy_updated.revision == 2
    assert policy_updated.version == "1.1.0"
    assert state.get_router_policy_history()[-1].revision == 1

    rolled_back = await state.rollback_router_policy(1)
    assert rolled_back.version == "1.0.0"
    assert rolled_back.checksum == first_checksum
    assert rolled_back.revision == 3

    with pytest.raises(ValueError):
        await state.rollback_router_policy(99)
